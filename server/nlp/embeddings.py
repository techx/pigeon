import json
import time

import numpy as np
import pandas as pd

import redis
import requests
from redis.commands.search.field import (
    NumericField,
    TagField,
    TextField,
    VectorField,
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from sentence_transformers import SentenceTransformer

from textwrap import TextWrapper
from server.config import RedisDocument, OpenAIMessage

import os

cwd = os.path.dirname(__file__)

VECTOR_DIMENSION = 768

# load redis client
client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# load corpus
# with open('corpus.json', 'r') as f:
#     corpus = json.load(f)

# load embedding model
embedder = SentenceTransformer('msmarco-distilbert-base-v4')

def load_corpus(corpus: list[RedisDocument]):
    """ loads given corpus into redis

    PARAMETERS
    ----------
    corpus : :obj:`list` of :obj:`RedisDocument`
        list of documents, each represented by dictionary

    RAISES
    ------
    Exception
        if failed to load corpus into redis
    """
    print("loading corpus...")

    pipeline = client.pipeline()
    for i, doc in enumerate(corpus, start=1):
        redis_key = f'documents:{i:03}'
        pipeline.json().set(redis_key, "$", doc)
    res = pipeline.execute()

    if not all(res):
        raise Exception('failed to load some documents')
    print("successfully loaded all documents")


def compute_embeddings():
    """ compute embeddings from redis documents
    """
    print("computing embeddings...")

    # get keys, questions, content
    keys = sorted(client.keys("documents:*"))
    questions = client.json().mget(keys, "$.question")
    content = client.json().mget(keys, "$.content")

    assert(len(questions) == len(content))

    # compute embeddings
    question_and_content = [questions[i][0] + " " +
                            content[i][0] for i in range(len(questions))]
    embeddings = embedder.encode(
        question_and_content).astype(np.float32).tolist()

    # save embeddings
    with open(f'{cwd}/embeddings.json', 'w') as f:
        json.dump(embeddings, f)

    VECTOR_DIMENSION = len(embeddings[0])

    print("successfully computed embeddings")
    return embeddings

def load_embeddings(embeddings : list[list[float]]):
    """ load embeddings into redis

    PARAMETERS
    ----------
    embeddings : :obj:`list` of :obj:`list` of :obj:`float`
        list of embeddings

    RAISES
    ------
    Exception
        if failed to load embeddings into redis
    """
    print("loading embeddings into redis...")

    # load embeddings into redis
    pipeline = client.pipeline()
    for i, embedding in enumerate(embeddings, start=1):
        redis_key = f'documents:{i:03}'
        pipeline.json().set(redis_key, "$.question_and_content_embeddings", embedding)
    res = pipeline.execute()
    
    if not all(res):
        raise Exception('failed to load embeddings')
    
    print("successfully loaded all embeddings")

def create_index(corpus_len : int):
    """ create search index in redis
    assumes that documents and embeddings have already been loaded into redis

    PARAMETERS
    ----------
    corpus_len : :obj:`int`
        number of documents in corpus

    RAISES
    ------
    Exception
        if failed to create index
    """
    print("creating index...")

    schema = (
        TextField("$.source", no_stem=True, as_name="source"),
        TextField("$.question", no_stem=True, as_name="question"),
        TextField("$.content", no_stem=True, as_name="content"),
        NumericField("$.sql_id", as_name="sql_id"),
        VectorField(
            "$.question_and_content_embeddings",
            "FLAT",
            {
                "TYPE": "FLOAT32",
                "DIM": VECTOR_DIMENSION,
                "DISTANCE_METRIC": "COSINE",
            },
            as_name="vector",
        ),
    )
    definition = IndexDefinition(prefix=["documents:"], index_type=IndexType.JSON)
    res = client.ft("idx:documents_vss").create_index(
        fields=schema, definition=definition
    )
    
    if (res == "OK"):
        start = time.time()
        while(1):
            if str(client.ft("idx:documents_vss").info()['num_docs']) == str(corpus_len):
                info = client.ft("idx:documents_vss").info()
                num_docs = info["num_docs"]
                indexing_failures = info["hash_indexing_failures"]
                print("num_docs", num_docs, "indexing_failures", indexing_failures)
                return
            if time.time() - start >= 60:
                raise Exception('time out')
    raise Exception('failed to create index')

def create_query(k : int):
    """ create k-NN redis query

    PARAMETERS
    ----------
    k : :obj:`int`
        number of nearest neighbors to return
    """
    return Query(f'(*)=>[KNN {k} @vector $query_vector AS vector_score]') \
        .sort_by('vector_score') \
        .return_fields('vector_score', 'source', 'question', 'content', 'sql_id') \
        .dialect(2)

def queries(query, queries : list[str]) -> list[dict]:
    """ run queries against redis

    PARAMETERS
    ----------
    query : :obj:`Query`
        redis query object
    queries : :obj:`list` of :obj:`str`
        list of question queries

    RETURNS
    -------
    :obj:`list` of :obj:`dict`
        list of dictionaries containing query and result
    """
    print("running queries...")

    # encode queries
    encoded_queries = embedder.encode(queries)

    # run queries
    results_list = []
    for i, encoded_query in enumerate(encoded_queries):
        result_docs = (
            client.ft("idx:documents_vss")
            .search(
                query,
                {
                    "query_vector": np.array(
                        encoded_query, dtype=np.float32
                    ).tobytes()
                },
            )
            .docs
        )
        query_result = []
        for doc in result_docs:
            vector_score = round(1 - float(doc.vector_score), 2)
            query_result.append(
                {
                    "score": vector_score,
                    "source": doc.source,
                    "question": doc.question,
                    "content": doc.content,
                    "sql_id": doc.sql_id,
                }
            )
        results_list.append({"query": queries[i], "result": query_result})

    print("done running query")
    return results_list

def query_all(k : int, questions : list[str]):
    """return k most similar documents for each query

    PARAMETERS
    ----------
    k : :obj:`int`
        number of nearest neighbors to return
    questions : :obj:`list` of :obj:`str`
        list of question queries
    
    RETURNS
    -------
    :obj:`list` of :obj:`dict`
        list of dictionaries containing query and result
    """
    redis_query = create_query(k)
    return queries(redis_query, questions)

def embed_corpus(corpus : list[RedisDocument]):
    """ load corpus, compute embeddings, load embeddings into redis   

    PARAMETERS
    ----------
    corpus : :obj:`list` of :obj:`dict`
        list of documents, each represented by dictionary

    RAISES
    ------
    Exception
        if failed to load corpus
    """
    # flush database
    print("cleaning database...")
    client.flushdb()
    print("done cleaning database")

    # embed corpus
    if not corpus:
        return
    load_corpus(corpus)
    embeddings = compute_embeddings()
    load_embeddings(embeddings)
    create_index(len(corpus))

def test():
    try:
        embed_corpus()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
    
    questions = ['What is the deadline to apply for the hackathon?',
               'When is HackMIT?',
               'What are the challenges?',
               'How does judging work?',
               'What building should I go to during the event?',
               'What prizes are available?',
               'How many people are allowed on a team?',
               'What is HackMIT?',
               'Can I attend HackMIT if I am an MIT grad student?',
               'Can I attend HackMIT if I am a sophomore in high school?',
               'I\'m a high school student, but I\'m really advanced. Can I attend HackMIT?',
               'Do I need to bring money to the event?',
               'Will we be able to sleep at the event?',
               'Will we be able to stay overnight at the event?',
               'What should I do if I am a beginner at the event?']
    results = query_all(3, questions)

    for result in results:
        print(result['query'])
        for doc in result['result']:
            print(f"Score: {doc['score']}")
            print(f"Source: {doc['source']}")
            print(f"Q: {doc['question']}")
            print(f"A: {doc['content']}")
        print()