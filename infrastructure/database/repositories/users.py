from typing import Optional
import logging

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from infrastructure.database.models.users import User
from infrastructure.database.repositories.base import BaseRepo


class UsersRepo(BaseRepo[User]):
    """
    Repository for managing User entities in the database.
    
    Provides methods for creating, updating, and retrieving users.
    """
    model = User
    
    async def get_or_create_user(
        self,
        user_id: int,
        first_name: str,
        last_name: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
        role: str = "user",
    ) -> Optional[User]:
        """
        Creates or updates a user in the database and returns the user object.
        
        Args:
            user_id: Telegram user ID
            first_name: User's first name
            last_name: User's last name
            username: Optional Telegram username
            email: Optional email address
            role: User role, defaults to "user"
            
        Returns:
            The created or updated User object, or None if an error occurred
        """
        try:
            insert_stmt = select(User).from_statement(
                insert(User)
                .values(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    role=role,
                )
                .returning(User)
                .on_conflict_do_update(
                    index_elements=[User.user_id],
                    set_=dict(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        # Don't update role on conflict to prevent overwriting admin status
                    ),
                )
            )
            result = await self.session.scalars(insert_stmt)
            await self.session.commit()
            return result.first()
        except SQLAlchemyError as e:
            logging.error(f"Error creating/updating user {user_id}: {e}")
            await self.session.rollback()
            return None

    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """
        Marks the user as inactive.
        
        Args:
            user_id: The user ID to deactivate
            
        Returns:
            The deactivated User object, or None if user not found or an error occurred
        """
        try:
            stmt = (
                update(User)
                .where(User.user_id == user_id)
                .values(active=False)
                .returning(User)
            )
            result = await self.session.scalars(stmt)
            await self.session.commit()
            return result.first()
        except SQLAlchemyError as e:
            logging.error(f"Error deactivating user {user_id}: {e}")
            await self.session.rollback()
            return None

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieves a user by ID.
        
        Args:
            user_id: The user ID to retrieve
            
        Returns:
            The User object if found, otherwise None
        """
        try:
            stmt = select(User).where(User.user_id == user_id)
            result = await self.session.scalars(stmt)
            return result.first()
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving user {user_id}: {e}")
            return None
            
    async def set_user_role(self, user_id: int, role: str) -> bool:
        """
        Updates a user's role.
        
        Args:
            user_id: The user ID to update
            role: The new role to assign
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return await self.update_field(user_id, "role", role)
        except Exception as e:
            logging.error(f"Error updating role for user {user_id}: {e}")
            return False
