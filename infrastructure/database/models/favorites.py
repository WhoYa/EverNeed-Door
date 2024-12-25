# infrastructure/database/models/favorites.py

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from infrastructure.database.models.base import Base, TableNameMixin, TimestampMixin


class Favorite(Base, TableNameMixin, TimestampMixin):
    """
    Favorite table representing user's favorite products.
    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)

    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorited_by")

    def __repr__(self):
        return (
            f"<Favorite id={self.id} user_id={self.user_id} "
            f"product_id={self.product_id} created_at={self.created_at}>"
        )
