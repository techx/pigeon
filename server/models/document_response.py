"""Association table for Document and Response."""

from sqlalchemy import Column, ForeignKey, Integer, Table

from server import db

document_response_table: Table = Table(
    "document_response_table",
    db.Model.metadata,
    Column(
        "document_id",
        Integer,
        ForeignKey("Documents.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "response_id",
        Integer,
        ForeignKey("Responses.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
