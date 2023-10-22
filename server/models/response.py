from server import db
from sqlalchemy.dialects.postgresql import ARRAY
from server.models.document import Document

class Response(db.Model):
    __tablename__ = "Responses"

    id = db.Column(db.Integer, primary_key = True)
    response = db.Column(db.Text(), nullable = False)
    questions = db.Column(ARRAY(db.Text()), nullable = False) # 1D array
    documents = db.Column(ARRAY(db.Integer), nullable = False) # 2D array
    documents_confidence = db.Column(ARRAY(db.Float), nullable = False) # 2D array
    confidence = db.Column(db.Float, nullable = False)
    email_id = db.Column(db.Integer, nullable = True)

    def __init__(self, response, questions, documents, documents_confidence, confidence, email_id = -1):
        self.response = response
        self.questions = questions
        self.documents = documents
        self.documents_confidence = documents_confidence
        self.confidence = confidence
        self.email_id = email_id

    def map(self):
        return {'id': self.id, 'questions': self.questions, 'documents': self.documents, 'documents_confidence': self.documents_confidence, 'confidence': self.confidence, 'email_id': self.email_id}
