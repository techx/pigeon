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

    Attributes:
        id (int): The ID of the thread.
        resolved (bool): Whether the thread is resolved.
        last_email (int): The ID of the last email in the thread.
        emails (list): The emails in the thread.
        read (bool): Whether the thread is read.
    """

    __tablename__ = "thread"

    id: Mapped[int] = mapped_column(primary_key=True, init=False, autoincrement=True)
    last_email: Mapped[Optional[int]] = mapped_column(nullable=True, init=False)
    resolved: Mapped[bool] = mapped_column(nullable=False, default=False, init=False)
    read: Mapped[bool] = mapped_column(nullable=False, default=False, init=False)

    emails: Mapped[List["Email"]] = relationship(
        "Email",
        back_populates="thread",
        default_factory=list,
        cascade="all, delete-orphan",
        init=False,
    )

    @hybrid_property
    def first_sender(self):
        """Get the first sender of the thread."""
        from server.models.email import Email

        email = db.session.execute(
            select(Email).where(Email.thread_id == self.id)
        ).scalar()
        return email.sender if email else None
