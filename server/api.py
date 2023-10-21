from server import app
from flask import request
import random
from utils import embed_text
@app.route('/api/upload', methods=['POST'])
def upload_document():
    data = request.get_json()
    label = data['label']
    content = data['content']
    embedding = embed_text(content)
    pipe = client.pipeline()
    pipe.hset(f"document: {label}, index: {random.randint(0, 10**5)}", mapping={"vector": embedding.tobytes(), "content": content})
    pipe.execute()

@app.route("/api/ask_question", methods=["POST"])
def ask_question():
    data = request.get_json()
    question = data["question"]
    question_embedding = embed_text(question)
    