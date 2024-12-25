# tgbot/keyboards/user_favorites.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from tgbot.misc.callback_factory import FavoriteActionCallback

def favorites_keyboard(favorites) -> InlineKeyboardMarkup:
    """
    Клавиатура для отображения списка избранных товаров с опциями просмотра и удаления.
    """
    builder = InlineKeyboardBuilder()
    for favorite in favorites:
        builder.button(
            text=favorite.product.name,
            callback_data=FavoriteActionCallback(action="view", product_id=favorite.product_id)
        )
        builder.button(
            text="❌ Удалить",
            callback_data=FavoriteActionCallback(action="remove", product_id=favorite.product_id)
        )
    builder.adjust(2)  # Две кнопки в строке: Просмотр и Удаление
    return builder.as_markup()

def empty_favorites_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для случая, когда у пользователя нет избранных товаров.
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔙 Назад",
        callback_data="main_menu"
    )
    builder.adjust(1)
    return builder.as_markup()
