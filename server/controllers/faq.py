from server import db
from flask import request
from apiflask import APIBlueprint
from server.utils import embed_text

faq = APIBlueprint("faq", __name__, url_prefix='/faq', tag='FAQ')

@faq.route("/ask_question", methods=["POST"])
def ask_question():
    data = request.get_json()
    question = data["question"]
    question_embedding = embed_text(question)
    