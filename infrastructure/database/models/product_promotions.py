from datetime import datetime
from sqlalchemy import ForeignKey, TIMESTAMP, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.models.base import Base, TableNameMixin

class ProductPromotion(Base, TableNameMixin):
    """
    Связующая таблица между товарами и акциями.
    
    Attributes:
        id: Уникальный идентификатор связи
        product_id: ID товара
        promo_id: ID акции
        created_at: Дата создания связи
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    promo_id: Mapped[int] = mapped_column(ForeignKey("promotions.promo_id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    
    # Отношения
    product = relationship("Product", back_populates="promotions")
    promotion = relationship("Promotion", back_populates="products")
    
    __table_args__ = (
        UniqueConstraint('product_id', 'promo_id', name='uq_product_promotion'),
    )
    
    def __repr__(self):
        return f"<ProductPromotion id={self.id} product_id={self.product_id} promo_id={self.promo_id}>"