# infrastructure/database/models/products.py

from typing import Optional, List
from sqlalchemy import String, Text, Numeric, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column
from infrastructure.database.models.base import Base, TimestampMixin, TableNameMixin


class Product(Base, TimestampMixin, TableNameMixin):
    __tablename__ = 'products'

    product_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    material: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Telegram media ID

    orders: Mapped[List["Order"]] = relationship(
        "Order", back_populates="product", cascade="all, delete-orphan"
    )
    favorited_by: Mapped[List["Favorite"]] = relationship(
        "Favorite", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Product {self.product_id} {self.name} {self.price}>"
