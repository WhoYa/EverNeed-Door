# tgbot/keyboards/back_button.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def back_button_keyboard(callback_data: str = "go_back") -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с одной кнопкой "Назад".
    
    Args:
        callback_data: Данные для callback_query. По умолчанию "go_back".
                     Для возврата в главное меню используйте "main_menu" или "admin_main".
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой назад
    """
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=callback_data
        )
    )
    return builder.as_markup()

def main_menu_button(is_admin: bool = False) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой возврата в главное меню.
    
    Args:
        is_admin: Флаг, указывающий, для администратора ли создается кнопка.
                 Если True, используется callback_data="admin_main".
                 Если False, используется callback_data="main_menu".
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой возврата в главное меню
    """
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="🔄 Главное меню",
            callback_data="admin_main" if is_admin else "main_menu"
        )
    )
    return builder.as_markup()
