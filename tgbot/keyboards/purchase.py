from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from tgbot.misc.callback_factory import PurchaseCallback, FavoriteActionCallback


def purchase_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для покупки товара.
    
    Args:
        product_id: ID товара
        
    Returns:
        InlineKeyboardMarkup с кнопками покупки и добавления в избранное
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопка покупки
    builder.row(
        InlineKeyboardButton(
            text="💳 Купить",
            callback_data=PurchaseCallback(product_id=product_id, action="buy").pack()
        )
    )
    
    # Кнопка добавления в избранное
    builder.row(
        InlineKeyboardButton(
            text="⭐ В избранное",
            callback_data=FavoriteActionCallback(action="add", product_id=product_id).pack()
        )
    )
    
    # Кнопка назад к каталогу
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к каталогу",
            callback_data="back_to_catalog"
        )
    )
    
    return builder.as_markup()

def purchase_keyboard_from_favorites(product_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для покупки товара из избранного.
    
    Args:
        product_id: ID товара
        
    Returns:
        InlineKeyboardMarkup с кнопками покупки и возврата к избранному
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопка покупки
    builder.row(
        InlineKeyboardButton(
            text="💳 Купить",
            callback_data=PurchaseCallback(product_id=product_id, action="buy").pack()
        )
    )
    
    # Кнопка добавления в избранное - здесь уже в избранном, поэтому удаление
    builder.row(
        InlineKeyboardButton(
            text="⭐ Удалить из избранного",
            callback_data=FavoriteActionCallback(action="remove", product_id=product_id).pack()
        )
    )
    
    # Кнопка назад к избранному
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к избранному",
            callback_data="view_favorites"
        )
    )
    
    return builder.as_markup()

def confirm_purchase_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для подтверждения покупки.
    
    Args:
        product_id: ID товара
        
    Returns:
        InlineKeyboardMarkup с кнопками подтверждения и отмены
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопка подтверждения
    builder.row(
        InlineKeyboardButton(
            text="✅ Подтвердить заказ",
            callback_data=PurchaseCallback(product_id=product_id, action="confirm").pack()
        )
    )
    
    # Кнопка отмены
    builder.row(
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data=PurchaseCallback(product_id=product_id, action="cancel").pack()
        )
    )
    
    return builder.as_markup()
