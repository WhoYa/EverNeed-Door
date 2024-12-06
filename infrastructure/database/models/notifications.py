from sqlalchemy import String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database.models.base import Base, TimestampMixin, TableNameMixin


class Notification(Base, TimestampMixin, TableNameMixin):
    """
    Notifications table representing notifications sent to users.
    """

    notification_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    def __repr__(self):
        return f"<Notification {self.notification_id} User: {self.user_id} Type: {self.type} Read: {self.is_read}>"
