from server import db
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from server.models.email import Email

class Thread(db.Model):
    __tablename__ = "Threads"

    id = db.Column(Integer, primary_key = True)
    resolved = db.Column(db.Boolean, nullable = False, default=False)
    last_email = db.Column(Integer)
    emails = relationship("Email", backref="threads", lazy=True)
  
    @hybrid_property
    def first_sender(self):
        return Email.query.filter_by(thread_id = self.id).order_by(Email.id).first().sender