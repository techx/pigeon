"""Email."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server import db

if TYPE_CHECKING:
    from server.models.response import Response
    from server.models.thread import Thread


class Email(db.Model):
    """Email.

    Table for storing emails.

    id(str): The ID of the email.
    date(DateTime): The date of the email in UTC.
    sender(str): The sender of the email.
    subject(str): The subject of the email.
    body(str): The body of the email.
    message_id(str): The message ID of the email.
    response(Response): AI response to the email.
    is_reply(bool): Whether the email is a reply to another email.
    thread_id(int): The ID of the thread the email belongs to.
    thread(Thread): The thread the email belongs to.
    """

    __tablename__ = "Emails"

    id: Mapped[str] = mapped_column(db.Integer, primary_key=True)
    date: Mapped[DateTime] = mapped_column(nullable=False)
    sender: Mapped[str] = mapped_column(nullable=False)
    subject: Mapped[str] = mapped_column(nullable=False)
    body: Mapped[str] = mapped_column(nullable=False)
    message_id: Mapped[str] = mapped_column(nullable=False)

    response: Mapped[Optional[Response]] = relationship(
        back_populates="email", init=False
    )

    is_reply: Mapped[bool] = mapped_column(nullable=False)

    thread_id: Mapped[int] = mapped_column(ForeignKey("Threads.id"), nullable=False)
    thread: Mapped[Thread] = relationship(back_populates="emails")

    def map(self):
        """Map the email to a dictionary."""
        return {
            "id": self.id,
            "date": self.date,
            "sender": self.sender,
            "subject": self.subject,
            "body": self.body,
            "message_id": self.message_id,
            "is_reply": self.is_reply,
            "thread_id": self.thread_id,
        }
