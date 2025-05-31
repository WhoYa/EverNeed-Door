# tgbot/handlers/admins/admin_statistics.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime, timedelta
from infrastructure.database.repositories.logs import LogsRepo
from infrastructure.database.repositories.products import ProductsRepo
from infrastructure.database.repositories.requests import RequestsRepo
from tgbot.keyboards.admin_main_menu import admin_back_button
from tgbot.filters.admin import AdminFilter

# Состояния для просмотра статистики
class StatsViewing(StatesGroup):
    select_period = State()  # Выбор периода просмотра
    select_log_filter = State()  # Выбор фильтра логов

admin_stats_router = Router()
admin_stats_router.message.filter(AdminFilter())
admin_stats_router.callback_query.filter(AdminFilter())

# Клавиатура для меню статистики
def stats_menu_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📊 Просмотр статистики товаров", callback_data="view_product_stats"),
        InlineKeyboardButton(text="📝 Просмотр логов пользователей", callback_data="view_user_logs"),
        InlineKeyboardButton(text="👤 Популярные товары", callback_data="popular_products"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main")
    )
    builder.adjust(1)
    return builder.as_markup()

# Клавиатура для выбора периода
def period_selection_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📅 За сегодня", callback_data="period_day"),
        InlineKeyboardButton(text="📅 За неделю", callback_data="period_week"),
        InlineKeyboardButton(text="📅 За месяц", callback_data="period_month"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="view_statistics")
    )
    builder.adjust(1)
    return builder.as_markup()

# Клавиатура для фильтрации логов
def log_filter_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🔍 Просмотры товаров", callback_data="log_view_product"),
        InlineKeyboardButton(text="❤️ Избранное", callback_data="log_favorite"),
        InlineKeyboardButton(text="🛒 Заказы", callback_data="log_order"),
        InlineKeyboardButton(text="⚙️ Все действия", callback_data="log_all"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="view_statistics")
    )
    builder.adjust(1)
    return builder.as_markup()

@admin_stats_router.callback_query(F.data == "view_statistics")
async def view_statistics_menu(callback: CallbackQuery):
    """
    Показывает меню статистики и логов.
    """
    await callback.message.edit_text(
        text="📊 <b>Статистика и логи</b>\n\n"
             "Выберите раздел для просмотра:",
        reply_markup=stats_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@admin_stats_router.callback_query(F.data == "view_product_stats")
async def view_product_stats(callback: CallbackQuery, state: FSMContext):
    """
    Запрашивает выбор периода для просмотра статистики товаров.
    """
    await state.set_state(StatsViewing.select_period)
    await state.update_data(stats_type="product")
    
    await callback.message.edit_text(
        text="📅 <b>Выберите период для просмотра статистики товаров:</b>",
        reply_markup=period_selection_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@admin_stats_router.callback_query(F.data == "view_user_logs")
async def view_user_logs(callback: CallbackQuery, state: FSMContext):
    """
    Запрашивает выбор фильтра для просмотра логов пользователей.
    """
    await state.set_state(StatsViewing.select_log_filter)
    
    await callback.message.edit_text(
        text="🔍 <b>Выберите тип действий для просмотра логов:</b>",
        reply_markup=log_filter_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@admin_stats_router.callback_query(F.data == "popular_products")
async def view_popular_products(callback: CallbackQuery, state: FSMContext):
    """
    Запрашивает выбор периода для просмотра популярных товаров.
    """
    await state.set_state(StatsViewing.select_period)
    await state.update_data(stats_type="popular")
    
    await callback.message.edit_text(
        text="📅 <b>Выберите период для просмотра популярных товаров:</b>",
        reply_markup=period_selection_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@admin_stats_router.callback_query(F.data.startswith("period_"))
async def process_period_selection(callback: CallbackQuery, state: FSMContext, request: RequestsRepo):
    """
    Обрабатывает выбор периода и показывает соответствующую статистику.
    """
    # Получаем данные о типе статистики
    user_data = await state.get_data()
    stats_type = user_data.get("stats_type", "product")
    
    # Определяем период
    period = callback.data.split("_")[1]
    now = datetime.now()
    
    if period == "day":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_name = "за сегодня"
    elif period == "week":
        start_date = now - timedelta(days=7)
        period_name = "за неделю"
    elif period == "month":
        start_date = now - timedelta(days=30)
        period_name = "за месяц"
    else:
        start_date = now - timedelta(days=7)  # По умолчанию неделя
        period_name = "за последнее время"
    
    # Формируем ответ в зависимости от типа статистики
    if stats_type == "product":
        # Здесь должна быть логика получения статистики товаров
        # Для примера формируем тестовую статистику
        product_stats = [
            {"name": "Дверь металлическая", "views": 45, "orders": 5},
            {"name": "Дверь деревянная", "views": 32, "orders": 3},
            {"name": "Ручка дверная", "views": 28, "orders": 8},
        ]
        
        # Формируем текст ответа
        text = f"📊 <b>Статистика товаров {period_name}</b>\n\n"
        for prod in product_stats:
            text += f"📦 <b>{prod['name']}</b>\n"
            text += f"👁 Просмотры: {prod['views']}\n"
            text += f"🛒 Заказы: {prod['orders']}\n\n"
        
    elif stats_type == "popular":
        # Логика получения популярных товаров
        logs_repo = request.logs
        products_repo = request.products
        
        # Получаем популярные товары по логам
        popular_products = await logs_repo.get_popular_products(
            days=30 if period == "month" else (7 if period == "week" else 1)
        )
        
        text = f"🔝 <b>Популярные товары {period_name}</b>\n\n"
        
        if popular_products:
            for idx, prod_data in enumerate(popular_products[:5], 1):
                product = await products_repo.get_product_by_id(prod_data["product_id"])
                if product:
                    text += f"{idx}. <b>{product.name}</b>\n"
                    text += f"👁 Просмотры: {prod_data['views']}\n\n"
        else:
            text += "Нет данных о популярных товарах за выбранный период."
    
    else:
        text = "Неизвестный тип статистики."
    
    # Сбрасываем состояние и отправляем ответ
    await state.clear()
    
    await callback.message.edit_text(
        text=text,
        reply_markup=admin_back_button("view_statistics"),
        parse_mode="HTML"
    )
    await callback.answer()

@admin_stats_router.callback_query(F.data.startswith("log_"))
async def process_log_filter(callback: CallbackQuery, state: FSMContext, request: RequestsRepo):
    """
    Обрабатывает выбор фильтра логов и показывает соответствующие логи.
    """
    # Определяем тип логов
    log_type = callback.data.split("_")[1]
    
    # Получаем логи из репозитория
    logs_repo = request.logs
    
    # Фильтруем логи по типу
    if log_type == "all":
        logs = await logs_repo.get_logs_by_date_range(
            datetime.now() - timedelta(days=7),
            datetime.now(),
            limit=20
        )
        filter_name = "всех действий"
    elif log_type == "view_product":
        logs = await logs_repo.get_logs_by_action("view_product", limit=20)
        filter_name = "просмотров товаров"
    elif log_type == "favorite":
        logs = await logs_repo.get_logs_by_action("add_favorite", limit=20)
        filter_name = "добавлений в избранное"
    elif log_type == "order":
        logs = await logs_repo.get_logs_by_action("create_order", limit=20)
        filter_name = "заказов"
    else:
        logs = []
        filter_name = "неизвестных действий"
    
    # Формируем текст ответа
    text = f"📝 <b>Логи {filter_name}</b>\n\n"
    
    if logs:
        for log in logs:
            # Форматируем дату
            date_str = log.timestamp.strftime("%d.%m.%Y %H:%M")
            text += f"👤 <b>Пользователь ID {log.user_id}</b>\n"
            text += f"🕒 {date_str}\n"
            text += f"🔹 Действие: {log.action}\n"
            if log.details:
                text += f"📄 Детали: {log.details}\n"
            text += "\n"
    else:
        text += "Нет логов за выбранный период."
    
    # Сбрасываем состояние и отправляем ответ
    await state.clear()
    
    # Если текст слишком длинный, обрезаем его
    if len(text) > 4000:
        text = text[:3997] + "..."
    
    await callback.message.edit_text(
        text=text,
        reply_markup=admin_back_button("view_statistics"),
        parse_mode="HTML"
    )
    await callback.answer()