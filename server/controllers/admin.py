"""The admin controller handles admin-related routes."""

import json
from ast import literal_eval
from typing import cast

import pandas as pd
from apiflask import APIBlueprint
from flask import request
from sqlalchemy import select

from server import db
from server.models.document import Document
from server.nlp.embeddings import embed_corpus

admin = APIBlueprint("admin", __name__, url_prefix="/admin", tag="Admin")


@admin.route("/upload_document", methods=["POST"])
def upload_text():
    """POST /admin/upload_document"""
    data = request.form
    document = Document(
        data["question"], data["content"], data["source"], data["label"]
    )
    db.session.add(document)
    db.session.commit()
    return {"message": "Document uploaded"}


@admin.route("/delete_document", methods=["POST"])
def delete_text():
    """POST /admin/delete_document"""
    data = request.form
    document = db.session.execute(
        select(Document).where(Document.id == data["id"])
    ).scalar()
    if document is None:
        return {"error": "Document not found"}, 404
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
    """POST /admin/edit_document"""
    data = request.form
    document = db.session.execute(
        select(Document).where(Document.id == data["id"])
    ).scalar()
    if document is None:
        return {"error": "Document not found"}, 404
    document.question = data["question"]
    document.content = data["content"]
    document.source = data["source"]
    document.label = data["label"]
    db.session.commit()
    return {"message": "Document updated"}


@admin.route("/get_documents", methods=["GET"])
def get_all():
    """GET /admin/get_documents"""
    documents = (
        db.session.execute(select(Document).order_by(Document.id.desc()))
        .scalars()
        .all()
    )
    return [document.map() for document in documents]


@admin.route("/update_embeddings", methods=["GET"])
def update_embeddings():
    """GET /admin/update_embeddings"""
    documents = (
        db.session.execute(select(Document).order_by(Document.id.desc()))
        .scalars()
        .all()
    )

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
    """POST /admin/import_json"""
    try:
        file = request.data
        json_data = literal_eval(file.decode("utf8"))
        for doc in json_data:
            document = Document(
                doc.get("question", ""),
                doc["content"],
                doc["source"],
                doc.get("label", ""),
            )
            db.session.add(document)
        db.session.commit()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 400
    return {"message": "JSON imported"}


@admin.route("/export_json", methods=["GET"])
def export_json():
    """GET /admin/export_json"""
    documents = (
        db.session.execute(select(Document).order_by(Document.id.desc()))
        .scalars()
        .all()
    )
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
    """POST /admin/import_csv"""
    try:
        file = request.files["file"]
        df = pd.read_csv(file.stream)

        for _, row in df.iterrows():
            document = Document(
                question=cast(str, "" if pd.isna(row["question"]) else row["question"]),  # type: ignore
                content=cast(str, row["content"]),
                source=cast(str, row["source"]),
                label=cast(str, "" if pd.isna(row["label"]) else row["label"]),  # type: ignore
            )
            db.session.add(document)
        db.session.commit()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 400
    return {"message": "CSV imported"}


@admin.route("/export_csv", methods=["GET"])
def export_csv():
    """GET /admin/export_csv"""
    documents = (
        db.session.execute(select(Document).order_by(Document.id.desc()))
        .scalars()
        .all()
    )
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
    """POST /admin/clear_documents"""
    try:
        documents = (
            db.session.execute(select(Document).order_by(Document.id.desc()))
            .scalars()
            .all()
        )
        for document in documents:
            if document.response_count > 0:
                document.to_delete = True
            else:
                db.session.delete(document)
        db.session.commit()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 400
    return {"message": "Documents cleared"}
