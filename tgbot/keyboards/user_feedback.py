# tgbot/keyboards/user_feedback.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def feedback_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для обратной связи с кнопкой отмены.
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❌ Отмена",
        callback_data="cancel_feedback"
    )
    builder.adjust(1)
    return builder.as_markup()
