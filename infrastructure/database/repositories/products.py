# infrastructure/database/repositories/products.py

from typing import List, Optional, Dict, Any, Union
from decimal import Decimal
import logging

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.exc import SQLAlchemyError
from infrastructure.database.models.products import Product, ProductType
from infrastructure.database.repositories.base import BaseRepo


class ProductsRepo(BaseRepo[Product]):
    """
    Repository for working with products in the database.
    
    Provides methods for creating, retrieving, updating, and deleting products.
    """
    model = Product
    
    async def create_product(self, product_data: Dict[str, Any]) -> Optional[Product]:
        """
        Creates a new product in the database.
        
        Args:
            product_data: Dictionary with product data (name, description, type, material, price, image_url)
            
        Returns:
            Created product object or None in case of error
        """
        # Convert numeric values to Decimal if needed
        if 'price' in product_data and not isinstance(product_data['price'], Decimal):
            try:
                product_data['price'] = Decimal(str(product_data['price']))
            except (ValueError, TypeError):
                self.logger.error(f"Invalid price value: {product_data['price']}")
                return None
                
        if 'discount_price' in product_data and product_data['discount_price'] is not None:
            if not isinstance(product_data['discount_price'], Decimal):
                try:
                    product_data['discount_price'] = Decimal(str(product_data['discount_price']))
                except (ValueError, TypeError):
                    self.logger.error(f"Invalid discount_price value: {product_data['discount_price']}")
                    product_data.pop('discount_price')
        
        # Set is_in_stock based on stock_quantity
        if 'stock_quantity' in product_data:
            product_data['is_in_stock'] = int(product_data['stock_quantity']) > 0
            
        return await self.create(product_data)

    async def get_all_products(self, in_stock_only: bool = False) -> List[Product]:
        """
        Gets all products from the database, sorted by ID.
        
        Args:
            in_stock_only: If True, only return products that are in stock
            
        Returns:
            List of all products
        """
        from tgbot.utils.error_handling import safe_db_operation
        
        @safe_db_operation("Failed to retrieve products")
        async def _get_products() -> List[Product]:
            conditions = []
            if in_stock_only:
                conditions.append(Product.is_in_stock == True)
                
            return await self.get_all(conditions=conditions if conditions else None, order_by="product_id")
        
        try:
            return await _get_products()
        except Exception as e:
            self.logger.error(f"Error retrieving all products: {e}")
            return []

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Gets a product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product object or None if product not found
        """
        return await self.get_by_id(product_id)

    async def update_product(self, product_id: int, update_data: Dict[str, Any]) -> Optional[Product]:
        """
        Updates a product by ID.
        
        Args:
            product_id: Product ID
            update_data: Dictionary with fields to update
            
        Returns:
            Updated product object or None in case of error
        """
        # Convert numeric values to Decimal if needed
        if 'price' in update_data and not isinstance(update_data['price'], Decimal):
            try:
                update_data['price'] = Decimal(str(update_data['price']))
            except (ValueError, TypeError):
                self.logger.error(f"Invalid price value: {update_data['price']}")
                return None
                
        if 'discount_price' in update_data and update_data['discount_price'] is not None:
            if not isinstance(update_data['discount_price'], Decimal):
                try:
                    update_data['discount_price'] = Decimal(str(update_data['discount_price']))
                except (ValueError, TypeError):
                    self.logger.error(f"Invalid discount_price value: {update_data['discount_price']}")
                    update_data.pop('discount_price')
        
        # Set is_in_stock based on stock_quantity
        if 'stock_quantity' in update_data:
            update_data['is_in_stock'] = int(update_data['stock_quantity']) > 0
            
        return await self.update(product_id, update_data)

    async def delete_product(self, product_id: int) -> bool:
        """
        Deletes a product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            True if product was successfully deleted, otherwise False
        """
        return await self.delete(product_id)
            
    async def update_product_field(self, product_id: int, field_name: str, field_value: Any) -> bool:
        """
        Updates a single field of a product by ID.
        
        Args:
            product_id: Product ID
            field_name: Field name to update
            field_value: New field value
            
        Returns:
            True if field was successfully updated, otherwise False
        """
        # Handle special cases for certain fields
        if field_name == 'price' and not isinstance(field_value, Decimal):
            try:
                field_value = Decimal(str(field_value))
            except (ValueError, TypeError):
                self.logger.error(f"Invalid price value: {field_value}")
                return False
                
        if field_name == 'discount_price' and field_value is not None:
            if not isinstance(field_value, Decimal):
                try:
                    field_value = Decimal(str(field_value))
                except (ValueError, TypeError):
                    self.logger.error(f"Invalid discount_price value: {field_value}")
                    return False
        
        # Update is_in_stock when stock_quantity changes
        if field_name == 'stock_quantity':
            try:
                quantity = int(field_value)
                # Also update is_in_stock field
                product = await self.get_by_id(product_id)
                if product:
                    is_in_stock = quantity > 0
                    if product.is_in_stock != is_in_stock:
                        await self.update_field(product_id, 'is_in_stock', is_in_stock)
            except (ValueError, TypeError):
                self.logger.error(f"Invalid stock_quantity value: {field_value}")
                return False
                
        return await self.update_field(product_id, field_name, field_value)
    
    async def search_products(self, query: str, limit: int = 10) -> List[Product]:
        """
        Search for products by name or description.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of found products
        """
        from tgbot.utils.error_handling import safe_db_operation
        
        @safe_db_operation(f"Failed to search products with query '{query}'")
        async def _search_products() -> List[Product]:
            # Validate input
            if not query or not isinstance(query, str):
                self.logger.warning(f"Invalid search query: {query}")
                return []
                
            # Search by name and description
            stmt = (
                select(Product)
                .where(
                    (Product.name.ilike(f"%{query}%")) | 
                    (Product.description.ilike(f"%{query}%"))
                )
                .order_by(Product.product_id)
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
            
        try:
            return await _search_products()
        except Exception as e:
            self.logger.error(f"Error searching products: {e}")
            return []
            
    async def filter_products(self, 
                            material: Optional[str] = None, 
                            product_type: Optional[str] = None, 
                            min_price: Optional[Union[float, Decimal]] = None, 
                            max_price: Optional[Union[float, Decimal]] = None, 
                            in_stock_only: bool = False,
                            limit: int = 20) -> List[Product]:
        """
        Filter products by material, type, and price range.
        
        Args:
            material: Product material
            product_type: Product type
            min_price: Minimum price
            max_price: Maximum price
            in_stock_only: If True, only return products that are in stock
            limit: Maximum number of results
            
        Returns:
            List of filtered products
        """
        try:
            # Start building query
            conditions = []
            
            # Add filter conditions
            if material:
                conditions.append(Product.material.ilike(f"%{material}%"))
            
            if product_type:
                conditions.append(Product.type.ilike(f"%{product_type}%"))
            
            if min_price is not None:
                if not isinstance(min_price, Decimal):
                    min_price = Decimal(str(min_price))
                conditions.append(Product.price >= min_price)
            
            if max_price is not None:
                if not isinstance(max_price, Decimal):
                    max_price = Decimal(str(max_price))
                conditions.append(Product.price <= max_price)
                
            if in_stock_only:
                conditions.append(Product.is_in_stock == True)
            
            # Build final query
            stmt = select(Product)
            
            # Apply conditions if any
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            # Add sorting and limit
            stmt = stmt.order_by(Product.product_id).limit(limit)
            
            # Execute query
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self.logger.error(f"Error filtering products: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error filtering products: {e}")
            return []
    
    async def get_products_with_discount(self, limit: int = 20) -> List[Product]:
        """
        Get products that have a discount price.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of products with discount
        """
        try:
            stmt = (
                select(Product)
                .where(Product.discount_price.is_not(None))
                .order_by(Product.product_id)
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            self.logger.error(f"Error retrieving products with discount: {e}")
            return []
            
    async def get_available_materials(self) -> List[str]:
        """
        Get a list of all unique product materials.
        
        Returns:
            List of unique materials
        """
        try:
            stmt = select(Product.material).distinct().where(Product.material.is_not(None))
            result = await self.session.execute(stmt)
            return [material for material, in result if material]
        except Exception as e:
            self.logger.error(f"Error retrieving available materials: {e}")
            return []
            
    async def get_available_types(self) -> List[str]:
        """
        Get a list of all unique product types.
        
        Returns:
            List of unique product types
        """
        try:
            stmt = select(Product.type).distinct().where(Product.type.is_not(None))
            result = await self.session.execute(stmt)
            return [product_type for product_type, in result if product_type]
        except Exception as e:
            self.logger.error(f"Error retrieving available product types: {e}")
            return []