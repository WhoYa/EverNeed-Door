# tgbot/keyboards/admin_subscription.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from infrastructure.database.models.subscriptions import SubscriptionType

def subscription_management_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для управления подписками.
    """
    builder = InlineKeyboardBuilder()
    
    # Просмотр подписчиков
    builder.row(
        InlineKeyboardButton(
            text="👥 Просмотр подписчиков",
            callback_data="view_subscribers"
        )
    )
    
    # Отправка уведомления
    builder.row(
        InlineKeyboardButton(
            text="📨 Отправить уведомление",
            callback_data="send_notification"
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

def subscription_type_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора типа подписки для уведомления.
    """
    builder = InlineKeyboardBuilder()
    
    # Типы подписок
    builder.row(
        InlineKeyboardButton(
            text="📢 Всем подписчикам",
            callback_data=f"notification_type_{SubscriptionType.ALL.value}"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📦 Подписчикам на новые товары",
            callback_data=f"notification_type_{SubscriptionType.NEW_PRODUCTS.value}"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🏷️ Подписчикам на акции",
            callback_data=f"notification_type_{SubscriptionType.PROMOTIONS.value}"
        )
    )
    
    # Кнопка назад
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="manage_subscriptions"
        )
    )
    
    return builder.as_markup()

def admin_back_button(callback_data: str) -> InlineKeyboardMarkup:
    """
    Кнопка назад для меню подписок.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=callback_data
        )
    )
    return builder.as_markup()