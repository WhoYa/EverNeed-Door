# tgbot/handlers/admin_product_management.py
import logging
import re
from typing import Optional, Dict, Any, Union

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.keyboards.product_management import (
    product_management_keyboard,
    product_list_keyboard_paginated,
    product_details_keyboard,
    edit_product_keyboard,
    confirmation_keyboard
)
from tgbot.keyboards.back_button import back_button_keyboard
from tgbot.keyboards.admin_main_menu import main_menu_keyboard
from tgbot.misc.states import ProductManagement, ProductField
from infrastructure.database.repositories.requests import RequestsRepo 
from tgbot.filters.admin import AdminFilter

# Используем константы из перечисления ProductField
PREVIOUS_STATE = ProductField.PREVIOUS_STATE
EDIT_FIELD = ProductField.EDIT_FIELD
PRODUCT_ID = ProductField.PRODUCT_ID
NAME = ProductField.NAME
DESCRIPTION = ProductField.DESCRIPTION
TYPE = ProductField.TYPE
MATERIAL = ProductField.MATERIAL
PRICE = ProductField.PRICE
IMAGE_URL = ProductField.IMAGE_URL

admin_product_router = Router()

# Применяем фильтр ко всем сообщениям и callback_query в этом роутере
admin_product_router.message.filter(AdminFilter())
admin_product_router.callback_query.filter(AdminFilter())


def format_product_info(product) -> str:
    """
    Форматирует информацию о товаре для отображения пользователю.
    
    Args:
        product: Объект товара с необходимыми атрибутами
        
    Returns:
        str: Отформатированная строка с информацией о товаре
    """
    if hasattr(product, 'formatted_info') and callable(getattr(product, 'formatted_info')):
        return product.formatted_info()
    
    # Запасной вариант, если метод не доступен
    return (
        f"📦 Информация о товаре:\n\n"
        f"ID: {product.product_id}\n"
        f"Название: {product.name}\n"
        f"Описание: {product.description or 'Не указано'}\n"
        f"Тип: {product.type or 'Не указан'}\n"
        f"Материал: {product.material or 'Не указан'}\n"
        f"Цена: {product.price}\n"
    )

@admin_product_router.callback_query(F.data == "manage_products")
async def show_product_management_menu(callback: CallbackQuery):
    """
    Переход в меню управления товарами.
    """
    try:
        await callback.message.edit_text(
            "Выберите действие с товарами:",
            reply_markup=product_management_keyboard()
        )
        await callback.answer()
    except Exception as e:
        # If there's an error editing the message (e.g., message is too old),
        # send a new message instead
        logging.error(f"Error editing message: {e}")
        await callback.message.answer(
            "Выберите действие с товарами:",
            reply_markup=product_management_keyboard()
        )
        await callback.answer()

@admin_product_router.callback_query(F.data == "view_products")
async def view_products_handler(callback: CallbackQuery, repo: RequestsRepo):
    """Показать страницу 1 со списком товаров."""
    products = await repo.products.get_all_products()
    
    # Сортируем товары по ID
    products.sort(key=lambda x: x.product_id)
    
    if not products:
        # Отправляем новое сообщение вместо редактирования
        try:
            await callback.message.delete()
        except Exception:
            pass
            
        await callback.message.answer(
            "На данный момент товары отсутствуют.",
            reply_markup=product_management_keyboard()
        )
        return

    # Формируем текст 
    text_lines = ["Список товаров (стр. 1):\n"]
    for p in products[:5]:  # только первые 5 для примера
        text_lines.append(f"- ID: {p.product_id}, «{p.name}», цена: {p.price}")
    text_output = "\n".join(text_lines)

    # Создаём клавиатуру для страницы 1
    keyboard = product_list_keyboard_paginated(products, page=1, page_size=5)

    # Отправляем новое сообщение и удаляем старое
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer(text_output, reply_markup=keyboard)


@admin_product_router.callback_query(F.data.regexp(r"^view_products_page_(\d+)$"))
async def view_products_page_handler(callback: CallbackQuery, repo: RequestsRepo):
    """
    Обработка нажатий на кнопки "view_products_page_X" для переключения страниц.
    """
    match = re.match(r"^view_products_page_(\d+)$", callback.data)
    if not match:
        return

    page = int(match.group(1))

    products = await repo.products.get_all_products()
    
    # Сортируем товары по ID
    products.sort(key=lambda x: x.product_id)
    
    total_products = len(products)

    if not products or page < 1:
        # Если товаров нет или некорректная страница
        await callback.answer("Нет данных для отображения.", show_alert=True)
        return
    
    # Текст – уточняем, какая страница отображается
    text_lines = [f"Список товаров (стр. {page}):\n"]
    page_size = 5
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    for p in products[start_index:end_index]:
        text_lines.append(f"- ID: {p.product_id}, «{p.name}», цена: {p.price}")
    text_output = "\n".join(text_lines)

    # Генерируем клавиатуру для указанной страницы
    keyboard = product_list_keyboard_paginated(products, page=page, page_size=page_size)

    # Отправляем новое сообщение и удаляем старое вместо редактирования
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    await callback.message.answer(text_output, reply_markup=keyboard)

@admin_product_router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """
    Возвращение в основную админ-панель.
    """
    logging.info(f"Пользователь {callback.from_user.id} нажал 'Назад' в меню управления товарами.")
    await callback.message.edit_text(
        "Добро пожаловать в админ-панель!\n\nВыберите действие из меню:",
        reply_markup=main_menu_keyboard()
    )
    await state.clear()

@admin_product_router.callback_query(F.data.regexp(r"^product_(\d+)$"))
async def view_product_details(callback: CallbackQuery, repo: RequestsRepo):
    """
    Показывает детальную информацию о товаре с кнопками для изменения/удаления.
    """
    match = re.match(r"^product_(\d+)$", callback.data)
    if not match:
        return
    
    product_id = int(match.group(1))
    product = await repo.products.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
    
    # Используем функцию форматирования информации о товаре
    text = format_product_info(product)
    
    # Если у товара есть изображение, отправляем его 
    image_url = getattr(product, 'image_url', None)
    if image_url:
        try:
            await callback.message.answer_photo(
                photo=image_url,
                caption=text,
                reply_markup=product_details_keyboard(product_id)
            )
            # Удаляем предыдущее сообщение
            await callback.message.delete()
        except Exception as e:
            logging.error(f"Error sending product photo: {e}")
            # Fallback to text message if photo can't be sent
            await callback.message.edit_text(
                text,
                reply_markup=product_details_keyboard(product_id)
            )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=product_details_keyboard(product_id)
        )

@admin_product_router.callback_query(F.data.regexp(r"^edit_(\d+)$"))
async def edit_product_handler(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик кнопки изменения товара из детального просмотра.
    """
    match = re.match(r"^edit_(\d+)$", callback.data)
    if not match:
        return
    
    product_id = int(match.group(1))
    product = await repo.products.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
    
    try:
        # Проверим, есть ли у сообщения фото
        if callback.message.photo:
            # Если фото есть, нужно отправить новое сообщение, так как нельзя редактировать фото на текст
            await callback.message.delete()
            await callback.message.answer(
                f"Выберите, что хотите изменить в товаре «{product.name}»:",
                reply_markup=edit_product_keyboard(product_id)
            )
        else:
            # Если фото нет, можем редактировать текст
            await callback.message.edit_text(
                f"Выберите, что хотите изменить в товаре «{product.name}»:",
                reply_markup=edit_product_keyboard(product_id)
            )
    except Exception as e:
        logging.error(f"Ошибка при обработке кнопки изменения: {e}")
        # Отправим новое сообщение
        await callback.message.answer(
            f"Выберите, что хотите изменить в товаре «{product.name}»:",
            reply_markup=edit_product_keyboard(product_id)
        )
    
    await state.update_data(product_id=product_id)
    
@admin_product_router.callback_query(F.data.regexp(r"^delete_(\d+)$"))
async def delete_product_handler(callback: CallbackQuery, repo: RequestsRepo):
    """
    Обработчик кнопки удаления товара из детального просмотра.
    """
    match = re.match(r"^delete_(\d+)$", callback.data)
    if not match:
        return
    
    product_id = int(match.group(1))
    product = await repo.products.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
    
    try:
        # Проверим, есть ли у сообщения фото
        if callback.message.photo:
            # Если фото есть, нужно отправить новое сообщение, так как нельзя редактировать фото на текст
            await callback.message.delete()
            await callback.message.answer(
                f"Вы уверены, что хотите удалить товар «{product.name}»?",
                reply_markup=confirmation_keyboard(product_id)
            )
        else:
            # Если фото нет, можем редактировать текст
            await callback.message.edit_text(
                f"Вы уверены, что хотите удалить товар «{product.name}»?",
                reply_markup=confirmation_keyboard(product_id)
            )
    except Exception as e:
        logging.error(f"Ошибка при обработке кнопки удаления: {e}")
        # Отправим новое сообщение
        await callback.message.answer(
            f"Вы уверены, что хотите удалить товар «{product.name}»?",
            reply_markup=confirmation_keyboard(product_id)
        )

@admin_product_router.callback_query(F.data.regexp(r"^confirm_delete_(\d+)$"))
async def confirm_delete_product(callback: CallbackQuery, repo: RequestsRepo):
    """
    Обработчик подтверждения удаления товара.
    """
    match = re.match(r"^confirm_delete_(\d+)$", callback.data)
    if not match:
        return
    
    product_id = int(match.group(1))
    product = await repo.products.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
    
    # Удаляем товар из базы данных
    success = await repo.products.delete_product(product_id)
    
    if success:
        await callback.answer(f"Товар «{product.name}» успешно удален.", show_alert=True)
        # Возвращаемся к списку товаров
        products = await repo.products.get_all_products()
        
        if not products:
            await callback.message.edit_text(
                "На данный момент товары отсутствуют.",
                reply_markup=product_management_keyboard()
            )
            return
        
        text_lines = ["Список товаров (стр. 1):\n"]
        for p in products[:5]:  # только первые 5 для примера
            text_lines.append(f"- ID: {p.product_id}, «{p.name}», цена: {p.price}")
        text_output = "\n".join(text_lines)
        
        keyboard = product_list_keyboard_paginated(products, page=1, page_size=5)
        
        await callback.message.edit_text(text_output, reply_markup=keyboard)
    else:
        await callback.answer("Ошибка при удалении товара. Попробуйте снова.", show_alert=True)

@admin_product_router.callback_query(F.data.regexp(r"^edit_(\w+)_(\d+)$"))
async def edit_product_field(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Универсальный обработчик изменения полей товара.
    
    Поддерживает редактирование следующих полей:
    - name: название товара
    - description: описание товара
    - type: тип товара
    - material: материал товара
    - price: цена товара
    - image_url: изображение товара
    """
    match = re.match(r"^edit_(\w+)_(\d+)$", callback.data)
    if not match:
        return
    
    field_name, product_id_str = match.groups()
    product_id = int(product_id_str)
    product = await repo.products.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
    
    # Словарь соответствия полей и их человекочитаемых названий
    field_titles = {
        "name": "название",
        "description": "описание",
        "type": "тип",
        "material": "материал",
        "price": "цену",
        "image_url": "изображение"
    }
    
    # Определяем название поля для сообщения пользователю
    if field_name not in field_titles:
        logging.error(f"Неизвестное поле для редактирования: {field_name}")
        await callback.answer("Операция не поддерживается.", show_alert=True)
        return
    
    field_title = field_titles[field_name]
    current_value = getattr(product, field_name, "")
    
    # Сохраняем данные для последующего обновления
    await state.update_data(
        product_id=product_id, 
        edit_field=field_name, 
        previous_state=PREVIOUS_STATE
    )
    
    # Формируем сообщение в зависимости от типа поля
    if field_name == "image_url":
        message_text = f"Прикрепите новое изображение товара:"
    else:
        message_text = f"Текущее {field_title}: {current_value}\n\nВведите новое {field_title} товара:"
    
    # Отправляем сообщение и устанавливаем соответствующее состояние
    await callback.message.edit_text(
        message_text,
        reply_markup=back_button_keyboard()
    )
    
    # Устанавливаем соответствующее состояние FSM
    field_state = getattr(ProductManagement, field_name, None)
    if field_state:
        await state.set_state(field_state)
    else:
        logging.error(f"Не найдено состояние для поля {field_name}")
        await callback.answer("Произошла ошибка. Попробуйте еще раз.", show_alert=True)

# Универсальная функция для обработки обновления текстовых полей товара
async def process_field_update(message: Message, state: FSMContext, repo: RequestsRepo, field_name: str, field_value: Any) -> bool:
    """
    Универсальная функция для обновления полей товара.
    
    Args:
        message: Telegram-сообщение пользователя
        state: Состояние FSM
        repo: Репозиторий для работы с базой данных
        field_name: Имя поля для обновления
        field_value: Новое значение поля
        
    Returns:
        bool: True если обновление прошло успешно, False в противном случае
    """
    data = await state.get_data()
    product_id = data.get(PRODUCT_ID)
    
    if not product_id:
        logging.error("process_field_update: product_id не найден в данных FSM")
        await message.answer("Ошибка при обновлении товара: отсутствует идентификатор.")
        return False
    
    # Обновляем поле товара
    try:
        success = await repo.products.update_product_field(product_id, field_name, field_value)
        
        if success:
            product = await repo.products.get_product_by_id(product_id)
            field_titles = {
                "name": "Название",
                "description": "Описание",
                "type": "Тип",
                "material": "Материал",
                "price": "Цена",
                "image_url": "Изображение"
            }
            
            field_title = field_titles.get(field_name, field_name.capitalize())
            await message.answer(f"{field_title} товара успешно изменено.")
            
            # Возвращаемся к просмотру товара
            product_info = format_product_info(product)
            await message.answer(
                product_info,
                reply_markup=product_details_keyboard(product_id)
            )
            return True
        else:
            await message.answer(f"Ошибка при обновлении поля {field_name} товара. Попробуйте снова.")
            return False
    except Exception as e:
        logging.error(f"Ошибка при обновлении поля {field_name} товара: {e}")
        await message.answer(f"Произошла ошибка при обновлении товара: {e}")
        return False
        
# Обработчик для редактирования имени товара
@admin_product_router.message(ProductManagement.name)
async def process_new_name(message: Message, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик ввода нового названия товара при редактировании.
    """
    await process_field_update(message, state, repo, NAME, message.text)
    await state.clear()

@admin_product_router.message(ProductManagement.description)
async def process_new_description(message: Message, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик ввода нового описания товара.
    """
    await process_field_update(message, state, repo, DESCRIPTION, message.text)
    await state.clear()

@admin_product_router.message(ProductManagement.type)
async def process_new_type(message: Message, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик ввода нового типа товара.
    """
    await process_field_update(message, state, repo, TYPE, message.text)
    await state.clear()

@admin_product_router.message(ProductManagement.material)
async def process_new_material(message: Message, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик ввода нового материала товара.
    """
    await process_field_update(message, state, repo, MATERIAL, message.text)
    await state.clear()

@admin_product_router.message(ProductManagement.price)
async def process_new_price(message: Message, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик ввода новой цены товара.
    """
    try:
        # Удаляем все нечисловые символы кроме точки и запятой
        price_text = message.text.strip()
        # Заменяем запятую на точку для поддержки разных форматов
        price_text = price_text.replace(',', '.')
        
        # Проверяем, что в тексте есть только цифры и точка
        if not all(c.isdigit() or c == '.' for c in price_text):
            raise ValueError("Цена должна содержать только цифры и точку")
            
        # Если точек больше одной - некорректный формат
        if price_text.count('.') > 1:
            raise ValueError("Некорректный формат числа")
            
        price = float(price_text)
        
        # Проверка на отрицательное или нулевое значение
        if price <= 0:
            await message.answer("Цена должна быть положительным числом. Попробуйте еще раз.")
            return
            
        # Проверка на слишком большую цену
        if price > 1000000:  # Примерное ограничение для реалистичной цены
            await message.answer("Введенная цена слишком большая. Пожалуйста, проверьте значение.")
            return
            
        # Обновляем цену товара
        await process_field_update(message, state, repo, PRICE, price)
        await state.clear()
    except ValueError as e:
        error_message = str(e) if str(e) != "could not convert string to float: " else "Введите корректное числовое значение для цены."
        await message.answer(error_message)

@admin_product_router.message(ProductManagement.image_url, F.photo)
async def process_new_image(message: Message, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик загрузки нового изображения товара.
    """
    # Берем идентификатор фото с лучшим разрешением
    photo_id = message.photo[-1].file_id
    
    # Используем универсальную функцию обновления, но с особой обработкой для отображения фото
    data = await state.get_data()
    edit_field = data.get(EDIT_FIELD)
    product_id = data.get(PRODUCT_ID)
    
    if edit_field == IMAGE_URL and product_id:
        # Обновляем изображение товара напрямую, т.к. нужна специальная обработка для ответа с фото
        success = await repo.products.update_product_field(product_id, IMAGE_URL, photo_id)
        
        if success:
            product = await repo.products.get_product_by_id(product_id)
            await message.answer("Изображение товара успешно обновлено.")
            
            # Форматируем информацию о товаре
            product_info = format_product_info(product)
            
            # Возвращаемся к просмотру товара с фото
            image_url = getattr(product, 'image_url', None)
            if image_url:
                try:
                    await message.answer_photo(
                        photo=image_url,
                        caption=product_info,
                        reply_markup=product_details_keyboard(product_id)
                    )
                except Exception as e:
                    logging.error(f"Error sending product photo: {e}")
                    await message.answer(
                        product_info,
                        reply_markup=product_details_keyboard(product_id)
                    )
            else:
                await message.answer(
                    product_info,
                    reply_markup=product_details_keyboard(product_id)
                )
        else:
            await message.answer("Ошибка при обновлении изображения товара. Попробуйте снова.")
    
    await state.clear()

@admin_product_router.callback_query(F.data == "add_product")
async def start_add_product(callback: CallbackQuery, state: FSMContext):
    """
    Начало добавления нового товара.
    """
    logging.info(f"Пользователь {callback.from_user.id} начал добавление товара.")
    await state.update_data({PREVIOUS_STATE: None})  # Сбрасываем предыдущее состояние
    await callback.message.edit_text("Введите название товара:", reply_markup=back_button_keyboard())
    await state.set_state(ProductManagement.name)

# Функция для общего процесса создания товара
async def process_product_creation(message: Message, state: FSMContext, 
                                   current_state: str, next_state: str, 
                                   field_name: str, prompt_text: str):
    """
    Обрабатывает ввод данных при создании товара.
    
    Args:
        message: Telegram-сообщение пользователя
        state: Состояние FSM
        current_state: Текущее состояние FSM
        next_state: Следующее состояние FSM
        field_name: Имя поля для сохранения
        prompt_text: Текст запроса следующего поля
    """
    logging.info(f"Пользователь {message.from_user.id} ввёл {field_name}: {message.text}")
    
    # Сохраняем текущее состояние и введенное значение
    await state.update_data({
        PREVIOUS_STATE: current_state,
        field_name: message.text
    })
    
    # Запрашиваем следующее поле
    await message.answer(prompt_text, reply_markup=back_button_keyboard())
    
    # Переходим к следующему состоянию
    await state.set_state(next_state)

@admin_product_router.message(ProductManagement.name)
async def set_product_name(message: Message, state: FSMContext):
    """
    Установка имени товара.
    """
    await process_product_creation(
        message, state,
        ProductManagement.name, ProductManagement.description,
        NAME, "Введите описание товара:"
    )

@admin_product_router.message(ProductManagement.description)
async def set_product_description(message: Message, state: FSMContext):
    """
    Установка описания товара.
    """
    await process_product_creation(
        message, state,
        ProductManagement.description, ProductManagement.type,
        DESCRIPTION, "Введите тип товара (например, 'дверь', 'аксессуар'):"
    )

@admin_product_router.message(ProductManagement.type)
async def set_product_type(message: Message, state: FSMContext):
    """
    Установка типа товара.
    """
    await process_product_creation(
        message, state,
        ProductManagement.type, ProductManagement.material,
        TYPE, "Введите материал товара:"
    )

@admin_product_router.message(ProductManagement.material)
async def set_product_material(message: Message, state: FSMContext):
    """
    Установка материала товара.
    """
    await process_product_creation(
        message, state,
        ProductManagement.material, ProductManagement.price,
        MATERIAL, "Введите цену товара:"
    )

@admin_product_router.message(ProductManagement.price)
async def set_product_price(message: Message, state: FSMContext):
    """
    Установка цены товара.
    """
    try:
        price = float(message.text)
        logging.info(f"Пользователь {message.from_user.id} ввёл цену товара: {price}")
        
        # Сохраняем текущее состояние и введенное значение
        await state.update_data({
            PREVIOUS_STATE: ProductManagement.price,
            PRICE: price
        })
        
        # Запрашиваем фото товара
        await message.answer("Прикрепите фото товара:", reply_markup=back_button_keyboard())
        await state.set_state(ProductManagement.image_url)
    except ValueError:
        await message.answer("Цена должна быть числом. Попробуйте ещё раз.")

@admin_product_router.message(ProductManagement.image_url, F.photo)
async def set_product_image(message: Message, state: FSMContext, repo: RequestsRepo):
    """
    Завершение добавления товара.
    """
    logging.info(f"Пользователь {message.from_user.id} прикрепил фото товара.")
    
    # Получаем идентификатор фото с лучшим разрешением
    photo_id = message.photo[-1].file_id
    await state.update_data({IMAGE_URL: photo_id})
    
    # Получаем все данные о товаре
    data = await state.get_data()

    # Создаем словарь с данными товара
    product_data = {
        NAME: data.get(NAME, ""),
        DESCRIPTION: data.get(DESCRIPTION, ""),
        TYPE: data.get(TYPE, ""),
        MATERIAL: data.get(MATERIAL, ""),
        PRICE: data.get(PRICE, 0),
        IMAGE_URL: photo_id
    }
    
    try:
        # Сохраняем товар в БД
        new_product = await repo.products.create_product(product_data)
        logging.info(f"Создан новый товар с ID: {new_product.product_id}")

        # Формируем сообщение о добавлении товара
        response_text = f"Товар успешно добавлен:\n\n{format_product_info(new_product)}"
        await message.answer(response_text)
    except Exception as e:
        logging.error(f"Ошибка при создании товара: {e}")
        await message.answer(f"Произошла ошибка при сохранении товара. Попробуйте снова.")
    
    # Очищаем состояние
    await state.clear()


@admin_product_router.callback_query(F.data == "go_back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    """
    Возвращение на предыдущий шаг.
    """
    logging.info(f"Пользователь {callback.from_user.id} нажал 'Назад'.")
    data = await state.get_data()
    previous_state = data.get(PREVIOUS_STATE)

    if not previous_state:
        # Если предыдущего состояния нет, возвращаем в меню управления товарами
        await callback.message.edit_text(
            "Выберите действие с товарами:",
            reply_markup=product_management_keyboard()
        )
        await state.clear()
        return

    # Словарь соответствия состояний и запросов
    state_prompts = {
        ProductManagement.name: "Введите название товара:",
        ProductManagement.description: "Введите описание товара:",
        ProductManagement.type: "Введите тип товара (например, 'дверь', 'аксессуар'):",
        ProductManagement.material: "Введите материал товара:",
        ProductManagement.price: "Введите цену товара:",
        ProductManagement.image_url: "Прикрепите фото товара:"
    }
    
    # Возвращаемся к предыдущему состоянию
    await state.set_state(previous_state)
    
    # Получаем соответствующий запрос для состояния
    prompt = state_prompts.get(previous_state, "Введите данные:")
    
    # Показываем пользователю текущее значение поля, если оно есть в данных
    field_name = str(previous_state).split(":")[-1]  # Извлекаем имя поля из состояния
    current_value = data.get(field_name)
    
    if current_value:
        prompt = f"{prompt}\n\nТекущее значение: {current_value}"
    
    # Отображаем сообщение
    await callback.message.edit_text(prompt, reply_markup=back_button_keyboard())
    logging.info(f"Возвращение к состоянию: {previous_state}")
