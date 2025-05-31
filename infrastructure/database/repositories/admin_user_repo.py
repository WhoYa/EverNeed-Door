from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, and_, or_
from infrastructure.database.models.admin_users import AdminUser, AdminRole
from infrastructure.database.repositories.base import BaseRepo
import logging

class AdminUserRepo(BaseRepo):
    """
    Репозиторий для работы с администраторами.
    """
    model = AdminUser
    
    async def create_admin(self, user_id: int, role: str = AdminRole.MANAGER.value, 
                          created_by: Optional[int] = None, username: Optional[str] = None) -> Optional[AdminUser]:
        """
        Создает нового администратора.
        
        Args:
            user_id: ID пользователя в Telegram
            role: Роль администратора (по умолчанию - manager)
            created_by: ID администратора, создавшего этого администратора
            username: Имя пользователя в Telegram
            
        Returns:
            Созданный объект администратора или None в случае ошибки
        """
        try:
            data = {
                "user_id": user_id,
                "role": role,
                "username": username,
                "is_active": True
            }
            
            if created_by:
                data["created_by"] = created_by
                
            admin = await self.create(data)
            logging.info(f"Создан новый администратор: user_id={user_id}, role={role}")
            return admin
        except Exception as e:
            logging.error(f"Ошибка при создании администратора: {e}")
            await self.session.rollback()
            return None
            
    async def get_admin_by_user_id(self, user_id: int) -> Optional[AdminUser]:
        """
        Получает администратора по ID пользователя Telegram.
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            Объект администратора или None, если не найден
        """
        try:
            stmt = select(AdminUser).where(
                and_(
                    AdminUser.user_id == user_id,
                    AdminUser.is_active == True
                )
            )
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            logging.error(f"Ошибка при получении администратора по user_id {user_id}: {e}")
            return None
            
    async def is_admin(self, user_id: int) -> bool:
        """
        Проверяет, является ли пользователь администратором.
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            True, если пользователь является администратором, иначе False
        """
        admin = await self.get_admin_by_user_id(user_id)
        return admin is not None
        
    async def is_super_admin(self, user_id: int) -> bool:
        """
        Проверяет, является ли пользователь суперадминистратором.
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            True, если пользователь является суперадминистратором, иначе False
        """
        try:
            stmt = select(AdminUser).where(
                and_(
                    AdminUser.user_id == user_id,
                    AdminUser.role == AdminRole.ADMIN.value,
                    AdminUser.is_active == True
                )
            )
            result = await self.session.execute(stmt)
            return result.scalars().first() is not None
        except Exception as e:
            logging.error(f"Ошибка при проверке статуса суперадмина для user_id {user_id}: {e}")
            return False
            
    async def get_all_admins(self) -> List[AdminUser]:
        """
        Получает список всех активных администраторов.
        
        Returns:
            Список активных администраторов
        """
        try:
            return await self.get_all(conditions=[AdminUser.is_active == True])
        except Exception as e:
            logging.error(f"Ошибка при получении списка администраторов: {e}")
            return []
            
    async def deactivate_admin(self, admin_id: int) -> bool:
        """
        Деактивирует администратора.
        
        Args:
            admin_id: ID администратора
            
        Returns:
            True, если администратор успешно деактивирован, иначе False
        """
        try:
            return await self.update_field(admin_id, "is_active", False)
        except Exception as e:
            logging.error(f"Ошибка при деактивации администратора {admin_id}: {e}")
            return False
            
    async def update_admin_role(self, admin_id: int, new_role: str) -> bool:
        """
        Обновляет роль администратора.
        
        Args:
            admin_id: ID администратора
            new_role: Новая роль администратора
            
        Returns:
            True, если роль успешно обновлена, иначе False
        """
        try:
            return await self.update_field(admin_id, "role", new_role)
        except Exception as e:
            logging.error(f"Ошибка при обновлении роли администратора {admin_id}: {e}")
            return False