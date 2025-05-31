from typing import Optional
from sqlalchemy import String, Text, Integer, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from infrastructure.database.models.base import Base, TimestampMixin, TableNameMixin


class Review(Base, TimestampMixin, TableNameMixin):
    """
    Модель отзыва о товаре.
    
    Attributes:
        review_id: Уникальный идентификатор отзыва
        product_id: ID товара, к которому относится отзыв
        user_id: ID пользователя, оставившего отзыв
        rating: Оценка товара от 1 до 5
        text: Текст отзыва
        is_approved: Флаг подтверждения отзыва администратором
    """
    __tablename__ = 'reviews'
    
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )
    
    review_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Отношения
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review id={self.review_id} rating={self.rating} product_id={self.product_id}>"
    
    @validates('rating')
    def validate_rating(self, key, rating) -> int:
        """Валидация рейтинга."""
        if not 1 <= rating <= 5:
            raise ValueError("Рейтинг должен быть от 1 до 5")
        return rating