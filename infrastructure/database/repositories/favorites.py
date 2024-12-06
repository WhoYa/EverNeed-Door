from sqlalchemy import select, delete
from infrastructure.database.models.favorites import Favorite
from infrastructure.database.repositories.base import BaseRepo


class FavoriteRepo(BaseRepo):
    async def add_favorite(self, user_id: int, product_id: int) -> Favorite:
        """
        Adds a product to a user's favorites.
        """
        favorite = Favorite(user_id=user_id, product_id=product_id)
        self.session.add(favorite)
        await self.session.commit()
        return favorite

    async def get_favorites_by_user(self, user_id: int):
        """
        Retrieves all favorite products for a user.
        """
        stmt = select(Favorite).where(Favorite.user_id == user_id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def remove_favorite(self, favorite_id: int):
        """
        Removes a favorite by ID.
        """
        stmt = delete(Favorite).where(Favorite.favorite_id == favorite_id)
        await self.session.execute(stmt)
        await self.session.commit()
