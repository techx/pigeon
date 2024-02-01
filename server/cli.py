from flask import Blueprint
import email
import email.mime.multipart
import email.mime.text
from server import db
from server.models.email import Email
from server.models.thread import Thread
from server.models.response import Response
from server.models.document import Document
from server.nlp.responses import generate_response
from datetime import datetime
from server.controllers.emails import (
    thread_emails_to_openai_messages,
    document_data,
    increment_response_count,
)

seed = Blueprint("seed", __name__)


@seed.cli.command()
def email():
    body = "Hello! What is blueprint?"
    body = "Dear Blueprint Team,\n\n" + body + "\n\nBest regards,\nAndrew\n\n"

    thread = Thread()
    db.session.add(thread)
    db.session.commit()
    email = Email(
        datetime.utcnow(),
        "azliu@mit.edu",
        "Help",
        body,
        "message-id",
        False,
        thread.id,
    )

    if email is not None and thread is not None:
        openai_messages = thread_emails_to_openai_messages(thread.emails)
        openai_res, documents, confidence = generate_response(
            email.sender, email.body, openai_messages
        )
        questions, document_ids, document_confidences = document_data(documents)
        db.session.add(email)
        db.session.commit()
        r = Response(
            openai_res,
            questions,
            document_ids,
            document_confidences,
            confidence,
            email.id,
        )
        db.session.add(r)
        thread.last_email = email.id
        thread.resolved = False
        db.session.commit()
        increment_response_count(document_ids)
