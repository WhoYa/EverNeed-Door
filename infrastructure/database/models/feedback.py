# infrastructure/database/models/feedback.py

from sqlalchemy import Column, Integer, ForeignKey, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from infrastructure.database.models.base import Base, TableNameMixin, TimestampMixin


class Feedback(Base, TableNameMixin, TimestampMixin):
    """
    Feedback table representing user feedback.
    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    user = relationship("User", back_populates="feedbacks")

    def __repr__(self):
        return f"<Feedback id={self.id} user_id={self.user_id} created_at={self.created_at}>"
