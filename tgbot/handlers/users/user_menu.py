# tgbot/handlers/user_menu.py
from aiogram import Router, F
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging

from tgbot.keyboards.user_menu import main_menu_keyboard
from tgbot.keyboards.user_products import products_keyboard
from infrastructure.database.repositories.requests import RequestsRepo

user_menu_router = Router()
logger = logging.getLogger(__name__)

@user_menu_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    await message.answer(
        text=(
            "Добро пожаловать!\n"
            "В нашем магазине вы найдёте лучшие двери для вашего дома и офиса.\n"
            "Что бы вы хотели сделать?"
        ),
        reply_markup=main_menu_keyboard(),
    )
    await state.clear()

@user_menu_router.message(F.text.lower().contains("меню"))
async def main_menu(message: Message, state: FSMContext):
    await command_start(message=message, state=state)

@user_menu_router.callback_query(F.data == "catalog")
async def catalog_callback(callback: CallbackQuery, repo: RequestsRepo):
    """
    Обрабатывает нажатие на кнопку "Каталог" в главном меню.
    Показывает список доступных товаров.
    """
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} запросил каталог товаров через callback.")
    
    products = await repo.products.get_all_products()
    if products:
        await callback.message.edit_text(
            text="📦 *Каталог товаров:*\nВыберите товар, чтобы узнать больше или воспользуйтесь фильтрами.",
            reply_markup=products_keyboard(products),
            parse_mode="Markdown"
        )
    else:
        logger.warning("В магазине нет доступных товаров.")
        await callback.message.edit_text(
            "❌ В магазине пока нет доступных товаров."
        )
    
    await callback.answer()

@user_menu_router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие на кнопку "Меню" или "Назад" для возврата в главное меню.
    Используется для навигации из различных разделов бота.
    """
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} вернулся в главное меню.")
    
    # Очищаем состояние FSM для предотвращения проблем с незавершенными операциями
    await state.clear()
    
    await callback.message.edit_text(
        text=(
            "Главное меню\n"
            "В нашем магазине вы найдёте лучшие двери для вашего дома и офиса.\n"
            "Что бы вы хотели сделать?"
        ),
        reply_markup=main_menu_keyboard()
    )
    
    await callback.answer()
