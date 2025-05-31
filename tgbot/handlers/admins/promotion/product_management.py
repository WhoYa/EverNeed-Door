"""
Handlers for managing products in promotions
"""
import logging
import re
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from infrastructure.database.repositories.promotion_repo import PromotionRepo
from infrastructure.database.repositories.products import ProductsRepo
from tgbot.keyboards.admin_promotion import product_selection_keyboard
from .base import PromotionManagement, show_promotion_details

logger = logging.getLogger(__name__)

def register_product_handlers(router: Router):
    """
    Register all handlers related to managing products in promotions
    """
    # Start product management
    router.callback_query.register(
        manage_promotion_products,
        F.data.regexp(r"^manage_promo_products_(\d+)$")
    )
    
    # Toggle product selection
    router.callback_query.register(
        toggle_product_selection,
        PromotionManagement.manage_products, 
        F.data.regexp(r"^select_product_(\d+)$")
    )
    
    # Confirm product selection
    router.callback_query.register(
        confirm_product_selection,
        PromotionManagement.manage_products, 
        F.data == "confirm_product_selection"
    )

async def manage_promotion_products(callback: CallbackQuery, state: FSMContext, repo: PromotionRepo, product_repo: ProductsRepo):
    """
    Displays interface for managing products in a promotion.
    """
    promo_id = int(callback.data.split('_')[-1])
    
    # Get promotion details
    promotion = await repo.get_promotion_by_id(promo_id)
    if not promotion:
        await callback.answer("Акция не найдена", show_alert=True)
        return
    
    # Get all available products
    all_products = await product_repo.get_all_products()
    
    # Get products currently in the promotion
    promoted_products = await repo.get_promotion_products(promo_id)
    selected_product_ids = [p.product_id for p in promoted_products]
    
    # Save data in state
    await state.update_data(promo_id=promo_id, selected_products=selected_product_ids)
    await state.set_state(PromotionManagement.manage_products)
    
    await callback.message.edit_text(
        f"Управление товарами для акции '{promotion.name}'\n\n"
        "Выберите товары, которые должны участвовать в акции:",
        reply_markup=product_selection_keyboard(all_products, selected_product_ids)
    )
    await callback.answer()

async def toggle_product_selection(callback: CallbackQuery, state: FSMContext, product_repo: ProductsRepo):
    """
    Toggles selection of a product for the promotion.
    """
    product_id = int(callback.data.split('_')[-1])
    
    # Get current selected products from state
    data = await state.get_data()
    promo_id = data.get("promo_id")
    selected_products = data.get("selected_products", [])
    
    # Toggle product selection (add/remove)
    if product_id in selected_products:
        selected_products.remove(product_id)
    else:
        selected_products.append(product_id)
    
    # Update state data
    await state.update_data(selected_products=selected_products)
    
    # Get all products for updating keyboard
    all_products = await product_repo.get_all_products()
    
    # Update message with new keyboard
    await callback.message.edit_text(
        f"Управление товарами для акции (ID: {promo_id})\n\n"
        "Выберите товары, которые должны участвовать в акции:",
        reply_markup=product_selection_keyboard(all_products, selected_products)
    )
    await callback.answer()

async def confirm_product_selection(callback: CallbackQuery, state: FSMContext, repo: PromotionRepo):
    """
    Confirms the selection of products for the promotion.
    """
    # Get data from state
    data = await state.get_data()
    promo_id = data.get("promo_id")
    selected_products = data.get("selected_products", [])
    
    # Update products in promotion
    try:
        updated = await repo.update_promotion_products(promo_id, selected_products)
        if updated:
            await callback.answer("✅ Список товаров в акции обновлен", show_alert=True)
        else:
            await callback.answer("❌ Не удалось обновить список товаров", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
    
    # Clear state
    await state.clear()
    
    # Show updated promotion details
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(callback=callback, promo_id=promo_id, promotion=promotion, repo=repo)