from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, desc, and_, between
from infrastructure.database.models.admin_logs import AdminLog
from infrastructure.database.repositories.base import BaseRepo
import logging

class AdminLogRepo(BaseRepo):
    """
    Репозиторий для работы с логами действий администраторов.
    """
    model = AdminLog
    
    async def log_action(self, admin_id: int, action: str, entity_type: str, 
                        entity_id: Optional[int] = None, details: Optional[str] = None) -> Optional[AdminLog]:
        """
        Логирует действие администратора.
        
        Args:
            admin_id: ID администратора
            action: Тип действия (add_product, edit_product, delete_product и т.д.)
            entity_type: Тип сущности (product, promotion и т.д.)
            entity_id: ID сущности (опционально)
            details: Детали действия (опционально)
            
        Returns:
            Созданный объект лога или None в случае ошибки
        """
        try:
            data = {
                "admin_id": admin_id,
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "details": details
            }
            
            log_entry = await self.create(data)
            return log_entry
        except Exception as e:
            logging.error(f"Ошибка при логировании действия администратора: {e}")
            await self.session.rollback()
            return None
            
    async def get_logs_by_admin(self, admin_id: int, limit: int = 100) -> List[AdminLog]:
        """
        Получает логи конкретного администратора.
        
        Args:
            admin_id: ID администратора
            limit: Максимальное количество логов
            
        Returns:
            Список логов администратора
        """
        try:
            stmt = (
                select(AdminLog)
                .where(AdminLog.admin_id == admin_id)
                .order_by(desc(AdminLog.timestamp))
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении логов администратора {admin_id}: {e}")
            return []
            
    async def get_logs_by_entity(self, entity_type: str, entity_id: Optional[int] = None, limit: int = 100) -> List[AdminLog]:
        """
        Получает логи по типу сущности и опционально по ID сущности.
        
        Args:
            entity_type: Тип сущности
            entity_id: ID сущности (опционально)
            limit: Максимальное количество логов
            
        Returns:
            Список логов для указанной сущности
        """
        try:
            conditions = [AdminLog.entity_type == entity_type]
            
            if entity_id is not None:
                conditions.append(AdminLog.entity_id == entity_id)
                
            stmt = (
                select(AdminLog)
                .where(and_(*conditions))
                .order_by(desc(AdminLog.timestamp))
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении логов для {entity_type} {entity_id}: {e}")
            return []
            
    async def get_logs_by_date_range(self, start_date: datetime, end_date: datetime, limit: int = 100) -> List[AdminLog]:
        """
        Получает логи за указанный период времени.
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            limit: Максимальное количество логов
            
        Returns:
            Список логов за указанный период
        """
        try:
            stmt = (
                select(AdminLog)
                .where(between(AdminLog.timestamp, start_date, end_date))
                .order_by(desc(AdminLog.timestamp))
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении логов за период {start_date} - {end_date}: {e}")
            return []
            
    async def get_recent_logs(self, limit: int = 100) -> List[AdminLog]:
        """
        Получает последние логи.
        
        Args:
            limit: Максимальное количество логов
            
        Returns:
            Список последних логов
        """
        try:
            stmt = (
                select(AdminLog)
                .order_by(desc(AdminLog.timestamp))
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении последних логов: {e}")
            return []