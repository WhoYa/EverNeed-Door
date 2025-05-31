from datetime import datetime
from sqlalchemy import ForeignKey, Integer, String, TIMESTAMP, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.models.base import Base, TableNameMixin

class ProductStatistic(Base, TableNameMixin):
    """
    Модель статистики товаров.
    
    Attributes:
        stat_id: Уникальный идентификатор записи статистики
        product_id: ID товара
        stat_type: Тип статистики (view - просмотр, favorite - добавление в избранное, purchase - покупка)
        count: Количество действий данного типа
        date: Дата записи статистики
    """
    stat_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    stat_type: Mapped[str] = mapped_column(String(20), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    
    # Отношения
    product = relationship("Product")
    
    # Уникальное ограничение: одна запись статистики на товар, тип и день
    __table_args__ = (
        UniqueConstraint('product_id', 'stat_type', func.date('date'), name='uq_product_stat_daily'),
    )
    
    def __repr__(self):
        return f"<ProductStatistic id={self.stat_id} product_id={self.product_id} type='{self.stat_type}' count={self.count}>"
    
    __table_args__ = (
    UniqueConstraint(
        "product_id",
        "stat_type",
        func.date(date).label("day"),
        name="uq_product_stat_daily"
    ),
)