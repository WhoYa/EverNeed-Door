# tgbot/handlers/admins/admin_subscriptions.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from infrastructure.database.repositories.requests import RequestsRepo
from infrastructure.database.repositories.users import UsersRepo
from infrastructure.database.repositories.logs import LogsRepo
from infrastructure.database.repositories.notifications import NotificationsRepo
from tgbot.keyboards.admin_main_menu import admin_back_button
from tgbot.filters.admin import AdminFilter

# Состояния для управления подписками и уведомлениями
class SubscriptionManagement(StatesGroup):
    select_notification_type = State()  # Выбор типа рассылки
    enter_notification_text = State()   # Ввод текста уведомления
    confirm_notification = State()      # Подтверждение отправки
    view_subscribers = State()          # Просмотр списка подписчиков

admin_subscription_router = Router()
admin_subscription_router.message.filter(AdminFilter())
admin_subscription_router.callback_query.filter(AdminFilter())

# Клавиатура для меню управления подписками
def subscription_management_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📩 Отправить уведомление", callback_data="send_notification"),
        InlineKeyboardButton(text="👥 Список подписчиков", callback_data="list_subscribers"),
        InlineKeyboardButton(text="📊 Статистика подписок", callback_data="subscription_stats"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main")
    )
    builder.adjust(1)
    return builder.as_markup()

# Клавиатура для выбора типа уведомления
def notification_type_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📣 Всем пользователям", callback_data="notify_all"),
        InlineKeyboardButton(text="🛍️ Подписчикам на товары", callback_data="notify_products"),
        InlineKeyboardButton(text="🏷️ Подписчикам на акции", callback_data="notify_promotions"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="manage_subscriptions")
    )
    builder.adjust(1)
    return builder.as_markup()

# Обработчик кнопки "Управление подписками"
@admin_subscription_router.callback_query(F.data == "manage_subscriptions")
async def manage_subscriptions_menu(callback: CallbackQuery):
    """
    Показывает меню управления подписками.
    """
    await callback.message.edit_text(
        text="🔔 <b>Управление подписками</b>\n\n"
             "Выберите действие:",
        reply_markup=subscription_management_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

# Обработчик кнопки "Отправить уведомление"
@admin_subscription_router.callback_query(F.data == "send_notification")
async def send_notification_callback(callback: CallbackQuery, state: FSMContext):
    """
    Начинает процесс отправки уведомления.
    """
    await state.set_state(SubscriptionManagement.select_notification_type)
    
    await callback.message.edit_text(
        text="📩 <b>Отправка уведомления</b>\n\n"
             "Выберите тип уведомления:",
        reply_markup=notification_type_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

# Обработчик выбора типа уведомления
@admin_subscription_router.callback_query(SubscriptionManagement.select_notification_type, F.data.startswith("notify_"))
async def process_notification_type(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает выбор типа уведомления и запрашивает ввод текста.
    """
    notification_type = callback.data.split("_")[1]
    
    # Сохраняем тип уведомления в состоянии
    await state.update_data(notification_type=notification_type)
    
    # Запрашиваем текст уведомления
    await state.set_state(SubscriptionManagement.enter_notification_text)
    
    type_description = {
        "all": "всем пользователям",
        "products": "подписчикам на товары",
        "promotions": "подписчикам на акции"
    }.get(notification_type, "выбранным пользователям")
    
    await callback.message.edit_text(
        text=f"📝 <b>Введите текст уведомления для отправки {type_description}:</b>\n\n"
             f"Сообщение будет отправлено от имени бота.",
        reply_markup=admin_back_button("send_notification"),
        parse_mode="HTML"
    )
    await callback.answer()

# Обработчик ввода текста уведомления
@admin_subscription_router.message(SubscriptionManagement.enter_notification_text)
async def process_notification_text(message: Message, state: FSMContext):
    """
    Обрабатывает ввод текста уведомления и запрашивает подтверждение.
    """
    notification_text = message.text.strip()
    
    if not notification_text:
        await message.answer(
            text="⚠️ Текст уведомления не может быть пустым. Пожалуйста, введите текст:"
        )
        return
    
    # Сохраняем текст уведомления в состоянии
    await state.update_data(notification_text=notification_text)
    
    # Получаем тип уведомления из состояния
    user_data = await state.get_data()
    notification_type = user_data.get("notification_type")
    
    type_description = {
        "all": "всем пользователям",
        "products": "подписчикам на товары",
        "promotions": "подписчикам на акции"
    }.get(notification_type, "выбранным пользователям")
    
    # Запрашиваем подтверждение
    await state.set_state(SubscriptionManagement.confirm_notification)
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    # Клавиатура для подтверждения
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✅ Да, отправить", callback_data="confirm_send"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="manage_subscriptions")
    )
    builder.adjust(1)
    
    await message.answer(
        text=f"📩 <b>Подтверждение отправки</b>\n\n"
             f"Тип: отправка {type_description}\n"
             f"Текст уведомления:\n\n"
             f"{notification_text}\n\n"
             f"Подтвердите отправку:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

# Обработчик подтверждения отправки уведомления
@admin_subscription_router.callback_query(SubscriptionManagement.confirm_notification, F.data == "confirm_send")
async def confirm_send_notification(callback: CallbackQuery, state: FSMContext, request: RequestsRepo):
    """
    Обрабатывает подтверждение отправки уведомления.
    """
    # Получаем данные из состояния
    user_data = await state.get_data()
    notification_type = user_data.get("notification_type")
    notification_text = user_data.get("notification_text")
    
    # Получаем репозитории
    users_repo = request.users
    notifications_repo = request.notifications
    logs_repo = request.logs
    
    # В зависимости от типа уведомления, получаем список пользователей
    if notification_type == "all":
        # Отправляем всем пользователям
        from sqlalchemy import select
        from infrastructure.database.models.users import User
        
        stmt = select(User.user_id).where(User.active == True)
        result = await users_repo.session.execute(stmt)
        user_ids = [row[0] for row in result]
        
        recipient_description = "всем пользователям"
    elif notification_type == "products":
        # Отправляем подписчикам на товары
        # В реальном проекте здесь должна быть логика получения подписчиков на товары
        user_ids = []  # Заглушка, в реальности должны быть ID пользователей
        recipient_description = "подписчикам на товары"
    elif notification_type == "promotions":
        # Отправляем подписчикам на акции
        # В реальном проекте здесь должна быть логика получения подписчиков на акции
        user_ids = []  # Заглушка, в реальности должны быть ID пользователей
        recipient_description = "подписчикам на акции"
    else:
        user_ids = []
        recipient_description = "никому (неизвестный тип)"
    
    # Отправляем уведомления
    sent_count = 0
    for user_id in user_ids:
        try:
            await notifications_repo.create_notification(
                user_id=user_id,
                notification_data={
                    "type": "admin_notification",
                    "message": notification_text
                }
            )
            sent_count += 1
        except Exception as e:
            # Логируем ошибку, но продолжаем отправку другим пользователям
            await logs_repo.create_log(
                user_id=callback.from_user.id,
                action="notification_error",
                details=f"Ошибка при отправке уведомления пользователю {user_id}: {str(e)}"
            )
    
    # Логируем действие
    await logs_repo.create_log(
        user_id=callback.from_user.id,
        action="send_notification",
        details=f"Отправлено уведомление {recipient_description}. Отправлено: {sent_count}"
    )
    
    # Сбрасываем состояние и отправляем ответ
    await state.clear()
    
    await callback.message.edit_text(
        text=f"✅ <b>Уведомление отправлено!</b>\n\n"
             f"Тип: {recipient_description}\n"
             f"Отправлено: {sent_count} пользователям\n\n"
             f"Текст уведомления:\n{notification_text}",
        reply_markup=admin_back_button("manage_subscriptions"),
        parse_mode="HTML"
    )
    await callback.answer()

# Обработчик кнопки "Список подписчиков"
@admin_subscription_router.callback_query(F.data == "list_subscribers")
async def list_subscribers_callback(callback: CallbackQuery, request: RequestsRepo):
    """
    Показывает список подписчиков на разные типы уведомлений.
    """
    # Получаем репозиторий пользователей
    users_repo = request.users
    
    # В реальном проекте здесь должна быть логика получения статистики по подпискам
    # Для примера формируем тестовую статистику
    subscriber_stats = {
        "all": 42,  # Всего пользователей
        "products": 28,  # Подписчики на товары
        "promotions": 35  # Подписчики на акции
    }
    
    text = "👥 <b>Статистика подписок</b>\n\n"
    text += f"Всего пользователей: {subscriber_stats['all']}\n"
    text += f"Подписаны на новые товары: {subscriber_stats['products']}\n"
    text += f"Подписаны на акции: {subscriber_stats['promotions']}\n\n"
    
    # Получаем список последних 5 активных пользователей для примера
    from sqlalchemy import select, desc
    from infrastructure.database.models.users import User
    
    stmt = select(User).where(User.active == True).order_by(desc(User.created_at)).limit(5)
    result = await users_repo.session.execute(stmt)
    recent_users = list(result.scalars().all())
    
    if recent_users:
        text += "<b>Недавно активные пользователи:</b>\n\n"
        for user in recent_users:
            text += f"ID: {user.user_id}\n"
            text += f"Имя: {user.first_name or 'Не указано'} {user.last_name or ''}\n"
            text += f"Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}\n\n"
    
    await callback.message.edit_text(
        text=text,
        reply_markup=admin_back_button("manage_subscriptions"),
        parse_mode="HTML"
    )
    await callback.answer()

# Обработчик кнопки "Статистика подписок"
@admin_subscription_router.callback_query(F.data == "subscription_stats")
async def subscription_stats_callback(callback: CallbackQuery):
    """
    Показывает статистику по подпискам.
    """
    # В реальном проекте здесь должна быть логика получения детальной статистики
    # Для примера формируем тестовую статистику
    stats = {
        "total_notifications": 156,  # Всего отправлено уведомлений
        "read_rate": 78,  # Процент прочтения
        "unsubscribe_rate": 5,  # Процент отписок
        "most_popular": "Новые товары"  # Самый популярный тип подписки
    }
    
    text = "📊 <b>Статистика уведомлений</b>\n\n"
    text += f"Всего отправлено: {stats['total_notifications']}\n"
    text += f"Процент прочтения: {stats['read_rate']}%\n"
    text += f"Процент отписок: {stats['unsubscribe_rate']}%\n"
    text += f"Самый популярный тип подписки: {stats['most_popular']}\n\n"
    
    text += "<b>Советы по улучшению:</b>\n"
    text += "• Отправляйте уведомления в рабочее время\n"
    text += "• Персонализируйте сообщения\n"
    text += "• Не отправляйте слишком много уведомлений\n"
    
    await callback.message.edit_text(
        text=text,
        reply_markup=admin_back_button("manage_subscriptions"),
        parse_mode="HTML"
    )
    await callback.answer()