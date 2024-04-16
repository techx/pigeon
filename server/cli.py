"""Flask CLI commands."""

from flask import Blueprint

from server import db
from server.fake_data import (
    generate_fake_email,
    generate_fake_thread,
    generate_test_documents,
)
from server.models.document import Document
from server.nlp.embeddings import embed_corpus

seed = Blueprint("seed", __name__)


def _embed_existing_documents(documents: list[Document]):
    """Embed existing documents."""
    to_embed_documents = [
        {
            "question": doc.question,
            "source": doc.source,
            "content": doc.content,
            "sql_id": doc.id,
        }
        for doc in documents
    ]
    embed_corpus(to_embed_documents)


@seed.cli.command()
def corpus():
    """Add test documents to the corpus."""
    test_documents = generate_test_documents()
    embed_corpus(test_documents)


@seed.cli.command()
def email():
    """Seed the database with a test email."""
    docs = db.session.query(Document).all()
    if len(docs) == 0:
        # the redis index needs to have non-zero documents to be able to generate
        # responses, so the only way this command succeeds is if the corpus is
        # already populated
        print("No documents in the database. Generating test documents...")
        test_documents = generate_test_documents()
        embed_corpus(test_documents)
    else:
        print("Embedding existing documents...")
        _embed_existing_documents(docs)

    generate_fake_email()


@seed.cli.command()
def thread():
    """Seed the database with a test thread."""
    docs = db.session.query(Document).all()
    if len(docs) == 0:
        # the redis index needs to have non-zero documents to be able to generate
        # responses, so the only way this command succeeds is if the corpus is
        # already populated
        print("No documents in the database. Generating test documents...")
        test_documents = generate_test_documents()
        embed_corpus(test_documents)
    else:
        print("Embedding existing documents...")
        _embed_existing_documents(docs)

    generate_fake_thread()
