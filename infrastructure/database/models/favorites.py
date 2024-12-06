from sqlalchemy import ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database.models.base import Base, TimestampMixin, TableNameMixin


class Favorite(Base, TimestampMixin, TableNameMixin):
    """
    Favorites table representing products favorited by a user.
    """
    favorite_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)

    def __repr__(self):
        return f"<Favorite {self.favorite_id} User: {self.user_id} Product: {self.product_id}>"

