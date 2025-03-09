# tgbot/handlers/users/__init__.py

from tgbot.handlers.admins.admin import admin_router
from tgbot.handlers.admins.admin_product_management import admin_product_router
from tgbot.handlers.admins.admin_orders import admin_orders_router
from tgbot.handlers.users.user_menu import user_menu_router
from tgbot.handlers.users.user_products import user_products_router
from tgbot.handlers.users.user_orders import user_orders_router
from tgbot.handlers.users.user_faq import user_faq_router
from tgbot.handlers.users.user_feedback import user_feedback_router
from tgbot.handlers.users.user_favorites import user_favorites_router

routers_list = [
    admin_router,           # Главное меню для администратора
    admin_product_router,   # Управление товарами
    admin_orders_router,    # Управление заказами
    user_menu_router,       # Главное меню пользователя
    user_faq_router,        # Часто задаваемые вопросы
    user_products_router,   # Каталог товаров
    user_orders_router,     # Управление заказами
    user_feedback_router,   # Обратная связь
    user_favorites_router,  # Избранное
]

__all__ = [
    "routers_list",
]
