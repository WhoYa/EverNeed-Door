from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from infrastructure.database.models.favorites import Favorite
from infrastructure.database.repositories.base import BaseRepo


class FavoritesRepo(BaseRepo):
    async def add_favorite(self, user_id: int, product_id: int) -> Favorite:
        """
        Adds a product to a user's favorites.
        """
        # Проверка, не добавлен ли продукт уже в избранное
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.product_id == product_id
        )
        existing_fav = await self.session.execute(stmt)
        existing_fav = existing_fav.scalar_one_or_none()
        if existing_fav:
            return existing_fav  # Или можно выбросить исключение

        favorite = Favorite(user_id=user_id, product_id=product_id)
        self.session.add(favorite)
        await self.session.commit()
        await self.session.refresh(favorite)
        return favorite

    async def get_favorites_by_user(self, user_id: int):
        """
        Retrieves all favorite products for a user.
        """
        stmt = select(Favorite).options(selectinload(Favorite.product)).where(Favorite.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def remove_favorite_by_user_product(self, user_id: int, product_id: int):
        """
        Removes a favorite by user ID and product ID.
        """
        stmt = delete(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.product_id == product_id
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def is_favorite(self, user_id: int, product_id: int) -> bool:
        """
        Checks if a product is already in the user's favorites.
        """
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.product_id == product_id
        )
        result = await self.session.execute(stmt)
        favorite = result.scalar_one_or_none()
        return favorite is not None
