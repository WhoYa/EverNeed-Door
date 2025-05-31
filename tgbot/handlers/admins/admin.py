# tgbot/handlers/admins/admin.py
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.admin_main_menu import main_menu_keyboard

admin_router = Router()
admin_router.message.filter(AdminFilter())
admin_router.callback_query.filter(AdminFilter())

@admin_router.message(CommandStart())
async def admin_start(message: Message):
    """
    Обрабатывает команду /start для администраторов.
    Показывает главное меню администратора.
    """
    await message.answer(
        text="Добро пожаловать в админ-панель!\n\n"
             "Выберите действие из меню:",
        reply_markup=main_menu_keyboard(),
    )

@admin_router.message(Command("admin_menu"))
async def admin_menu_command(message: Message):
    """
    Обрабатывает команду /admin_menu.
    Возвращает пользователя в главное меню администратора.
    """
    await message.answer(
        text="Главное меню администратора",
        reply_markup=main_menu_keyboard(),
    )

@admin_router.callback_query(F.data.in_({"admin_main", "back_to_main_menu"}))
async def admin_menu_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает возврат в главное меню администратора через callback.
    Поддерживает как "admin_main", так и "back_to_main_menu" для обратной совместимости.
    """
    # Очищаем состояние для предотвращения проблем
    await state.clear()
    
    try:
        await callback.message.edit_text(
            text="Главное меню администратора",
            reply_markup=main_menu_keyboard(),
        )
    except Exception as e:
        # Если не удалось отредактировать сообщение, отправляем новое
        logging.error(f"Ошибка при возврате в админ-меню: {e}")
        
        try:
            await callback.message.delete()
        except Exception:
            pass
            
        await callback.message.answer(
            text="Главное меню администратора",
            reply_markup=main_menu_keyboard(),
        )
    
    await callback.answer()

# Removed duplicated handler as it's handled in admin_product_management.py

# Removed duplicated handler as it's handled in admin_statistics.py

@admin_router.callback_query(F.data == "manage_subscriptions")
async def manage_subscriptions_callback(callback: CallbackQuery):
    """
    Обрабатывает нажатие на кнопку "Управление подписками".
    Передает управление в соответствующий хендлер из admin_subscriptions.py
    """
    # Перенаправляем в хендлер управления подписками
    # Реальная обработка происходит в admin_subscriptions.py
    await callback.answer("Переход к управлению подписками...")

@admin_router.callback_query(F.data == "manage_admins")
async def manage_admins_callback(callback: CallbackQuery):
    """
    Обрабатывает нажатие на кнопку "Управление администраторами".
    Передает управление в соответствующий хендлер из admin_auth.py
    """
    # Перенаправляем в хендлер управления администраторами
    # Реальная обработка происходит в admin_auth.py
    await callback.answer("Переход к управлению администраторами...")

@admin_router.callback_query(F.data == "manage_promotions")
async def manage_promotions_callback(callback: CallbackQuery):
    """
    Обрабатывает нажатие на кнопку "Управление акциями".
    Передает управление в соответствующий хендлер из admin_promotion.py
    """
    # Перенаправляем в хендлер управления акциями
    # Реальная обработка происходит в admin_promotion.py
    await callback.answer("Переход к управлению акциями...")

# Removed duplicated handler as it's handled in admin_orders.py