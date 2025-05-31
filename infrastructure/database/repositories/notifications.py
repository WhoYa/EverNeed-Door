from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, and_
from infrastructure.database.models.notifications import Notification
from infrastructure.database.repositories.base import BaseRepo
import logging


class NotificationsRepo(BaseRepo[Notification]):
    """
    Репозиторий для работы с уведомлениями.
    """
    model = Notification
    
    async def create_notification(self, user_id: int, notification_data: dict) -> Optional[Notification]:
        """
        Создает новое уведомление для пользователя.
        
        Args:
            user_id: ID пользователя
            notification_data: Данные уведомления (type, message)
            
        Returns:
            Созданное уведомление или None в случае ошибки
        """
        try:
            data = {
                "user_id": user_id,
                **notification_data
            }
            notification = await self.create(data)
            return notification
        except Exception as e:
            logging.error(f"Ошибка при создании уведомления для пользователя {user_id}: {e}")
            return None

    async def get_notifications_by_user(self, user_id: int, only_unread: bool = False) -> List[Notification]:
        """
        Получает уведомления пользователя.
        
        Args:
            user_id: ID пользователя
            only_unread: Флаг для получения только непрочитанных уведомлений
            
        Returns:
            Список уведомлений пользователя
        """
        try:
            conditions = [Notification.user_id == user_id]
            
            if only_unread:
                conditions.append(Notification.is_read == False)
                
            return await self.get_all(conditions=conditions, order_by="-created_at")
        except Exception as e:
            logging.error(f"Ошибка при получении уведомлений для пользователя {user_id}: {e}")
            return []

    async def mark_as_read(self, notification_id: int) -> bool:
        """
        Отмечает уведомление как прочитанное.
        
        Args:
            notification_id: ID уведомления
            
        Returns:
            True, если уведомление успешно отмечено как прочитанное, иначе False
        """
        try:
            return await self.update_field(notification_id, "is_read", True)
        except Exception as e:
            logging.error(f"Ошибка при отметке уведомления {notification_id} как прочитанного: {e}")
            return False
            
    async def mark_all_as_read(self, user_id: int) -> bool:
        """
        Отмечает все уведомления пользователя как прочитанные.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True, если все уведомления успешно отмечены как прочитанные, иначе False
        """
        try:
            stmt = (
                update(Notification)
                .where(
                    and_(
                        Notification.user_id == user_id,
                        Notification.is_read == False
                    )
                )
                .values(is_read=True)
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            return True
        except Exception as e:
            logging.error(f"Ошибка при отметке всех уведомлений пользователя {user_id} как прочитанных: {e}")
            await self.session.rollback()
            return False
            
    async def delete_notification(self, notification_id: int) -> bool:
        """
        Удаляет уведомление.
        
        Args:
            notification_id: ID уведомления
            
        Returns:
            True, если уведомление успешно удалено, иначе False
        """
        return await self.delete(notification_id)
        
    async def create_price_change_notification(self, user_id: int, product_id: int, old_price: float, new_price: float) -> Optional[Notification]:
        """
        Создает уведомление об изменении цены товара в избранном.
        
        Args:
            user_id: ID пользователя
            product_id: ID товара
            old_price: Старая цена
            new_price: Новая цена
            
        Returns:
            Созданное уведомление или None в случае ошибки
        """
        try:
            change_type = "снижение" if new_price < old_price else "повышение"
            message = f"Изменение цены товара в вашем избранном (ID: {product_id}). {change_type} с {old_price}₽ до {new_price}₽."
            
            notification_data = {
                "type": "price_change",
                "message": message
            }
            
            return await self.create_notification(user_id, notification_data)
        except Exception as e:
            logging.error(f"Ошибка при создании уведомления об изменении цены для пользователя {user_id}: {e}")
            return None
            
    async def create_new_product_notification(self, user_ids: List[int], product_id: int, product_name: str) -> bool:
        """
        Создает уведомления о новом товаре для нескольких пользователей.
        
        Args:
            user_ids: Список ID пользователей
            product_id: ID нового товара
            product_name: Название нового товара
            
        Returns:
            True, если все уведомления успешно созданы, иначе False
        """
        try:
            message = f"Новый товар в магазине: {product_name} (ID: {product_id})"
            
            notification_data = {
                "type": "new_product",
                "message": message
            }
            
            # Создаем уведомления для всех пользователей
            for user_id in user_ids:
                await self.create_notification(user_id, notification_data)
            
            return True
        except Exception as e:
            logging.error(f"Ошибка при создании уведомлений о новом товаре: {e}")
            return False
            
    async def create_discount_notification(self, user_ids: List[int], product_id: int, product_name: str, discount_percent: float) -> bool:
        """
        Создает уведомления о скидке на товар для нескольких пользователей.
        
        Args:
            user_ids: Список ID пользователей
            product_id: ID товара со скидкой
            product_name: Название товара
            discount_percent: Процент скидки
            
        Returns:
            True, если все уведомления успешно созданы, иначе False
        """
        try:
            message = f"Скидка {discount_percent}% на товар: {product_name} (ID: {product_id})"
            
            notification_data = {
                "type": "discount",
                "message": message
            }
            
            # Создаем уведомления для всех пользователей
            for user_id in user_ids:
                await self.create_notification(user_id, notification_data)
            
            return True
        except Exception as e:
            logging.error(f"Ошибка при создании уведомлений о скидке: {e}")
            return False