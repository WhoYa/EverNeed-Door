from math import ceil
from typing import List, Optional, Union, Any
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

class KeyboardBuilder:
    """
    Базовый класс для построения клавиатур.
    Предоставляет общие методы для создания клавиатур с различными настройками.
    """
    
    @staticmethod
    def create_builder() -> InlineKeyboardBuilder:
        """
        Создает новый экземпляр InlineKeyboardBuilder.
        
        Returns:
            InlineKeyboardBuilder: Новый экземпляр строителя клавиатуры
        """
        return InlineKeyboardBuilder()
    
    @staticmethod
    def add_navigation_buttons(
        builder: InlineKeyboardBuilder, 
        current_page: int, 
        total_pages: int, 
        callback_prefix: str
    ) -> None:
        """
        Добавляет кнопки навигации для пагинации.
        
        Args:
            builder: Экземпляр InlineKeyboardBuilder
            current_page: Текущая страница
            total_pages: Общее количество страниц
            callback_prefix: Префикс для callback данных
        """
        nav_buttons = []
        
        # Добавляем кнопки навигации
        if current_page > 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="<< Назад", 
                    callback_data=f"{callback_prefix}_{current_page-1}"
                )
            )
        
        if current_page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="Далее >>", 
                    callback_data=f"{callback_prefix}_{current_page+1}"
                )
            )
        
        # Если есть кнопки навигации, добавляем их одной строкой
        if nav_buttons:
            builder.row(*nav_buttons)
    
    @staticmethod
    def add_back_button(
        builder: InlineKeyboardBuilder, 
        text: str = "Назад", 
        callback_data: str = "go_back"
    ) -> None:
        """
        Добавляет кнопку "Назад" в клавиатуру.
        
        Args:
            builder: Экземпляр InlineKeyboardBuilder
            text: Текст кнопки
            callback_data: Данные для обратного вызова
        """
        builder.button(text=text, callback_data=callback_data)
    
    @staticmethod
    def create_confirmation_buttons(
        builder: InlineKeyboardBuilder,
        yes_text: str = "Да",
        no_text: str = "Нет",
        yes_callback: str = "confirm_yes",
        no_callback: str = "confirm_no"
    ) -> None:
        """
        Добавляет кнопки подтверждения (Да/Нет) в клавиатуру.
        
        Args:
            builder: Экземпляр InlineKeyboardBuilder
            yes_text: Текст кнопки "Да"
            no_text: Текст кнопки "Нет"
            yes_callback: Данные для обратного вызова кнопки "Да"
            no_callback: Данные для обратного вызова кнопки "Нет"
        """
        builder.button(text=yes_text, callback_data=yes_callback)
        builder.button(text=no_text, callback_data=no_callback)
        builder.adjust(2)  # Располагаем кнопки в одной строке

def product_management_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для управления товарами.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками для управления товарами
    """
    builder = KeyboardBuilder.create_builder()
    builder.button(text="Добавить товар", callback_data="add_product")
    builder.button(text="Удалить товар", callback_data="delete_product")
    builder.button(text="Просмотреть товары", callback_data="view_products")
    KeyboardBuilder.add_back_button(builder, text="Назад", callback_data="back_to_main_menu")
    builder.adjust(2)  # Располагаем кнопки по 2 в строке
    return builder.as_markup()

def product_list_keyboard_paginated(products, page: int = 1, page_size: int = 5) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру с товарами для текущей страницы.
    
    Также добавляет кнопки навигации и "Назад" в главное меню управления товарами.
    
    Args:
        products: Список товаров
        page: Текущая страница
        page_size: Количество товаров на странице
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с товарами и навигацией
    """
    builder = KeyboardBuilder.create_builder()
    
    total_products = len(products)
    total_pages = ceil(total_products / page_size)  # округление вверх

    # Формируем срез товаров для текущей страницы
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    page_products = products[start_index:end_index]

    # Создаём кнопку для каждого товара
    for product in page_products:
        builder.button(
            text=product.name, 
            callback_data=f"product_{product.product_id}"
        )

    # Добавляем кнопки навигации
    KeyboardBuilder.add_navigation_buttons(
        builder, 
        page, 
        total_pages, 
        "view_products_page"
    )

    # Кнопка "Назад" для возврата в меню управления товарами
    KeyboardBuilder.add_back_button(
        builder,
        text="Назад", 
        callback_data="manage_products"
    )

    # Настраиваем по две кнопки в строке (кроме row для навигации)
    builder.adjust(2)
    return builder.as_markup()

def confirmation_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для подтверждения действия с товаром.
    
    Args:
        product_id: ID товара
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками "Да" и "Нет"
    """
    builder = KeyboardBuilder.create_builder()
    KeyboardBuilder.create_confirmation_buttons(
        builder,
        yes_text="Да", 
        no_text="Нет",
        yes_callback=f"confirm_delete_{product_id}",
        no_callback=f"product_{product_id}"
    )
    return builder.as_markup()

def edit_product_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для редактирования товара.
    
    Args:
        product_id: ID товара
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками для редактирования полей товара
    """
    builder = KeyboardBuilder.create_builder()
    
    # Кнопки для редактирования полей товара
    field_buttons = [
        ("Название", f"edit_name_{product_id}"),
        ("Описание", f"edit_description_{product_id}"),
        ("Тип", f"edit_type_{product_id}"),
        ("Материал", f"edit_material_{product_id}"),
        ("Цена", f"edit_price_{product_id}"),
        ("Фото", f"edit_image_url_{product_id}")
    ]
    
    # Добавляем кнопки редактирования
    for text, callback_data in field_buttons:
        builder.button(text=text, callback_data=callback_data)
    
    # Добавляем кнопку "Назад"
    KeyboardBuilder.add_back_button(
        builder,
        text="Назад", 
        callback_data=f"product_{product_id}"
    )
    
    # Располагаем кнопки по 3 в строке
    builder.adjust(3)
    return builder.as_markup()

def product_details_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для просмотра деталей товара с кнопками действий.
    
    Args:
        product_id: ID товара
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками действий
    """
    builder = KeyboardBuilder.create_builder()
    
    # Кнопки действий с товаром
    builder.button(text="✏️ Изменить", callback_data=f"edit_{product_id}")
    builder.button(text="🗑 Удалить", callback_data=f"delete_{product_id}")
    
    # Кнопка "Назад"
    KeyboardBuilder.add_back_button(
        builder,
        text="◀️ Назад", 
        callback_data="view_products"
    )
    
    # Располагаем кнопки по 3 в строке
    builder.adjust(3)
    return builder.as_markup()
