"""Flask CLI commands."""

import datetime

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
from server.nlp.responses import generate_response

seed = Blueprint("seed", __name__)


@seed.cli.command()
def email():
    """Seed the database with a test email."""
    subject = "Test Email Subject"
    body = "Hello! What is blueprint?"
    body = "Dear Blueprint Team,\n\n" + body + "\n\nBest regards,\nAndrew\n\n"

    thread = Thread()
    db.session.add(thread)
    db.session.commit()

    email = Email(
        date=datetime.datetime.now(datetime.timezone.utc),  # type: ignore
        sender="azliu@mit.edu",
        subject=subject,
        body=body,
        message_id="message-id",
        is_reply=False,
        thread_id=thread.id,
    )

    if email is not None and thread is not None:
        openai_messages = thread_emails_to_openai_messages(thread.emails)
        openai_res, documents, confidence = generate_response(
            email.sender, email.body, openai_messages
        )
        questions, document_ids, document_confidences = document_data(documents)
        db.session.add(email)
        db.session.commit()

        documents = []
        for i, doc_ids_question in enumerate(document_ids):
            documents.append([])
            for doc_id in doc_ids_question:
                document = db.session.execute(
                    db.select(Document).where(Document.id == doc_id)
                ).scalar()
                if document:
                    documents[i].append(document)

        r = Response(
            openai_res,
            questions,
            documents,
            document_confidences,
            confidence,
            email.id,
        )

        db.session.add(r)
        thread.last_email = email.id
        thread.resolved = False
        db.session.commit()
        increment_response_count(document_ids)
