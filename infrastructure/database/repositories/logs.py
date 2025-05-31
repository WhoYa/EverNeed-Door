from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, between, desc
from infrastructure.database.models.logs import Log
from infrastructure.database.repositories.base import BaseRepo
import logging


class LogsRepo(BaseRepo[Log]):
    """
    Репозиторий для работы с логами действий пользователей.
    """
    model = Log
    
    async def create_log(self, user_id: int, action: str, details: Optional[str] = None) -> Optional[Log]:
        """
        Создает запись лога о действии пользователя.
        
        Args:
            user_id: ID пользователя
            action: Тип действия (просмотр товара, фильтрация, добавление в избранное и т.д.)
            details: Дополнительная информация о действии
            
        Returns:
            Созданная запись лога или None в случае ошибки
        """
        try:
            data = {
                "user_id": user_id,
                "action": action,
                "details": details
            }
            
            log_entry = await self.create(data)
            return log_entry
        except Exception as e:
            logging.error(f"Ошибка при создании записи лога для пользователя {user_id}: {e}")
            return None
            
    async def create_with_timestamp(self, log_data: Dict[str, Any]) -> Optional[Log]:
        """
        Создает запись лога с указанным timestamp (для тестовых данных).
        
        Args:
            log_data: Словарь с данными лога, включая timestamp
            
        Returns:
            Созданная запись лога или None в случае ошибки
        """
        try:
            log_entry = await self.create(log_data)
            return log_entry
        except Exception as e:
            logging.error(f"Ошибка при создании лога с timestamp: {e}")
            return None

    async def get_logs_by_user(self, user_id: int, limit: int = 100) -> List[Log]:
        """
        Получает историю действий пользователя.
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество записей
            
        Returns:
            Список записей логов пользователя
        """
        try:
            stmt = (
                select(Log)
                .where(Log.user_id == user_id)
                .order_by(desc(Log.timestamp))
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении логов для пользователя {user_id}: {e}")
            return []
            
    async def get_logs_by_action(self, action: str, limit: int = 100) -> List[Log]:
        """
        Получает логи по конкретному типу действия.
        
        Args:
            action: Тип действия
            limit: Максимальное количество записей
            
        Returns:
            Список записей логов по указанному действию
        """
        try:
            stmt = (
                select(Log)
                .where(Log.action == action)
                .order_by(desc(Log.timestamp))
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении логов для действия {action}: {e}")
            return []
            
    async def get_logs_by_date_range(self, start_date: datetime, end_date: datetime, limit: int = 100) -> List[Log]:
        """
        Получает логи за указанный временной период.
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            limit: Максимальное количество записей
            
        Returns:
            Список записей логов за указанный период
        """
        try:
            stmt = (
                select(Log)
                .where(between(Log.timestamp, start_date, end_date))
                .order_by(desc(Log.timestamp))
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении логов за период {start_date} - {end_date}: {e}")
            return []
            
    async def get_action_count_by_user(self, user_id: int) -> Dict[str, int]:
        """
        Подсчитывает количество действий каждого типа для пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь {тип_действия: количество}
        """
        try:
            stmt = (
                select(Log.action, func.count(Log.log_id))
                .where(Log.user_id == user_id)
                .group_by(Log.action)
            )
            
            result = await self.session.execute(stmt)
            
            return {action: count for action, count in result}
        except Exception as e:
            logging.error(f"Ошибка при подсчете действий для пользователя {user_id}: {e}")
            return {}
            
    async def get_popular_products(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получает список самых популярных товаров на основе просмотров за указанный период.
        
        Args:
            days: Количество дней для анализа
            limit: Максимальное количество результатов
            
        Returns:
            Список словарей с информацией о популярных товарах
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Получаем ID товаров из деталей логов (предполагается формат "Просмотр товара с ID X")
            # Это простая версия, в реальности может потребоваться более сложная логика извлечения ID товаров
            stmt = (
                select(
                    Log.details,
                    func.count(Log.log_id).label("views")
                )
                .where(
                    and_(
                        Log.action == "view_product",
                        Log.timestamp >= start_date
                    )
                )
                .group_by(Log.details)
                .order_by(desc("views"))
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            
            # Преобразуем результаты в удобный формат
            popular_products = []
            for details, views in result:
                # Извлекаем ID товара из деталей (пример: "Просмотр товара с ID 123")
                try:
                    product_id_str = details.split("ID")[-1].strip()
                    product_id = int(product_id_str)
                    
                    popular_products.append({
                        "product_id": product_id,
                        "views": views
                    })
                except (IndexError, ValueError):
                    # Пропускаем записи с неправильным форматом деталей
                    continue
                    
            return popular_products
        except Exception as e:
            logging.error(f"Ошибка при получении популярных товаров: {e}")
            return []