from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from infrastructure.database.models.base import Base, TimestampMixin, TableNameMixin


class Order(Base, TimestampMixin, TableNameMixin):
    """
    Represents an order in the database.

    Attributes:
        order_id: Primary key, unique identifier for the order.
        user_id: Foreign key linking to the user who placed the order.
        product_id: Foreign key linking to the product being ordered.
        quantity: Number of items in the order.
        total_price: Total price for the order (calculated as product price * quantity).
        status: Current status of the order (e.g., 'Processing', 'Delivered', 'Cancelled').
        created_at: Timestamp of when the order was created.
        updated_at: Timestamp of when the order was last updated.
    """

    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="Processing")

    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")

    def __repr__(self):
        return (
            f"<Order(order_id={self.order_id}, user_id={self.user_id}, "
            f"product_id={self.product_id}, quantity={self.quantity}, "
            f"total_price={self.total_price}, status={self.status})>"
        )
