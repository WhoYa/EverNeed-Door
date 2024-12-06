from typing import Optional
from sqlalchemy import select
from infrastructure.database.models.logs import Log
from infrastructure.database.repositories.base import BaseRepo


class LogRepo(BaseRepo):
    async def create_log(self, user_id: int, action: str, details: Optional[str] = None) -> Log:
        """
        Logs a user action.
        """
        log = Log(user_id=user_id, action=action, details=details)
        self.session.add(log)
        await self.session.commit()
        return log

    async def get_logs_by_user(self, user_id: int):
        """
        Retrieves logs for a specific user.
        """
        stmt = select(Log).where(Log.user_id == user_id)
        result = await self.session.scalars(stmt)
        return result.all()
