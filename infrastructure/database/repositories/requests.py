# infrastructure/database/repositories/requests.py

from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repositories.users import UsersRepo
from infrastructure.database.repositories.products import ProductsRepo  
from infrastructure.database.repositories.orders import OrdersRepo
from infrastructure.database.repositories.notifications import NotificationsRepo
from infrastructure.database.repositories.feedback import FeedbackRepo
from infrastructure.database.repositories.favorites import FavoritesRepo
from infrastructure.database.repositories.reviews import ReviewsRepo
from infrastructure.database.repositories.categories import CategoriesRepo
from infrastructure.database.repositories.specifications import SpecificationsRepo
from infrastructure.database.repositories.logs import LogsRepo
from infrastructure.database.repositories.chat import ChatRepo
from infrastructure.database.repositories.admin_user_repo import AdminUserRepo


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def users(self) -> UsersRepo:
        """
        The User repository for managing user-related operations.
        """
        return UsersRepo(self.session)

    @property
    def products(self) -> ProductsRepo:
        """
        The Product repository for managing product-related operations.
        """
        return ProductsRepo(self.session)

    @property
    def orders(self) -> OrdersRepo:
        """
        The Order repository for managing order-related operations.
        """
        return OrdersRepo(self.session)

    @property
    def notifications(self) -> NotificationsRepo:
        """
        The Notification repository for managing notification-related operations.
        """
        return NotificationsRepo(self.session)
    
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
        
    @property
    def reviews(self) -> ReviewsRepo:
        """
        The Reviews repository for managing product reviews.
        """
        return ReviewsRepo(self.session)
        
    @property
    def categories(self) -> CategoriesRepo:
        """
        The Categories repository for managing product categories.
        """
        return CategoriesRepo(self.session)
        
    @property
    def specifications(self) -> SpecificationsRepo:
        """
        The Specifications repository for managing product specifications.
        """
        return SpecificationsRepo(self.session)
        
    @property
    def logs(self) -> LogsRepo:
        """
        The Logs repository for managing user activity logs.
        """
        return LogsRepo(self.session)
        
    @property
    def feedback(self) -> FeedbackRepo:
        """
        The Feedback repository for managing user feedback.
        """
        return FeedbackRepo(self.session)
        
    @property
    def chat(self) -> ChatRepo:
        """
        The Chat repository for managing user-manager chat messages.
        """
        return ChatRepo(self.session)
        
    @property
    def admin_users(self) -> AdminUserRepo:
        """
        The AdminUser repository for managing admin users.
        """
        return AdminUserRepo(self.session)
