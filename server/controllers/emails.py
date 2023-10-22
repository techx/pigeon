import os
import smtplib
import re
import email
import email.mime.multipart
import email.mime.text
from flask import request
from jinja2 import Environment, FileSystemLoader
from apiflask import APIBlueprint
from server import db
from server.config import MAIL_USERNAME, MAIL_PASSWORD, MAIL_USERNAME, MAIL_SENDER_TAG, OpenAIMessage
from server.models.email import Email
from server.models.thread import Thread
from server.models.response import Response
from server.nlp.responses import generate_response

cwd = os.path.dirname(__file__)
env = Environment(loader=FileSystemLoader([f'{cwd}/../email_template']))
emails = APIBlueprint("emails", __name__, url_prefix='/emails', tag='Emails')

def thread_emails_to_openai_messages(thread_emails : list[int]) -> list[OpenAIMessage]:
    """converts list of email to openai messages

    Parameters
    ----------
    thread_email_ids : :obj:`list` of :obj:`int`
        list of email ids

    Returns
    -------
    :obj:`list` of :obj:`OpenAIMessage`
        list of openai messages
    """
    openai_messages = []
    for email in thread_emails:
        role = "user" if email.sender != MAIL_USERNAME else "assistant"
        openai_messages.append({"role": role, "content": email.body})
    return openai_messages

def document_data(documents : list[dict]) -> tuple[list[str], list[list[int]], list[list[float]]]:
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
            doc_ids_question.append(doc['sql_id'])
            doc_confidences_question.append(doc['score'])
        doc_ids.append(doc_ids_question)
        doc_confidences.append(doc_confidences_question)
    return questions, doc_ids, doc_confidences

@emails.route("/receive_email", methods=["POST"])
def receive_email():
    data = request.form

    if "Date" not in data or "From" not in data or "Subject" not in data or "stripped-text" not in data or "stripped-html" not in data or "Message-Id" not in data:
        return {"message": "Missing fields"}, 400

    email = None
    thread = None
    
    if "In-Reply-To" in data:
        # reply to existing email, add to existing thread
        replied_to_email = Email.query.filter_by(message_id = data["In-Reply-To"]).first()
        if data["sender"] != MAIL_USERNAME and replied_to_email:
            thread = Thread.query.get(replied_to_email.thread_id)
            if thread:
                email = Email(data["Date"], data["From"], data["Subject"], data["stripped-text"], data["stripped-html"], data["Message-Id"], False, thread.id)
    else:
        # new email, create new thread
        thread = Thread()
        db.session.add(thread)
        db.session.commit()
        email = Email(data["Date"], data["From"], data["Subject"], data["stripped-text"], data["stripped-html"], data["Message-Id"], False, thread.id)

    if email is not None and thread is not None:
        openai_messages = thread_emails_to_openai_messages(thread.emails)
        openai_res, documents, confidence = generate_response(email.sender, email.body, openai_messages)
        questions, document_ids, document_confidences = document_data(documents)
        db.session.add(email)
        db.session.commit()
        r = Response(openai_res, questions, document_ids, document_confidences, confidence, email.id)
        db.session.add(r)
        thread.last_email = email.id
        thread.resolved = False
        thread_emails = thread.emails
        db.session.commit()
    return data

@emails.route("/send_email", methods=["POST"])
def send_email():
    data = request.form
    reply_to_email = Email.query.get(data["id"])
    clean_regex = re.compile('<.*?>')
    clean_text = re.sub(clean_regex, ' ', data["body"])
    context = {'body': data["body"]}
    template = env.get_template("template.html")
    body = template.render(**context)
    thread = Thread.query.get(reply_to_email.thread_id)
    server = smtplib.SMTP('smtp.mailgun.org', 587)
    server.starttls()
    server.ehlo()
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    msg = email.mime.multipart.MIMEMultipart()
    msg['Subject'] = reply_to_email.subject
    msg['FROM'] = MAIL_SENDER_TAG
    msg['In-Reply-To'] = reply_to_email.message_id
    msg['References'] = reply_to_email.message_id
    msg['To'] = thread.first_sender
    msg['Cc'] = MAIL_USERNAME 
    message_id = email.utils.make_msgid(domain='my.hackmit.org')
    msg['message-id'] = message_id
    msg.attach(email.mime.text.MIMEText(body, 'HTML'))
    server.sendmail(MAIL_USERNAME, [thread.first_sender], msg.as_bytes())
    thread.resolved = True
    reply_email = Email(MAIL_SENDER_TAG, reply_to_email.subject, clean_text, data["body"], message_id, True, thread.id)
    db.session.add(reply_email)
    db.session.commit()
    thread.last_email = reply_email.id
    db.session.commit()
    return {'message': 'Email sent successfully'}

@emails.route("/get_response", methods=["POST"])
def get_response():
    data = request.form
    response = Response.query.filter_by(email_id = data["id"]).first()
    if not response:
        return {'message': 'Response not found'}, 400
    return response.map()

@emails.route("/regen_response", methods=["POST"])
def regen_response():
    data = request.form
    thread = Thread.query.get(data["id"])
    email = Email.query.get(thread.last_email)
    response = Response.query.filter_by(email_id = email.id).first()
    if not thread or not email or not response:
        return {'message': 'Something went wrong!'}, 400
    
    openai_messages = thread_emails_to_openai_messages(thread.emails)
    openai_res, documents, confidence = generate_response(email.sender, email.body, openai_messages)
    questions, document_ids, document_confidences = document_data(documents)

    response.response = openai_res
    response.questions = questions
    response.documents = document_ids
    response.documents_confidence = document_confidences
    response.confidence = confidence
    db.session.commit()

    return response.map()
    

@emails.route("/get_threads", methods=["GET"])
def get_threads():
    thread_list = Thread.query.order_by(Thread.resolved, Thread.last_email.desc()).all()
    email_list = [{'id': thread.id, 'resolved': thread.resolved, 'emailList': [thread_email.map() for thread_email in Email.query.filter_by(thread_id=thread.id).order_by(Email.id).all()]} for thread in thread_list]
    return email_list