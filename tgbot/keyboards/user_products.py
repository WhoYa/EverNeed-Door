# tgbot/keyboards/user_products.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from tgbot.misc.callback_factory import ProductViewCallback, FavoriteActionCallback, FilterCallback

def products_keyboard(products, with_filter: bool = True, page: int = 0, items_per_page: int = 5) -> InlineKeyboardMarkup:
    """
    Клавиатура для отображения списка товаров с опциями просмотра и добавления в избранное.
    
    Args:
        products: Список объектов продуктов
        with_filter: Флаг для отображения кнопки фильтрации
        page: Текущая страница для пагинации
        items_per_page: Количество товаров на странице
    
    Returns:
        InlineKeyboardMarkup с кнопками для каждого продукта и навигации
    """
    builder = InlineKeyboardBuilder()
    
    # Определяем товары для текущей страницы
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(products))
    current_page_products = products[start_idx:end_idx]
    
    # Добавляем кнопки для товаров текущей страницы
    for product in current_page_products:
        # Кнопка для просмотра продукта
        view_button = InlineKeyboardButton(
            text=f"🔍 {product.name}",
            callback_data=ProductViewCallback(product_id=product.product_id).pack()
        )
        
        # Кнопка для добавления в избранное
        favorite_button = InlineKeyboardButton(
            text="⭐️",
            callback_data=FavoriteActionCallback(action="add", product_id=product.product_id).pack()
        )
        
        # Добавляем кнопки в строку
        builder.row(view_button, favorite_button)
    
    # Кнопки пагинации
    pagination_buttons = []
    
    # Кнопка "Предыдущая страница", если не на первой странице
    if page > 0:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"page_{page-1}"
            )
        )
    
    # Информация о текущей странице
    pagination_buttons.append(
        InlineKeyboardButton(
            text=f"📄 {page+1}/{(len(products) + items_per_page - 1) // items_per_page}",
            callback_data="current_page"
        )
    )
    
    # Кнопка "Следующая страница", если не на последней странице
    if end_idx < len(products):
        pagination_buttons.append(
            InlineKeyboardButton(
                text="Вперёд ▶️",
                callback_data=f"page_{page+1}"
            )
        )
    
    # Добавляем кнопки пагинации, если есть больше одной страницы
    if len(products) > items_per_page:
        builder.row(*pagination_buttons)
    
    # Кнопка фильтрации и возврата в меню
    bottom_row = []
    
    if with_filter:
        bottom_row.append(
            InlineKeyboardButton(
                text="🔍 Фильтры",
                callback_data="filter_products"
            )
        )
    
    bottom_row.append(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="main_menu"
        )
    )
    
    builder.row(*bottom_row)
    
    return builder.as_markup()

def filter_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для меню фильтрации товаров.
    
    Returns:
        InlineKeyboardMarkup с опциями фильтрации
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопки фильтрации
    builder.row(
        InlineKeyboardButton(
            text="🧱 Материал",
            callback_data=FilterCallback(action="material").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📋 Тип товара",
            callback_data=FilterCallback(action="type").pack()
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="💰 Цена",
            callback_data=FilterCallback(action="price").pack()
        )
    )
    
    # Кнопки применения и сброса фильтров
    builder.row(
        InlineKeyboardButton(
            text="✅ Применить",
            callback_data=FilterCallback(action="apply").pack()
        ),
        InlineKeyboardButton(
            text="❌ Сбросить",
            callback_data=FilterCallback(action="reset").pack()
        )
    )
    
    # Кнопка возврата в каталог
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад в каталог",
            callback_data="main_menu"
        )
    )
    
    return builder.as_markup()

def build_materials_keyboard(materials: list) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора материала товара.
    
    Args:
        materials: Список доступных материалов
        
    Returns:
        InlineKeyboardMarkup с кнопками для каждого материала
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопку для каждого материала
    for material in materials:
        builder.row(
            InlineKeyboardButton(
                text=material,
                callback_data=material
            )
        )
    
    # Кнопка возврата в меню фильтров
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="back_to_filter"
        )
    )
    
    return builder.as_markup()

def build_types_keyboard(types: list) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора типа товара.
    
    Args:
        types: Список доступных типов товаров
        
    Returns:
        InlineKeyboardMarkup с кнопками для каждого типа
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопку для каждого типа
    for product_type in types:
        builder.row(
            InlineKeyboardButton(
                text=product_type,
                callback_data=product_type
            )
        )
    
    # Кнопка возврата в меню фильтров
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="back_to_filter"
        )
    )
    
    return builder.as_markup()

def build_price_range_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора ценового диапазона.
    
    Returns:
        InlineKeyboardMarkup с предустановленными ценовыми диапазонами
    """
    builder = InlineKeyboardBuilder()
    
    # Предустановленные ценовые диапазоны
    price_ranges = [
        ("До 5000₽", "0_5000"),
        ("5000₽ - 10000₽", "5000_10000"),
        ("10000₽ - 20000₽", "10000_20000"),
        ("20000₽ - 50000₽", "20000_50000"),
        ("Более 50000₽", "50000_any")
    ]
    
    # Добавляем кнопки для каждого ценового диапазона
    for label, value in price_ranges:
        builder.row(
            InlineKeyboardButton(
                text=label,
                callback_data=value
            )
        )
    
    # Кнопка возврата в меню фильтров
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="back_to_filter"
        )
    )
    
    return builder.as_markup()