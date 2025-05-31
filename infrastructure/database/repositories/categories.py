from typing import List, Optional, Dict, Any
import logging

from sqlalchemy import select, func
from infrastructure.database.models.categories import Category
from infrastructure.database.repositories.base import BaseRepo


class CategoriesRepo(BaseRepo[Category]):
    """
    Репозиторий для работы с категориями товаров.
    
    Предоставляет методы для создания, получения, обновления и удаления категорий товаров.
    """
    model = Category
    
    async def create_category(self, category_data: Dict[str, Any]) -> Optional[Category]:
        """
        Создает новую категорию товаров в базе данных.
        
        Args:
            category_data: Словарь с данными категории (name, description, parent_id)
            
        Returns:
            Созданный объект категории или None в случае ошибки
        """
        try:
            return await self.create(category_data)
        except Exception as e:
            logging.error(f"Ошибка при создании категории: {e}")
            return None
    
    async def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """
        Получает категорию по ID.
        
        Args:
            category_id: ID категории
            
        Returns:
            Объект категории или None, если категория не найдена
        """
        return await self.get_by_id(category_id)
    
    async def get_category_by_name(self, name: str) -> Optional[Category]:
        """
        Получает категорию по названию.
        
        Args:
            name: Название категории
            
        Returns:
            Объект категории или None, если категория не найдена
        """
        try:
            stmt = select(self.model).where(self.model.name == name)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            logging.error(f"Ошибка при получении категории по названию '{name}': {e}")
            return None
    
    async def get_all_categories(self) -> List[Category]:
        """
        Получает все категории товаров, отсортированные по имени.
        
        Returns:
            Список всех категорий
        """
        return await self.get_all(order_by="name")
    
    async def get_root_categories(self) -> List[Category]:
        """
        Получает все корневые категории (без родительской категории).
        
        Returns:
            Список корневых категорий
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.parent_id.is_(None))
                .order_by(self.model.name)
            )
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении корневых категорий: {e}")
            return []
    
    async def get_subcategories(self, parent_id: int) -> List[Category]:
        """
        Получает все подкатегории для указанной родительской категории.
        
        Args:
            parent_id: ID родительской категории
            
        Returns:
            Список подкатегорий
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.parent_id == parent_id)
                .order_by(self.model.name)
            )
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении подкатегорий для категории {parent_id}: {e}")
            return []
    
    async def update_category(self, category_id: int, update_data: Dict[str, Any]) -> Optional[Category]:
        """
        Обновляет категорию по ID.
        
        Args:
            category_id: ID категории
            update_data: Словарь с обновляемыми полями
            
        Returns:
            Обновленный объект категории или None в случае ошибки
        """
        return await self.update(category_id, update_data)
    
    async def delete_category(self, category_id: int) -> bool:
        """
        Удаляет категорию по ID.
        
        Args:
            category_id: ID категории
            
        Returns:
            True, если категория успешно удалена, иначе False
        """
        return await self.delete(category_id)
    
    async def get_full_category_path(self, category_id: int) -> List[Category]:
        """
        Получает полный путь к категории, включая все родительские категории.
        
        Args:
            category_id: ID категории
            
        Returns:
            Список категорий, начиная с корневой и заканчивая указанной
        """
        try:
            result = []
            current_category = await self.get_by_id(category_id)
            
            # Если категория не найдена, возвращаем пустой список
            if not current_category:
                return []
                
            # Добавляем текущую категорию в результат
            result.append(current_category)
            
            # Рекурсивно добавляем родительские категории
            while current_category and current_category.parent_id:
                parent = await self.get_by_id(current_category.parent_id)
                if parent:
                    result.insert(0, parent)
                    current_category = parent
                else:
                    break
                    
            return result
        except Exception as e:
            logging.error(f"Ошибка при получении пути к категории {category_id}: {e}")
            return []