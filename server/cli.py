"""Flask CLI commands."""

import datetime
import json

from flask import Blueprint

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
from server.nlp.embeddings import embed_corpus
from server.nlp.responses import generate_response

seed = Blueprint("seed", __name__)


def _generate_test_documents():
    """Generate test documents."""
    with open("server/nlp/corpus_mit.json") as f:
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


@seed.cli.command()
def corpus():
    """Add test documents to the corpus."""
    test_documents = _generate_test_documents()
    embed_corpus(test_documents)


@seed.cli.command()
def email():
    """Seed the database with a test email."""
    subject = "Test Email Subject"
    body = "Hello! What is blueprint?"
    body = "Dear Blueprint Team,\n\n" + body + "\n\nBest regards,\nAndrew\n\n"

    thread = Thread()

    if thread is None:
        raise ValueError("Thread is None")

    db.session.add(thread)
    db.session.commit()

    email = Email(
        date=datetime.datetime.now(datetime.timezone.utc),
        sender="azliu@mit.edu",
        subject=subject,
        body=body,
        message_id="message-id",
        is_reply=False,
        thread_id=thread.id,
    )

    if email is None:
        raise ValueError("Email is None")

    openai_messages = thread_emails_to_openai_messages(thread.emails)
    openai_res, documents, confidence = generate_response(
        email.sender, email.body, openai_messages
    )
    questions, documents, doc_confs, docs_per_question = document_data(documents)
    db.session.add(email)
    db.session.commit()

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
    thread.last_email = email.id
    thread.resolved = False
    db.session.commit()
    increment_response_count(documents)
