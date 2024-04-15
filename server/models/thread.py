"""Thread."""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server import db

if TYPE_CHECKING:
    from server.models.email import Email


class Thread(db.Model):
    """Thread.

    Table for storing threads.

    id(str): The ID of the thread.
    resolved(bool): Whether the thread is resolved.
    last_email(str): The ID of the last email in the thread.
    emails(list): The emails in the thread.
    """

    __tablename__ = "Threads"

    id: Mapped[str] = mapped_column(primary_key=True, init=False)
    last_email: Mapped[Optional[str]] = mapped_column(nullable=True)
    resolved: Mapped[bool] = mapped_column(nullable=False, default=False)

    emails: Mapped[List[Email]] = relationship(
        "Email",
        back_populates="thread",
        default_factory=list,
        cascade="all, delete-orphan",
    )

    @hybrid_property
    def first_sender(self):
        """Get the first sender of the thread."""
        from server.models.email import Email

        email = db.session.execute(
            select(Email).where(Email.thread_id == self.id)
        ).scalar_one_or_none()
        return email.sender if email else None
