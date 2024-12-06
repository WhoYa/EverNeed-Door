from typing import List, Optional
from sqlalchemy import select, update, delete
from infrastructure.database.models.orders import Order
from infrastructure.database.repositories.base import BaseRepo


class OrderRepo(BaseRepo):
    async def create_order(self, order_data: dict) -> Order:
        """
        Creates a new order in the database.

        :param order_data: Dictionary containing order details (user_id, product_id, quantity, etc.)
        :return: Created Order object.
        """
        order = Order(**order_data)
        self.session.add(order)
        await self.session.commit()
        return order

    async def get_all_orders(self) -> List[Order]:
        """
        Retrieves all orders from the database.

        :return: List of all Order objects.
        """
        stmt = select(Order)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """
        Retrieves an order by its ID.

        :param order_id: ID of the order to retrieve.
        :return: Order object or None if not found.
        """
        stmt = select(Order).where(Order.order_id == order_id)
        result = await self.session.scalars(stmt)
        return result.first()

    async def get_orders_by_user(self, user_id: int) -> List[Order]:
        """
        Retrieves all orders placed by a specific user.

        :param user_id: ID of the user.
        :return: List of Order objects for the user.
        """
        stmt = select(Order).where(Order.user_id == user_id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        """
        Updates the status of an order by its ID.

        :param order_id: ID of the order to update.
        :param status: New status for the order.
        :return: Updated Order object or None if not found.
        """
        stmt = (
            update(Order)
            .where(Order.order_id == order_id)
            .values(status=status)
            .returning(Order)
        )
        result = await self.session.scalars(stmt)
        await self.session.commit()
        return result.first()

    async def delete_order(self, order_id: int):
        """
        Deletes an order by its ID.

        :param order_id: ID of the order to delete.
        """
        stmt = delete(Order).where(Order.order_id == order_id)
        await self.session.execute(stmt)
        await self.session.commit()
