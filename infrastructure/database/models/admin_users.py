from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum as PyEnum
from infrastructure.database.models.base import Base, TimestampMixin, TableNameMixin

class AdminRole(str, PyEnum):
    """
    Перечисление ролей администраторов.
    """
    ADMIN = "admin"  # Полный доступ ко всем функциям
    MANAGER = "manager"  # Ограниченный доступ, только чаты с клиентами

class AdminUser(Base, TimestampMixin, TableNameMixin):
    __tablename__ = "admin_users"
    """
    Модель администраторов бота.
    
    Attributes:
        admin_id: Уникальный идентификатор администратора
        user_id: ID пользователя в Telegram
        username: Имя пользователя в Telegram (опционально)
        role: Роль администратора (admin или manager)
        is_active: Активен ли аккаунт администратора
        created_by: ID администратора, создавшего этого администратора
    """
    admin_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=False, unique=True)  # Telegram User ID
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=AdminRole.MANAGER.value)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[int] = mapped_column(Integer, nullable=True)  # ID администратора, создавшего этого администратора
    
    def __repr__(self):
        return f"<Admin id={self.admin_id} user_id={self.user_id} role={self.role}>"
    
    