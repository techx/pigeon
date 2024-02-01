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
    if document.response_count > 0:
        document.to_delete = True
        db.session.commit()
        return {"message": "Document marked for deletion"}
    else:
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
def update_embeddings(init=False):
    documents = Document.query.order_by(Document.id.desc()).all()
    if init and len(documents) == 0:
        # initialize with some default documents to create the index
        document = Document(
            "what is hackmit?",
            "HackMIT is a weekend-long event where thousands of students from around the world come together to work on cool new software and/or hardware projects.",
            "https://hackmit.org",
            "what is hackmit?",
        )
        db.session.add(document)
        document = Document(
            "what is blueprint?",
            "Blueprint is a weekend-long learnathon and hackathon for high school students hosted at MIT",
            "https://blueprint.hackmit.org",
            "what is blueprint?",
        )
        db.session.add(document)
        db.session.commit()

    docs = [document.map() for document in documents if not document.to_delete]
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


@admin.route("/import_json", methods=["POST"])
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
    return {"message": "JSON imported"}


@admin.route("/export_json", methods=["GET"])
def export_json():
    documents = Document.query.order_by(Document.id.desc()).all()
    return json.dumps(
        [
            {
                "question": document.question,
                "content": document.content,
                "source": document.source,
                "label": document.label,
            }
            for document in documents
            if not document.to_delete
        ],
        indent=4,
    )


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
    return {"message": "CSV imported"}


@admin.route("/export_csv", methods=["GET"])
def export_csv():
    documents = Document.query.order_by(Document.id.desc()).all()
    df = pd.DataFrame(
        [
            {
                "question": document.question,
                "content": document.content,
                "source": document.source,
                "label": document.label,
            }
            for document in documents
            if not document.to_delete
        ]
    )
    csv = df.to_csv(index=False)
    return csv


@admin.route("/clear_documents", methods=["POST"])
def clear_documents():
    try:
        documents = Document.query.order_by(Document.id.desc()).all()
        for document in documents:
            if document.response_count > 0:
                document.to_delete = True
            else:
                db.session.delete(document)
        db.session.commit()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 400
    return {"message": "Documents cleared"}


# on server start, re-embed all documents
update_embeddings(init=True)
