from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, update, delete, and_, or_, func
from infrastructure.database.models.promotions import Promotion
from infrastructure.database.models.product_promotions import ProductPromotion
from infrastructure.database.repositories.base import BaseRepo
import logging

class PromotionRepo(BaseRepo):
    """
    Репозиторий для работы с акциями и скидками.
    """
    model = Promotion
    
    async def create_promotion(self, promotion_data: Dict[str, Any]) -> Optional[Promotion]:
        """
        Создает новую акцию.
        
        Args:
            promotion_data: Словарь с данными акции
            
        Returns:
            Созданный объект акции или None в случае ошибки
        """
        try:
            promotion = await self.create(promotion_data)
            logging.info(f"Создана новая акция: {promotion.name}")
            return promotion
        except Exception as e:
            logging.error(f"Ошибка при создании акции: {e}")
            await self.session.rollback()
            return None
            
    async def get_active_promotions(self) -> List[Promotion]:
        """
        Получает все активные акции, действующие на текущий момент.
        
        Returns:
            Список активных акций
        """
        try:
            now = datetime.now()
            stmt = select(Promotion).where(
                and_(
                    Promotion.is_active == True,
                    Promotion.start_date <= now,
                    or_(
                        Promotion.end_date.is_(None),
                        Promotion.end_date >= now
                    )
                )
            )
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении активных акций: {e}")
            return []
            
    async def apply_promotion_to_product(self, promo_id: int, product_id: int) -> bool:
        """
        Применяет акцию к товару.
        
        Args:
            promo_id: ID акции
            product_id: ID товара
            
        Returns:
            True, если акция успешно применена к товару, иначе False
        """
        try:
            # Проверяем, существует ли уже связь
            stmt = select(ProductPromotion).where(
                and_(
                    ProductPromotion.promo_id == promo_id,
                    ProductPromotion.product_id == product_id
                )
            )
            result = await self.session.execute(stmt)
            if result.scalars().first():
                logging.info(f"Акция {promo_id} уже применена к товару {product_id}")
                return True
                
            # Создаем новую связь
            link = ProductPromotion(promo_id=promo_id, product_id=product_id)
            self.session.add(link)
            await self.session.commit()
            logging.info(f"Акция {promo_id} применена к товару {product_id}")
            return True
        except Exception as e:
            logging.error(f"Ошибка при применении акции {promo_id} к товару {product_id}: {e}")
            await self.session.rollback()
            return False
            
    async def remove_promotion_from_product(self, promo_id: int, product_id: int) -> bool:
        """
        Удаляет акцию с товара.
        
        Args:
            promo_id: ID акции
            product_id: ID товара
            
        Returns:
            True, если акция успешно удалена с товара, иначе False
        """
        try:
            stmt = delete(ProductPromotion).where(
                and_(
                    ProductPromotion.promo_id == promo_id,
                    ProductPromotion.product_id == product_id
                )
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logging.info(f"Акция {promo_id} удалена с товара {product_id}")
            return True
        except Exception as e:
            logging.error(f"Ошибка при удалении акции {promo_id} с товара {product_id}: {e}")
            await self.session.rollback()
            return False
            
    async def get_promotions_for_product(self, product_id: int) -> List[Promotion]:
        """
        Получает все активные акции для товара.
        
        Args:
            product_id: ID товара
            
        Returns:
            Список активных акций для товара
        """
        try:
            now = datetime.now()
            stmt = select(Promotion).join(
                ProductPromotion,
                and_(
                    ProductPromotion.promo_id == Promotion.promo_id,
                    ProductPromotion.product_id == product_id
                )
            ).where(
                and_(
                    Promotion.is_active == True,
                    Promotion.start_date <= now,
                    or_(
                        Promotion.end_date.is_(None),
                        Promotion.end_date >= now
                    )
                )
            )
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении акций для товара {product_id}: {e}")
            return []
            
    async def update_promotion(self, promo_id: int, update_data: Dict[str, Any]) -> Optional[Promotion]:
        """
        Обновляет акцию.
        
        Args:
            promo_id: ID акции
            update_data: Словарь с обновляемыми полями
            
        Returns:
            Обновленный объект акции или None в случае ошибки
        """
        return await self.update(promo_id, update_data)
        
    async def deactivate_promotion(self, promo_id: int) -> bool:
        """
        Деактивирует акцию.
        
        Args:
            promo_id: ID акции
            
        Returns:
            True, если акция успешно деактивирована, иначе False
        """
        try:
            return await self.update_field(promo_id, "is_active", False)
        except Exception as e:
            logging.error(f"Ошибка при деактивации акции {promo_id}: {e}")
            return False