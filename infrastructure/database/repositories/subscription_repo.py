from typing import List, Optional
from sqlalchemy import select, update, and_, or_
from infrastructure.database.models.subscriptions import Subscription, SubscriptionType
from infrastructure.database.repositories.base import BaseRepo
import logging

class SubscriptionRepo(BaseRepo):
    """
    Репозиторий для работы с подписками пользователей.
    """
    model = Subscription
    
    async def subscribe_user(self, user_id: int, subscription_type: str = SubscriptionType.ALL.value) -> Optional[Subscription]:
        """
        Подписывает пользователя на уведомления.
        
        Args:
            user_id: ID пользователя
            subscription_type: Тип подписки
            
        Returns:
            Созданная подписка или None в случае ошибки
        """
        try:
            # Проверяем, существует ли уже подписка
            stmt = select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.subscription_type == subscription_type
                )
            )
            
            result = await self.session.execute(stmt)
            existing_sub = result.scalars().first()
            
            if existing_sub:
                # Если существует, но неактивна, активируем
                if not existing_sub.is_active:
                    existing_sub.is_active = True
                    await self.session.commit()
                return existing_sub
                
            # Создаем новую подписку
            subscription = Subscription(
                user_id=user_id,
                subscription_type=subscription_type,
                is_active=True
            )
            
            self.session.add(subscription)
            await self.session.commit()
            return subscription
        except Exception as e:
            logging.error(f"Ошибка при подписке пользователя {user_id} на {subscription_type}: {e}")
            await self.session.rollback()
            return None
            
    async def unsubscribe_user(self, user_id: int, subscription_type: str = SubscriptionType.ALL.value) -> bool:
        """
        Отписывает пользователя от уведомлений.
        
        Args:
            user_id: ID пользователя
            subscription_type: Тип подписки
            
        Returns:
            True, если пользователь успешно отписан, иначе False
        """
        try:
            # Устанавливаем подписку как неактивную
            stmt = (
                update(Subscription)
                .where(
                    and_(
                        Subscription.user_id == user_id,
                        Subscription.subscription_type == subscription_type,
                        Subscription.is_active == True
                    )
                )
                .values(is_active=False)
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            return True
        except Exception as e:
            logging.error(f"Ошибка при отписке пользователя {user_id} от {subscription_type}: {e}")
            await self.session.rollback()
            return False
            
    async def get_user_subscriptions(self, user_id: int) -> List[Subscription]:
        """
        Получает все подписки пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список подписок пользователя
        """
        try:
            stmt = select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.is_active == True
                )
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logging.error(f"Ошибка при получении подписок пользователя {user_id}: {e}")
            return []
            
    async def is_subscribed(self, user_id: int, subscription_type: str = SubscriptionType.ALL.value) -> bool:
        """
        Проверяет, подписан ли пользователь на определенный тип уведомлений.
        
        Args:
            user_id: ID пользователя
            subscription_type: Тип подписки
            
        Returns:
            True, если пользователь подписан, иначе False
        """
        try:
            stmt = select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.subscription_type.in_([subscription_type, SubscriptionType.ALL.value]),
                    Subscription.is_active == True
                )
            )
            
            result = await self.session.execute(stmt)
            return result.scalars().first() is not None
        except Exception as e:
            logging.error(f"Ошибка при проверке подписки пользователя {user_id} на {subscription_type}: {e}")
            return False
            
    async def get_subscribers_by_type(self, subscription_type: str = SubscriptionType.ALL.value) -> List[int]:
        """
        Получает список ID пользователей, подписанных на определенный тип уведомлений.
        
        Args:
            subscription_type: Тип подписки
            
        Returns:
            Список ID пользователей
        """
        try:
            stmt = select(Subscription.user_id).where(
                and_(
                    or_(
                        Subscription.subscription_type == subscription_type,
                        Subscription.subscription_type == SubscriptionType.ALL.value
                    ),
                    Subscription.is_active == True
                )
            ).distinct()
            
            result = await self.session.execute(stmt)
            return [row[0] for row in result]
        except Exception as e:
            logging.error(f"Ошибка при получении подписчиков на {subscription_type}: {e}")
            return []