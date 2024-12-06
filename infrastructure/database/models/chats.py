from datetime import datetime
from sqlalchemy import ForeignKey, Text, TIMESTAMP, BIGINT, func
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database.models.base import Base, TableNameMixin


class Chat(Base, TableNameMixin):
    """
    Chats table representing messages exchanged between users and managers.
    """

    chat_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    manager_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=True)  # Manager is optional
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<Chat {self.chat_id} User: {self.user_id} Manager: {self.manager_id} Sent: {self.sent_at}>"
