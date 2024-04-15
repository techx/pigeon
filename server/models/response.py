"""Response."""

from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric

from server import db
from server.models.document_response import document_response_table

if TYPE_CHECKING:
    from server.models.document import Document
    from server.models.email import Email


class Response(db.Model):
    """Response.

    Table for storing AI responses.

    Attributes:
        id (int): The ID of the response.
        response (str): The response content.
        questions (List[str]): The list of questions.
        docs_per_question (List[int]): The list of documents per question.
        documents (List[Document]): The list of documents.
        document_confidences (List[float]): The list of documents' confidence.
        confidence (float): The confidence of the response.
        email_id (str): The ID of the original email.
        email (Email): The original email.
    """

    __tablename__ = "response"
    __table_args__ = (UniqueConstraint("email_id", name="unique_email_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    response: Mapped[str] = mapped_column(nullable=False)
    questions: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    docs_per_question: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=False)
    documents: Mapped[List["Document"]] = relationship(
        "Document", secondary=document_response_table, back_populates="responses"
    )
    document_confidences: Mapped[List[float]] = mapped_column(
        ARRAY(Numeric), nullable=False
    )
    confidence: Mapped[float] = mapped_column(nullable=False)
    email_id: Mapped[int] = mapped_column(
        ForeignKey("email.id", ondelete="CASCADE"), nullable=False
    )
    email: Mapped["Email"] = relationship(
        "Email", back_populates="response", init=False, single_parent=True
    )

    def map(self):
        """Map the response to a dictionary."""
        return {
            "id": self.id,
            "content": self.response,
            "questions": self.questions,
            "document_confidences": self.document_confidences,
            "confidence": self.confidence,
            "emailId": self.email_id,
        }
