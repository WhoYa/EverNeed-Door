"""
Admin handlers router configuration
"""
from aiogram import Router
from .admin import admin_router
from .admin_orders import admin_orders_router
from .admin_product_management import admin_product_router
from .admin_auth import admin_auth_router
from .admin_statistics import admin_stats_router
from .admin_subscriptions import admin_subscription_router  # Fixed singular/plural mismatch
from .promotion import promotion_router, register_promotion_handlers

# Initialize and configure all admin-related routers
admin_routers = [
    admin_router,                   # Main admin router
    admin_orders_router,            # Order management
    admin_product_router,           # Product management
    admin_auth_router,              # Admin authentication
    admin_stats_router,             # Statistics and logs
    admin_subscription_router,      # Subscription management (fixed name)
    register_promotion_handlers(),  # Promotion management
]