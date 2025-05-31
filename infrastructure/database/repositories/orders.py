from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from infrastructure.database.models.orders import Order
from infrastructure.database.repositories.base import BaseRepo


class OrdersRepo(BaseRepo[Order]):
    model = Order
    async def create_order(self, order_data: dict) -> Optional[Order]:
        """
        Creates a new order in the database.

        :param order_data: Dictionary containing order details (user_id, product_id, quantity, etc.)
        :return: Created Order object or None if error occurs.
        """
        try:
            order = Order(**order_data)
            self.session.add(order)
            await self.session.commit()
            await self.session.refresh(order)
            return order
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating order: {e}")
            await self.session.rollback()
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error creating order: {e}")
            await self.session.rollback()
            return None

    async def get_all_orders(self) -> List[Order]:
        """
        Retrieves all orders from the database.

        :return: List of all Order objects.
        """
        try:
            stmt = select(Order)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving all orders: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving all orders: {e}")
            return []

    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """
        Retrieves an order by its ID.

        :param order_id: ID of the order to retrieve.
        :return: Order object or None if not found.
        """
        try:
            stmt = select(Order).where(Order.order_id == order_id)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving order by ID {order_id}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving order by ID {order_id}: {e}")
            return None

    async def get_orders_by_user(self, user_id: int) -> List[Order]:
        """
        Retrieves all orders placed by a specific user.

        :param user_id: ID of the user.
        :return: List of Order objects for the user.
        """
        try:
            stmt = select(Order).where(Order.user_id == user_id)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving orders for user {user_id}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving orders for user {user_id}: {e}")
            return []

    async def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        """
        Updates the status of an order by its ID.

        :param order_id: ID of the order to update.
        :param status: New status for the order.
        :return: Updated Order object or None if not found.
        """
        try:
            stmt = (
                update(Order)
                .where(Order.order_id == order_id)
                .values(status=status)
                .returning(Order)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalars().first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error updating order status for order ID {order_id}: {e}")
            await self.session.rollback()
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error updating order status for order ID {order_id}: {e}")
            await self.session.rollback()
            return None

    async def delete_order(self, order_id: int) -> bool:
        """
        Deletes an order by its ID.

        :param order_id: ID of the order to delete.
        :return: True if deletion was successful, otherwise False
        """
        try:
            stmt = delete(Order).where(Order.order_id == order_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.logger.error(f"Error deleting order with ID {order_id}: {e}")
            await self.session.rollback()
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error deleting order with ID {order_id}: {e}")
            await self.session.rollback()
            return False
