"""Utils for testing."""

import logging

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
