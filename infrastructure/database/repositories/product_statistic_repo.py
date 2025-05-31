from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, between, desc
from infrastructure.database.models.statistics import ProductStatistic
from infrastructure.database.repositories.base import BaseRepo
import logging

class ProductStatisticRepo(BaseRepo):
    """
    Репозиторий для работы со статистикой товаров.
    """
    model = ProductStatistic
    
    async def increment_statistic(self, product_id: int, stat_type: str) -> bool:
        """
        Увеличивает счетчик статистики товара за текущий день.
        
        Args:
            product_id: ID товара
            stat_type: Тип статистики (view, favorite, purchase)
            
        Returns:
            True, если статистика успешно обновлена, иначе False
        """
        try:
            # Получаем текущую дату (начало дня)
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Проверяем, существует ли статистика за сегодня
            stmt = select(ProductStatistic).where(
                and_(
                    ProductStatistic.product_id == product_id,
                    ProductStatistic.stat_type == stat_type,
                    func.date(ProductStatistic.date) == today.date()
                )
            )
            
            result = await self.session.execute(stmt)
            stat = result.scalars().first()
            
            if stat:
                # Обновляем существующую статистику
                stat.count += 1
            else:
                # Создаем новую запись статистики
                stat = ProductStatistic(
                    product_id=product_id,
                    stat_type=stat_type,
                    count=1,
                    date=today
                )
                self.session.add(stat)
                
            await self.session.commit()
            return True
        except Exception as e:
            logging.error(f"Ошибка при обновлении статистики для товара {product_id}, тип {stat_type}: {e}")
            await self.session.rollback()
            return False
            
    async def get_product_stats_by_period(self, product_id: int, stat_type: str, 
                                         days: int = 30) -> List[ProductStatistic]:
        """
        Получает статистику товара за указанный период.
        
        Args:
            product_id: ID товара
            stat_type: Тип статистики
            days: Количество дней для анализа
            
        Returns:
            Список записей статистики
        """
        try:
            # Вычисляем начальную дату
            start_date = datetime.now() - timedelta(days=days)
            
            stmt = (
                select(ProductStatistic)
                .where(
                    and_(
                        ProductStatistic.product_id == product_id,
                        ProductStatistic.stat_type == stat_type,
                        ProductStatistic.date >= start_date
                    )
                )
                .order_by(ProductStatistic.date)
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении статистики для товара {product_id}, тип {stat_type}: {e}")
            return []
            
    async def get_top_products_by_stat(self, stat_type: str, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получает топ товаров по определенному типу статистики.
        
        Args:
            stat_type: Тип статистики
            days: Количество дней для анализа
            limit: Максимальное количество результатов
            
        Returns:
            Список словарей с информацией о товарах и их статистике
        """
        try:
            # Вычисляем начальную дату
            start_date = datetime.now() - timedelta(days=days)
            
            # Получаем сумму счетчиков, сгруппированную по product_id
            stmt = (
                select(
                    ProductStatistic.product_id,
                    func.sum(ProductStatistic.count).label("total")
                )
                .where(
                    and_(
                        ProductStatistic.stat_type == stat_type,
                        ProductStatistic.date >= start_date
                    )
                )
                .group_by(ProductStatistic.product_id)
                .order_by(desc("total"))
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            
            # Преобразуем в список словарей
            return [{"product_id": row[0], "total": row[1]} for row in result]
        except Exception as e:
            logging.error(f"Ошибка при получении топ товаров по {stat_type}: {e}")
            return []
            
    async def get_stats_summary_by_period(self, days: int = 30) -> Dict[str, Dict[str, int]]:
        """
        Получает сводную статистику по всем типам за указанный период.
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Словарь с общей статистикой по типам
        """
        try:
            # Вычисляем начальную дату
            start_date = datetime.now() - timedelta(days=days)
            
            # Получаем суммы по каждому типу статистики
            stmt = (
                select(
                    ProductStatistic.stat_type,
                    func.sum(ProductStatistic.count).label("total")
                )
                .where(ProductStatistic.date >= start_date)
                .group_by(ProductStatistic.stat_type)
            )
            
            result = await self.session.execute(stmt)
            
            # Формируем итоговый словарь
            summary = {
                "view": 0,
                "favorite": 0,
                "purchase": 0
            }
            
            for stat_type, total in result:
                summary[stat_type] = total
                
            return summary
        except Exception as e:
            logging.error(f"Ошибка при получении сводной статистики: {e}")
            return {"view": 0, "favorite": 0, "purchase": 0}