from server import db
from flask import request
from apiflask import APIBlueprint
from server.models.document import Document
from server.models.response import Response
from server.nlp.embeddings import embed_corpus
from ast import literal_eval
import json
import pandas as pd
import numpy as np
import csv
import io


admin = APIBlueprint("admin", __name__, url_prefix="/admin", tag="Admin")


@admin.route("/upload_document", methods=["POST"])
def upload_text():
    data = request.form
    document = Document(
        data["question"], data["content"], data["source"], data["label"]
    )
    db.session.add(document)
    db.session.commit()
    return {"message": "Document uploaded"}


@admin.route("/delete_document", methods=["POST"])
def delete_text():
    data = request.form
    document = Document.query.get(data["id"])
    db.session.delete(document)
    db.session.commit()
    return {"message": "Document deleted"}


@admin.route("/edit_document", methods=["POST"])
def update_text():
    data = request.form
    document = Document.query.get(data["id"])
    document.question = data["question"]
    document.content = data["content"]
    document.source = data["source"]
    document.label = data["label"]
    db.session.commit()
    return {"message": "Document updated"}


@admin.route("/get_documents", methods=["GET"])
def get_all():
    documents = Document.query.order_by(Document.id.desc()).all()
    return [document.map() for document in documents]


@admin.route("/update_embeddings", methods=["GET"])
def update_embeddings():
    documents = Document.query.order_by(Document.id.desc()).all()
    docs = [document.map() for document in documents]
    modified_corpus = [
        {
            "question": doc["question"],
            "source": doc["source"],
            "content": doc["content"],
            "sql_id": doc["id"],
        }
        for doc in docs
    ]
    embed_corpus(modified_corpus)
    return {"message": "Embeddings updated"}


@admin.route("/upload_json", methods=["POST"])
def upload_json():
    try:
        file = request.data
        json_data = literal_eval(file.decode("utf8"))
        for doc in json_data:
            document = Document(
                doc["question"] if "question" in doc else "",
                doc["content"],
                doc["source"],
                doc["label"] if "label" in doc else "",
            )
            db.session.add(document)
        db.session.commit()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 400
    return {"message": "Documents imported"}


@admin.route("/import_csv", methods=["POST"])
def import_csv():
    try:
        file = request.files["file"]
        df = pd.read_csv(file.stream)

        for _, row in df.iterrows():
            document = Document(
                "" if pd.isna(row["question"]) else row["question"],
                row["content"],
                row["source"],
                "" if pd.isna(row["label"]) else row["label"],
            )
            db.session.add(document)
        db.session.commit()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 400
    return {"message": "Documents imported"}


@admin.route("/clear_documents", methods=["POST"])
def clear_documents():
    try:
        Document.query.delete()
        db.session.commit()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 400
    return {"message": "Documents cleared"}
