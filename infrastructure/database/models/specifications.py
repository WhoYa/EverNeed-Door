from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.models.base import Base, TimestampMixin, TableNameMixin


class Specification(Base, TimestampMixin, TableNameMixin):
    """
    Модель для хранения характеристик товаров.
    
    Attributes:
        spec_id: Уникальный идентификатор характеристики
        product_id: ID товара, к которому относится характеристика
        name: Название характеристики
        value: Значение характеристики
        
    Relationships:
        product: Товар, к которому относится характеристика
    """
    __tablename__ = 'specifications'
    
    spec_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Отношения
    product = relationship("Product", back_populates="specifications")
    
    __table_args__ = (
        UniqueConstraint('product_id', 'name', name='uq_product_spec_name'),
    )
    
    def __repr__(self):
        return f"<Specification id={self.spec_id} name='{self.name}' value='{self.value}'>"