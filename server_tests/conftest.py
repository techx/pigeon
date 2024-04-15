import os
from typing import cast

import psycopg2
import pytest
from apiflask import APIFlask
from flask.testing import FlaskClient, FlaskCliRunner
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.engine import Engine
from sqlalchemy.engine.base import Connection

from server import create_app, db


@pytest.fixture(scope="session")
def db_url(db_name="pigeondb_test"):
    """Creates a test database in postgres, yielding the database URL.

    Drops and recreates the database if it already exists.
    """
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="password",
        host="localhost",
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

    yield "postgresql://postgres:password@localhost/pigeondb_test"


@pytest.fixture(scope="session")
def app(db_url: str):
    os.environ["DATABASE_URL"] = db_url

    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


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
