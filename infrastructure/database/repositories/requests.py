# infrastructure/database/repositories/requests.py

from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repositories.users import UserRepo
from infrastructure.database.repositories.products import ProductsRepo  
from infrastructure.database.repositories.orders import OrderRepo
from infrastructure.database.repositories.notifications import NotificationRepo
from infrastructure.database.repositories.feedback import FeedbackRepo
from infrastructure.database.repositories.favorites import FavoritesRepo


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def users(self) -> UserRepo:
        """
        The User repository for managing user-related operations.
        """
        return UserRepo(self.session)

    @property
    def products(self) -> ProductsRepo:
        """
        The Product repository for managing product-related operations.
        """
        return ProductsRepo(self.session)

    @property
    def orders(self) -> OrderRepo:
        """
        The Order repository for managing order-related operations.
        """
        return OrderRepo(self.session)

    @property
    def notifications(self) -> NotificationRepo:
        """
        The Notification repository for managing notification-related operations.
        """
        return NotificationRepo(self.session)
    
    @property
    def feedbacks(self) -> FeedbackRepo:
        """
        The Feedback repository for managing user feedback operations.
        """
        return FeedbackRepo(self.session)
    
    @property
    def favorites(self) -> FavoritesRepo:
        """
        The Favorites repository for managing user favorites operations.
        """
        return FavoritesRepo(self.session)
