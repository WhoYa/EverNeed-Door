# tgbot/keyboards/admin_main_menu.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="📦 Управление товарами",
            callback_data="manage_products"
        ),
        InlineKeyboardButton(
            text="🛒 Просмотр заказов",
            callback_data="view_orders"
        ),
        InlineKeyboardButton(
            text="🔔 Управление уведомлениями",
            callback_data="manage_notifications"
        )
    )
    builder.adjust(1)  # Каждый пункт в отдельной строке
    return builder.as_markup()
