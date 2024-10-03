import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command


bot = Bot(token='7916328183:AAGzmNS2o6nlWzaUzheAsQXTPvQe5s7ragg')
dp = Dispatcher()


@dp.message()
async def reply_echo(message: Message):
    await bot.send_message(message.from_user.id, message.text)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('ботик выключен')