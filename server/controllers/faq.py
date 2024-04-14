"""The faq controller handles FAQ-related routes.

This controller is a placeholder for future routes that may be used in the
future. For example, a Discord bot could be used to answer frequently asked
questions.
"""

from apiflask import APIBlueprint

faq = APIBlueprint("faq", __name__, url_prefix="/faq", tag="FAQ")


# @faq.route("/ask_question", methods=["POST"])
# def ask_question():
#     data = request.get_json()
#     question = data["question"]
# question_embedding = embed_text(question)
