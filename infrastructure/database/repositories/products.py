# infrastructure/database/repositories/products.py

from typing import List, Optional

from sqlalchemy import select, update, delete
from infrastructure.database.models.products import Product
from infrastructure.database.repositories.base import BaseRepo


class ProductsRepo(BaseRepo):  # Переименовано с ProductRepo на ProductsRepo
    async def create_product(self, product_data: dict) -> Product:
        """
        Creates a new product in the database.
        """
        product = Product(**product_data)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def get_all_products(self) -> List[Product]:
        """
        Retrieves all products from the database, sorted by product_id.
        """
        stmt = select(Product).order_by(Product.product_id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Retrieves a product by ID.
        """
        stmt = select(Product).where(Product.product_id == product_id)
        result = await self.session.scalars(stmt)
        return result.first()

    async def update_product(self, product_id: int, update_data: dict) -> Optional[Product]:
        """
        Updates a product by ID.
        """
        stmt = (
            update(Product)
            .where(Product.product_id == product_id)
            .values(**update_data)
            .returning(Product)
        )
        result = await self.session.scalars(stmt)
        await self.session.commit()
        return result.first()

    async def delete_product(self, product_id: int) -> bool:
        """
        Deletes a product by ID.
        Returns True if the product was successfully deleted, False otherwise.
        """
        try:
            stmt = delete(Product).where(Product.product_id == product_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.session.rollback()
            return False
            
    async def update_product_field(self, product_id: int, field_name: str, field_value) -> bool:
        """
        Updates a single field of a product by ID.
        Returns True if the product was successfully updated, False otherwise.
        """
        try:
            update_data = {field_name: field_value}
            stmt = (
                update(Product)
                .where(Product.product_id == product_id)
                .values(**update_data)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.session.rollback()
            return False
