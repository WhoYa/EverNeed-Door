from aiogram import Router, F
from aiogram.types import Message
from infrastructure.database.repositories.requests import RequestsRepo

user_orders_router = Router()


@user_orders_router.message(F.text.lower().contains("мои заказы"))
async def orders_info(message: Message, repo: RequestsRepo):
    orders = await repo.orders.get_orders_by_user(message.from_user.id)

    if orders:
        text = "*Ваши заказы:*\n\n"
        for order in orders:
            text += f"№{order.order_id}: {order.product.name} — *{order.status}*\n"
        await message.answer(text)
    else:
        await message.answer("У вас нет активных заказов\\.")
