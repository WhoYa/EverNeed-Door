from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, Text, TIMESTAMP, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.models.base import Base, TableNameMixin

class AdminLog(Base, TableNameMixin):
    """
    Модель логов действий администраторов.
    
    Attributes:
        log_id: Уникальный идентификатор лога
        admin_id: ID администратора, выполнившего действие
        action: Тип действия (add_product, edit_product, delete_product, и т.д.)
        entity_type: Тип сущности, над которой выполнено действие (product, promotion, и т.д.)
        entity_id: ID сущности, над которой выполнено действие (опционально)
        details: Детали действия (опционально)
        timestamp: Время выполнения действия
    """
    log_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("admin_users.admin_id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    
    # Отношения
    admin = relationship("AdminUser", foreign_keys=[admin_id], primaryjoin="AdminLog.admin_id == AdminUser.admin_id")
    
    def __repr__(self):
        return f"<AdminLog id={self.log_id} admin_id={self.admin_id} action='{self.action}' entity={self.entity_type}>"