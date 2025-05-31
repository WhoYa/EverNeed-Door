from enum import Enum
from sqlalchemy import ForeignKey, String, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.models.base import Base, TimestampMixin, TableNameMixin

class SubscriptionType(str, Enum):
    """
    Перечисление типов подписок.
    """
    NEW_PRODUCTS = "new_products"  # Подписка на новые товары
    PROMOTIONS = "promotions"  # Подписка на акции и скидки
    ALL = "all"  # Подписка на все уведомления

class Subscription(Base, TimestampMixin, TableNameMixin):
    """
    Модель подписок пользователей.
    
    Attributes:
        sub_id: Уникальный идентификатор подписки
        user_id: ID пользователя
        subscription_type: Тип подписки
        is_active: Активна ли подписка
    """
    sub_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    subscription_type: Mapped[str] = mapped_column(String(20), nullable=False, default=SubscriptionType.ALL.value)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Отношения
    user = relationship("User", back_populates="subscriptions")
    
    # Уникальное ограничение: один тип подписки на пользователя
    __table_args__ = (
        UniqueConstraint('user_id', 'subscription_type', name='uq_user_subscription_type'),
    )
    
    def __repr__(self):
        status = "active" if self.is_active else "inactive"
        return f"<Subscription id={self.sub_id} user_id={self.user_id} type='{self.subscription_type}' {status}>"