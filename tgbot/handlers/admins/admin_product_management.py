# tgbot/handlers/admin_product_management.py
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from tgbot.keyboards.product_management import product_management_keyboard
from tgbot.keyboards.back_button import back_button_keyboard
from tgbot.misc.states import ProductManagement
from tgbot.keyboards.admin_main_menu import main_menu_keyboard  # Импортируем основную клавиатуру
from tgbot.filters.admin import AdminFilter
import logging

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

@admin_product_router.callback_query(F.data == "add_product")
async def start_add_product(callback: CallbackQuery, state: FSMContext):
    """
    Начало добавления нового товара.
    """
    logging.info(f"Пользователь {callback.from_user.id} начал добавление товара.")
    await state.update_data(previous_state=None)  # Сбрасываем предыдущее состояние
    await callback.message.edit_text("Введите название товара:", reply_markup=back_button_keyboard())
    await state.set_state(ProductManagement.name)

@admin_product_router.message(ProductManagement.name)
async def set_product_name(message: Message, state: FSMContext):
    """
    Установка имени товара.
    """
    logging.info(f"Пользователь {message.from_user.id} ввёл имя товара: {message.text}")
    await state.update_data(previous_state=ProductManagement.name)  # Сохраняем текущее состояние
    await state.update_data(name=message.text)
    await message.answer("Введите описание товара:", reply_markup=back_button_keyboard())
    await state.set_state(ProductManagement.description)

@admin_product_router.message(ProductManagement.description)
async def set_product_description(message: Message, state: FSMContext):
    """
    Установка описания товара.
    """
    logging.info(f"Пользователь {message.from_user.id} ввёл описание товара: {message.text}")
    await state.update_data(previous_state=ProductManagement.description)  # Сохраняем текущее состояние
    await state.update_data(description=message.text)
    await message.answer("Введите тип товара (например, 'дверь', 'аксессуар'):", reply_markup=back_button_keyboard())
    await state.set_state(ProductManagement.type)

@admin_product_router.message(ProductManagement.type)
async def set_product_type(message: Message, state: FSMContext):
    """
    Установка типа товара.
    """
    logging.info(f"Пользователь {message.from_user.id} ввёл тип товара: {message.text}")
    await state.update_data(previous_state=ProductManagement.type)  # Сохраняем текущее состояние
    await state.update_data(type=message.text)
    await message.answer("Введите материал товара:", reply_markup=back_button_keyboard())
    await state.set_state(ProductManagement.material)

@admin_product_router.message(ProductManagement.material)
async def set_product_material(message: Message, state: FSMContext):
    """
    Установка материала товара.
    """
    logging.info(f"Пользователь {message.from_user.id} ввёл материал товара: {message.text}")
    await state.update_data(previous_state=ProductManagement.material)  # Сохраняем текущее состояние
    await state.update_data(material=message.text)
    await message.answer("Введите цену товара:", reply_markup=back_button_keyboard())
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

    await message.answer("Прикрепите фото товара:", reply_markup=back_button_keyboard())
    await state.set_state(ProductManagement.image_url)

@admin_product_router.message(ProductManagement.image_url, F.photo)
async def set_product_image(message: Message, state: FSMContext):
    """
    Завершение добавления товара.
    """
    logging.info(f"Пользователь {message.from_user.id} прикрепил фото товара.")
    await state.update_data(image_url=message.photo[-1].file_id)
    data = await state.get_data()

    # Формируем сообщение о добавлении товара
    response_text = (
        f"Товар успешно добавлен:\n\n"
        f"Имя: {data['name']}\n"
        f"Описание: {data['description']}\n"
        f"Тип: {data['type']}\n"
        f"Материал: {data['material']}\n"
        f"Цена: {data['price']}\n"
    )

    await message.answer(response_text)
    await state.clear()

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
        await callback.message.edit_text(
            "Выберите действие с товарами:",
            reply_markup=product_management_keyboard()
        )
        await state.clear()
        return

    # Возвращаемся к предыдущему состоянию
    await state.set_state(previous_state)

    # Отображаем соответствующее сообщение для предыдущего состояния
    if previous_state == ProductManagement.name:
        await callback.message.edit_text("Введите название товара:", reply_markup=back_button_keyboard())
    elif previous_state == ProductManagement.description:
        await callback.message.edit_text("Введите описание товара:", reply_markup=back_button_keyboard())
    elif previous_state == ProductManagement.type:
        await callback.message.edit_text("Введите тип товара (например, 'дверь', 'аксессуар'):", reply_markup=back_button_keyboard())
    elif previous_state == ProductManagement.material:
        await callback.message.edit_text("Введите материал товара:", reply_markup=back_button_keyboard())
    elif previous_state == ProductManagement.price:
        await callback.message.edit_text("Введите цену товара:", reply_markup=back_button_keyboard())

    logging.info(f"Возвращение к состоянию: {previous_state}")
