from server import db
from flask import request
from apiflask import APIBlueprint

admin = APIBlueprint("admin", __name__, url_prefix='/admin', tag='Admin')
  
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