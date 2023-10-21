from server import db
from flask import request
from apiflask import APIBlueprint
from server.utils import embed_text

admin = APIBlueprint("admin", __name__, url_prefix='/admin', tag='Admin')

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
  
@admin.route('/upload_document', methods=['POST'])
def upload_text():
    data = request.form
    # label = data['label']
    # content = data['content']
    # embedding = embed_text(content)
    # pipe = client.pipeline()
    # pipe.hset(f"document: {label}, index: {random.randint(0, 10**5)}", mapping={"vector": embedding.tobytes(), "content": content})
    # pipe.execute()

    document = Document(data['question'], data['content'], data['source'], data['label'])
    db.session.add(document)
    db.session.commit()
    return {'message': 'Document uploaded'}

@admin.route('/delete_document', methods=['POST'])
def delete_text():
    data = request.form
    document = Document.query.get(data['id'])
    db.session.delete(document)
    db.session.commit()
    return {'message': 'Document deleted'}

@admin.route('/update_document', methods=['POST'])
def update_text():
    data = request.form
    document = Document.query.get(data['id'])
    document.question = data['question']
    document.content = data['content']
    document.source = data['source']
    db.session.commit()
    return {'message', 'Document updated'}

@admin.route('/get_documents', methods=['GET'])
def get_all():
    documents = Document.query.all()
    return [document.map() for document in documents]