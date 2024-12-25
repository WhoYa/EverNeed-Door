# tgbot/handlers/admin.py
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.admin_main_menu import main_menu_keyboard

admin_router = Router()
admin_router.message.filter(AdminFilter())

@admin_router.message(CommandStart())
async def admin_main_menu(message: Message):
    # Убираем клавиатуру пользователя и сразу показываем админское меню
    await message.answer(
        text="Добро пожаловать в админ-панель!\n\n"
             "Выберите действие из меню:",
        reply_markup=main_menu_keyboard(),
    )
