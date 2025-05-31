from typing import List, Optional, Dict, Any
import logging

from sqlalchemy import select, and_
from infrastructure.database.models.specifications import Specification
from infrastructure.database.repositories.base import BaseRepo


class SpecificationsRepo(BaseRepo[Specification]):
    """
    Репозиторий для работы с характеристиками товаров.
    
    Предоставляет методы для создания, получения, обновления и удаления характеристик товаров.
    """
    model = Specification
    
    async def create_specification(self, spec_data: Dict[str, Any]) -> Optional[Specification]:
        """
        Создает новую характеристику товара в базе данных.
        
        Args:
            spec_data: Словарь с данными характеристики (product_id, name, value)
            
        Returns:
            Созданный объект характеристики или None в случае ошибки
        """
        try:
            return await self.create(spec_data)
        except Exception as e:
            logging.error(f"Ошибка при создании характеристики: {e}")
            return None
    
    async def get_specification_by_id(self, spec_id: int) -> Optional[Specification]:
        """
        Получает характеристику по ID.
        
        Args:
            spec_id: ID характеристики
            
        Returns:
            Объект характеристики или None, если характеристика не найдена
        """
        return await self.get_by_id(spec_id)
    
    async def get_product_specifications(self, product_id: int) -> List[Specification]:
        """
        Получает все характеристики для конкретного товара.
        
        Args:
            product_id: ID товара
            
        Returns:
            Список характеристик товара
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.product_id == product_id)
                .order_by(self.model.name)
            )
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении характеристик для товара {product_id}: {e}")
            return []
    
    async def get_specification_by_name(self, product_id: int, name: str) -> Optional[Specification]:
        """
        Получает характеристику товара по названию характеристики.
        
        Args:
            product_id: ID товара
            name: Название характеристики
            
        Returns:
            Объект характеристики или None, если характеристика не найдена
        """
        try:
            stmt = (
                select(self.model)
                .where(
                    and_(
                        self.model.product_id == product_id,
                        self.model.name == name
                    )
                )
            )
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            logging.error(f"Ошибка при получении характеристики '{name}' для товара {product_id}: {e}")
            return None
    
    async def update_specification(self, spec_id: int, update_data: Dict[str, Any]) -> Optional[Specification]:
        """
        Обновляет характеристику по ID.
        
        Args:
            spec_id: ID характеристики
            update_data: Словарь с обновляемыми полями
            
        Returns:
            Обновленный объект характеристики или None в случае ошибки
        """
        return await self.update(spec_id, update_data)
    
    async def delete_specification(self, spec_id: int) -> bool:
        """
        Удаляет характеристику по ID.
        
        Args:
            spec_id: ID характеристики
            
        Returns:
            True, если характеристика успешно удалена, иначе False
        """
        return await self.delete(spec_id)
    
    async def update_or_create_specification(self, product_id: int, name: str, value: str) -> Optional[Specification]:
        """
        Обновляет существующую характеристику или создает новую, если она не существует.
        
        Args:
            product_id: ID товара
            name: Название характеристики
            value: Значение характеристики
            
        Returns:
            Обновленный или созданный объект характеристики или None в случае ошибки
        """
        try:
            # Проверяем, существует ли уже характеристика с таким названием для этого товара
            existing_spec = await self.get_specification_by_name(product_id, name)
            
            if existing_spec:
                # Если существует, обновляем её
                return await self.update(existing_spec.spec_id, {"value": value})
            else:
                # Если не существует, создаем новую
                return await self.create({
                    "product_id": product_id,
                    "name": name,
                    "value": value
                })
        except Exception as e:
            logging.error(f"Ошибка при обновлении/создании характеристики '{name}' для товара {product_id}: {e}")
            return None
    
    async def delete_product_specifications(self, product_id: int) -> bool:
        """
        Удаляет все характеристики товара.
        
        Args:
            product_id: ID товара
            
        Returns:
            True, если операция выполнена успешно, иначе False
        """
        try:
            # Получаем все характеристики товара
            specs = await self.get_product_specifications(product_id)
            
            # Удаляем каждую характеристику
            for spec in specs:
                await self.delete(spec.spec_id)
                
            return True
        except Exception as e:
            logging.error(f"Ошибка при удалении всех характеристик товара {product_id}: {e}")
            return False
    
    async def bulk_create_specifications(self, specs_data: List[Dict[str, Any]]) -> List[Specification]:
        """
        Массовое создание характеристик товара.
        
        Args:
            specs_data: Список словарей с данными характеристик
            
        Returns:
            Список созданных характеристик
        """
        try:
            result = []
            
            for spec_data in specs_data:
                spec = await self.create(spec_data)
                if spec:
                    result.append(spec)
                    
            return result
        except Exception as e:
            logging.error(f"Ошибка при массовом создании характеристик: {e}")
            return []