from typing import Callable, Dict, Any, Awaitable, Optional
import logging

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TelegramUser

from infrastructure.database.repositories.requests import RequestsRepo

class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_pool) -> None:
        super().__init__()
        self.session_pool = session_pool
        self.logger = logging.getLogger(__name__)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Extract Telegram user from event
        from_user: Optional[TelegramUser] = getattr(event, "from_user", None)
        if not from_user:
            # Skip middleware for updates without user information
            self.logger.debug("Skipping database middleware for update without user info")
            return await handler(event, data)

        try:
            async with self.session_pool() as session:
                repo = RequestsRepo(session)

                # Get correctly typed user attributes
                user_id = from_user.id
                first_name = from_user.first_name
                last_name = from_user.last_name or ""
                username = from_user.username

                # Create or get the user
                user = await repo.users.get_or_create_user(
                    user_id=user_id,
                    first_name=first_name,
                    last_name=last_name,
                    username=username
                )

                # Add to handler data
                data["session"] = session
                data["repo"] = repo
                data["user"] = user

                # Execute handler
                return await handler(event, data)
        except Exception as e:
            self.logger.error(f"Error in database middleware: {e}")
            # Still try to handle the update even if database operations failed
            return await handler(event, data)
