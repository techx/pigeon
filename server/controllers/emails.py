"""The email controller handles sending and receiving of emails."""

import email
import email.mime.multipart
import email.mime.text
import os
import re
from datetime import datetime, timezone
from typing import List

import boto3
from apiflask import APIBlueprint
from flask import request
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import select

from server import db
from server.config import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    MAIL_CC,
    MAIL_USERNAME,
    OpenAIMessage,
    RedisDocument,
)
from server.models.document import Document
from server.models.email import Email
from server.models.response import Response
from server.models.thread import Thread
from server.nlp.responses import generate_response

cwd = os.path.dirname(__file__)
env = Environment(loader=FileSystemLoader([f"{cwd}/../email_template"]))
emails = APIBlueprint("emails", __name__, url_prefix="/emails", tag="Emails")


def thread_emails_to_openai_messages(thread_emails: List[Email]) -> List[OpenAIMessage]:
    """Converts list of email to openai messages.

    Args:
        thread_emails: list of emails

    Returns:
        list of openai messages
    """
    openai_messages = []
    for t_email in thread_emails:
        role = "user" if t_email.sender != MAIL_USERNAME else "assistant"
        openai_messages.append({"role": role, "content": t_email.body})
    return openai_messages


def document_data(
    documents: dict[str, List[RedisDocument]],
) -> tuple[List[str], List["Document"], List[float], List[int]]:
    """Process raw openai document output.

    Args:
    documents:
        raw openai document output

    Returns:
        list of questions parsed from the original email body
        list of documents. each element in the list is a document
        list of document confidence. each element in the list is the confidence
        score for each document
        list of the number of documents per question
    """
    questions = list(documents.keys())
    db_documents = []
    doc_confidences = []
    docs_per_question = []
    for question in questions:
        for doc in documents[question]:
            document = db.session.execute(
                select(Document).where(Document.id == doc["sql_id"])
            ).scalar()
            db_documents.append(document)
            doc_confidences.append(doc["score"])
        docs_per_question.append(len(documents[question]))
    return questions, db_documents, doc_confidences, docs_per_question


def increment_response_count(documents: List["Document"]):
    """Increment response count for documents.

    Args:
        documents:
            list of documents. each element in the list is a document
            used to answer a specific question
    """
    for doc in documents:
        document = db.session.execute(
            select(Document).where(Document.id == doc.id)
        ).scalar()
        if document:
            document.response_count += 1
        db.session.commit()


def decrement_response_count(documents: List["Document"]):
    """Decrement response count for documents.

    Args:
        documents:
            list of documents. each element in the list is a document
            used to answer a specific question
    """
    for doc in documents:
        document = db.session.execute(
            select(Document).where(Document.id == doc.id)
        ).scalar()
        if document:
            if document.to_delete and document.response_count == 1:
                db.session.delete(document)
            else:
                document.response_count -= 1
        db.session.commit()


# not used as of 1/28/2024
# save for future reference, in case we ever need to switch back to mailgun or a similar
# provider
# @emails.route("/receive_email_mailgun", methods=["POST"])
# def receive_email_mailgun():
#     data = request.form

#     if (
#         "From" not in data
#         or "Subject" not in data
#         or "stripped-text" not in data
#         or "stripped-html" not in data
#         or "Message-Id" not in data
#     ):
#         return {"message": "Missing fields"}, 400

#     email = None
#     thread = None

#     if "In-Reply-To" in data:
#         # reply to existing email, add to existing thread
#         replied_to_email =
# Email.query.filter_by(message_id=data["In-Reply-To"]).first()
#         if data["sender"] != MAIL_USERNAME and replied_to_email:
#             thread = Thread.query.get(replied_to_email.thread_id)
#             if thread:
#                 email = Email(
#                     datetime.now(timezone.utc),
#                     data["From"],
#                     data["Subject"],
#                     data["stripped-text"],
#                     data["stripped-html"],
#                     data["Message-Id"],
#                     False,
#                     thread.id,
#                 )
#     else:
#         # new email, create new thread
#         thread = Thread()
#         db.session.add(thread)
#         db.session.commit()
#         email = Email(
#             datetime.now(timezone.utc),
#             data["From"],
#             data["Subject"],
#             data["stripped-text"],
#             data["stripped-html"],
#             data["Message-Id"],
#             False,
#             thread.id,
#         )
#     if email is not None and thread is not None:
#         openai_messages = thread_emails_to_openai_messages(thread.emails)
#         openai_res, documents, confidence = generate_response(
#             email.sender, email.body, openai_messages
#         )
#         questions, document_ids, document_confidences = document_data(documents)
#         db.session.add(email)
#         db.session.commit()
#         r = Response(
#             openai_res,
#             questions,
#             document_ids,
#             document_confidences,
#             confidence,
#             email.id,
#         )
#         db.session.add(r)
#         thread.last_email = email.id
#         thread.resolved = False
#         db.session.commit()
#     return data


@emails.route("/receive_email", methods=["POST"])
def receive_email():
    """GET /receive_email

    More information about the way that AWS SES sends emails can be found at
    go/pigeon-emails
    """
    data = request.form
    print(data, flush=True)

    if (
        "From" not in data
        or "Subject" not in data
        or "stripped-text" not in data
        or "Message-Id" not in data
    ):
        return {"message": "Missing fields"}, 400

    # aws sends duplicate emails sometimes. ignore if duplicate
    email_exists = db.session.execute(
        select(Email).where(Email.message_id == data["Message-Id"])
    ).scalar()
    if email_exists:
        print("duplicate email", flush=True)
        return data

    # by default, body contains the full email bodies of all previous emails in the
    # thread here, we filter out previous emails so that only the body of the current
    # email is used. this filtering is purposely not done on AWS because of potentially
    # needing context for the TODO below
    body = data["stripped-text"]
    body = str(body)
    start_of_reply = body.find("________________________________")

    if start_of_reply != -1:
        body = body[:start_of_reply]

    email = None
    thread = None

    if "In-Reply-To" in data:
        # reply to existing email, add to existing thread

        # for some reason AWS adds three spaces to the message id
        real_message_id = data["In-Reply-To"].strip()

        replied_to_email = db.session.execute(
            select(Email).where(Email.message_id == real_message_id)
        ).scalar()
        print("replied to email", replied_to_email, flush=True)
        print("real message id", real_message_id, len(real_message_id), flush=True)
        print(
            "data from",
            data["From"],
            "blueprint@my.hackmit.org" not in data["From"],
            flush=True,
        )
        if "blueprint@my.hackmit.org" not in data["From"] and replied_to_email:
            thread = db.session.execute(
                select(Thread).where(Thread.id == replied_to_email.thread_id)
            ).scalar()
            if thread:
                email = Email(
                    datetime.now(timezone.utc),
                    data["From"],
                    data["Subject"],
                    body,
                    data["Message-Id"],
                    False,
                    thread.id,
                )
        # TODO(#5): this ignores case where user responds to an email that isn't in the
        # database. should we handle this?
    else:
        # new email, create new thread
        thread = Thread()
        db.session.add(thread)
        db.session.commit()
        email = Email(
            datetime.now(timezone.utc),
            data["From"],
            data["Subject"],
            body,
            data["Message-Id"],
            False,
            thread.id,
        )
    if email is not None and thread is not None:
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
    return data


# not used as of 1/28/2024
# save for future reference, in case we ever need to switch back to mailgun or a
# similar provider
# @emails.route("/send_email_mailgun", methods=["POST"])
# def send_email_mailgun():
#     data = request.form
#     reply_to_email = Email.query.get(data["id"])
#     clean_regex = re.compile("<.*?>")
#     clean_text = re.sub(clean_regex, " ", data["body"])
#     context = {"body": data["body"]}
#     template = env.get_template("template.html")
#     body = template.render(**context)
#     thread = Thread.query.get(reply_to_email.thread_id)
#     server = smtplib.SMTP("smtp.mailgun.org", 587)
#     server.starttls()
#     server.ehlo()
#     server.login(MAIL_USERNAME, MAIL_PASSWORD)
#     msg = email.mime.multipart.MIMEMultipart()
#     msg["Subject"] = reply_to_email.subject
#     msg["FROM"] = MAIL_SENDER_TAG
#     msg["In-Reply-To"] = reply_to_email.message_id
#     msg["References"] = reply_to_email.message_id
#     msg["To"] = thread.first_sender
#     msg["Cc"] = MAIL_USERNAME
#     message_id = email.utils.make_msgid(domain="my.hackmit.org")
#     msg["message-id"] = message_id
#     msg.attach(email.mime.text.MIMEText(body, "HTML"))
#     server.sendmail(MAIL_USERNAME, [thread.first_sender], msg.as_bytes())
#     thread.resolved = True
#     reply_email = Email(
#         datetime.now(timezone.utc),
#         MAIL_SENDER_TAG,
#         reply_to_email.subject,
#         clean_text,
#         data["body"],
#         message_id,
#         True,
#         thread.id,
#     )
#     db.session.add(reply_email)
#     db.session.commit()
#     thread.last_email = reply_email.id
#     db.session.commit()
#     return {"message": "Email sent successfully"}


def get_full_message_id(message_id):
    """Get full SES-formatted message id."""
    return f"<{message_id}@us-east-2.amazonses.com>"


@emails.route("/send_email", methods=["POST"])
def send_email():
    """POST /send_email"""
    data = request.form
    reply_to_email = db.session.execute(
        select(Email).where(Email.id == data["id"])
    ).scalar()
    if not reply_to_email:
        return {"message": "Email not found"}, 400
    thread = db.session.execute(
        select(Thread).where(Thread.id == reply_to_email.thread_id)
    ).scalar()
    if not thread:
        return {"message": "Thread not found"}, 400
    clean_regex = re.compile("<.*?>")
    clean_text = re.sub(clean_regex, " ", data["body"])
    context = {"body": data["body"]}
    template = env.get_template("template.html")
    body = template.render(**context)

    client = boto3.client(
        "ses",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    msg = email.mime.multipart.MIMEMultipart()
    msg["Subject"] = reply_to_email.subject
    # msg["FROM"] = MAIL_SENDER_TAG
    msg["FROM"] = '"Blueprint Team" <blueprint@my.hackmit.org>'
    msg["In-Reply-To"] = reply_to_email.message_id
    msg["References"] = reply_to_email.message_id
    to_email_addresses = [thread.first_sender, MAIL_CC]
    msg["To"] = ", ".join(to_email_addresses)
    # msg["Cc"] = MAIL_CC
    msg["Reply-To"] = MAIL_CC
    msg.attach(email.mime.text.MIMEText(body, "HTML"))

    response = client.send_raw_email(
        # Destinations=[thread.first_sender],
        Destinations=to_email_addresses,
        RawMessage={"Data": msg.as_string()},
    )

    new_mesage_id = get_full_message_id(response["MessageId"])
    print(
        "sending a new repsonse with message id",
        new_mesage_id,
        len(new_mesage_id),
        flush=True,
    )

    thread.resolved = True
    reply_email = Email(
        datetime.now(timezone.utc),
        '"Blueprint Team" <blueprint@my.hackmit.org>',
        reply_to_email.subject,
        clean_text,
        get_full_message_id(response["MessageId"]),
        True,
        thread.id,
    )

    db.session.add(reply_email)
    db.session.commit()
    thread.last_email = reply_email.id
    db.session.commit()

    response = db.session.execute(
        select(Response).where(Response.email_id == reply_to_email.id)
    ).scalar()
    if response:
        decrement_response_count(response.documents)

    return {"message": "Email sent successfully"}


@emails.route("/get_response", methods=["POST"])
def get_response():
    """POST /get_response"""
    data = request.form
    response = db.session.execute(
        select(Response).where(Response.email_id == data["id"])
    ).scalar()

    if not response:
        return {"message": "Response not found"}, 400
    return response.map()


@emails.route("/regen_response", methods=["POST"])
def regen_response():
    """POST /regen_response

    Regenerate the AI-gen response response for an email.
    """
    data = request.form
    thread = db.session.execute(select(Thread).where(Thread.id == data["id"])).scalar()
    if not thread:
        return {"message": "Thread not found"}, 400
    email = db.session.execute(
        select(Email).where(Email.id == thread.last_email)
    ).scalar()
    if not email:
        return {"message": "Email not found"}, 400
    response = db.session.execute(
        select(Response).where(Response.email_id == email.id)
    ).scalar()
    if not thread or not email or not response:
        return {"message": "Something went wrong!"}, 400

    openai_messages = thread_emails_to_openai_messages(thread.emails)
    openai_res, documents, confidence = generate_response(
        email.sender, email.body, openai_messages
    )
    decrement_response_count(response.documents)
    questions, documents, doc_confs, docs_per_question = document_data(documents)
    increment_response_count(documents)
    response.response = openai_res
    response.questions = questions
    response.docs_per_question = docs_per_question
    response.documents = documents
    response.document_confidences = doc_confs
    response.confidence = confidence
    db.session.commit()

    return {"message": "Successfully updated"}, 200


@emails.route("/resolve", methods=["POST"])
def resolve():
    """POST /resolve

    Mark an email thread as resolved.
    """
    data = request.form
    thread = db.session.execute(select(Thread).where(Thread.id == data["id"])).scalar()
    if not thread:
        return {"message": "Thread not found"}, 400
    thread.resolved = True
    db.session.commit()

    return {"message": "Successfully updated"}, 200


@emails.route("/unresolve", methods=["POST"])
def unresolve():
    """POST /unresolve

    Mark an email thread as unresolved.
    """
    data = request.form
    thread = db.session.execute(select(Thread).where(Thread.id == data["id"])).scalar()
    if not thread:
        return {"message": "Thread not found"}, 400
    thread.resolved = False
    db.session.commit()

    return {"message": "Successfully updated"}, 200


@emails.route("/get_threads", methods=["GET"])
def get_threads():
    """GET /get_threads

    Get a list of all threads.
    """
    thread_list = (
        db.session.execute(
            select(Thread).order_by(Thread.resolved, Thread.last_email.desc())
        )
        .scalars()
        .all()
    )
    email_list = [
        {
            "id": thread.id,
            "resolved": thread.resolved,
            "read": thread.read,
            "emailList": [
                thread_email.map()
                for thread_email in db.session.execute(
                    select(Email).where(Email.thread_id == thread.id)
                )
                .scalars()
                .all()
            ],
        }
        for thread in thread_list
    ]
    return email_list


@emails.route("/mark_as_read/<int:thread_id>", methods=["GET"])
def mark_as_read(thread_id):
    """GET /mark_as_read/<threadId>

    Mark a thread as read.
    """
    thread = db.session.execute(select(Thread).where(Thread.id == thread_id)).scalar()
    if not thread:
        return {"message": "Thread not found"}, 400
    thread.read = True
    db.session.commit()

    return {"message": "Successfully updated"}, 200
