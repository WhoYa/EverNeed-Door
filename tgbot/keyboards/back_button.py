# tgbot/keyboards/back_button.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def back_button_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="go_back"
        )
    )
    # Делаем кнопку оптимальной ширины, а не на всю ширину сообщения
    return builder.as_markup(resize_keyboard=True, width=1)
