"""Document."""

from sqlalchemy.orm import Mapped, mapped_column

from server import db


class Document(db.Model):
    """Document.

    Table for storing documents.

    id(str): The ID of the document.
    question(str): The question of the document.
    content(str): The content of the document.
    source(str): The source of the document.
    label(str): The label of the document.
    to_delete(bool): Whether the document is to be deleted.
    response_count(int): The number of responses the document has.
    """

    __tablename__ = "Documents"

    id: Mapped[str] = mapped_column(primary_key=True, init=False)
    question: Mapped[str] = mapped_column(nullable=False)
    label: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    source: Mapped[str] = mapped_column(nullable=False)
    to_delete: Mapped[bool] = mapped_column(default=False, init=False)
    response_count: Mapped[int] = mapped_column(default=0, init=False)

    def map(self):
        """Map the document to a dictionary."""
        return {
            "id": self.id,
            "question": self.question,
            "content": self.content,
            "source": self.source,
            "label": self.label,
            "to_delete": self.to_delete,
            "response_count": self.response_count,
        }
