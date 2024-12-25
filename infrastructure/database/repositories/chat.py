from sqlalchemy import select
from infrastructure.database.models.chats import Chat
from infrastructure.database.repositories.base import BaseRepo


class ChatRepo(BaseRepo):
    async def create_message(self, user_id: int, manager_id: int, message: str) -> Chat:
        """
        Adds a new message to the chat.
        """
        chat_message = Chat(user_id=user_id, manager_id=manager_id, message=message)
        self.session.add(chat_message)
        await self.session.commit()
        return chat_message

    async def get_chat_by_user(self, user_id: int):
        """
        Retrieves chat messages for a specific user.
        """
        stmt = select(Chat).where(Chat.user_id == user_id)
        result = await self.session.scalars(stmt)
        return result.all()
