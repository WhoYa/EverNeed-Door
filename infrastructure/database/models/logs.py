from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, Text, TIMESTAMP, BIGINT, func
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database.models.base import Base, TableNameMixin


class Log(Base, TableNameMixin):
    """
    Logs table representing user actions for audit or debugging purposes.
    """

    log_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<Log {self.log_id} User: {self.user_id} Action: {self.action} Time: {self.timestamp}>"
