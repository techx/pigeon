from apiflask import APIFlask
from flask.testing import FlaskClient

from server_tests.utils import assert_status


def test_get_threads(app: APIFlask, client: FlaskClient):
    """Test fetching threads."""
    response = client.get("/api/emails/get_threads")
    assert_status(response, 200)
