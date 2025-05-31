# tgbot/keyboards/admin_management.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_management_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для управления администраторами.
    """
    builder = InlineKeyboardBuilder()
    
    # Добавление администратора
    builder.row(
        InlineKeyboardButton(
            text="➕ Добавить администратора",
            callback_data="add_admin"
        )
    )
    
    # Удаление администратора
    builder.row(
        InlineKeyboardButton(
            text="➖ Удалить администратора",
            callback_data="remove_admin"
        )
    )
    
    # Кнопка назад
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад в меню",
            callback_data="admin_main"
        )
    )
    
    return builder.as_markup()