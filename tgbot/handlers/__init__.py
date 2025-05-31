# tgbot/handlers/__init__.py

from tgbot.handlers.admins import admin_routers
from tgbot.handlers.users.user_menu import user_menu_router
from tgbot.handlers.users.user_products import user_products_router
from tgbot.handlers.users.user_orders import user_orders_router
from tgbot.handlers.users.user_faq import user_faq_router
from tgbot.handlers.users.user_feedback import user_feedback_router
from tgbot.handlers.users.user_favorites import user_favorites_router
from tgbot.handlers.error import error_router

# Список всех роутеров администратора
admin_router_list = admin_routers

# Список всех роутеров пользователя
user_router_list = [
    user_menu_router,       # Главное меню пользователя
    user_faq_router,        # Часто задаваемые вопросы
    user_products_router,   # Каталог товаров
    user_orders_router,     # Управление заказами
    user_feedback_router,   # Обратная связь
    user_favorites_router,  # Избранное
]

# Объединяем все роутеры в один список
routers_list = [
    *admin_router_list,     # Все роутеры администратора
    *user_router_list,      # Все роутеры пользователя
    error_router,           # Обработчик ошибок
]

__all__ = [
    "routers_list",
]