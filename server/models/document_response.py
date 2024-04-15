"""Association table for Document and Response."""

from sqlalchemy import Column, ForeignKey, Table

from server import db

document_response_table: Table = Table(
    "document_response_table",
    db.Model.metadata,
    Column(
        "document_id",
        ForeignKey("document.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "response_id",
        ForeignKey("response.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
