"""Response."""

from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server import db
from server.models.document import Document

if TYPE_CHECKING:
    from server.models.email import Email


class Response(db.Model):
    """Response.

    Table for storing AI responses.

    Attributes:
    id(str): The ID of the response.
    response(str): The response content.
    questions(List[str]): The list of questions.
    documents(List[List[int]]): The list of documents.
    documents_confidence(List[List[float]]): The list of documents' confidence.
    confidence(float): The confidence of the response.
    email_id(int): The ID of the original email.
    email(Email): The original email.
    """

    __tablename__ = "Responses"
    __table_args__ = (UniqueConstraint("email_id", name="unique_email_id"),)

    id: Mapped[str] = mapped_column(primary_key=True, init=False)
    response: Mapped[str] = mapped_column(nullable=False)
    questions: Mapped[List[str]] = mapped_column(nullable=False)
    documents: Mapped[List[List[int]]] = mapped_column(nullable=False)
    documents_confidence: Mapped[List[List[float]]] = mapped_column(nullable=False)
    confidence: Mapped[float] = mapped_column(nullable=False)

    email_id: Mapped[int] = mapped_column(ForeignKey("Emails.id", ondelete="CASCADE"))
    email: Mapped[Email] = relationship(
        back_populates="response", init=False, single_parent=True
    )

    def map(self):
        """Map the response to a dictionary."""
        documents = []
        for index in range(len(self.questions)):
            question_documents = []
            for document_index in range(len(self.documents[index])):
                doc = Document.query.get(self.documents[index][document_index])
                if doc is not None:
                    doc = doc.map()
                    del doc["id"]
                    doc["confidence"] = self.documents_confidence[index][document_index]
                    question_documents.append(doc)
            documents.append(question_documents)
        return {
            "id": self.id,
            "content": self.response,
            "questions": self.questions,
            "documents": documents,
            "confidence": self.confidence,
            "emailId": self.email_id,
        }
