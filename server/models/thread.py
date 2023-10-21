from server import db
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from server.models.email import Email

class Thread(db.Model):
    __tablename__ = "Threads"

    id = db.Column(Integer, primary_key = True)
    email_list = db.Column(ARRAY(Integer), nullable = False)
    last_email = db.Column(Integer, nullable=False)

    def __init__(self, email):
        self.email_list = [email]
        self.last_email = email

    def map(self):
        return {'id': self.id, 'email_list': self.email_list}

    @hybrid_method
    def has_email(self, email):
        return email in self.email_list
        
    @has_email.expression
    def has_email(cls, email):
        return cls.email_list.contains([email])
    
    @hybrid_property
    def first_sender(self):
        return Email.query.filter_by(id=self.email_list[0]).first().sender