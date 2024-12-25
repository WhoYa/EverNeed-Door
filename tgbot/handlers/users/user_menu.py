# tgbot/handlers/user_menu.py
from aiogram import Router, F
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types.message import Message

from tgbot.keyboards.user_menu import main_menu_keyboard

user_menu_router = Router()

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
