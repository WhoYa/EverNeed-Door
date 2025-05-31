from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, desc
from infrastructure.database.models.chats import Chat
from infrastructure.database.repositories.base import BaseRepo
import logging


class ChatRepo(BaseRepo[Chat]):
    """
    Репозиторий для работы с сообщениями чата.
    """
    model = Chat
    
    async def create_message(self, user_id: int, message: str, manager_id: Optional[int] = None) -> Optional[Chat]:
        """
        Создает новое сообщение в чате.
        
        Args:
            user_id: ID пользователя
            message: Текст сообщения
            manager_id: ID менеджера (если сообщение от менеджера)
            
        Returns:
            Созданное сообщение или None в случае ошибки
        """
        try:
            data = {
                "user_id": user_id,
                "message": message
            }
            
            if manager_id is not None:
                data["manager_id"] = manager_id
                
            chat_message = await self.create(data)
            logging.info(f"Создано новое сообщение в чате: user_id={user_id}, manager_id={manager_id}")
            return chat_message
        except Exception as e:
            logging.error(f"Ошибка при создании сообщения в чате: {e}")
            return None

    async def get_chat_by_user(self, user_id: int, limit: int = 50) -> List[Chat]:
        """
        Получает историю чата для конкретного пользователя.
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество сообщений
            
        Returns:
            Список сообщений чата
        """
        try:
            stmt = (
                select(Chat)
                .where(Chat.user_id == user_id)
                .order_by(desc(Chat.sent_at))
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            messages = list(result.scalars().all())
            
            # Возвращаем сообщения в хронологическом порядке (от старых к новым)
            return list(reversed(messages))
        except Exception as e:
            logging.error(f"Ошибка при получении истории чата для пользователя {user_id}: {e}")
            return []
            
    async def get_chats_for_manager(self, manager_id: Optional[int] = None, limit_per_user: int = 1) -> Dict[int, List[Chat]]:
        """
        Получает последние сообщения от всех пользователей для менеджера.
        
        Args:
            manager_id: ID менеджера (если None, возвращаются все чаты)
            limit_per_user: Количество последних сообщений от каждого пользователя
            
        Returns:
            Словарь {user_id: [сообщения]} с последними сообщениями от каждого пользователя
        """
        try:
            # Сначала получаем список уникальных пользователей с сообщениями
            users_stmt = (
                select(Chat.user_id)
                .distinct()
                .order_by(Chat.user_id)
            )
            
            if manager_id is not None:
                users_stmt = users_stmt.where(
                    or_(
                        Chat.manager_id == manager_id,
                        Chat.manager_id.is_(None)
                    )
                )
                
            result = await self.session.execute(users_stmt)
            user_ids = [row[0] for row in result]
            
            # Затем для каждого пользователя получаем последние сообщения
            chats = {}
            for user_id in user_ids:
                messages_stmt = (
                    select(Chat)
                    .where(Chat.user_id == user_id)
                    .order_by(desc(Chat.sent_at))
                    .limit(limit_per_user)
                )
                
                messages_result = await self.session.execute(messages_stmt)
                messages = list(messages_result.scalars().all())
                
                # Возвращаем сообщения в хронологическом порядке
                chats[user_id] = list(reversed(messages))
                
            return chats
        except Exception as e:
            logging.error(f"Ошибка при получении чатов для менеджера {manager_id}: {e}")
            return {}
            
    async def assign_manager_to_chat(self, user_id: int, manager_id: int) -> bool:
        """
        Назначает менеджера для чата с пользователем.
        
        Args:
            user_id: ID пользователя
            manager_id: ID менеджера
            
        Returns:
            True, если менеджер успешно назначен, иначе False
        """
        try:
            # Создаем системное сообщение о назначении менеджера
            await self.create_message(
                user_id=user_id,
                message=f"Менеджер (ID: {manager_id}) присоединился к чату.",
                manager_id=None  # Системное сообщение
            )
            
            return True
        except Exception as e:
            logging.error(f"Ошибка при назначении менеджера {manager_id} для чата с пользователем {user_id}: {e}")
            return False