from sqlalchemy import select, update
from infrastructure.database.models.notifications import Notification
from infrastructure.database.repositories.base import BaseRepo


class NotificationRepo(BaseRepo):
    async def create_notification(self, user_id: int, notification_data: dict) -> Notification:
        """
        Creates a notification for a user.
        """
        notification = Notification(user_id=user_id, **notification_data)
        self.session.add(notification)
        await self.session.commit()
        return notification

    async def get_notifications_by_user(self, user_id: int):
        """
        Retrieves all notifications for a user.
        """
        stmt = select(Notification).where(Notification.user_id == user_id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def mark_as_read(self, notification_id: int):
        """
        Marks a notification as read.
        """
        stmt = (
            update(Notification)
            .where(Notification.notification_id == notification_id)
            .values(is_read=True)
        )
        await self.session.execute(stmt)
        await self.session.commit()
