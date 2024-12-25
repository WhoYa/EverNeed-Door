# tgbot/keyboards/user_menu.py

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Главное меню пользователя с добавленной кнопкой обратной связи.
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📦 Каталог",
        callback_data="catalog"
    )
    builder.button(
        text="🛒 Мои заказы",
        callback_data="my_orders"
    )
    builder.button(
        text="⭐ Избранное",
        callback_data="view_favorites"
    )
    builder.button(
        text="💬 Обратная связь",
        callback_data="start_feedback"
    )
    builder.button(
        text="❓ Часто задаваемые вопросы",
        callback_data="faq"
    )
    builder.button(
        text="🔄 Меню",
        callback_data="main_menu"
    )
    builder.adjust(1)  # Каждая кнопка в отдельной строке
    return builder.as_markup()
