from server import db

class Document(db.Model):
    __tablename__ = "Documents"

    id = db.Column(db.Integer, primary_key = True)
    question = db.Column(db.Text(), nullable = False)
    label = db.Column(db.Text(), nullable = False)
    content = db.Column(db.Text(), nullable = False)
    source = db.Column(db.Text(), nullable = False)

    def __init__(self, question, content, source, label):
        self.question = question
        self.content = content
        self.source = source
        self.label = label
    
    def map(self):
        return {'id': self.id, 'question': self.question, 'content': self.content, 'source': self.source, 'label': self.label}