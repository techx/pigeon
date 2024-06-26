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
        """Map the response to a dictionary.

        Groups documents and document_confidences into a list of lists clustered by
        question.
        """
        doc_confs = []
        docs = []
        cur_idx = 0
        for num_docs in self.docs_per_question:
            doc_confs.append(self.document_confidences[cur_idx : cur_idx + num_docs])
            docs.append(self.documents[cur_idx : cur_idx + num_docs])
            cur_idx += num_docs
        docs = [[doc.map() for doc in doc_list] for doc_list in docs]
        for i, doc_list in enumerate(docs):
            for j, doc in enumerate(doc_list):
                doc["confidence"] = doc_confs[i][j]
        return {
            "id": self.id,
            "content": self.response,
            "questions": self.questions,
            "documents": docs,
            "confidence": self.confidence,
            "emailId": self.email_id,
        }
