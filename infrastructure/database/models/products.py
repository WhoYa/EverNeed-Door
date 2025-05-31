# infrastructure/database/models/products.py

from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, TIMESTAMP, CheckConstraint, Integer, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from infrastructure.database.models.base import Base, TimestampMixin, TableNameMixin


class ProductType(str, Enum):
    """
    Enumeration of product types.
    """
    DOOR = "дверь"
    ACCESSORY = "аксессуар"
    OTHER = "другое"
    

class Product(Base, TimestampMixin, TableNameMixin):
    """
    Product model.
    
    Attributes:
        product_id: Unique product identifier
        name: Product name
        description: Product description
        type: Product type (door, accessory, etc.)
        material: Product material
        price: Product price
        stock_quantity: Quantity in stock
        is_in_stock: Flag indicating product availability
        discount_price: Discounted price (if promotion is applied)
        image_url: Image URL or Telegram media ID
        average_rating: Average product rating
        
    Relationships:
        orders: Relationship with orders
        favorited_by: Relationship with favorites
        promotions: Relationship with promotions
        categories: Relationship with categories
        specifications: Relationship with specifications
        reviews: Relationship with reviews
    """
    __tablename__ = 'products'
    
    # Price constraints
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_non_negative'),
    )

    product_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    material: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_in_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    discount_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Telegram media ID
    average_rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)

    # Relationships
    if TYPE_CHECKING:
        from infrastructure.database.models.orders import Order
        from infrastructure.database.models.favorites import Favorite
        from infrastructure.database.models.product_promotions import ProductPromotion
        from infrastructure.database.models.categories import Category
        from infrastructure.database.models.specifications import Specification
        from infrastructure.database.models.reviews import Review
    
    orders: Mapped[List["Order"]] = relationship(
        "Order", back_populates="product", cascade="all, delete-orphan"
    )
    favorited_by: Mapped[List["Favorite"]] = relationship(
        "Favorite", back_populates="product", cascade="all, delete-orphan"
    )
    promotions: Mapped[List["ProductPromotion"]] = relationship(
        "ProductPromotion", back_populates="product", cascade="all, delete-orphan"
    )
    categories: Mapped[List["Category"]] = relationship(
        "Category", secondary="product_categories", back_populates="products"
    )
    specifications: Mapped[List["Specification"]] = relationship(
        "Specification", back_populates="product", cascade="all, delete-orphan"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of the object for debugging."""
        return f"<Product id={self.product_id} name='{self.name}' price={self.price}>"
    
    @validates('price')
    def validate_price(self, key, price) -> Decimal:
        """Validate product price."""
        if isinstance(price, (int, float)):
            price = Decimal(str(price))
        if price < 0:
            raise ValueError("Price cannot be negative")
        return price
    
    @validates('discount_price')
    def validate_discount_price(self, key, price) -> Optional[Decimal]:
        """Validate discount price."""
        if price is None:
            return None
        if isinstance(price, (int, float)):
            price = Decimal(str(price))
        if price < 0:
            raise ValueError("Discount price cannot be negative")
        if hasattr(self, 'price') and self.price is not None and price > self.price:
            raise ValueError("Discount price cannot be greater than regular price")
        return price
    
    @validates('name')
    def validate_name(self, key, name) -> str:
        """Validate product name."""
        if not name or len(name.strip()) == 0:
            raise ValueError("Product name cannot be empty")
        return name.strip()
    
    @validates('stock_quantity')
    def validate_stock_quantity(self, key, quantity) -> int:
        """Validate stock quantity and update is_in_stock flag."""
        quantity = int(quantity)
        if quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        
        # Update is_in_stock based on quantity
        if hasattr(self, 'is_in_stock'):
            self.is_in_stock = quantity > 0
            
        return quantity
    
    def formatted_info(self) -> str:
        """
        Format product information for user display.
        
        Returns:
            str: Formatted string with product information
        """
        price_str = f"{self.price}" if self.price is not None else "Not specified"
        discount_str = f" (Скидка: {self.discount_price})" if self.discount_price is not None else ""
        
        return (
            f"📦 Информация о товаре:\n\n"
            f"ID: {self.product_id}\n"
            f"Название: {self.name}\n"
            f"Описание: {self.description or 'Не указано'}\n"
            f"Тип: {self.type or 'Не указан'}\n"
            f"Материал: {self.material or 'Не указан'}\n"
            f"Цена: {price_str}{discount_str}\n"
            f"В наличии: {'Да' if self.is_in_stock else 'Нет'}\n"
        )
