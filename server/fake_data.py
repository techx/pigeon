"""Fake data for seed cli and testing."""

import json

from server import db
from server.models.document import Document

FLASK_SEED_CORPUS = "server/nlp/corpus_flask_seed.json"


def generate_test_documents():
    """Generate test documents."""
    with open(FLASK_SEED_CORPUS) as f:
        corpus = json.load(f)

    documents = []
    for doc in corpus:
        document = Document(
            question=doc["question"],
            label=doc["question"],
            source=doc["source"],
            content=doc["content"],
        )
        db.session.add(document)
        db.session.commit()
        documents.append(document)

    test_documents = [
        {
            "question": doc.question,
            "source": doc.source,
            "content": doc.content,
            "sql_id": doc.id,
        }
        for doc in documents
    ]
    return test_documents
