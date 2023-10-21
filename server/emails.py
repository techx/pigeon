import os
from server import app, db, mail
from flask import request
from flask_mail import Message
from jinja2 import Environment, FileSystemLoader

cwd = os.path.dirname(__file__)
env = Environment(loader=FileSystemLoader([f'{cwd}/emails']))

class Email(db.Model):
    __tablename__ = "Emails"

    id = db.Column(db.Integer, primary_key = True)
    sender = db.Column(db.Text(), nullable = False)
    subject = db.Column(db.String(100), nullable = False)
    body = db.Column(db.Text(), nullable = False)
    resolved = db.Column(db.Boolean, default = False)

    def __init__(self, sender, subject, body, embedding):
        self.sender = sender
        self.subject = subject
        self.body = body

@app.route("/api/receive_email", methods=["POST"])
def receive_email():
    data = request.get_json()
    db.session.add(Email(data["sender"], data["subject"], data["body"]))
    db.session.commit()

@app.route("/api/send_email", methods=["POST"])
def send_email():
    data = request.get_json()
    context = {'body': data["body"]}
    template = env.get_template("template.html")
    body = template.render(**context)
    msg = Message(subject=data["subject"], recipients=[data["email"]], html=body)
    with mail.connect() as conn:
        conn.send(msg)
    email = Email.query.filter_by(sender="", subject="").first()
    email['resolved'] = True
    db.session.commit()