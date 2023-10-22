import os
import smtplib
import email
import email.mime.multipart
import email.mime.text
from flask import request
from jinja2 import Environment, FileSystemLoader
from apiflask import APIBlueprint
from server import db
from server.config import MAIL_USERNAME, MAIL_PASSWORD
from server.models.email import Email
from server.models.thread import Thread

cwd = os.path.dirname(__file__)
env = Environment(loader=FileSystemLoader([f'{cwd}/../email_template']))
emails = APIBlueprint("emails", __name__, url_prefix='/emails', tag='Emails')


@emails.route("/receive_email", methods=["POST"])
def receive_email():
    data = request.form
    if "In-Reply-To" in data:
        replied_to_email = Email.query.filter_by(message_id = data["In-Reply-To"]).first()
        if data["sender"] != "help@my.hackmit.org" and replied_to_email:
            thread = Thread.query.get(replied_to_email.thread_id)
            if thread:
                e = Email(data["From"], data["Subject"], data["stripped-text"], data["stripped-html"], data["Message-Id"], False, thread.id)
                db.session.add(e)
                db.session.commit()
                thread.last_email = e.id
                thread.resolved = False
    else:
        thread = Thread()
        db.session.add(thread)
        db.session.commit()
        e = Email(data["From"], data["Subject"], data["stripped-text"], data["stripped-html"], data["Message-Id"], False, thread.id)
        db.session.add(e)
        db.session.commit()
        thread.last_email = e.id
    db.session.commit()
    return data

@emails.route("/send_email", methods=["POST"])
def send_email():
    data = request.form
    reply_to_email = Email.query.get(data["index"])
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
    msg['FROM'] = "HackMIT Team <help@my.hackmit.org>"
    msg['In-Reply-To'] = reply_to_email.message_id
    msg['References'] = reply_to_email.message_id
    msg['To'] = thread.first_sender
    msg['Cc'] = "help@my.hackmit.org" 
    message_id = email.utils.make_msgid(domain='my.hackmit.org')
    msg['message-id'] = message_id
    msg.attach(email.mime.text.MIMEText(body, 'HTML'))
    server.sendmail("help@my.hackmit.org", [thread.first_sender], msg.as_bytes())
    thread.resolved = True
    reply_email = Email('help@my.hackmit.org', reply_to_email.subject, data["body"], data["body"], message_id, True, thread.id)
    db.session.add(reply_email)
    db.session.commit()
    thread.last_email = reply_email.id
    db.session.commit()
    return {'message': 'Email sent successfully'}

@emails.route("/get_threads", methods=["GET"])
def get_threads():
    thread_list = Thread.query.order_by(Thread.resolved, Thread.last_email.desc()).all()
    email_list = [{'id': thread.id, 'resolved': thread.resolved, 'emailList': [thread_email.map() for thread_email in Email.query.filter_by(thread_id=thread.id).order_by(Email.id).all()]} for thread in thread_list]
    return email_list