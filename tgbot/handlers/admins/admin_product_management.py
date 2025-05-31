# tgbot/handlers/admin_product_management.py
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
from tgbot.misc.states import ProductManagement
from tgbot.keyboards.admin_main_menu import main_menu_keyboard  # Импортируем основную клавиатуру
from infrastructure.database.repositories.requests import RequestsRepo 
from tgbot.filters.admin import AdminFilter
import logging
import re


admin_product_router = Router()

# Применяем фильтр ко всем сообщениям и callback_query в этом роутере
admin_product_router.message.filter(AdminFilter())
admin_product_router.callback_query.filter(AdminFilter())

@admin_product_router.callback_query(F.data == "manage_products")
async def show_product_management_menu(callback: CallbackQuery):
    """
    Переход в меню управления товарами.
    """
    await callback.message.edit_text(
        "Выберите действие с товарами:",
        reply_markup=product_management_keyboard()
    )

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
    
    # Формируем текст с детальной информацией о товаре
    text = (
        f"📦 Информация о товаре:\n\n"
        f"ID: {product.product_id}\n"
        f"Название: {product.name}\n"
        f"Описание: {product.description}\n"
        f"Тип: {product.type}\n"
        f"Материал: {product.material}\n"
        f"Цена: {product.price}\n"
    )
    
    # Если у товара есть изображение, отправляем его 
    if product.image_url:
        await callback.message.answer_photo(
            photo=product.image_url,
            caption=text,
            reply_markup=product_details_keyboard(product_id)
        )
        # Удаляем предыдущее сообщение
        await callback.message.delete()
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

@admin_product_router.callback_query(F.data.regexp(r"^edit_name_(\d+)$"))
async def edit_product_name(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик изменения названия товара.
    """
    match = re.match(r"^edit_name_(\d+)$", callback.data)
    if not match:
        return
    
    product_id = int(match.group(1))
    product = await repo.products.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
    
    await state.update_data(product_id=product_id, edit_field="name", previous_state="editing_product")
    await callback.message.edit_text(
        f"Текущее название: {product.name}\n\nВведите новое название товара:",
        reply_markup=back_button_keyboard()
    )
    await state.set_state(ProductManagement.name)

@admin_product_router.callback_query(F.data.regexp(r"^edit_description_(\d+)$"))
async def edit_product_description(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик изменения описания товара.
    """
    match = re.match(r"^edit_description_(\d+)$", callback.data)
    if not match:
        return
    
    product_id = int(match.group(1))
    product = await repo.products.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
    
    await state.update_data(product_id=product_id, edit_field="description", previous_state="editing_product")
    await callback.message.edit_text(
        f"Текущее описание: {product.description}\n\nВведите новое описание товара:",
        reply_markup=back_button_keyboard()
    )
    await state.set_state(ProductManagement.description)

@admin_product_router.callback_query(F.data.regexp(r"^edit_type_(\d+)$"))
async def edit_product_type(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик изменения типа товара.
    """
    match = re.match(r"^edit_type_(\d+)$", callback.data)
    if not match:
        return
    
    product_id = int(match.group(1))
    product = await repo.products.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
    
    await state.update_data(product_id=product_id, edit_field="type", previous_state="editing_product")
    await callback.message.edit_text(
        f"Текущий тип: {product.type}\n\nВведите новый тип товара:",
        reply_markup=back_button_keyboard()
    )
    await state.set_state(ProductManagement.type)

@admin_product_router.callback_query(F.data.regexp(r"^edit_material_(\d+)$"))
async def edit_product_material(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик изменения материала товара.
    """
    match = re.match(r"^edit_material_(\d+)$", callback.data)
    if not match:
        return
    
    product_id = int(match.group(1))
    product = await repo.products.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
    
    await state.update_data(product_id=product_id, edit_field="material", previous_state="editing_product")
    await callback.message.edit_text(
        f"Текущий материал: {product.material}\n\nВведите новый материал товара:",
        reply_markup=back_button_keyboard()
    )
    await state.set_state(ProductManagement.material)

@admin_product_router.callback_query(F.data.regexp(r"^edit_price_(\d+)$"))
async def edit_product_price(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик изменения цены товара.
    """
    match = re.match(r"^edit_price_(\d+)$", callback.data)
    if not match:
        return
    
    product_id = int(match.group(1))
    product = await repo.products.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
    
    await state.update_data(product_id=product_id, edit_field="price", previous_state="editing_product")
    await callback.message.edit_text(
        f"Текущая цена: {product.price}\n\nВведите новую цену товара:",
        reply_markup=back_button_keyboard()
    )
    await state.set_state(ProductManagement.price)

@admin_product_router.callback_query(F.data.regexp(r"^edit_image_url_(\d+)$"))
async def edit_product_image(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик изменения изображения товара.
    """
    match = re.match(r"^edit_image_url_(\d+)$", callback.data)
    if not match:
        return
    
    product_id = int(match.group(1))
    product = await repo.products.get_product_by_id(product_id)
    
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
    
    await state.update_data(product_id=product_id, edit_field="image_url", previous_state="editing_product")
    await callback.message.edit_text(
        f"Прикрепите новое изображение товара:",
        reply_markup=back_button_keyboard()
    )
    await state.set_state(ProductManagement.image_url)

# Обработчики для получения новых значений полей товара
@admin_product_router.message(ProductManagement.name)
async def process_new_name(message: Message, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик ввода нового названия товара.
    """
    data = await state.get_data()
    edit_field = data.get("edit_field")
    product_id = data.get("product_id")
    
    if edit_field == "name" and product_id:
        # Обновляем название товара
        success = await repo.products.update_product_field(product_id, "name", message.text)
        
        if success:
            product = await repo.products.get_product_by_id(product_id)
            await message.answer(f"Название товара успешно изменено на: {message.text}")
            
            # Возвращаемся к просмотру товара
            await message.answer(
                f"📦 Информация о товаре:\n\n"
                f"ID: {product.product_id}\n"
                f"Название: {product.name}\n"
                f"Описание: {product.description}\n"
                f"Тип: {product.type}\n"
                f"Материал: {product.material}\n"
                f"Цена: {product.price}\n",
                reply_markup=product_details_keyboard(product_id)
            )
        else:
            await message.answer("Ошибка при обновлении названия товара. Попробуйте снова.")
    
    await state.clear()

@admin_product_router.message(ProductManagement.description)
async def process_new_description(message: Message, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик ввода нового описания товара.
    """
    data = await state.get_data()
    edit_field = data.get("edit_field")
    product_id = data.get("product_id")
    
    if edit_field == "description" and product_id:
        # Обновляем описание товара
        success = await repo.products.update_product_field(product_id, "description", message.text)
        
        if success:
            product = await repo.products.get_product_by_id(product_id)
            await message.answer(f"Описание товара успешно изменено.")
            
            # Возвращаемся к просмотру товара
            await message.answer(
                f"📦 Информация о товаре:\n\n"
                f"ID: {product.product_id}\n"
                f"Название: {product.name}\n"
                f"Описание: {product.description}\n"
                f"Тип: {product.type}\n"
                f"Материал: {product.material}\n"
                f"Цена: {product.price}\n",
                reply_markup=product_details_keyboard(product_id)
            )
        else:
            await message.answer("Ошибка при обновлении описания товара. Попробуйте снова.")
    
    await state.clear()

@admin_product_router.message(ProductManagement.type)
async def process_new_type(message: Message, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик ввода нового типа товара.
    """
    data = await state.get_data()
    edit_field = data.get("edit_field")
    product_id = data.get("product_id")
    
    if edit_field == "type" and product_id:
        # Обновляем тип товара
        success = await repo.products.update_product_field(product_id, "type", message.text)
        
        if success:
            product = await repo.products.get_product_by_id(product_id)
            await message.answer(f"Тип товара успешно изменен на: {message.text}")
            
            # Возвращаемся к просмотру товара
            await message.answer(
                f"📦 Информация о товаре:\n\n"
                f"ID: {product.product_id}\n"
                f"Название: {product.name}\n"
                f"Описание: {product.description}\n"
                f"Тип: {product.type}\n"
                f"Материал: {product.material}\n"
                f"Цена: {product.price}\n",
                reply_markup=product_details_keyboard(product_id)
            )
        else:
            await message.answer("Ошибка при обновлении типа товара. Попробуйте снова.")
    
    await state.clear()

@admin_product_router.message(ProductManagement.material)
async def process_new_material(message: Message, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик ввода нового материала товара.
    """
    data = await state.get_data()
    edit_field = data.get("edit_field")
    product_id = data.get("product_id")
    
    if edit_field == "material" and product_id:
        # Обновляем материал товара
        success = await repo.products.update_product_field(product_id, "material", message.text)
        
        if success:
            product = await repo.products.get_product_by_id(product_id)
            await message.answer(f"Материал товара успешно изменен на: {message.text}")
            
            # Возвращаемся к просмотру товара
            await message.answer(
                f"📦 Информация о товаре:\n\n"
                f"ID: {product.product_id}\n"
                f"Название: {product.name}\n"
                f"Описание: {product.description}\n"
                f"Тип: {product.type}\n"
                f"Материал: {product.material}\n"
                f"Цена: {product.price}\n",
                reply_markup=product_details_keyboard(product_id)
            )
        else:
            await message.answer("Ошибка при обновлении материала товара. Попробуйте снова.")
    
    await state.clear()

@admin_product_router.message(ProductManagement.price)
async def process_new_price(message: Message, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик ввода новой цены товара.
    """
    data = await state.get_data()
    edit_field = data.get("edit_field")
    product_id = data.get("product_id")
    
    try:
        price = float(message.text)
        
        if edit_field == "price" and product_id:
            # Обновляем цену товара
            success = await repo.products.update_product_field(product_id, "price", price)
            
            if success:
                product = await repo.products.get_product_by_id(product_id)
                await message.answer(f"Цена товара успешно изменена на: {price}")
                
                # Возвращаемся к просмотру товара
                await message.answer(
                    f"📦 Информация о товаре:\n\n"
                    f"ID: {product.product_id}\n"
                    f"Название: {product.name}\n"
                    f"Описание: {product.description}\n"
                    f"Тип: {product.type}\n"
                    f"Материал: {product.material}\n"
                    f"Цена: {product.price}\n",
                    reply_markup=product_details_keyboard(product_id)
                )
            else:
                await message.answer("Ошибка при обновлении цены товара. Попробуйте снова.")
        
        await state.clear()
    except ValueError:
        await message.answer("Введите корректное числовое значение для цены.")

@admin_product_router.message(ProductManagement.image_url, F.photo)
async def process_new_image(message: Message, state: FSMContext, repo: RequestsRepo):
    """
    Обработчик загрузки нового изображения товара.
    """
    data = await state.get_data()
    edit_field = data.get("edit_field")
    product_id = data.get("product_id")
    
    if edit_field == "image_url" and product_id:
        # Берем идентификатор фото с лучшим разрешением
        photo_id = message.photo[-1].file_id
        
        # Обновляем изображение товара
        success = await repo.products.update_product_field(product_id, "image_url", photo_id)
        
        if success:
            product = await repo.products.get_product_by_id(product_id)
            await message.answer("Изображение товара успешно обновлено.")
            
            # Возвращаемся к просмотру товара
            await message.answer_photo(
                photo=product.image_url,
                caption=f"📦 Информация о товаре:\n\n"
                        f"ID: {product.product_id}\n"
                        f"Название: {product.name}\n"
                        f"Описание: {product.description}\n"
                        f"Тип: {product.type}\n"
                        f"Материал: {product.material}\n"
                        f"Цена: {product.price}\n",
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
    await state.update_data(previous_state=None)  # Сбрасываем предыдущее состояние
    await callback.message.edit_text("Введите название товара", reply_markup=back_button_keyboard())
    await state.set_state(ProductManagement.name)

@admin_product_router.message(ProductManagement.name)
async def set_product_name(message: Message, state: FSMContext):
    """
    Установка имени товара.
    """
    logging.info(f"Пользователь {message.from_user.id} ввёл имя товара: {message.text}")
    await state.update_data(previous_state=ProductManagement.name)  # Сохраняем текущее состояние
    await state.update_data(name=message.text)
    await message.answer("Введите описание товара", reply_markup=back_button_keyboard())
    await state.set_state(ProductManagement.description)

@admin_product_router.message(ProductManagement.description)
async def set_product_description(message: Message, state: FSMContext):
    """
    Установка описания товара.
    """
    logging.info(f"Пользователь {message.from_user.id} ввёл описание товара: {message.text}")
    await state.update_data(previous_state=ProductManagement.description)  # Сохраняем текущее состояние
    await state.update_data(description=message.text)
    await message.answer("Введите тип товара (например, 'дверь', 'аксессуар')", reply_markup=back_button_keyboard())
    await state.set_state(ProductManagement.type)

@admin_product_router.message(ProductManagement.type)
async def set_product_type(message: Message, state: FSMContext):
    """
    Установка типа товара.
    """
    logging.info(f"Пользователь {message.from_user.id} ввёл тип товара: {message.text}")
    await state.update_data(previous_state=ProductManagement.type)  # Сохраняем текущее состояние
    await state.update_data(type=message.text)
    await message.answer("Введите материал товара", reply_markup=back_button_keyboard())
    await state.set_state(ProductManagement.material)

@admin_product_router.message(ProductManagement.material)
async def set_product_material(message: Message, state: FSMContext):
    """
    Установка материала товара.
    """
    logging.info(f"Пользователь {message.from_user.id} ввёл материал товара: {message.text}")
    await state.update_data(previous_state=ProductManagement.material)  # Сохраняем текущее состояние
    await state.update_data(material=message.text)
    await message.answer("Введите цену товара", reply_markup=back_button_keyboard())
    await state.set_state(ProductManagement.price)

@admin_product_router.message(ProductManagement.price)
async def set_product_price(message: Message, state: FSMContext):
    """
    Установка цены товара.
    """
    try:
        price = float(message.text)
        logging.info(f"Пользователь {message.from_user.id} ввёл цену товара: {price}")
        await state.update_data(previous_state=ProductManagement.price)  # Сохраняем текущее состояние
        await state.update_data(price=price)
    except ValueError:
        await message.answer("Цена должна быть числом. Попробуйте ещё раз.")
        return

    await message.answer("Прикрепите фото товара", reply_markup=back_button_keyboard())
    await state.set_state(ProductManagement.image_url)

@admin_product_router.message(ProductManagement.image_url, F.photo)
async def set_product_image(message: Message, state: FSMContext):
    """
    Подготовка к подтверждению добавления товара.
    """
    logging.info(f"Пользователь {message.from_user.id} прикрепил фото товара.")
    await state.update_data(previous_state=ProductManagement.image_url)  # Сохраняем текущее состояние
    await state.update_data(image_url=message.photo[-1].file_id)
    data = await state.get_data()

    # Формируем сообщение для подтверждения данных
    confirm_text = (
        f"📦 Проверьте данные нового товара:\n\n"
        f"Название: {data['name']}\n"
        f"Описание: {data['description']}\n"
        f"Тип: {data['type']}\n"
        f"Материал: {data['material']}\n"
        f"Цена: {data['price']}\n"
    )

    # Создаем клавиатуру для подтверждения
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, всё верно", callback_data="confirm_add_product")
    builder.button(text="❌ Нет, создать заново", callback_data="cancel_add_product")
    builder.adjust(1)  # По одной кнопке в строке
    
    # Отправляем фото с информацией и запросом подтверждения
    await message.answer_photo(
        photo=data['image_url'],
        caption=confirm_text,
        reply_markup=builder.as_markup()
    )
    
    await state.set_state(ProductManagement.confirm)

@admin_product_router.callback_query(F.data == "confirm_add_product", ProductManagement.confirm)
async def confirm_add_product(callback: CallbackQuery, state: FSMContext, repo: RequestsRepo):
    """
    Подтверждение и сохранение товара в БД.
    """
    data = await state.get_data()
    
    # Формируем данные для сохранения в БД
    product_data = {
        "name": data['name'],
        "description": data['description'],
        "type": data['type'],
        "material": data['material'],
        "price": data['price'],
        "image_url": data['image_url']
    }
    
    # Сохраняем товар в БД
    try:
        new_product = await repo.products.create_product(product_data)
        logging.info(f"Создан новый товар с ID: {new_product.product_id}")
        
        await callback.message.edit_caption(
            caption=f"✅ Товар успешно добавлен!\n\n"
                   f"ID: {new_product.product_id}\n"
                   f"Название: {new_product.name}\n"
                   f"Тип: {new_product.type}\n"
                   f"Цена: {new_product.price}"
        )
        
        # Предлагаем дальнейшие действия
        await callback.message.answer(
            "Выберите дальнейшее действие:",
            reply_markup=product_management_keyboard()
        )
    except Exception as e:
        logging.error(f"Ошибка при добавлении товара: {e}")
        await callback.message.edit_caption(
            caption="❌ Произошла ошибка при сохранении товара. Попробуйте снова."
        )
    
    await state.clear()

@admin_product_router.callback_query(F.data == "cancel_add_product", ProductManagement.confirm)
async def cancel_add_product(callback: CallbackQuery, state: FSMContext):
    """
    Отмена добавления товара и начало заново.
    """
    await callback.message.delete()
    await callback.message.answer("Добавление товара отменено. Начнем заново.")
    
    # Возвращаемся к началу добавления товара
    await callback.message.answer("Введите название товара", reply_markup=back_button_keyboard())
    await state.clear()
    await state.set_state(ProductManagement.name)

@admin_product_router.callback_query(F.data == "go_back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    """
    Возвращение на предыдущий шаг.
    """
    logging.info(f"Пользователь {callback.from_user.id} нажал 'Назад'.")
    data = await state.get_data()
    previous_state = data.get("previous_state")

    if not previous_state:
        # Если предыдущего состояния нет, возвращаем в меню управления товарами
        try:
            await callback.message.delete()
        except Exception:
            pass
            
        await callback.message.answer(
            "Выберите действие с товарами:",
            reply_markup=product_management_keyboard()
        )
        await state.clear()
        return

    # Возвращаемся к предыдущему состоянию
    await state.set_state(previous_state)

    # Отображаем соответствующее сообщение для предыдущего состояния с сохраненными данными
    if previous_state == ProductManagement.name:
        prev_value = data.get('name', '')
        if prev_value:
            prompt = f"Введите название товара\n\nТекущее значение: {prev_value}"
        else:
            prompt = "Введите название товара"
            
        try:
            await callback.message.edit_text(prompt, reply_markup=back_button_keyboard())
        except Exception:
            await callback.message.answer(prompt, reply_markup=back_button_keyboard())
            
    elif previous_state == ProductManagement.description:
        prev_value = data.get('description', '')
        if prev_value:
            prompt = f"Введите описание товара\n\nТекущее значение: {prev_value}"
        else:
            prompt = "Введите описание товара"
            
        try:
            await callback.message.edit_text(prompt, reply_markup=back_button_keyboard())
        except Exception:
            await callback.message.answer(prompt, reply_markup=back_button_keyboard())
            
    elif previous_state == ProductManagement.type:
        prev_value = data.get('type', '')
        if prev_value:
            prompt = f"Введите тип товара (например, 'дверь', 'аксессуар')\n\nТекущее значение: {prev_value}"
        else:
            prompt = "Введите тип товара (например, 'дверь', 'аксессуар')"
            
        try:
            await callback.message.edit_text(prompt, reply_markup=back_button_keyboard())
        except Exception:
            await callback.message.answer(prompt, reply_markup=back_button_keyboard())
            
    elif previous_state == ProductManagement.material:
        prev_value = data.get('material', '')
        if prev_value:
            prompt = f"Введите материал товара\n\nТекущее значение: {prev_value}"
        else:
            prompt = "Введите материал товара"
            
        try:
            await callback.message.edit_text(prompt, reply_markup=back_button_keyboard())
        except Exception:
            await callback.message.answer(prompt, reply_markup=back_button_keyboard())
            
    elif previous_state == ProductManagement.price:
        prev_value = data.get('price', '')
        if prev_value:
            prompt = f"Введите цену товара\n\nТекущее значение: {prev_value}"
        else:
            prompt = "Введите цену товара"
            
        try:
            await callback.message.edit_text(prompt, reply_markup=back_button_keyboard())
        except Exception:
            await callback.message.answer(prompt, reply_markup=back_button_keyboard())
            
    elif previous_state == ProductManagement.image_url:
        # Если возвращаемся к загрузке фото, просто предлагаем загрузить фото снова
        try:
            await callback.message.edit_text("Прикрепите фото товара", reply_markup=back_button_keyboard())
        except Exception:
            await callback.message.answer("Прикрепите фото товара", reply_markup=back_button_keyboard())

    logging.info(f"Возвращение к состоянию: {previous_state}")
