from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from tgbot.misc.callback_factory import ProductsCallbackFactory


def purchase_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="💳 Оплатить",
        callback_data=ProductsCallbackFactory(category="purchase", product_id=product_id)
    )
    builder.button(
        text="🔙 Назад",
        callback_data=ProductsCallbackFactory(category="back_to_catalog")
    )
    return builder.as_markup()
