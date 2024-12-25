# tgbot/misc/states.py

from aiogram.fsm.state import StatesGroup, State

# Состояния для управления товарами
class ProductManagement(StatesGroup):
    name = State()
    description = State()
    type = State()
    material = State()
    price = State()
    image_url = State()
    confirm = State()

# Состояния для работы с заказами
class OrderManagement(StatesGroup):
    viewing = State()  # Просмотр заказов
    updating_status = State()  # Обновление статуса заказа
    confirming_cancellation = State()  # Подтверждение отмены заказа

# Состояния для работы с пользователями
class UserInteraction(StatesGroup):
    browsing_catalog = State()  # Просмотр каталога
    viewing_order_details = State()  # Просмотр деталей заказа
    confirming_purchase = State()  # Подтверждение покупки

# Состояния для уведомлений
class NotificationManagement(StatesGroup):
    creating_notification = State()
    editing_notification = State()
    sending_notification = State()

# Состояния для обратной связи
class FeedbackStates(StatesGroup):
    waiting_for_feedback = State()  # Ожидание ввода отзыва

# Состояния для избранного
class FavoritesStates(StatesGroup):
    viewing_favorites = State()  # Просмотр избранных товаров
    adding_favorite = State()  # Добавление товара в избранное
    removing_favorite = State()  # Удаление товара из избранного
