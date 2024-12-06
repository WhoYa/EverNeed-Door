from typing import Optional
from sqlalchemy import String, Boolean, text, BIGINT
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database.models.base import Base, TimestampMixin, TableNameMixin
from sqlalchemy.orm import relationship


class User(Base, TimestampMixin, TableNameMixin):
    """
    User table representing a user in the application.
    """

    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, unique=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    role: Mapped[str] = mapped_column(String(10), nullable=False, server_default=text("'user'"))
    active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))

    def __repr__(self):
        return f"<User {self.user_id} {self.username} {self.first_name} {self.last_name} {self.role}>"
