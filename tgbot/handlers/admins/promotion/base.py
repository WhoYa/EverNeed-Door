"""
Base module for promotion management - contains shared states, router, and utility functions
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime
from infrastructure.database.models.promotions import DiscountType
from infrastructure.database.repositories.promotion_repo import PromotionRepo

# Set up logging
logger = logging.getLogger(__name__)

# Create router
admin_promotion_router = Router()

# Shared state classes
class PromotionManagement(StatesGroup):
    # Create promotion states
    add_name = State()
    add_description = State()
    add_discount_type = State()
    add_discount_value = State()
    add_start_date = State()
    add_end_date = State()
    add_select_products = State()
    add_confirm = State()
    
    # Edit promotion states
    edit_select_promotion = State()
    edit_select_field = State()
    edit_name = State()
    edit_description = State()
    edit_discount_type = State()
    edit_discount_value = State()
    edit_start_date = State()
    edit_end_date = State()
    edit_is_active = State()
    
    # Manage products states
    manage_products = State()
    
    # Delete promotion states
    delete_confirm = State()

# Shared utility functions
async def show_promotion_details(callback: CallbackQuery = None, message: Message = None, 
                                promo_id: int = None, promotion = None, repo: PromotionRepo = None):
    """
    Displays promotion details in a formatted message.
    This utility function is used by multiple promotion handlers.
    
    Args:
        callback: Optional callback query for edit_text responses
        message: Optional message for answer responses
        promo_id: ID of the promotion to display
        promotion: Optional pre-fetched promotion object
        repo: Promotion repository for database access
    """
    from tgbot.keyboards.admin_promotion import promotion_edit_keyboard, promotion_management_keyboard
    
    # If promotion object not provided, fetch it
    if not promotion and promo_id:
        promotion = await repo.get_promotion_by_id(promo_id)
    
    if not promotion:
        text = "❌ Акция не найдена"
        reply_markup = promotion_management_keyboard()
    else:
        # Format dates
        start_date = promotion.start_date.strftime("%d-%m-%Y") if promotion.start_date else "Не указана"
        end_date = promotion.end_date.strftime("%d-%m-%Y") if promotion.end_date else "Бессрочно"
        
        # Determine discount type
        discount_type = "Процентная" if promotion.discount_type == DiscountType.PERCENTAGE.value else "Фиксированная"
        discount_value = f"{promotion.discount_value}%" if promotion.discount_type == DiscountType.PERCENTAGE.value else f"{promotion.discount_value}₽"
        
        # Format promotion information text
        text = (
            f"🏷️ *Акция: {promotion.name}*\n"
            f"📝 Описание: {promotion.description}\n"
            f"💰 Скидка: {discount_type}, {discount_value}\n"
            f"📅 Период: с {start_date} по {end_date}\n"
            f"Статус: {'✅ Активна' if promotion.is_active else '❌ Неактивна'}\n\n"
        )
        
        # Get and add products in promotion
        promoted_products = await repo.get_promotion_products(promo_id)
        
        text += "📦 *Товары в акции:*\n"
        if promoted_products:
            for i, product in enumerate(promoted_products[:5], 1):
                text += f"{i}. {product.name} - {product.price}₽\n"
            
            if len(promoted_products) > 5:
                text += f"... и еще {len(promoted_products) - 5} товаров\n"
        else:
            text += "Нет товаров в акции.\n"
        
        reply_markup = promotion_edit_keyboard(promo_id)
    
    # Send or edit message based on context
    if callback:
        await callback.message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    elif message:
        await message.answer(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )