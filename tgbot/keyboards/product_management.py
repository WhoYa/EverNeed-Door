from math import ceil
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def product_management_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Добавить товар", callback_data="add_product")
    builder.button(text="Удалить товар", callback_data="delete_product")
    builder.button(text="Просмотреть товары", callback_data="view_products")
    builder.button(text="Назад", callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()

def product_list_keyboard_paginated(products, page: int = 1, page_size: int = 5) -> InlineKeyboardMarkup:
    """
    Создаём клавиатуру, где показываем товары для текущей страницы,
    а также кнопки навигации и "Назад" в главное меню управления товарами.
    """
    builder = InlineKeyboardBuilder()
    
    total_products = len(products)
    total_pages = ceil(total_products / page_size)  # округление вверх

    # Срез товаров для текущей страницы:
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    page_products = products[start_index:end_index]

    # Создаём кнопку для каждого товара
    for product in page_products:
        builder.button(
            text=product.name, 
            callback_data=f"product_{product.product_id}"
        )

    # Кнопки навигации (<< Назад | Далее >>)
    # Показываем, только если есть соответствующие страницы
    nav_buttons = []
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="<< Назад", 
                callback_data=f"view_products_page_{page-1}"
            )
        )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Далее >>", 
                callback_data=f"view_products_page_{page+1}"
            )
        )
    if nav_buttons:
        # Выведем их в одну строку, если обе есть
        builder.row(*nav_buttons)

    # Кнопка "Назад" для возврата в меню управления товарами
    builder.button(
        text="Назад", 
        callback_data="manage_products"
    )

    # Настраиваем, чтобы каждая кнопка шла на своей строке (кроме row для навигации)
    builder.adjust(1)
    return builder.as_markup()

def confirmation_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data=f"confirm_delete_{product_id}")
    builder.button(text="Нет", callback_data=f"product_{product_id}")
    builder.adjust(2)
    return builder.as_markup()

def edit_product_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Название", callback_data=f"edit_name_{product_id}")
    builder.button(text="Описание", callback_data=f"edit_description_{product_id}")
    builder.button(text="Тип", callback_data=f"edit_type_{product_id}")
    builder.button(text="Материал", callback_data=f"edit_material_{product_id}")
    builder.button(text="Цена", callback_data=f"edit_price_{product_id}")
    builder.button(text="Фото", callback_data=f"edit_image_url_{product_id}")
    builder.button(text="Назад", callback_data=f"product_{product_id}")
    builder.adjust(1)
    return builder.as_markup()

def product_details_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для просмотра деталей товара с кнопками действий.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="Изменить", callback_data=f"edit_{product_id}")
    builder.button(text="Удалить", callback_data=f"delete_{product_id}")
    builder.button(text="Назад", callback_data="view_products")
    builder.adjust(1)
    return builder.as_markup()
