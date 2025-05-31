# tgbot/handlers/users/user_favorites.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from tgbot.keyboards.user_favorites import favorites_keyboard, empty_favorites_keyboard
from infrastructure.database.repositories.favorites import FavoritesRepo
from tgbot.misc.callback_factory import FavoriteActionCallback
from infrastructure.database.repositories.products import ProductsRepo
import logging

user_favorites_router = Router()

# Настройка логирования для данного модуля
logger = logging.getLogger(__name__)

@user_favorites_router.callback_query(F.data == "view_favorites")
async def view_favorites(callback: CallbackQuery, repo):
    """
    Показывает список избранных товаров пользователя.
    """
    user_id = callback.from_user.id
    favorites = await repo.favorites.get_favorites_by_user(user_id=user_id)

    # Удаляем старое сообщение и отправляем новое
    try:
        await callback.message.delete()
    except Exception:
        pass  # Игнорируем ошибки удаления
    
    if favorites:
        keyboard = favorites_keyboard(favorites)
        text = "*Ваше избранное:*\n\n"
        for fav in favorites:
            text += f"• {fav.product.name}\n"
        await callback.message.answer(
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    else:
        await callback.message.answer(
            "У вас нет избранных товаров.",
            reply_markup=empty_favorites_keyboard()
        )
    await callback.answer()

@user_favorites_router.callback_query(FavoriteActionCallback.filter(F.action == "remove"))
async def remove_favorite(callback: CallbackQuery, callback_data: FavoriteActionCallback, repo):
    """
    Удаляет товар из избранного.
    """
    user_id = callback.from_user.id
    product_id = callback_data.product_id

    await repo.favorites.remove_favorite_by_user_product(user_id=user_id, product_id=product_id)
    logger.info(f"Пользователь {user_id} удалил продукт {product_id} из избранного.")

    # Уведомление пользователя
    await callback.answer("⭐ Товар удалён из избранного.", show_alert=True)

    # Обновить список избранного
    favorites = await repo.favorites.get_favorites_by_user(user_id=user_id)
    
    # Удаляем старое сообщение и отправляем новое
    try:
        await callback.message.delete()
    except Exception:
        pass  # Игнорируем ошибки удаления
    
    if favorites:
        keyboard = favorites_keyboard(favorites)
        text = "*Ваше избранное:*\n\n"
        for fav in favorites:
            text += f"• {fav.product.name}\n"
        await callback.message.answer(
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    else:
        await callback.message.answer(
            "У вас нет избранных товаров.",
            reply_markup=empty_favorites_keyboard()
        )

@user_favorites_router.callback_query(FavoriteActionCallback.filter(F.action == "view"))
async def view_favorite_product(callback: CallbackQuery, callback_data: FavoriteActionCallback, repo):
    """
    Показывает детали избранного товара, отправляя фотографию.
    """
    product_id = callback_data.product_id
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
            from tgbot.keyboards.purchase import purchase_keyboard_from_favorites
            from aiogram.types import FSInputFile
            
            # Создаем объект файла для отправки
            photo_file = FSInputFile(product.image_url)
            
            await callback.message.answer_photo(
                photo=photo_file,
                caption=text,
                parse_mode="Markdown",
                reply_markup=purchase_keyboard_from_favorites(product_id)
            )
            await callback.answer()
            logger.info(f"Отправлена информация о продукте {product_id} пользователю {callback.from_user.id}.")
        except Exception as e:
            logger.error(f"Ошибка при отправке фото продукта {product_id}: {e}")
            await callback.answer("❌ Не удалось отправить фото товара.", show_alert=True)
    else:
        logger.warning(f"Пользователь {callback.from_user.id} запросил несуществующий продукт {product_id}.")
        await callback.answer("❌ Товар не найден.", show_alert=True)
