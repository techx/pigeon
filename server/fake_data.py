"""Fake data for seed cli and testing."""

import datetime
import json

from server import db
from server.controllers.emails import (
    document_data,
    increment_response_count,
    thread_emails_to_openai_messages,
)
from server.models.document import Document
from server.models.email import Email
from server.models.response import Response
from server.models.thread import Thread
from server.nlp.responses import generate_response

FLASK_SEED_CORPUS = "server/nlp/corpus_flask_seed.json"


def generate_test_documents():
    """Generate test documents."""
    with open(FLASK_SEED_CORPUS) as f:
        corpus = json.load(f)

    documents = []
    for doc in corpus:
        document = Document(
            question=doc["question"],
            label=doc["question"],
            source=doc["source"],
            content=doc["content"],
        )
        db.session.add(document)
        db.session.commit()
        documents.append(document)

    test_documents = [
        {
            "question": doc.question,
            "source": doc.source,
            "content": doc.content,
            "sql_id": doc.id,
        }
        for doc in documents
    ]
    return test_documents


def _generate_response(email: Email, thread: Thread):
    """Generate response for a given thread.

    Email arg should be the last email in the thread.
    """
    openai_messages = thread_emails_to_openai_messages(thread.emails)
    openai_res, documents, confidence = generate_response(
        email.sender, email.body, openai_messages
    )
    questions, documents, doc_confs, docs_per_question = document_data(documents)

    r = Response(
        openai_res,
        questions,
        docs_per_question,
        documents,
        doc_confs,
        confidence,
        email.id,
    )

    db.session.add(r)
    db.session.commit()
    increment_response_count(documents)


def generate_fake_email(generate_response=True):
    """Generate fake email."""
    thread = Thread()
    db.session.add(thread)
    db.session.commit()

    og_sender = "azliu@mit.edu"
    subject = "inquiry about hackmit"
    body_1 = (
        "Dear HackMIT Team,\n\n" "What is HackMIT? \n\n" "Best regards,\n" "Andrew\n\n"
    )
    message_id = "test-message-id"
    email = Email(
        date=datetime.datetime.now(datetime.timezone.utc),
        sender=og_sender,
        subject=subject,
        body=body_1,
        message_id=message_id,
        is_reply=False,
        thread_id=thread.id,
    )
    db.session.add(email)
    db.session.commit()

    thread.last_email = email.id
    thread.resolved = False
    db.session.commit()

    if generate_response:
        _generate_response(email, thread)


def generate_fake_thread(generate_response=True):
    """Generate fake unresolved thread."""
    thread = Thread()
    db.session.add(thread)
    db.session.commit()

    og_sender = "azliu@mit.edu"
    subject = "inquiry about hackmit"
    body_1 = (
        "Dear HackMIT Team,\n\n" "What is HackMIT? \n\n" "Best regards,\n" "Andrew\n\n"
    )
    message_id = "test-message-id"
    email_1 = Email(
        date=datetime.datetime.now(datetime.timezone.utc),
        sender=og_sender,
        subject=subject,
        body=body_1,
        message_id=f"{message_id}-1",
        is_reply=False,
        thread_id=thread.id,
    )
    db.session.add(email_1)

    pigeon_sender = '"Blueprint Team" <blueprint@my.hackmit.org>'
    body_2 = (
        "Hello!\n\n"
        "This is a reply to your inquiry about HackMIT.\n\n"
        "Best regards,\n"
        "HackMIT Team\n\n"
    )
    email_2 = Email(
        date=datetime.datetime.now(datetime.timezone.utc),
        sender=pigeon_sender,
        subject=subject,
        body=body_2,
        message_id=f"{message_id}-2",
        is_reply=True,
        thread_id=thread.id,
    )
    db.session.add(email_2)

    body_3 = (
        "Dear HackMIT Team,\n\n"
        "Thanks for your response! Unfortunately, that didn't answer my question.\n\n"
        "Best regards,\n"
        "Andrew\n\n"
    )
    email_3 = Email(
        date=datetime.datetime.now(datetime.timezone.utc),
        sender=og_sender,
        subject=subject,
        body=body_3,
        message_id=f"{message_id}-3",
        is_reply=False,
        thread_id=thread.id,
    )
    db.session.add(email_3)

    body_4 = (
        "Hello!\n\n"
        "This is another reply to your inquiry about HackMIT.\n\n"
        "Best regards,\n"
        "HackMIT Team\n\n"
    )
    email_4 = Email(
        date=datetime.datetime.now(datetime.timezone.utc),
        sender=pigeon_sender,
        subject=subject,
        body=body_4,
        message_id=f"{message_id}-4",
        is_reply=True,
        thread_id=thread.id,
    )
    db.session.add(email_4)

    body_5 = (
        "Dear HackMIT Team,\n\n" "Please answer my question.\n\n" "Best,\n" "Andrew\n\n"
    )
    email_5 = Email(
        date=datetime.datetime.now(datetime.timezone.utc),
        sender=og_sender,
        subject=subject,
        body=body_5,
        message_id=f"{message_id}-5",
        is_reply=False,
        thread_id=thread.id,
    )
    db.session.add(email_5)
    db.session.commit()

    thread.last_email = email_5.id
    thread.resolved = False
    db.session.commit()

    if generate_response:
        _generate_response(email_5, thread)
