from apiflask import APIFlask
from flask.testing import FlaskClient
from sqlalchemy import select

from server import db
from server.models.thread import Thread
from server_tests.utils import assert_status


def test_thread_first_sender(app: APIFlask):
    """Test fetching the first thread."""
    with app.app_context():
        thread = (
            db.session.execute(
                select(Thread)
            )
            .scalar_one()
        )
        earliest_email = min(thread.emails, key=lambda x: x.date)
        assert earliest_email.sender == thread.first_sender


def test_get_threads(app: APIFlask, client: FlaskClient):
    """Test fetching threads."""
    response = client.get("/api/emails/get_threads")
    assert_status(response, 200)

    threads = response.json
    assert threads is not None
    assert len(threads) == 1

    thread = threads[0]
    thread_id = thread["id"]
    assert thread_id == 1
    assert not thread["resolved"]  # resolved is false
    assert len(thread["emailList"]) == 5

    for email in thread["emailList"]:
        # checking that .map() is intact
        assert email["id"] is not None
        assert email["body"] is not None
        assert email["subject"] is not None
        assert email["sender"] is not None
        assert email["message_id"] is not None
        assert email["is_reply"] is not None
        assert email["thread_id"] == thread_id
