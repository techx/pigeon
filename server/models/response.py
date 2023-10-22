from server import db
from sqlalchemy.dialects.postgresql import ARRAY
from server.models.document import Document

class Response(db.Model):
    __tablename__ = "Responses"

    id = db.Column(db.Integer, primary_key = True)
    email_id = db.Column(db.Integer, nullable = False)
    documents = db.Column(ARRAY(db.Integer), nullable = False)
    confidence = db.Column(db.Float, nullable = False)

    def __init__(self, email_id, documents, confidence):
        self.email_id = email_id
        self.documents = documents
        self.confidence = confidence

    def map(self):
        return {'id': self.id, 'email_id': self.email_id, 'documents': self.documents, 'confidence': self.confidence}
