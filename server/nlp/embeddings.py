"""Embeddings.

This module provides functions for embedding documents and querying them in Redis.
"""

import os
import time

import numpy as np
import openai
from redis.commands.search.field import (
    NumericField,
    TextField,
    VectorField,
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from server import redis_client
from server.config import VECTOR_DIMENSION, RedisDocument
from server.utils import custom_log

assert redis_client is not None

cwd = os.path.dirname(__file__)

embedding_model = "text-embedding-3-small"


def load_corpus(corpus: list[RedisDocument]):
    """Loads given corpus into redis.

    Args:
        corpus: list of documents, each represented by dictionary

    Raises:
        exception: if failed to load corpus into redis
    """
    custom_log("loading corpus...")

    pipeline = redis_client.pipeline()
    for i, doc in enumerate(corpus, start=1):
        redis_key = f"documents:{i:03}"
        pipeline.json().set(redis_key, "$", doc)
    res = pipeline.execute()

    if not all(res):
        raise Exception("failed to load some documents")
    custom_log("successfully loaded all documents")


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
    custom_log("computing embeddings...")

    # get keys, questions, content
    keys = sorted(redis_client.keys("documents:*"))  # type: ignore
    questions = redis_client.json().mget(keys, "$.question")
    content = redis_client.json().mget(keys, "$.content")

    # compute embeddings
    question_and_content = [
        questions[i][0] + " " + content[i][0]  # type: ignore
        for i in range(len(questions))  # type: ignore
    ]

    embeddings = compute_openai_embeddings(question_and_content)

    custom_log("successfully computed embeddings")
    return embeddings


def load_embeddings(embeddings: list[list[float]]):
    """Load embeddings into redis.

    Args:
        embeddings:
            list of embeddings

    Raises:
        exception: if failed to load embeddings into redis
    """
    custom_log("loading embeddings into redis...")

    # load embeddings into redis
    pipeline = redis_client.pipeline()
    for i, embedding in enumerate(embeddings, start=1):
        redis_key = f"documents:{i:03}"
        pipeline.json().set(redis_key, "$.question_and_content_embeddings", embedding)
    res = pipeline.execute()

    if not all(res):
        raise Exception("failed to load embeddings")

    custom_log("successfully loaded all embeddings")


def create_index(corpus_len: int):
    """Create search index in redis.

    Assumes that documents and embeddings have already been loaded into redis

    Args:
        corpus_len:
            number of documents in corpus

    Raises:
        exception: if failed to create index
    """
    custom_log("creating index...")

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
    res = redis_client.ft("idx:documents_vss").create_index(
        fields=schema, definition=definition
    )

    if res == "OK":
        start = time.time()
        while 1:
            if str(redis_client.ft("idx:documents_vss").info()["num_docs"]) == str(
                corpus_len
            ):
                info = redis_client.ft("idx:documents_vss").info()
                num_docs = info["num_docs"]
                indexing_failures = info["hash_indexing_failures"]
                custom_log("num_docs", num_docs, "indexing_failures", indexing_failures)
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
    custom_log("running queries...")

    # encode queries
    encoded_queries = compute_openai_embeddings(queries)

    # run queries
    results_list = []
    for i, encoded_query in enumerate(encoded_queries):
        result_docs = (
            redis_client.ft("idx:documents_vss")
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

    custom_log("done running query")
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
    custom_log("cleaning database...")
    redis_client.flushdb()
    custom_log("done cleaning database")

    # embed corpus
    if not corpus:
        return
    load_corpus(corpus)
    embeddings = compute_embeddings()
    load_embeddings(embeddings)
    create_index(len(corpus))
