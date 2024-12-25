# tgbot/filters/admin.py 
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from typing import Union

from tgbot.config import Config


class AdminFilter(BaseFilter):
    is_admin: bool = True

    async def __call__(self, obj: Union[Message, CallbackQuery], config: Config) -> bool:
        if isinstance(obj, Message):
            user_id = obj.from_user.id
        elif isinstance(obj, CallbackQuery):
            user_id = obj.from_user.id
        else:
            return False
        return (user_id in config.tg_bot.admin_ids) == self.is_admin
