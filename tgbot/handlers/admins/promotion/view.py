"""
Handlers for viewing promotions and promotion details
"""
import logging
import re
from aiogram import Router, F
from aiogram.types import CallbackQuery
from tgbot.keyboards.admin_promotion import (
    promotion_management_keyboard,
    promotion_list_keyboard,
)
from infrastructure.database.repositories.promotion_repo import PromotionRepo
from infrastructure.database.repositories.products import ProductsRepo
from .base import show_promotion_details

logger = logging.getLogger(__name__)

def register_view_handlers(router: Router):
    """
    Register all handlers related to viewing promotions
    """
    # Main promotion management menu
    router.callback_query.register(
        manage_promotions_menu, 
        F.data == "manage_promotions"
    )
    
    # View all promotions
    router.callback_query.register(
        view_promotions, 
        F.data == "view_promotions"
    )
    
    # View promotion details
    router.callback_query.register(
        view_promotion_details, 
        F.data.regexp(r"^promotion_(\d+)$")
    )

async def manage_promotions_menu(callback: CallbackQuery):
    """
    Shows the promotion management menu.
    """
    await callback.message.edit_text(
        "🏷️ *Управление акциями и скидками*\n\nВыберите действие:",
        reply_markup=promotion_management_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def view_promotions(callback: CallbackQuery, repo: PromotionRepo):
    """
    Shows the list of all promotions.
    """
    promotions = await repo.get_all_promotions()
    
    if promotions:
        await callback.message.edit_text(
            "Список доступных акций:",
            reply_markup=promotion_list_keyboard(promotions)
        )
    else:
        await callback.message.edit_text(
            "В системе пока нет акций.",
            reply_markup=promotion_management_keyboard()
        )
    
    await callback.answer()

async def view_promotion_details(callback: CallbackQuery, repo: PromotionRepo):
    """
    Shows detailed information about a specific promotion.
    """
    # Extract promotion ID from callback data
    match = re.match(r"^promotion_(\d+)$", callback.data)
    if not match:
        await callback.answer("Неверный формат данных", show_alert=True)
        return
    
    promo_id = int(match.group(1))
    await show_promotion_details(callback=callback, promo_id=promo_id, repo=repo)