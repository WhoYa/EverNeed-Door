from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum
from sqlalchemy import String, Text, Float, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.models.base import Base, TimestampMixin, TableNameMixin

class DiscountType(str, PyEnum):
    """
    Перечисление типов скидок.
    """
    PERCENTAGE = "percentage"  # Процентная скидка
    FIXED = "fixed"  # Фиксированная скидка в рублях

class Promotion(Base, TimestampMixin, TableNameMixin):
    """
    Модель акций и скидок.
    
    Attributes:
        promo_id: Уникальный идентификатор акции
        name: Название акции
        description: Описание акции
        discount_type: Тип скидки (процент или фиксированная сумма)
        discount_value: Значение скидки (процент или сумма в рублях)
        start_date: Дата начала действия акции
        end_date: Дата окончания действия акции (опционально)
        is_active: Активна ли акция
        created_by: ID администратора, создавшего акцию
    """
    promo_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    discount_type: Mapped[str] = mapped_column(String(20), nullable=False)
    discount_value: Mapped[float] = mapped_column(Float, nullable=False)  # Процент или фиксированная сумма
    start_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    
    # Отношения
    products = relationship("ProductPromotion", back_populates="promotion", cascade="all, delete-orphan")
    creator = relationship("User", back_populates="created_promotions")
    
    def __repr__(self):
        return f"<Promotion id={self.promo_id} name='{self.name}' type={self.discount_type} value={self.discount_value}>"
    
    @property
    def is_valid(self) -> bool:
        """Проверяет, действительна ли акция на текущий момент"""
        now = datetime.now()
        if not self.is_active:
            return False
        if now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True