from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from infrastructure.database.models.base import Base, TimestampMixin, TableNameMixin


class Category(Base, TimestampMixin, TableNameMixin):
    """
    Модель категории товаров.
    
    Attributes:
        category_id: Уникальный идентификатор категории
        name: Название категории
        description: Описание категории
        parent_id: ID родительской категории (для иерархии)
        
    Relationships:
        parent: Родительская категория
        children: Дочерние категории
        products: Товары в данной категории
    """
    __tablename__ = 'categories'
    
    category_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.category_id", ondelete="SET NULL"), nullable=True)
    
    # Отношения
    parent = relationship("Category", remote_side=[category_id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    products = relationship("Product", secondary="product_categories", back_populates="categories")
    
    def __repr__(self):
        return f"<Category id={self.category_id} name='{self.name}'>"
    
    @validates('name')
    def validate_name(self, key, name) -> str:
        """Валидация названия категории."""
        if not name or len(name.strip()) == 0:
            raise ValueError("Название категории не может быть пустым")
        return name.strip()


class ProductCategory(Base):
    """
    Связующая таблица между товарами и категориями (многие ко многим).
    """
    __tablename__ = 'product_categories'
    
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.category_id", ondelete="CASCADE"), primary_key=True)