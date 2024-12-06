from typing import List, Optional

from sqlalchemy import select, update, delete
from infrastructure.database.models.products import Product
from infrastructure.database.repositories.base import BaseRepo


class ProductRepo(BaseRepo):
    async def create_product(self, product_data: dict) -> Product:
        """
        Creates a new product in the database.
        """
        product = Product(**product_data)
        self.session.add(product)
        await self.session.commit()
        return product

    async def get_all_products(self) -> List[Product]:
        """
        Retrieves all products from the database.
        """
        stmt = select(Product)
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

    async def delete_product(self, product_id: int):
        """
        Deletes a product by ID.
        """
        stmt = delete(Product).where(Product.product_id == product_id)
        await self.session.execute(stmt)
        await self.session.commit()