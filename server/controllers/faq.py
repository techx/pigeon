from apiflask import APIBlueprint

faq = APIBlueprint("faq", __name__, url_prefix="/faq", tag="FAQ")


# this is a placeholder for a route that might be used in the future
# (e.g., discord bot)
# @faq.route("/ask_question", methods=["POST"])
# def ask_question():
#     data = request.get_json()
#     question = data["question"]
# question_embedding = embed_text(question)
