from typing import List, Optional, Dict, Any
import logging

from sqlalchemy import select, and_, func
from infrastructure.database.models.reviews import Review
from infrastructure.database.repositories.base import BaseRepo


class ReviewsRepo(BaseRepo[Review]):
    """
    Репозиторий для работы с отзывами о товарах.
    
    Предоставляет методы для создания, получения, обновления и удаления отзывов.
    """
    model = Review
    
    async def create_review(self, review_data: Dict[str, Any]) -> Optional[Review]:
        """
        Создает новый отзыв о товаре в базе данных.
        
        Args:
            review_data: Словарь с данными отзыва (user_id, product_id, rating, text)
            
        Returns:
            Созданный объект отзыва или None в случае ошибки
        """
        try:
            return await self.create(review_data)
        except Exception as e:
            logging.error(f"Ошибка при создании отзыва: {e}")
            return None
    
    async def get_product_reviews(self, product_id: int) -> List[Review]:
        """
        Получает все отзывы для конкретного товара.
        
        Args:
            product_id: ID товара
            
        Returns:
            Список отзывов для товара
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.product_id == product_id)
                .order_by(self.model.created_at.desc())
            )
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении отзывов для товара {product_id}: {e}")
            return []
    
    async def get_user_reviews(self, user_id: int) -> List[Review]:
        """
        Получает все отзывы, оставленные конкретным пользователем.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список отзывов пользователя
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.user_id == user_id)
                .order_by(self.model.created_at.desc())
            )
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении отзывов пользователя {user_id}: {e}")
            return []
    
    async def get_review_by_id(self, review_id: int) -> Optional[Review]:
        """
        Получает отзыв по ID.
        
        Args:
            review_id: ID отзыва
            
        Returns:
            Объект отзыва или None, если отзыв не найден
        """
        return await self.get_by_id(review_id)
    
    async def update_review(self, review_id: int, update_data: Dict[str, Any]) -> Optional[Review]:
        """
        Обновляет отзыв по ID.
        
        Args:
            review_id: ID отзыва
            update_data: Словарь с обновляемыми полями
            
        Returns:
            Обновленный объект отзыва или None в случае ошибки
        """
        return await self.update(review_id, update_data)
    
    async def delete_review(self, review_id: int) -> bool:
        """
        Удаляет отзыв по ID.
        
        Args:
            review_id: ID отзыва
            
        Returns:
            True, если отзыв успешно удален, иначе False
        """
        return await self.delete(review_id)
    
    async def get_avg_product_rating(self, product_id: int) -> Optional[float]:
        """
        Получает среднюю оценку товара на основе всех отзывов.
        
        Args:
            product_id: ID товара
            
        Returns:
            Средняя оценка товара или None, если отзывов нет
        """
        try:
            stmt = (
                select(func.avg(self.model.rating))
                .where(self.model.product_id == product_id)
            )
            result = await self.session.execute(stmt)
            return result.scalar()
        except Exception as e:
            logging.error(f"Ошибка при получении средней оценки товара {product_id}: {e}")
            return None
    
    async def get_review_count(self, product_id: int) -> int:
        """
        Получает количество отзывов для товара.
        
        Args:
            product_id: ID товара
            
        Returns:
            Количество отзывов
        """
        try:
            stmt = (
                select(func.count())
                .where(self.model.product_id == product_id)
            )
            result = await self.session.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            logging.error(f"Ошибка при получении количества отзывов для товара {product_id}: {e}")
            return 0
    
    async def check_user_review_exists(self, user_id: int, product_id: int) -> bool:
        """
        Проверяет, оставлял ли пользователь отзыв о товаре.
        
        Args:
            user_id: ID пользователя
            product_id: ID товара
            
        Returns:
            True, если отзыв существует, иначе False
        """
        try:
            stmt = (
                select(self.model)
                .where(
                    and_(
                        self.model.user_id == user_id,
                        self.model.product_id == product_id
                    )
                )
            )
            result = await self.session.execute(stmt)
            return result.scalar() is not None
        except Exception as e:
            logging.error(f"Ошибка при проверке наличия отзыва пользователя {user_id} для товара {product_id}: {e}")
            return False