# tgbot/handlers/users/user_products.py

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from tgbot.keyboards.user_products import products_keyboard
from infrastructure.database.repositories.requests import RequestsRepo
from tgbot.misc.callback_factory import ProductViewCallback, FavoriteActionCallback

user_products_router = Router()

# Настройка логирования для данного модуля
logger = logging.getLogger(__name__)

@user_products_router.message(F.text.casefold() == "каталог")
async def products_menu(message: Message, repo: RequestsRepo):
    """
    Обрабатывает команду для отображения каталога товаров.
    """
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил каталог товаров.")
    
    products = await repo.products.get_all_products()
    if products:
        await message.answer(
            text="📦 *Каталог товаров:*\nВыберите товар, чтобы узнать больше.",
            reply_markup=products_keyboard(products),
            parse_mode="Markdown"
        )
    else:
        logger.warning("В магазине нет доступных товаров.")
        await message.answer("❌ В магазине пока нет доступных товаров.")

@user_products_router.callback_query(ProductViewCallback.filter())
async def view_product(callback: CallbackQuery, callback_data: ProductViewCallback, repo: RequestsRepo):
    """
    Отправляет подробную информацию и фотографию выбранного товара.
    """
    user_id = callback.from_user.id
    product_id = callback_data.product_id
    logger.info(f"Пользователь {user_id} запросил просмотр продукта {product_id}.")
    
    product = await repo.products.get_product_by_id(product_id)
    
    if product:
        text = (
            f"*{product.name}*\n\n"
            f"{product.description}\n"
            f"🔹 *Тип:* {product.type}\n"
            f"🔹 *Материал:* {product.material}\n"
            f"💰 *Цена:* {product.price}₽"
        )
        try:
            await callback.message.answer_photo(
                photo=product.image_url,
                caption=text,
                parse_mode="Markdown"
            )
            await callback.answer()
            logger.info(f"Отправлена информация о продукте {product_id} пользователю {user_id}.")
        except Exception as e:
            logger.error(f"Ошибка при отправке фото продукта {product_id} пользователю {user_id}: {e}")
            await callback.answer("❌ Не удалось отправить фото товара.", show_alert=True)
    else:
        logger.warning(f"Пользователь {user_id} запросил несуществующий продукт {product_id}.")
        await callback.answer("❌ Товар не найден.", show_alert=True)

@user_products_router.callback_query(FavoriteActionCallback.filter(F.action == "add"))
async def add_favorite(callback: CallbackQuery, callback_data: FavoriteActionCallback, repo: RequestsRepo):
    """
    Добавляет товар в избранное пользователя.
    """
    user_id = callback.from_user.id
    product_id = callback_data.product_id
    logger.info(f"Пользователь {user_id} пытается добавить продукт {product_id} в избранное.")

    try:
        is_fav = await repo.favorites.is_favorite(user_id, product_id)
        if is_fav:
            logger.info(f"Пользователь {user_id} уже имеет продукт {product_id} в избранном.")
            await callback.answer("⭐ Товар уже в избранном.", show_alert=True)
            return
        
        await repo.favorites.add_favorite(user_id, product_id)
        logger.info(f"Пользователь {user_id} добавил продукт {product_id} в избранное.")
        await callback.answer("⭐ Товар добавлен в избранное!", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка при добавлении продукта {product_id} пользователем {user_id} в избранное: {e}")
        await callback.answer("❌ Не удалось добавить товар в избранное. Попробуйте позже.", show_alert=True)
