"""Utils for testing."""

import logging

from apiflask import APIFlask
from werkzeug.test import TestResponse


def assert_status(response: TestResponse, status: int):
    """Asserts a response's status code, logging the response if it fails."""
    try:
        assert response.status_code == status
    except AssertionError:
        logging.error(
            f"Assertion failed: expected {status}, got {response.status_code}. "
            f"Response body: {response.data.decode()}"
        )
        raise

def seed_database(app: APIFlask):
    """Seeds the database with some fake data."""

    with app.app_context():
        from server.fake_data import generate_fake_thread, generate_test_documents

        generate_test_documents()
        generate_fake_thread(generate_response=False)
