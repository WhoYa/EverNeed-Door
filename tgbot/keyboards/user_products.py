# tgbot/keyboards/user_products.py

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from tgbot.misc.callback_factory import ProductViewCallback, FavoriteActionCallback

def products_keyboard(products) -> InlineKeyboardMarkup:
    """
    Клавиатура для отображения списка товаров с опциями просмотра и добавления в избранное.
    
    :param products: Список объектов продуктов.
    :return: InlineKeyboardMarkup с кнопками для каждого продукта.
    """
    builder = InlineKeyboardBuilder()
    for product in products:
        # Кнопка для просмотра продукта
        view_button = InlineKeyboardButton(
            text="🔍 Просмотреть",
            callback_data=ProductViewCallback(product_id=product.product_id).pack()
        )
        
        # Кнопка для добавления в избранное
        favorite_button = InlineKeyboardButton(
            text="⭐ Добавить в избранное",
            callback_data=FavoriteActionCallback(action="add", product_id=product.product_id).pack()
        )
        
        # Добавляем кнопки в строку
        builder.row(view_button, favorite_button)
    
    # Опционально: Добавить кнопку "Назад" или другие навигационные кнопки
    back_button = InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="main_menu"
    )
    builder.row(back_button)
    
    return builder.as_markup()
