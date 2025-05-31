# tgbot/keyboards/admin_stats.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def stats_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура меню статистики.
    """
    builder = InlineKeyboardBuilder()
    
    # Статистика товаров
    builder.row(
        InlineKeyboardButton(
            text="📊 Статистика товаров",
            callback_data="product_stats"
        )
    )
    
    # Логи администраторов
    builder.row(
        InlineKeyboardButton(
            text="📋 Логи администраторов",
            callback_data="admin_logs"
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

def period_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора периода для статистики.
    """
    builder = InlineKeyboardBuilder()
    
    # Периоды
    builder.row(
        InlineKeyboardButton(
            text="📅 За сегодня",
            callback_data="period_day"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📅 За неделю",
            callback_data="period_week"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📅 За месяц",
            callback_data="period_month"
        )
    )
    
    # Кнопка назад
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="view_statistics"
        )
    )
    
    return builder.as_markup()

def log_filter_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура фильтров для логов.
    """
    builder = InlineKeyboardBuilder()
    
    # Фильтры
    builder.row(
        InlineKeyboardButton(
            text="📋 Все действия",
            callback_data="log_filter_all"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📦 Действия с товарами",
            callback_data="log_filter_products"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🏷️ Действия с акциями",
            callback_data="log_filter_promotions"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🕒 За последние 24 часа",
            callback_data="log_filter_recent"
        )
    )
    
    # Кнопка назад
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="view_statistics"
        )
    )
    
    return builder.as_markup()

def admin_back_button(callback_data: str) -> InlineKeyboardMarkup:
    """
    Кнопка назад для меню статистики.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=callback_data
        )
    )
    return builder.as_markup()