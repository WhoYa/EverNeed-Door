# infrastructure/database/repositories/feedback.py

from typing import List
from sqlalchemy.future import select

from infrastructure.database.models.feedback import Feedback
from infrastructure.database.repositories.base import BaseRepo

class FeedbackRepo(BaseRepo):
    async def create_feedback(self, user_id: int, message: str) -> Feedback:
        """
        Создает новый отзыв от пользователя.
        """
        feedback = Feedback(user_id=user_id, message=message)
        self.session.add(feedback)
        await self.session.commit()
        await self.session.refresh(feedback)
        return feedback

    async def get_feedbacks_by_user(self, user_id: int) -> List[Feedback]:
        """
        Получает все отзывы пользователя.
        """
        stmt = select(Feedback).where(Feedback.user_id == user_id).order_by(Feedback.created_at.desc())
        result = await self.session.execute(stmt)
        feedbacks = result.scalars().all()
        return feedbacks
