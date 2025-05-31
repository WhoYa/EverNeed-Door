# tgbot/keyboards/admin_promotion.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional
from infrastructure.database.models.products import Product

def promotion_management_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для управления акциями.
    """
    builder = InlineKeyboardBuilder()
    
    # Добавление акции
    builder.row(
        InlineKeyboardButton(
            text="➕ Добавить акцию",
            callback_data="add_promotion"
        )
    )
    
    # Просмотр акций
    builder.row(
        InlineKeyboardButton(
            text="📋 Просмотр акций",
            callback_data="view_promotions"
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

def promotion_list_keyboard(promotions: List) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком акций.
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопку для каждой акции
    for promo in promotions:
        builder.row(
            InlineKeyboardButton(
                text=f"{promo.name} {'✅' if promo.is_active else '❌'}",
                callback_data=f"promotion_{promo.promo_id}"
            )
        )
    
    # Кнопка назад
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="manage_promotions"
        )
    )
    
    return builder.as_markup()

def promotion_edit_keyboard(promo_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для редактирования акции.
    """
    builder = InlineKeyboardBuilder()
    
    # Редактирование полей акции
    builder.row(
        InlineKeyboardButton(
            text="✏️ Редактировать акцию",
            callback_data=f"edit_promotion_{promo_id}"
        )
    )
    
    # Управление товарами в акции
    builder.row(
        InlineKeyboardButton(
            text="📦 Управление товарами",
            callback_data=f"manage_promo_products_{promo_id}"
        )
    )
    
    # Деактивация/активация акции
    builder.row(
        InlineKeyboardButton(
            text="🔄 Изменить статус",
            callback_data=f"toggle_promo_status_{promo_id}"
        )
    )
    
    # Удаление акции
    builder.row(
        InlineKeyboardButton(
            text="🗑️ Удалить акцию",
            callback_data=f"delete_promotion_{promo_id}"
        )
    )
    
    # Кнопка назад
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к списку",
            callback_data="view_promotions"
        )
    )
    
    return builder.as_markup()

def product_selection_keyboard(products: List[Product], selected_products: Optional[List[int]] = None) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора товаров при создании акции.
    """
    builder = InlineKeyboardBuilder()
    
    if selected_products is None:
        selected_products = []
    
    # Добавляем кнопку для каждого товара
    for product in products:
        # Отмечаем выбранные товары
        mark = "✅ " if product.product_id in selected_products else ""
        builder.row(
            InlineKeyboardButton(
                text=f"{mark}{product.name} ({product.price}₽)",
                callback_data=f"select_product_{product.product_id}"
            )
        )
    
    # Кнопки для подтверждения выбора и отмены
    builder.row(
        InlineKeyboardButton(
            text="✅ Подтвердить выбор",
            callback_data="confirm_product_selection"
        ),
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="manage_promotions"
        )
    )
    
    return builder.as_markup()

def admin_back_button(callback_data: str) -> InlineKeyboardMarkup:
    """
    Кнопка назад для меню акций.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=callback_data
        )
    )
    return builder.as_markup()