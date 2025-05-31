"""
Promotion management module - handles all promotion-related admin functions
"""
from aiogram import Router
from tgbot.filters.admin import AdminFilter
from .base import admin_promotion_router
from .create import register_create_handlers
from .view import register_view_handlers
from .edit import register_edit_handlers
from .product_management import register_product_handlers

# Create main router for all promotion-related functionality
promotion_router = Router()
promotion_router.callback_query.filter(AdminFilter())
promotion_router.message.filter(AdminFilter())

# Register all promotion-related handlers
def register_promotion_handlers():
    """
    Registers all promotion-related handlers with the main promotion router
    """
    register_create_handlers(admin_promotion_router)
    register_view_handlers(admin_promotion_router)
    register_edit_handlers(admin_promotion_router)
    register_product_handlers(admin_promotion_router)
    
    # Include the admin_promotion_router in the main promotion router
    promotion_router.include_router(admin_promotion_router)
    
    return promotion_router