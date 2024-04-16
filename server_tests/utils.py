"""Utils for testing."""

import datetime
import logging

from werkzeug.test import TestResponse

from server import ProperlyTypedSQLAlchemy
from server.fake_data import generate_test_documents
from server.models.email import Email
from server.models.thread import Thread


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

def seed_database(db: ProperlyTypedSQLAlchemy):
    """Seeds the database with some fake data."""

    # add some documents to the database
    generate_test_documents()

    # create fake thread with 5 emails
    thread = Thread()
    db.session.add(thread)
    db.session.commit()

    emails = []
    for i in range(5):
        # every other email is a reply sent from pigeon
        is_reply = i % 2 == 1
        test_email = Email(
            date=datetime.datetime.now(datetime.timezone.utc),
            sender=f"test-{i}@test.com",
            subject=f"Test Subject {i}",
            body=f"Test Body {i}",
            message_id=f"test-message-id-{i}",
            is_reply=is_reply,
            thread_id=thread.id
        )
        emails.append(test_email)
        db.session.add(test_email)

    db.session.commit()
    thread.last_email = emails[-1].id
    db.session.commit()
