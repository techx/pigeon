from server import db

class Email(db.Model):
    __tablename__ = "Emails"

    id = db.Column(db.Integer, primary_key = True)
    sender = db.Column(db.Text(), nullable = False)
    subject = db.Column(db.String(100), nullable = False)
    body = db.Column(db.Text(), nullable = False)
    message_id = db.Column(db.Text(), nullable = False)
    resolved = db.Column(db.Boolean, default = False)
    reply = db.Column(db.Boolean, default = False)

    def __init__(self, sender, subject, body, message_id, reply):
        self.sender = sender
        self.subject = subject
        self.body = body
        self.reply = reply
        if reply:
            self.message_id = ""
        else:
            self.message_id = message_id

    def map(self):
        return {'id': self.id, 'sender': self.sender, 'subject': self.subject, 'body': self.body, 'message_id': self.message_id, 'resolved': self.resolved, 'reply': self.reply}
