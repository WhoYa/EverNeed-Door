from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models.users import User
from infrastructure.database.repositories.base import BaseRepo


class UserRepo(BaseRepo):
    async def get_or_create_user(
        self,
        user_id: int,
        first_name: str,
        last_name: str,
        email: Optional[str] = None,
        username: Optional[str] = None,
        role: str = "user",
    ) -> User:
        """
        Creates or updates a user in the database and returns the user object.
        """
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
                    role=role,
                ),
            )
        )
        result = await self.session.scalars(insert_stmt)

        await self.session.commit()
        return result.first()

    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """
        Marks the user as inactive.
        """
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(active=False)
            .returning(User)
        )
        result = await self.session.scalars(stmt)

        await self.session.commit()
        return result.first()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieves a user by ID.
        """
        stmt = select(User).where(User.user_id == user_id)
        result = await self.session.scalars(stmt)
        return result.first()
