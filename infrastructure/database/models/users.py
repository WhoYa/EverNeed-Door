# infrastructure/database/models/users.py

from typing import Optional, List
from sqlalchemy import String, Boolean, text, BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.models.base import Base, TimestampMixin, TableNameMixin


class User(Base, TimestampMixin, TableNameMixin):
    """
    User table representing a user in the application.
    """

    user_id: Mapped[int] = mapped_column(
        BIGINT, primary_key=True, unique=True, autoincrement=False
    )
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default=text("'user'")
    )
    active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))

    # Отношения с заказами
    orders: Mapped[List["Order"]] = relationship(
        "Order", back_populates="user", cascade="all, delete-orphan"
    )

    # Новые отношения с обратной связью и избранным
    feedbacks: Mapped[List["Feedback"]] = relationship(
        "Feedback", back_populates="user", cascade="all, delete-orphan"
    )
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite", back_populates="user", cascade="all, delete-orphan"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="user", cascade="all, delete-orphan"
    )
    created_promotions: Mapped[List["Promotion"]] = relationship(
        "Promotion", back_populates="creator", cascade="all, delete-orphan"
    )
    
    # Отношения с подписками
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<User {self.user_id} {self.username} "
            f"{self.first_name} {self.last_name} {self.role}>"
        )
