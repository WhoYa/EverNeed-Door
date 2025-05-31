# tgbot/handlers/users/user_products.py

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from tgbot.keyboards.user_products import products_keyboard, filter_keyboard, build_materials_keyboard, build_types_keyboard, build_price_range_keyboard
from infrastructure.database.repositories.requests import RequestsRepo
from tgbot.misc.callback_factory import ProductViewCallback, FavoriteActionCallback, FilterCallback, PurchaseCallback
from tgbot.keyboards.purchase import purchase_keyboard, confirm_purchase_keyboard
from tgbot.misc.states import FilterStates

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
            text="📦 *Каталог товаров:*\nВыберите товар, чтобы узнать больше или воспользуйтесь фильтрами.",
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
    
    # Логируем действие пользователя
    await repo.logs.create_log(
        user_id=user_id,
        action="view_product",
        details=f"Просмотр товара с ID {product_id}"
    )
    
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
            from aiogram.types import FSInputFile
            
            # Создаем объект файла для отправки
            photo_file = FSInputFile(product.image_url)
            
            await callback.message.answer_photo(
                photo=photo_file,
                caption=text,
                parse_mode="Markdown",
                reply_markup=purchase_keyboard(product_id)
            )
            await callback.answer()
            logger.info(f"Отправлена информация о продукте {product_id} пользователю {user_id}.")
        except Exception as e:
            logger.error(f"Ошибка при отправке фото продукта {product_id} пользователю {user_id}: {e}")
            await callback.answer("❌ Не удалось отправить фото товара.", show_alert=True)
    else:
        logger.warning(f"Пользователь {user_id} запросил несуществующий продукт {product_id}.")
        await callback.answer("❌ Товар не найден.", show_alert=True)

@user_products_router.callback_query(F.data == "filter_products")
async def show_filter_menu(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Показывает меню фильтрации товаров.
    """
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} открывает меню фильтрации товаров.")
    
    # Сбрасываем текущие фильтры
    await state.clear()
    
    # Логируем действие пользователя
    await repo.logs.create_log(
        user_id=user_id,
        action="open_filter_menu",
        details="Открытие меню фильтрации товаров"
    )
    
    await callback.message.edit_text(
        "🔍 *Фильтрация товаров*\n\nВыберите параметры для фильтрации:",
        reply_markup=filter_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@user_products_router.callback_query(FilterCallback.filter(F.action == "material"))
async def select_material(callback: CallbackQuery, repo: RequestsRepo, state: FSMContext):
    """
    Показывает список доступных материалов для фильтрации.
    """
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} выбирает материал для фильтрации.")
    
    # Получаем список доступных материалов
    materials = await repo.products.get_available_materials()
    
    if materials:
        await callback.message.edit_text(
            "🔍 *Выберите материал:*",
            reply_markup=build_materials_keyboard(materials),
            parse_mode="Markdown"
        )
        await state.set_state(FilterStates.selecting_material)
    else:
        await callback.answer("❌ Не удалось загрузить список материалов.", show_alert=True)
    
@user_products_router.callback_query(FilterCallback.filter(F.action == "type"))
async def select_type(callback: CallbackQuery, repo: RequestsRepo, state: FSMContext):
    """
    Показывает список доступных типов товаров для фильтрации.
    """
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} выбирает тип товара для фильтрации.")
    
    # Получаем список доступных типов
    types = await repo.products.get_available_types()
    
    if types:
        await callback.message.edit_text(
            "🔍 *Выберите тип товара:*",
            reply_markup=build_types_keyboard(types),
            parse_mode="Markdown"
        )
        await state.set_state(FilterStates.selecting_type)
    else:
        await callback.answer("❌ Не удалось загрузить список типов товаров.", show_alert=True)

@user_products_router.callback_query(FilterCallback.filter(F.action == "price"))
async def select_price(callback: CallbackQuery, state: FSMContext):
    """
    Показывает опции для выбора диапазона цен.
    """
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} выбирает диапазон цен для фильтрации.")
    
    await callback.message.edit_text(
        "💰 *Выберите диапазон цен:*",
        reply_markup=build_price_range_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(FilterStates.selecting_price)

@user_products_router.callback_query(FilterCallback.filter(F.action == "apply"))
async def apply_filters(callback: CallbackQuery, repo: RequestsRepo, state: FSMContext):
    """
    Применяет выбранные фильтры и показывает результаты.
    """
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} применяет фильтры.")
    
    # Получаем сохраненные параметры фильтрации
    data = await state.get_data()
    material = data.get("material")
    product_type = data.get("type")
    min_price = data.get("min_price")
    max_price = data.get("max_price")
    
    # Логирование параметров фильтрации
    logger.info(f"Применяемые фильтры: материал={material}, тип={product_type}, мин_цена={min_price}, макс_цена={max_price}")
    
    # Создаем лог действия пользователя
    await repo.logs.create_log(
        user_id=user_id,
        action="filter_products",
        details=f"Фильтры: материал={material}, тип={product_type}, цена={min_price}-{max_price}"
    )
    
    # Получаем отфильтрованные товары
    products = await repo.products.filter_products(
        material=material,
        product_type=product_type,
        min_price=min_price,
        max_price=max_price
    )
    
    if products:
        await callback.message.edit_text(
            f"🔍 *Результаты поиска:*\nНайдено товаров: {len(products)}",
            reply_markup=products_keyboard(products, with_filter=True),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "❌ По вашему запросу ничего не найдено. Попробуйте изменить параметры фильтрации.",
            reply_markup=filter_keyboard(),
            parse_mode="Markdown"
        )
    
    await callback.answer()
    await state.clear()

@user_products_router.callback_query(FilterCallback.filter(F.action == "reset"))
async def reset_filters(callback: CallbackQuery, repo: RequestsRepo, state: FSMContext):
    """
    Сбрасывает все фильтры и показывает полный каталог.
    """
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} сбрасывает фильтры.")
    
    # Очищаем состояние
    await state.clear()
    
    # Получаем все товары
    products = await repo.products.get_all_products()
    
    if products:
        await callback.message.edit_text(
            "📦 *Каталог товаров:*\nФильтры сброшены.",
            reply_markup=products_keyboard(products),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "❌ В магазине пока нет доступных товаров."
        )
    
    await callback.answer("✅ Фильтры сброшены.", show_alert=True)

# Обработчики установки конкретных значений фильтров
@user_products_router.callback_query(FilterStates.selecting_material)
async def process_material_selection(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обрабатывает выбор материала.
    """
    if callback.data == "back_to_filter":
        await show_filter_menu(callback, state, repo)
        return
    
    material = callback.data
    await state.update_data(material=material)
    logger.info(f"Пользователь {callback.from_user.id} выбрал материал: {material}")
    
    await callback.message.edit_text(
        f"✅ Выбран материал: *{material}*\n\nПродолжите настройку фильтров:",
        reply_markup=filter_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(None)
    await callback.answer()

@user_products_router.callback_query(FilterStates.selecting_type)
async def process_type_selection(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обрабатывает выбор типа товара.
    """
    if callback.data == "back_to_filter":
        await show_filter_menu(callback, state, repo)
        return
    
    product_type = callback.data
    await state.update_data(type=product_type)
    logger.info(f"Пользователь {callback.from_user.id} выбрал тип товара: {product_type}")
    
    await callback.message.edit_text(
        f"✅ Выбран тип товара: *{product_type}*\n\nПродолжите настройку фильтров:",
        reply_markup=filter_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(None)
    await callback.answer()

@user_products_router.callback_query(FilterStates.selecting_price)
async def process_price_selection(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обрабатывает выбор ценового диапазона.
    """
    if callback.data == "back_to_filter":
        await show_filter_menu(callback, state, repo)
        return
    
    price_range = callback.data.split("_")
    min_price = None if price_range[0] == "any" else float(price_range[0])
    max_price = None if price_range[1] == "any" else float(price_range[1])
    
    await state.update_data(min_price=min_price, max_price=max_price)
    
    min_str = "любая" if min_price is None else f"{min_price}₽"
    max_str = "любая" if max_price is None else f"{max_price}₽"
    
    logger.info(f"Пользователь {callback.from_user.id} выбрал ценовой диапазон: {min_str} - {max_str}")
    
    await callback.message.edit_text(
        f"✅ Выбран ценовой диапазон: от *{min_str}* до *{max_str}*\n\nПродолжите настройку фильтров:",
        reply_markup=filter_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(None)
    await callback.answer()

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

@user_products_router.callback_query(F.data == "back_to_filter")
async def handle_back_to_filter(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обрабатывает нажатие кнопки "Назад" к фильтрам.
    """
    await show_filter_menu(callback, state, repo)
    await callback.answer()

@user_products_router.callback_query(F.data == "back_to_catalog")
async def handle_back_to_catalog(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обрабатывает возврат к каталогу товаров.
    """
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} возвращается к каталогу товаров.")
    
    # Сбрасываем состояние
    await state.clear()
    
    products = await repo.products.get_all_products()
    
    # Удаляем старое сообщение и отправляем новое
    try:
        await callback.message.delete()
    except Exception:
        pass  # Игнорируем ошибки удаления
    
    if products:
        await callback.message.answer(
            text="📦 *Каталог товаров:*\nВыберите товар, чтобы узнать больше или воспользуйтесь фильтрами.",
            reply_markup=products_keyboard(products),
            parse_mode="Markdown"
        )
    else:
        await callback.message.answer("❌ В магазине пока нет доступных товаров.")
    await callback.answer()

@user_products_router.callback_query(F.data == "view_favorites")
async def handle_view_favorites(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обрабатывает переход к избранному.
    """
    try:
        # Сбрасываем состояние
        await state.clear()
        
        # Используем обработчик из user_favorites.py
        from tgbot.handlers.users.user_favorites import view_favorites
        await view_favorites(callback, repo)
    except Exception as e:
        logger.error(f"Ошибка при переходе к избранному: {e}")
        await callback.answer("Ошибка навигации. Попробуйте снова.", show_alert=True)

@user_products_router.callback_query(F.data == "main_menu")
async def handle_main_menu(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает возврат в главное меню.
    """
    try:
        # Сбрасываем состояние
        await state.clear()
        
        # Используем обработчик из user_menu.py
        from tgbot.handlers.users.user_menu import main_menu_callback
        await main_menu_callback(callback, state)
    except Exception as e:
        logger.error(f"Ошибка при возврате в главное меню: {e}")
        await callback.answer("Ошибка навигации. Попробуйте снова.", show_alert=True)

@user_products_router.callback_query(F.data.regexp(r'^\d+_\d+$|^\d+_any$|^any_\d+$'))
async def handle_price_range_selection(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обрабатывает выбор ценового диапазона вне состояния.
    """
    current_state = await state.get_state()
    if current_state == FilterStates.selecting_price:
        # Если в состоянии фильтрации цены, используем основной обработчик
        await process_price_selection(callback, state, repo)
    else:
        # Иначе просто показываем фильтры
        await show_filter_menu(callback, state, repo)
        await callback.answer()

@user_products_router.callback_query(F.data.startswith("page_"))
async def handle_pagination(callback: CallbackQuery, repo: RequestsRepo):
    """
    Обрабатывает пагинацию каталога товаров.
    """
    page = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} переходит на страницу {page+1} каталога.")
    
    products = await repo.products.get_all_products()
    if products:
        await callback.message.edit_text(
            text="📦 *Каталог товаров:*\nВыберите товар, чтобы узнать больше или воспользуйтесь фильтрами.",
            reply_markup=products_keyboard(products, page=page),
            parse_mode="Markdown"
        )
    await callback.answer()

@user_products_router.callback_query(F.data == "go_back")
async def handle_go_back(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обрабатывает нажатие на кнопку "Назад".
    В зависимости от контекста, возвращает пользователя на предыдущий экран.
    """
    # Получаем текущее состояние
    current_state = await state.get_state()
    
    # Логика обработки возврата в зависимости от текущего состояния
    if current_state:
        # Если пользователь находится в состоянии фильтрации, вернуть к меню фильтров
        if current_state.startswith('FilterStates'):
            await show_filter_menu(callback, state, repo)
            return
    
    # По умолчанию возвращаем в главное меню
    # Используем общий обработчик из user_menu.py
    try:
        # Сбрасываем состояние
        await state.clear()
        
        await callback.message.edit_text(
            text="Возвращаемся в главное меню...",
            reply_markup=None
        )
        
        # Имитируем нажатие на кнопку главного меню
        from tgbot.handlers.users.user_menu import main_menu_callback
        await main_menu_callback(callback, state)
    except Exception as e:
        logger.error(f"Ошибка при возврате на предыдущий экран: {e}")
        await callback.answer("Ошибка навигации. Попробуйте снова.", show_alert=True)

# Purchase handlers
@user_products_router.callback_query(PurchaseCallback.filter(F.action == "buy"))
async def initiate_purchase(callback: CallbackQuery, callback_data: PurchaseCallback, repo: RequestsRepo):
    """
    Инициирует процесс покупки товара.
    """
    user_id = callback.from_user.id
    product_id = callback_data.product_id
    logger.info(f"Пользователь {user_id} инициирует покупку товара {product_id}.")
    
    # Получаем информацию о товаре
    product = await repo.products.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("❌ Товар не найден.", show_alert=True)
        return
    
    if not product.is_in_stock:
        await callback.answer("❌ Товар закончился на складе.", show_alert=True)
        return
    
    # Логируем действие пользователя
    await repo.logs.create_log(
        user_id=user_id,
        action="initiate_purchase",
        details=f"Инициирование покупки товара с ID {product_id}"
    )
    
    # Формируем сообщение с подтверждением
    text = (
        f"🛒 *Подтверждение заказа*\n\n"
        f"Товар: *{product.name}*\n"
        f"Цена: *{product.price}₽*\n\n"
        f"Подтвердите заказ для продолжения."
    )
    
    # Удаляем старое сообщение и отправляем новое
    try:
        await callback.message.delete()
    except Exception:
        pass  # Игнорируем ошибки удаления
    
    await callback.message.answer(
        text=text,
        reply_markup=confirm_purchase_keyboard(product_id),
        parse_mode="Markdown"
    )
    await callback.answer()

@user_products_router.callback_query(PurchaseCallback.filter(F.action == "confirm"))
async def confirm_purchase(callback: CallbackQuery, callback_data: PurchaseCallback, repo: RequestsRepo):
    """
    Подтверждает покупку и создает заказ.
    """
    user_id = callback.from_user.id
    product_id = callback_data.product_id
    logger.info(f"Пользователь {user_id} подтверждает покупку товара {product_id}.")
    
    try:
        # Получаем информацию о товаре
        product = await repo.products.get_product_by_id(product_id)
        
        if not product:
            await callback.answer("❌ Товар не найден.", show_alert=True)
            return
        
        if not product.is_in_stock:
            await callback.answer("❌ Товар закончился на складе.", show_alert=True)
            return
        
        # Создаем заказ
        order_data = {
            "user_id": user_id,
            "product_id": product_id,
            "quantity": 1,
            "total_price": float(product.price),
            "status": "Новый"
        }
        
        order = await repo.orders.create_order(order_data)
        
        if order:
            # Логируем успешное создание заказа
            await repo.logs.create_log(
                user_id=user_id,
                action="order_created",
                details=f"Создан заказ #{order.order_id} на товар {product.name}"
            )
            
            # Уведомляем пользователя
            success_text = (
                f"✅ *Заказ успешно создан!*\n\n"
                f"Номер заказа: *#{order.order_id}*\n"
                f"Товар: *{product.name}*\n"
                f"Сумма: *{product.price}₽*\n"
                f"Статус: *{order.status}*\n\n"
                f"Администратор свяжется с вами в ближайшее время для уточнения деталей доставки."
            )
            
            # Создаем клавиатуру для возврата к каталогу
            from aiogram.utils.keyboard import InlineKeyboardBuilder
            from aiogram.types import InlineKeyboardButton
            
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(
                    text="🔙 Назад к каталогу",
                    callback_data="back_to_catalog"
                )
            )
            
            await callback.message.edit_text(
                text=success_text,
                parse_mode="Markdown",
                reply_markup=builder.as_markup()
            )
            
            # Отправляем уведомление администраторам
            await notify_admins_about_new_order(order, product, callback.from_user, repo)
            
            await callback.answer("✅ Заказ создан!", show_alert=True)
            logger.info(f"Заказ #{order.order_id} успешно создан пользователем {user_id}.")
        else:
            await callback.answer("❌ Ошибка при создании заказа. Попробуйте позже.", show_alert=True)
            logger.error(f"Не удалось создать заказ для пользователя {user_id} на товар {product_id}.")
    
    except Exception as e:
        logger.error(f"Ошибка при подтверждении покупки пользователем {user_id}: {e}")
        await callback.answer("❌ Произошла ошибка. Попробуйте позже.", show_alert=True)

@user_products_router.callback_query(PurchaseCallback.filter(F.action == "cancel"))
async def cancel_purchase(callback: CallbackQuery, callback_data: PurchaseCallback, repo: RequestsRepo):
    """
    Отменяет покупку товара.
    """
    user_id = callback.from_user.id
    product_id = callback_data.product_id
    logger.info(f"Пользователь {user_id} отменил покупку товара {product_id}.")
    
    # Логируем действие пользователя
    await repo.logs.create_log(
        user_id=user_id,
        action="cancel_purchase",
        details=f"Отмена покупки товара с ID {product_id}"
    )
    
    # Создаем клавиатуру для возврата к каталогу
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад к каталогу",
            callback_data="back_to_catalog"
        )
    )
    
    await callback.message.edit_text(
        text="❌ Покупка отменена.",
        reply_markup=builder.as_markup()
    )
    await callback.answer("Покупка отменена.")

async def notify_admins_about_new_order(order, product, user, repo: RequestsRepo):
    """
    Отправляет уведомление администраторам о новом заказе.
    """
    try:
        from tgbot.config import load_config
        
        # Получаем конфигурацию и список админов из .env
        config = load_config(".env")
        admin_ids = config.tg_bot.admin_ids
        
        if not admin_ids:
            logger.warning("Нет админов в конфигурации для отправки уведомления о новом заказе.")
            return
        
        # Формируем текст уведомления
        notification_text = (
            f"🔔 *Новый заказ #{order.order_id}*\n\n"
            f"👤 Пользователь: @{user.username if user.username else 'Без username'} (ID: {user.id})\n"
            f"📦 Товар: *{product.name}*\n"
            f"💰 Сумма: *{product.price}₽*\n"
            f"📅 Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"Свяжитесь с клиентом для уточнения деталей доставки."
        )
        
        # Отправляем уведомление каждому админу
        for admin_id in admin_ids:
            try:
                from aiogram import Bot
                
                # Создаем экземпляр бота с токеном из конфигурации
                bot = Bot(token=config.tg_bot.token)
                
                await bot.send_message(
                    chat_id=admin_id,
                    text=notification_text,
                    parse_mode="Markdown"
                )
                
                # Закрываем сессию бота
                await bot.session.close()
                
                logger.info(f"Уведомление о заказе #{order.order_id} отправлено админу {admin_id}.")
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления админу {admin_id}: {e}")
    
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомлений админам о заказе #{order.order_id}: {e}")
