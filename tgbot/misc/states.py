# tgbot/misc/states.py

from aiogram.fsm.state import StatesGroup, State
from enum import Enum, auto

# Константы для названий полей в FSM данных
class ProductField(str, Enum):
    """
    Перечисление полей продукта, используемых в FSM.
    Используется для согласования имен полей между моделями и FSM.
    """
    NAME = "name"
    DESCRIPTION = "description"
    TYPE = "type"
    MATERIAL = "material"
    PRICE = "price"
    IMAGE_URL = "image_url"
    PREVIOUS_STATE = "previous_state"
    EDIT_FIELD = "edit_field"
    PRODUCT_ID = "product_id"

# Состояния для управления товарами
class ProductManagement(StatesGroup):
    """
    Состояния конечного автомата для управления товарами.
    Описывает этапы создания и редактирования товара.
    """
    name = State()  # Ввод названия товара
    description = State()  # Ввод описания товара
    type = State()  # Ввод типа товара
    material = State()  # Ввод материала товара
    price = State()  # Ввод цены товара
    image_url = State()  # Загрузка изображения товара
    confirm = State()  # Подтверждение добавления/изменения

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
    
# Состояния для фильтрации товаров
class FilterStates(StatesGroup):
    selecting_material = State()  # Выбор материала
    selecting_type = State()  # Выбор типа товара
    selecting_price = State()  # Выбор ценового диапазона
    applying_filters = State()  # Применение фильтров
