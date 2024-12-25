# tgbot/keyboards/product_management.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def product_management_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Добавить товар", callback_data="add_product")
    builder.button(text="Удалить товар", callback_data="delete_product")
    builder.button(text="Изменить товар", callback_data="edit_product")
    builder.button(text="Назад", callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()

def product_list_keyboard(products) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(text=product.name, callback_data=f"edit_{product.product_id}")
    builder.adjust(1)
    return builder.as_markup()

def confirmation_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data=f"confirm_delete_{product_id}")
    builder.button(text="Нет", callback_data="back_to_main_menu")
    builder.adjust(2)
    return builder.as_markup()

def edit_product_keyboard(product_name: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Название", callback_data="edit_name")
    builder.button(text="Описание", callback_data="edit_description")
    builder.button(text="Тип", callback_data="edit_type")
    builder.button(text="Материал", callback_data="edit_material")
    builder.button(text="Цена", callback_data="edit_price")
    builder.button(text="Фото", callback_data="edit_image_url")
    builder.button(text="Назад", callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()
