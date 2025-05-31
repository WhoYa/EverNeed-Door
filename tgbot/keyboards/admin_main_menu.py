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
            text="🏷️ Управление акциями",
            callback_data="manage_promotions"
        ),
        InlineKeyboardButton(
            text="📊 Статистика и логи",
            callback_data="view_statistics"
        ),
        InlineKeyboardButton(
            text="🔔 Управление подписками",
            callback_data="manage_subscriptions"
        ),
        InlineKeyboardButton(
            text="👨‍💼 Управление администраторами",
            callback_data="manage_admins"
        ),
        InlineKeyboardButton(
            text="🛒 Просмотр заказов",
            callback_data="view_orders"
        )
    )
    builder.adjust(1)  # Каждый пункт в отдельной строке
    return builder.as_markup()

def admin_back_button(callback_data: str = "admin_main") -> InlineKeyboardMarkup:
    """
    Простая кнопка "Назад" для админ-меню.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=callback_data
        )
    )
    return builder.as_markup()