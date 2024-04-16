import datetime
import os
from typing import cast
from unittest.mock import patch

import psycopg2
import pytest
import redis
from apiflask import APIFlask
from flask.testing import FlaskClient, FlaskCliRunner
from openai.types.chat import ChatCompletionMessage
from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.create_embedding_response import CreateEmbeddingResponse, Usage
from openai.types.embedding import Embedding
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.engine import Engine
from sqlalchemy.engine.base import Connection

from server import create_app, db
from server.config import LOCAL, VECTOR_DIMENSION


@pytest.fixture(scope="session")
def db_url(db_name="pigeondb_test"):
    """Creates a test database in postgres, yielding the database URL.

    Drops and recreates the database if it already exists.
    """
    host = "database" if LOCAL else "localhost"
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="password",
        host=host,
        port="5432",
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cur.fetchone()
        if exists:
            cur.execute(sql.SQL(f"DROP DATABASE {db_name}"))
        cur.execute(sql.SQL(f"CREATE DATABASE {db_name}"))

    conn.close()

    yield f"postgresql://postgres:password@{host}/{db_name}"


@pytest.fixture(scope="session")
def redis_host():
    """Yields test redis db host.

    Flushes test db if it already exists.
    """
    host = "redis-test" if LOCAL else "localhost"
    client = redis.Redis(host=host, port=6379)
    client.flushdb()
    client.close()

    yield host


@pytest.fixture(scope="session")
def app(db_url: str, redis_host: str):
    os.environ["DATABASE_URL"] = db_url
    os.environ["REDIS_HOST"] = redis_host

    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    with app.app_context():
        from server_tests.utils import seed_database
        seed_database()

    yield app


@pytest.fixture(autouse=True)
def mock_openai_chat_completion():
    """Mock the OpenAI chat completion API."""
    with patch("openai.chat.completions.create") as mock:
        mock.return_value = ChatCompletion(
            id="foo",
            model="gpt-3.5-turbo",
            object="chat.completion",
            choices=[
                Choice(
                    finish_reason="stop",
                    index=0,
                    message=ChatCompletionMessage(
                        content="mocked openai message!",
                        role="assistant",
                    ),
                )
            ],
            created=int(datetime.datetime.now().timestamp()),
        )
        yield mock


@pytest.fixture(autouse=True)
def mock_openai_embeddings():
    """Mock the OpenAI embeddings API."""
    with patch("openai.embeddings.create") as mock:
        mock.return_value = CreateEmbeddingResponse(
            model="gpt-3.5-turbo",
            object="list",
            data=[
                Embedding(
                    embedding=[0.1 for _ in range(VECTOR_DIMENSION)],
                    index=0,
                    object="embedding",
                )
            ],
            usage=Usage(
                prompt_tokens=10,
                total_tokens=10,
            ),
        )
        yield mock


@pytest.fixture(autouse=True)
def enable_transactional_tests(app: APIFlask):
    """Enables fast independent tests by rolling back changes made during every test.

    Taken from https://github.com/pallets-eco/flask-sqlalchemy/issues/1171,
    with modifications for static type checking.
    """

    with app.app_context():
        engines = cast(dict[str | None, Engine | Connection], db._app_engines[app])

    engine_cleanup = []

    for key, engine in engines.items():
        connection = (cast(Engine, engine)).connect()
        transaction = connection.begin()
        engines[key] = connection
        engine_cleanup.append((key, engine, connection, transaction))

    yield

    for key, engine, connection, transaction in engine_cleanup:
        transaction.rollback()
        connection.close()
        engines[key] = engine


@pytest.fixture()
def client(app: APIFlask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def runner(app: APIFlask) -> FlaskCliRunner:
    return app.test_cli_runner()
