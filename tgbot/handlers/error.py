from aiogram import Router
from aiogram.types.message import Message
from aiogram.types import ReplyKeyboardRemove

user_error_router = Router()


@user_error_router.message()
async def error_message(message: Message):
    await message.answer(
        text="Я не понял \;\(\n"
             "Пожалуйста, воспользуйтесь кнопками"
    )
