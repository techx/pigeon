from server import db

class Email(db.Model):
    __tablename__ = "Emails"

    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime)
    sender = db.Column(db.Text(), nullable = False)
    subject = db.Column(db.String(100), nullable = False)
    body = db.Column(db.Text(), nullable = True)
    html = db.Column(db.Text(), nullable = False)
    message_id = db.Column(db.Text(), nullable = False)
    reply = db.Column(db.Boolean, default = False)
    thread_id = db.Column(db.Integer, db.ForeignKey('Threads.id'), nullable = False)

    def __init__(self, date, sender, subject, body, html, message_id, reply, thread_id):
        self.date = date
        self.sender = sender
        self.subject = subject
        self.body = body
        self.html = html
        self.reply = reply
        self.message_id = message_id
        self.thread_id = thread_id

    def map(self):
        return {'id': self.id, 'date': self.date, 'sender': self.sender, 'subject': self.subject, 'body': self.body, 'html': self.html, 'messageId': self.message_id, 'reply': self.reply, 'threadId': self.thread_id}
