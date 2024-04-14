import os
import re
import email
import email.mime.multipart
import email.mime.text
from typing import Any
from flask import request
from jinja2 import Environment, FileSystemLoader
from apiflask import APIBlueprint
from server import db
from server.config import (
    MAIL_USERNAME,
    MAIL_CC,
    AWS_REGION,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    OpenAIMessage,
)
from server.models.email import Email
from server.models.thread import Thread
from server.models.response import Response
from server.models.document import Document
from server.nlp.responses import generate_response
from datetime import datetime, timezone
import boto3

cwd = os.path.dirname(__file__)
env = Environment(loader=FileSystemLoader([f"{cwd}/../email_template"]))
emails = APIBlueprint("emails", __name__, url_prefix="/emails", tag="Emails")


def thread_emails_to_openai_messages(thread_emails: list[Any]) -> list[OpenAIMessage]:
    """converts list of email to openai messages

    Parameters
    ----------
    thread_email_ids : :obj:`list` of :obj:`Any`
        TODO(azliu): change "any" to the correct type.
        list of email ids

    Returns
    -------
    :obj:`list` of :obj:`OpenAIMessage`
        list of openai messages
    """
    openai_messages = []
    for t_email in thread_emails:
        role = "user" if t_email.sender != MAIL_USERNAME else "assistant"
        openai_messages.append({"role": role, "content": t_email.body})
    return openai_messages


def document_data(
    documents: list[dict],
) -> tuple[list[str], list[list[int]], list[list[float]]]:
    """process raw openai document output

    Parameters
    ----------
    documents : :obj:`list` of :obj:`dict`
        raw openai document output

    Returns
    -------
    :obj:`list` of :obj:`str`
        list of questions parsed from the original email body
    :obj:`list` of :obj:`list` of :obj:`int`
        list of document ids. each element in the list is a list of document ids used to answer a specific question
    :obj:`list` of :obj:`list` of :obj:`float`
        list of document confidence. each element in the list is the corresponding list of confidence scores for each document used to answer a specific question
    """
    questions = documents.keys()
    doc_ids = []
    doc_confidences = []
    for question in questions:
        doc_ids_question = []
        doc_confidences_question = []
        for doc in documents[question]:
            doc_ids_question.append(doc["sql_id"])
            doc_confidences_question.append(doc["score"])
        doc_ids.append(doc_ids_question)
        doc_confidences.append(doc_confidences_question)
    return questions, doc_ids, doc_confidences


def increment_response_count(document_ids: list[list[int]]):
    """increment response count for documents

    Parameters
    ----------
    document_ids : :obj:`list` of :obj:`list` of :obj:`int`
        list of document ids. each element in the list is a list of document ids used to answer a specific question
    """
    for doc_ids_question in document_ids:
        for doc_id in doc_ids_question:
            document = Document.query.get(doc_id)
            if document:
                document.response_count += 1
            db.session.commit()


def decrement_response_count(document_ids: list[list[int]]):
    """decrement response count for documents

    Parameters
    ----------
    document_ids : :obj:`list` of :obj:`list` of :obj:`int`
        list of document ids. each element in the list is a list of document ids used to answer a specific question
    """
    for doc_ids_question in document_ids:
        for doc_id in doc_ids_question:
            document = Document.query.get(doc_id)
            if document:
                if document.to_delete and document.response_count == 1:
                    db.session.delete(document)
                else:
                    document.response_count -= 1
            db.session.commit()


# not used as of 1/28/2024
# save for future reference, in case we ever need to switch back to mailgun or a similar provider
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
#         replied_to_email = Email.query.filter_by(message_id=data["In-Reply-To"]).first()
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
    email_exists = Email.query.filter_by(message_id=data["Message-Id"]).first()
    if email_exists:
        print("duplicate email", flush=True)
        return data

    # by default, body contains the full email bodies of all previous emails in the thread
    # here, we filter out previous emails so that only the body of the current email is used
    # this filtering is purposely not done on AWS because of potentially needing context for the TODO below
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

        replied_to_email = Email.query.filter_by(message_id=real_message_id).first()
        print("replied to email", replied_to_email, flush=True)
        print("real message id", real_message_id, len(real_message_id), flush=True)
        print(
            "data from",
            data["From"],
            "blueprint@my.hackmit.org" not in data["From"],
            flush=True,
        )
        if "blueprint@my.hackmit.org" not in data["From"] and replied_to_email:
            thread = Thread.query.get(replied_to_email.thread_id)
            if thread:
                email = Email(
                    datetime.utcnow(),
                    data["From"],
                    data["Subject"],
                    body,
                    data["Message-Id"],
                    False,
                    thread.id,
                )
        # TODO(#5): this ignores case where user responds to an email that isn't in the database. should we handle this?
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
    return data


# not used as of 1/28/2024
# save for future reference, in case we ever need to switch back to mailgun or a similar provider
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
    return f"<{message_id}@us-east-2.amazonses.com>"


@emails.route("/send_email", methods=["POST"])
def send_email():
    data = request.form
    reply_to_email = Email.query.get(data["id"])
    if not reply_to_email:
        return {"message": "Email not found"}, 400
    thread = Thread.query.get(reply_to_email.thread_id)
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

    response = Response.query.filter_by(email_id=reply_to_email.id).first()
    if response:
        decrement_response_count(response.documents)

    return {"message": "Email sent successfully"}


@emails.route("/get_response", methods=["POST"])
def get_response():
    data = request.form
    response = Response.query.filter_by(email_id=data["id"]).first()
    if not response:
        return {"message": "Response not found"}, 400
    return response.map()


@emails.route("/regen_response", methods=["POST"])
def regen_response():
    data = request.form
    thread = Thread.query.get(data["id"])
    if not thread:
        return {"message": "Thread not found"}, 400
    email = Email.query.get(thread.last_email)
    if not email:
        return {"message": "Email not found"}, 400
    response = Response.query.filter_by(email_id=email.id).first()
    if not thread or not email or not response:
        return {"message": "Something went wrong!"}, 400

    openai_messages = thread_emails_to_openai_messages(thread.emails)
    openai_res, documents, confidence = generate_response(
        email.sender, email.body, openai_messages
    )
    decrement_response_count(response.documents)
    questions, document_ids, document_confidences = document_data(documents)
    increment_response_count(document_ids)
    response.response = openai_res
    response.questions = questions
    response.documents = document_ids
    response.documents_confidence = document_confidences
    response.confidence = confidence
    db.session.commit()

    return {"message": "Successfully updated"}, 200


@emails.route("/resolve", methods=["POST"])
def resolve():
    data = request.form
    thread = Thread.query.get(data["id"])
    if not thread:
        return {"message": "Thread not found"}, 400
    thread.resolved = True
    db.session.commit()

    return {"message": "Successfully updated"}, 200


@emails.route("/unresolve", methods=["POST"])
def unresolve():
    data = request.form
    thread = Thread.query.get(data["id"])
    if not thread:
        return {"message": "Thread not found"}, 400
    thread.resolved = False
    db.session.commit()

    return {"message": "Successfully updated"}, 200


@emails.route("/get_threads", methods=["GET"])
def get_threads():
    thread_list = Thread.query.order_by(Thread.resolved, Thread.last_email.desc()).all()
    email_list = [
        {
            "id": thread.id,
            "resolved": thread.resolved,
            "emailList": [
                thread_email.map()
                for thread_email in Email.query.filter_by(thread_id=thread.id)
                .order_by(Email.id)
                .all()
            ],
        }
        for thread in thread_list
    ]
    return email_list
