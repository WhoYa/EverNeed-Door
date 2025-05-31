# tgbot/handlers/admins/admin_orders.py
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from tgbot.keyboards.admin_main_menu import main_menu_keyboard
from tgbot.misc.states import OrderManagement
from tgbot.filters.admin import AdminFilter
from infrastructure.database.repositories.requests import RequestsRepo
from math import ceil
import re
import logging

admin_orders_router = Router()
admin_orders_router.callback_query.filter(AdminFilter())

def order_list_keyboard_paginated(orders, page: int = 1, page_size: int = 5) -> InlineKeyboardMarkup:
    """
    Создаём клавиатуру для списка заказов с пагинацией
    """
    builder = InlineKeyboardBuilder()
    
    total_orders = len(orders)
    total_pages = ceil(total_orders / page_size)
    
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    page_orders = orders[start_index:end_index]
    
    # Создаем кнопку для каждого заказа
    for order in page_orders:
        builder.button(
            text=f"Заказ #{order.order_id} - {order.status}",
            callback_data=f"order_{order.order_id}"
        )
    
    # Кнопки навигации
    nav_buttons = []
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="<< Назад",
                callback_data=f"view_orders_page_{page-1}"
            )
        )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Далее >>",
                callback_data=f"view_orders_page_{page+1}"
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)
    
    # Кнопка "Назад" для возврата в меню
    builder.button(
        text="Назад",
        callback_data="back_to_main_menu"
    )
    
    builder.adjust(1)
    return builder.as_markup()

def order_details_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для просмотра деталей заказа
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад к заказам", callback_data="view_orders")
    builder.adjust(1)
    return builder.as_markup()

# Обработчик кнопки просмотра заказов
@admin_orders_router.callback_query(F.data == "view_orders")
async def view_orders_handler(callback: CallbackQuery, repo: RequestsRepo):
    """Показать первую страницу со списком заказов."""
    # Просто отправляем новое сообщение вместо редактирования существующего
    # Это самый надежный способ избежать ошибки "message is not modified"
    
    orders = await repo.orders.get_all_orders()
    
    if not orders:
        # Даже здесь не редактируем, а отправляем новое сообщение
        await callback.message.delete()
        await callback.message.answer(
            "На данный момент заказы отсутствуют.",
            reply_markup=main_menu_keyboard()
        )
        return
    
    # Формируем текст 
    text_lines = ["Список заказов (стр. 1):\n"]
    for o in orders[:5]:  # только первые 5 для примера
        text_lines.append(f"- #{o.order_id}, пользователь: {o.user_id}, статус: {o.status}")
    text_output = "\n".join(text_lines)
    
    # Создаём клавиатуру для страницы 1
    keyboard = order_list_keyboard_paginated(orders, page=1, page_size=5)
    
    # Отправляем новое сообщение и удаляем старое
    await callback.message.delete()
    await callback.message.answer(text_output, reply_markup=keyboard)

# Обработчик пагинации для списка заказов
@admin_orders_router.callback_query(F.data.regexp(r"^view_orders_page_(\d+)$"))
async def view_orders_page_handler(callback: CallbackQuery, repo: RequestsRepo):
    """Обработка переключения страниц в списке заказов."""
    match = re.match(r"^view_orders_page_(\d+)$", callback.data)
    if not match:
        return
    
    page = int(match.group(1))
    orders = await repo.orders.get_all_orders()
    
    if not orders or page < 1:
        await callback.answer("Нет данных для отображения.", show_alert=True)
        return
    
    # Формируем текст
    text_lines = [f"Список заказов (стр. {page}):\n"]
    page_size = 5
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    for o in orders[start_index:end_index]:
        text_lines.append(f"- #{o.order_id}, пользователь: {o.user_id}, статус: {o.status}")
    text_output = "\n".join(text_lines)
    
    # Генерируем клавиатуру для указанной страницы
    keyboard = order_list_keyboard_paginated(orders, page=page, page_size=page_size)
    
    # Отправляем новое сообщение и удаляем старое
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer(text_output, reply_markup=keyboard)

# Обработчик для просмотра деталей заказа
@admin_orders_router.callback_query(F.data.regexp(r"^order_(\d+)$"))
async def view_order_details(callback: CallbackQuery, repo: RequestsRepo):
    """Показывает детальную информацию о заказе."""
    match = re.match(r"^order_(\d+)$", callback.data)
    if not match:
        return
    
    order_id = int(match.group(1))
    order = await repo.orders.get_order_by_id(order_id)
    
    if not order:
        await callback.answer("Заказ не найден.", show_alert=True)
        return
    
    # Получаем информацию о товаре
    product = await repo.products.get_product_by_id(order.product_id)
    product_name = product.name if product else "Неизвестный товар"
    
    # Получаем информацию о пользователе
    user = await repo.users.get_user_by_id(order.user_id)
    user_name = f"{user.first_name} {user.last_name}" if user else "Неизвестный пользователь"
    
    # Формируем текст с детальной информацией о заказе
    text = (
        f"🛒 Информация о заказе #{order.order_id}:\n\n"
        f"Статус: {order.status}\n"
        f"Товар: {product_name}\n"
        f"Количество: {order.quantity}\n"
        f"Общая стоимость: {order.total_price}\n"
        f"Пользователь: {user_name}\n"
        f"ID пользователя: {order.user_id}\n"
        f"Создан: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"Обновлен: {order.updated_at.strftime('%d.%m.%Y %H:%M')}\n"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=order_details_keyboard(order_id)
    )