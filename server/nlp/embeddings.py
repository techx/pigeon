"""Embeddings.

This module provides functions for embedding documents and querying them in Redis.
"""

import os
import time

import numpy as np
import openai
import redis
from redis.commands.search.field import (
    NumericField,
    TextField,
    VectorField,
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from server.config import REDIS_URL, RedisDocument

cwd = os.path.dirname(__file__)

VECTOR_DIMENSION = 1536

# load redis client
client = redis.Redis(host=REDIS_URL, port=6379, decode_responses=True)

# load corpus
# with open('corpus.json', 'r') as f:
#     corpus = json.load(f)

# load embedding model
# embedder = SentenceTransformer("msmarco-distilbert-base-v4")
embedding_model = "text-embedding-3-small"


def load_corpus(corpus: list[RedisDocument]):
    """Loads given corpus into redis.

    Args:
        corpus: list of documents, each represented by dictionary

    Raises:
        exception: if failed to load corpus into redis
    """
    print("loading corpus...")

    pipeline = client.pipeline()
    for i, doc in enumerate(corpus, start=1):
        redis_key = f"documents:{i:03}"
        pipeline.json().set(redis_key, "$", doc)
    res = pipeline.execute()

    if not all(res):
        raise Exception("failed to load some documents")
    print("successfully loaded all documents")


def compute_openai_embeddings(texts):
    """Compute embeddings from texts using OpenAI.

    Args:
        texts: list of texts to embed

    Returns:
        list of embeddings
    """
    embeddings = []
    for i in range(len(texts)):
        embeddings.append(
            openai.embeddings.create(input=texts[i], model=embedding_model)
            .data[0]
            .embedding
        )
    return embeddings


def compute_embeddings():
    """Compute embeddings from redis documents."""
    print("computing embeddings...")

    # get keys, questions, content
    keys = sorted(client.keys("documents:*"))  # type: ignore
    questions = client.json().mget(keys, "$.question")
    content = client.json().mget(keys, "$.content")

    assert len(questions) == len(content)

    # compute embeddings
    question_and_content = [
        questions[i][0] + " " + content[i][0]
        for i in range(len(questions))  # type: ignore
    ]

    # embeddings = embedder.encode(question_and_content).astype(np.float32).tolist()
    embeddings = compute_openai_embeddings(question_and_content)

    # save embeddings
    # with open(f"{cwd}/embeddings.json", "w") as f:
    #     json.dump(embeddings, f)

    # VECTOR_DIMENSION = len(embeddings[0])

    print("successfully computed embeddings")
    return embeddings


def load_embeddings(embeddings: list[list[float]]):
    """Load embeddings into redis.

    Args:
        embeddings:
            list of embeddings

    Raises:
        exception: if failed to load embeddings into redis
    """
    print("loading embeddings into redis...")

    # load embeddings into redis
    pipeline = client.pipeline()
    for i, embedding in enumerate(embeddings, start=1):
        redis_key = f"documents:{i:03}"
        pipeline.json().set(redis_key, "$.question_and_content_embeddings", embedding)
    res = pipeline.execute()

    if not all(res):
        raise Exception("failed to load embeddings")

    print("successfully loaded all embeddings")


def create_index(corpus_len: int):
    """Create search index in redis.

    Assumes that documents and embeddings have already been loaded into redis

    Args:
        corpus_len:
            number of documents in corpus

    Raises:
        exception: if failed to create index
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

    if res == "OK":
        start = time.time()
        while 1:
            if str(client.ft("idx:documents_vss").info()["num_docs"]) == str(
                corpus_len
            ):
                info = client.ft("idx:documents_vss").info()
                num_docs = info["num_docs"]
                indexing_failures = info["hash_indexing_failures"]
                print("num_docs", num_docs, "indexing_failures", indexing_failures)
                return
            if time.time() - start >= 60:
                raise Exception("time out")
    raise Exception("failed to create index")


def create_query(k: int):
    """Create k-NN redis query.

    Args:
        k: number of nearest neighbors to return

    Returns:
        redis query object
    """
    return (
        Query(f"(*)=>[KNN {k} @vector $query_vector AS vector_score]")
        .sort_by("vector_score")
        .return_fields("vector_score", "source", "question", "content", "sql_id")
        .dialect(2)
    )


def queries(query, queries: list[str]) -> list[dict]:
    """Run queries against redis.

    Args:
        query: redis query object
        queries: list of question queries

    Returns:
        list of dictionaries containing query and result
    """
    print("running queries...")

    # encode queries
    encoded_queries = compute_openai_embeddings(queries)

    # run queries
    results_list = []
    for i, encoded_query in enumerate(encoded_queries):
        result_docs = (
            client.ft("idx:documents_vss")
            .search(
                query,
                {"query_vector": np.array(encoded_query, dtype=np.float32).tobytes()},
            )
            .docs  # type: ignore
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


def query_all(k: int, questions: list[str]):
    """Return k most similar documents for each query.

    Args:
        k: number of nearest neighbors to return
        questions: list of question queries

    Returns:
        list of dictionaries containing query and result
    """
    redis_query = create_query(k)
    return queries(redis_query, questions)


def embed_corpus(corpus: list[RedisDocument]):
    """Load corpus, compute embeddings, load embeddings into redis.

    Args:
        corpus: list of documents, each represented by dictionary

    Raises:
        exception: if failed to load corpus
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


# TODO(azliu): turn this into a test case
# def test():
#     try:
#         embed_corpus()
#     except Exception as err:
#         print(f"Unexpected {err=}, {type(err)=}")
#         raise

#     questions = [
#         "What is the deadline to apply for the hackathon?",
#         "When is HackMIT?",
#         "What are the challenges?",
#         "How does judging work?",
#         "What building should I go to during the event?",
#         "What prizes are available?",
#         "How many people are allowed on a team?",
#         "What is HackMIT?",
#         "Can I attend HackMIT if I am an MIT grad student?",
#         "Can I attend HackMIT if I am a sophomore in high school?",
#         "I'm a high school student, but I'm really advanced. Can I attend HackMIT?",
#         "Do I need to bring money to the event?",
#         "Will we be able to sleep at the event?",
#         "Will we be able to stay overnight at the event?",
#         "What should I do if I am a beginner at the event?",
#     ]
#     results = query_all(3, questions)

#     for result in results:
#         print(result["query"])
#         for doc in result["result"]:
#             print(f"Score: {doc['score']}")
#             print(f"Source: {doc['source']}")
#             print(f"Q: {doc['question']}")
#             print(f"A: {doc['content']}")
#         print()
