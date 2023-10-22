import os
import smtplib
import email
import email.mime.multipart
import email.mime.text
from flask import request
from jinja2 import Environment, FileSystemLoader
from apiflask import APIBlueprint
from server import db
from server.config import MAIL_USERNAME, MAIL_PASSWORD, OpenAIMessage
from server.models.email import Email
from server.models.thread import Thread
from server.models.response import Response
from server.nlp.responses import generate_response

cwd = os.path.dirname(__file__)
env = Environment(loader=FileSystemLoader([f'{cwd}/../email_template']))
emails = APIBlueprint("emails", __name__, url_prefix='/emails', tag='Emails')

def thread_email_ids_to_openai_messages(thread_email_ids : list[int]) -> list[OpenAIMessage]:
    """converts list of email ids to openai messages

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
    for email_id in thread_email_ids:
        email = Email.query.get(email_id)
        role = "user" if email.sender != "help@my.hackmit.org" else "assistant"
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
    e = Email(data["From"], data["Subject"], data["stripped-text"], data["Message-Id"], False)
    db.session.add(e)
    db.session.commit()

    thread_email_ids = []
    if "In-Reply-To" in data:
        if data["sender"] != "help@my.hackmit.org":
            email = Email.query.filter_by(message_id = data["In-Reply-To"]).first()
            if not email:
                # email not already in the db. start a new thread with current email
                thread = Thread(e.id)
                db.session.add(thread)
            else:
                thread = Thread.query.filter(Thread.has_email(email.id)).first()
                if not thread:
                    # thread not already in the db. start a new thread with the previous email
                    thread = Thread(email.id)
                    db.session.add(thread)
                thread.email_list = thread.email_list + [e.id]
                thread.last_email = e.id
                thread_email_ids = thread.email_list
    else:
        thread = Thread(e.id)
        db.session.add(thread)
    db.session.commit()

    openai_messages = thread_email_ids_to_openai_messages(thread_email_ids)
    openai_res, documents, confidence = generate_response(e.body, openai_messages)
    questions, document_ids, document_confidences = document_data(documents)
    r = Response(openai_res, questions, document_ids, document_confidences, confidence, e.id)

    db.session.add(r)
    db.session.commit()

    return data

@emails.route("/send_email", methods=["POST"])
def send_email():
    data = request.form
    reply_to_email = Email.query.get(data["index"])
    context = {'body': data["body"]}
    template = env.get_template("template.html")
    body = template.render(**context)
    thread = Thread.query.filter(Thread.has_email(reply_to_email.id)).first()
    server = smtplib.SMTP('smtp.mailgun.org', 587)
    server.starttls()
    server.ehlo()
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    msg = email.mime.multipart.MIMEMultipart()
    msg['Subject'] = f"RE: {reply_to_email.subject}"
    msg['FROM'] = "HackMIT Team <help@my.hackmit.org>"
    msg['In-Reply-To'] = reply_to_email.message_id
    msg['References'] = reply_to_email.message_id
    msg['To'] = thread.first_sender
    msg['Cc'] = "help@my.hackmit.org" 
    message_id = email.utils.make_msgid(domain='my.hackmit.org')
    msg['message-id'] = message_id
    msg.attach(email.mime.text.MIMEText(body, 'HTML'))
    server.sendmail("help@my.hackmit.org", [thread.first_sender], msg.as_bytes())
    reply_to_email.resolved = True
    reply_email = Email('help@my.hackmit.org', f"RE: {reply_to_email.subject}", data["body"], message_id, True)
    db.session.add(reply_email)
    db.session.commit()
    thread.email_list = thread.email_list + [reply_email.id]
    thread.last_email = reply_email.id
    db.session.commit()
    return {'message': 'Email sent successfully'}

@emails.route("/get_threads", methods=["GET"])
def get_threads():
    thread_list = Thread.query.order_by(Thread.last_email.desc()).all()
    email_list = []
    for thread in thread_list:
        thread_emails = []
        for email_id in thread.email_list:
          thread_emails.append(Email.query.get(email_id).map())
        email_list.append({'id': thread.id, 'email_list': thread_emails})
    return email_list