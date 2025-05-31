from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime, timedelta
import logging
from infrastructure.database.repositories.promotion_repo import PromotionRepo
from infrastructure.database.repositories.products import ProductsRepo
from infrastructure.database.repositories.admin_log_repo import AdminLogRepo
from infrastructure.database.repositories.admin_user_repo import AdminUserRepo
from infrastructure.database.repositories.subscription_repo import SubscriptionRepo
from infrastructure.database.models.promotions import DiscountType
from infrastructure.database.models.subscriptions import SubscriptionType
from tgbot.keyboards.admin_promotion import (
    promotion_management_keyboard,
    promotion_list_keyboard,
    promotion_edit_keyboard,
    product_selection_keyboard,
    admin_back_button
)
from tgbot.filters.admin import AdminFilter

# Set up logging
logger = logging.getLogger(__name__)

# Состояния для управления акциями
class PromotionManagement(StatesGroup):
    # Добавление акции
    add_name = State()
    add_description = State()
    add_discount_type = State()
    add_discount_value = State()
    add_start_date = State()
    add_end_date = State()
    add_select_products = State()
    add_confirm = State()
    
    # Редактирование акции
    edit_select_promotion = State()
    edit_select_field = State()
    edit_name = State()
    edit_description = State()
    edit_discount_type = State()
    edit_discount_value = State()
    edit_start_date = State()
    edit_end_date = State()
    edit_is_active = State()
    
    # Управление товарами в акции
    manage_products = State()
    
    # Удаление акции
    delete_confirm = State()

admin_promotion_router = Router()
admin_promotion_router.message.filter(AdminFilter())
admin_promotion_router.callback_query.filter(AdminFilter())

@admin_promotion_router.callback_query(F.data == "manage_promotions")
async def manage_promotions_menu(callback: CallbackQuery):
    """
    Показывает меню управления акциями и скидками.
    """
    await callback.message.edit_text(
        "🏷️ *Управление акциями и скидками*\n\nВыберите действие:",
        reply_markup=promotion_management_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@admin_promotion_router.callback_query(F.data == "add_promotion")
async def add_promotion_start(callback: CallbackQuery, state: FSMContext):
    """
    Начинает процесс добавления новой акции.
    """
    await callback.message.edit_text(
        "Давайте создадим новую акцию!\n\n"
        "Введите название акции:",
        reply_markup=admin_back_button("manage_promotions"),
        parse_mode="Markdown"
    )
    await state.set_state(PromotionManagement.add_name)
    await callback.answer()

@admin_promotion_router.message(PromotionManagement.add_name)
async def process_promotion_name(message: Message, state: FSMContext):
    """
    Обрабатывает ввод названия акции.
    """
    name = message.text.strip()
    
    # Проверяем корректность названия
    if not name or len(name) > 100:
        await message.answer(
            "❌ Название должно быть от 1 до 100 символов.\n"
            "Пожалуйста, попробуйте снова:"
        )
        return
    
    await state.update_data(name=name)
    await message.answer(
        "Введите описание акции:"
    )
    await state.set_state(PromotionManagement.add_description)

@admin_promotion_router.message(PromotionManagement.add_description)
async def process_promotion_description(message: Message, state: FSMContext):
    """
    Обрабатывает ввод описания акции.
    """
    description = message.text.strip()
    
    await state.update_data(description=description)
    await message.answer(
        "Выберите тип скидки:\n"
        "1. Процентная скидка (например, 10% от цены)\n"
        "2. Фиксированная скидка (например, 500₽)"
    )
    await state.set_state(PromotionManagement.add_discount_type)

@admin_promotion_router.message(PromotionManagement.add_discount_type)
async def process_discount_type(message: Message, state: FSMContext):
    """
    Обрабатывает выбор типа скидки.
    """
    selection = message.text.strip()
    
    if selection == "1":
        discount_type = DiscountType.PERCENTAGE.value
        await state.update_data(discount_type=discount_type)
        await message.answer(
            "Введите процент скидки (например, 10 для 10%):"
        )
        await state.set_state(PromotionManagement.add_discount_value)
    elif selection == "2":
        discount_type = DiscountType.FIXED.value
        await state.update_data(discount_type=discount_type)
        await message.answer(
            "Введите сумму скидки в рублях (например, 500):"
        )
        await state.set_state(PromotionManagement.add_discount_value)
    else:
        await message.answer(
            "❌ Пожалуйста, выберите 1 для процентной скидки или 2 для фиксированной скидки."
        )

@admin_promotion_router.message(PromotionManagement.add_discount_value)
async def process_discount_value(message: Message, state: FSMContext):
    """
    Обрабатывает ввод значения скидки.
    """
    try:
        value = float(message.text.strip())
        if value <= 0:
            raise ValueError("Скидка должна быть положительным числом")
        
        data = await state.get_data()
        discount_type = data.get("discount_type")
        
        # Проверяем, что процент скидки не больше 100%
        if discount_type == DiscountType.PERCENTAGE.value and value > 100:
            await message.answer(
                "❌ Процент скидки не может быть больше 100%. Пожалуйста, введите корректное значение:"
            )
            return
            
        await state.update_data(discount_value=value)
        
        # Запрашиваем дату начала (по умолчанию - сегодня)
        today = datetime.now().strftime("%d-%m-%Y")
        await message.answer(
            f"Введите дату начала акции в формате ДД-ММ-ГГГГ:\n"
            f"Или нажмите Enter, чтобы использовать сегодняшнюю дату ({today})"
        )
        await state.set_state(PromotionManagement.add_start_date)
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите корректное числовое значение для скидки."
        )

@admin_promotion_router.message(PromotionManagement.add_start_date)
async def process_start_date(message: Message, state: FSMContext):
    """
    Обрабатывает ввод даты начала акции.
    """
    date_text = message.text.strip()
    
    if not date_text:
        # Используем сегодняшнюю дату по умолчанию
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        try:
            start_date = datetime.strptime(date_text, "%d-%m-%Y")
        except ValueError:
            await message.answer(
                "❌ Неверный формат даты. Пожалуйста, используйте формат ДД-ММ-ГГГГ."
            )
            return
    
    await state.update_data(start_date=start_date)
    
    # Запрашиваем дату окончания (опционально)
    await message.answer(
        "Введите дату окончания акции в формате ДД-ММ-ГГГГ:\n"
        "Или нажмите Enter, чтобы сделать акцию бессрочной"
    )
    await state.set_state(PromotionManagement.add_end_date)

@admin_promotion_router.message(PromotionManagement.add_end_date)
async def process_end_date(message: Message, state: FSMContext, products_repo: ProductsRepo):
    """
    Обрабатывает ввод даты окончания акции и запрашивает выбор товаров.
    """
    date_text = message.text.strip()
    
    if not date_text:
        # Бессрочная акция
        end_date = None
    else:
        try:
            end_date = datetime.strptime(date_text, "%d-%m-%Y")
            
            # Проверяем, что дата окончания после даты начала
            data = await state.get_data()
            start_date = data.get("start_date")
            
            if end_date <= start_date:
                await message.answer(
                    "❌ Дата окончания должна быть позже даты начала. Пожалуйста, введите корректную дату:"
                )
                return
        except ValueError:
            await message.answer(
                "❌ Неверный формат даты. Пожалуйста, используйте формат ДД-ММ-ГГГГ."
            )
            return
    
    await state.update_data(end_date=end_date)
    
    # Получаем товары для выбора
    products = await products_repo.get_all_products()
    
    if products:
        await message.answer(
            "Выберите товары для применения акции:",
            reply_markup=product_selection_keyboard(products)
        )
        await state.set_state(PromotionManagement.add_select_products)
    else:
        await message.answer(
            "❌ Товары не найдены. Сначала добавьте товары в каталог."
        )
        await state.clear()

@admin_promotion_router.callback_query(F.data.startswith("select_product_"), PromotionManagement.add_select_products)
async def select_product_for_promotion(callback: CallbackQuery, state: FSMContext, products_repo: ProductsRepo):
    """
    Обрабатывает выбор товара для акции.
    """
    product_id = int(callback.data.split("_")[2])
    
    data = await state.get_data()
    selected_products = data.get("selected_products", [])
    
    if product_id in selected_products:
        selected_products.remove(product_id)
    else:
        selected_products.append(product_id)
    
    await state.update_data(selected_products=selected_products)
    
    # Обновляем клавиатуру для отображения выбора
    products = await products_repo.get_all_products()
    await callback.message.edit_reply_markup(
        reply_markup=product_selection_keyboard(products, selected_products)
    )
    await callback.answer()

@admin_promotion_router.callback_query(F.data == "confirm_product_selection", PromotionManagement.add_select_products)
async def confirm_product_selection(callback: CallbackQuery, state: FSMContext, products_repo: ProductsRepo):
    """
    Подтверждает выбор товаров и показывает сводку по акции.
    """
    data = await state.get_data()
    selected_products = data.get("selected_products", [])
    
    if not selected_products:
        await callback.message.edit_text(
            "❌ Пожалуйста, выберите хотя бы один товар для акции.",
            reply_markup=admin_back_button("manage_promotions")
        )
        await callback.answer()
        return
    
    # Получаем названия товаров для сводки
    product_names = []
    for product_id in selected_products:
        product = await products_repo.get_product_by_id(product_id)
        if product:
            product_names.append(product.name)
    
    # Форматируем даты для отображения
    start_date_str = data.get("start_date").strftime("%d-%m-%Y") if data.get("start_date") else "Сегодня"
    end_date_str = data.get("end_date").strftime("%d-%m-%Y") if data.get("end_date") else "Бессрочно"
    
    # Формируем сводку
    discount_type_display = "процентная" if data.get("discount_type") == DiscountType.PERCENTAGE.value else "фиксированная"
    discount_value_display = f"{data.get('discount_value')}%" if data.get("discount_type") == DiscountType.PERCENTAGE.value else f"{data.get('discount_value')}₽"
    
    summary = (
        f"🏷️ *Сводка по акции:*\n\n"
        f"Название: {data.get('name')}\n"
        f"Описание: {data.get('description')}\n"
        f"Скидка: {discount_value_display} ({discount_type_display})\n"
        f"Дата начала: {start_date_str}\n"
        f"Дата окончания: {end_date_str}\n"
        f"Товары: {', '.join(product_names)}\n\n"
        f"Для подтверждения введите 'да' или 'нет' для отмены."
    )
    
    await callback.message.edit_text(summary, parse_mode="Markdown")
    await state.set_state(PromotionManagement.add_confirm)
    await callback.answer()

@admin_promotion_router.message(PromotionManagement.add_confirm)
async def confirm_add_promotion(message: Message, state: FSMContext, 
                               promo_repo: PromotionRepo, admin_repo: AdminUserRepo, 
                               log_repo: AdminLogRepo, sub_repo: SubscriptionRepo, bot):
    """
    Подтверждает создание акции.
    """
    confirmation = message.text.strip().lower()
    
    if confirmation in ["да", "yes", "y", "д"]:
        data = await state.get_data()
        
        # Подготавливаем данные для создания акции
        promotion_data = {
            "name": data.get("name"),
            "description": data.get("description"),
            "discount_type": data.get("discount_type"),
            "discount_value": data.get("discount_value"),
            "start_date": data.get("start_date"),
            "end_date": data.get("end_date"),
            "is_active": True
        }
        
        # Получаем ID администратора
        admin = await admin_repo.get_admin_by_user_id(message.from_user.id)
        if admin:
            promotion_data["created_by"] = admin.admin_id
        
        # Создаем акцию
        promotion = await promo_repo.create_promotion(promotion_data)
        
        if promotion:
            # Применяем акцию к выбранным товарам
            selected_products = data.get("selected_products", [])
            for product_id in selected_products:
                await promo_repo.apply_promotion_to_product(promotion.promo_id, product_id)
            
            # Логируем действие
            if admin:
                await log_repo.log_action(
                    admin_id=admin.admin_id,
                    action="add_promotion",
                    entity_type="promotion",
                    entity_id=promotion.promo_id,
                    details=f"Добавлена акция: {promotion.name} с {len(selected_products)} товарами"
                )
            
            # Отправляем уведомления подписчикам
            subscribers = await sub_repo.get_subscribers_by_type(SubscriptionType.PROMOTIONS.value)
            
            if subscribers:
                # Формируем текст уведомления
                notification_text = (
                    f"🎉 *Новая акция в магазине!*\n\n"
                    f"*{promotion.name}*\n"
                    f"{promotion.description}\n\n"
                    f"Скидка: {data.get('discount_value')}% на выбранные товары\n"
                    f"Действует с {start_date_str} по {end_date_str}\n\n"
                    f"Откройте каталог, чтобы увидеть товары со скидкой!"
                )
                
                # Отправляем уведомление каждому подписчику
                success_count = 0
                for user_id in subscribers:
                    try:
                        await bot.send_message(
                            chat_id=user_id,
                            text=notification_text,
                            parse_mode="Markdown"
                        )
                        success_count += 1
                    except Exception as e:
                        logger.error(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")
                
                await message.answer(
                    f"✅ Акция '{promotion.name}' успешно создана и применена к {len(selected_products)} товарам!\n"
                    f"Отправлено уведомлений: {success_count} из {len(subscribers)}"
                )
            else:
                await message.answer(
                    f"✅ Акция '{promotion.name}' успешно создана и применена к {len(selected_products)} товарам!"
                )
        else:
            await message.answer(
                "❌ Не удалось создать акцию. Пожалуйста, попробуйте позже."
            )
    else:
        await message.answer(
            "Создание акции отменено."
        )
    
    await state.clear()

@admin_promotion_router.callback_query(F.data == "view_promotions")
async def view_promotions_list(callback: CallbackQuery, promo_repo: PromotionRepo):
    """
    Показывает список всех акций.
    """
    # Получаем все акции
    promotions = await promo_repo.get_all()
    
    if promotions:
        active_promotions = [p for p in promotions if p.is_active]
        inactive_promotions = [p for p in promotions if not p.is_active]
        
        text = "🏷️ *Список акций*\n\n"
        
        # Активные акции
        if active_promotions:
            text += "*Активные акции:*\n"
            for i, promo in enumerate(active_promotions, 1):
                status = "✅ Действует" if promo.is_valid else "⏳ Ожидает начала"
                end_date = promo.end_date.strftime("%d.%m.%Y") if promo.end_date else "бессрочно"
                text += f"{i}. {promo.name} - {status} (до {end_date})\n"
        else:
            text += "Нет активных акций.\n"
            
        text += "\n"
        
        # Неактивные акции
        if inactive_promotions:
            text += "*Неактивные акции:*\n"
            for i, promo in enumerate(inactive_promotions, 1):
                text += f"{i}. {promo.name} - ❌ Завершена\n"
                
        await callback.message.edit_text(
            text,
            reply_markup=promotion_list_keyboard(promotions),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "Акции не найдены. Создайте новую акцию.",
            reply_markup=admin_back_button("manage_promotions")
        )
    
    await callback.answer()

@admin_promotion_router.callback_query(F.data.startswith("promotion_"))
async def view_promotion_details(callback: CallbackQuery, promo_repo: PromotionRepo, products_repo: ProductsRepo):
    """
    Показывает детальную информацию об акции.
    """
    promo_id = int(callback.data.split("_")[1])
    promotion = await promo_repo.get_by_id(promo_id)
    
    if not promotion:
        await callback.message.edit_text(
            "❌ Акция не найдена.",
            reply_markup=admin_back_button("view_promotions")
        )
        await callback.answer()
        return
    
    # Получаем товары, к которым применена акция
    promoted_products = await promo_repo.get_products_for_promotion(promo_id)
    
    # Форматируем даты
    start_date = promotion.start_date.strftime("%d.%m.%Y")
    end_date = promotion.end_date.strftime("%d.%m.%Y") if promotion.end_date else "бессрочно"
    
    # Форматируем скидку
    discount = f"{promotion.discount_value}%" if promotion.discount_type == DiscountType.PERCENTAGE.value else f"{promotion.discount_value}₽"
    
    # Формируем текст
    text = (
        f"🏷️ *Акция: {promotion.name}*\n\n"
        f"{promotion.description}\n\n"
        f"Тип скидки: {promotion.discount_type}\n"
        f"Размер скидки: {discount}\n"
        f"Дата начала: {start_date}\n"
        f"Дата окончания: {end_date}\n"
        f"Статус: {'✅ Активна' if promotion.is_active else '❌ Неактивна'}\n\n"
    )
    
    # Добавляем список товаров
    if promoted_products:
        text += "*Товары в акции:*\n"
        for i, product in enumerate(promoted_products[:5], 1):
            text += f"{i}. {product.name} - {product.price}₽\n"
        
        if len(promoted_products) > 5:
            text += f"... и еще {len(promoted_products) - 5} товаров\n"
    else:
        text += "Нет товаров в акции.\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=promotion_edit_keyboard(promo_id),
        parse_mode="Markdown"
    )
    await callback.answer()

# Обработчики для редактирования акций
@admin_promotion_router.callback_query(F.data.regexp(r"^edit_promotion_(\d+)$"))
async def start_edit_promotion(callback: CallbackQuery, state: FSMContext):
    """
    Начинает процесс редактирования акции.
    """
    promo_id = int(callback.data.split('_')[-1])
    
    await state.update_data(promo_id=promo_id)
    
    await callback.message.edit_text(
        "Выберите, что именно вы хотите изменить:",
        reply_markup=edit_field_keyboard(promo_id)
    )
    await state.set_state(PromotionManagement.edit_select_field)
    await callback.answer()

def edit_field_keyboard(promo_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора поля акции для редактирования.
    """
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки для каждого поля
    builder.row(
        InlineKeyboardButton(
            text="Название",
            callback_data=f"edit_field_name_{promo_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Описание",
            callback_data=f"edit_field_description_{promo_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Тип скидки",
            callback_data=f"edit_field_discount_type_{promo_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Значение скидки",
            callback_data=f"edit_field_discount_value_{promo_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Дата начала",
            callback_data=f"edit_field_start_date_{promo_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Дата окончания",
            callback_data=f"edit_field_end_date_{promo_id}"
        )
    )
    
    # Кнопка назад
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=f"promotion_{promo_id}"
        )
    )
    
    return builder.as_markup()

@admin_promotion_router.callback_query(PromotionManagement.edit_select_field, F.data.regexp(r"^edit_field_(\w+)_(\d+)$"))
async def edit_promotion_field(callback: CallbackQuery, state: FSMContext, repo: PromotionRepo):
    """
    Запрашивает новое значение для выбранного поля акции.
    """
    field, promo_id = callback.data.split('_')[2:4]
    promo_id = int(promo_id)
    
    # Получаем акцию для отображения текущего значения
    promotion = await repo.get_promotion_by_id(promo_id)
    if not promotion:
        await callback.answer("Акция не найдена", show_alert=True)
        await state.clear()
        return
    
    # В зависимости от поля, устанавливаем соответствующее состояние
    if field == "name":
        await state.set_state(PromotionManagement.edit_name)
        current_value = promotion.name
        field_name = "названия"
    elif field == "description":
        await state.set_state(PromotionManagement.edit_description)
        current_value = promotion.description
        field_name = "описания"
    elif field == "discount_type":
        await state.set_state(PromotionManagement.edit_discount_type)
        current_value = "Процентная" if promotion.discount_type == DiscountType.PERCENTAGE.value else "Фиксированная"
        field_name = "типа скидки"
        await callback.message.edit_text(
            f"Текущий тип скидки: {current_value}\n\n"
            "Выберите новый тип скидки:\n"
            "1. Процентная скидка\n"
            "2. Фиксированная скидка",
            reply_markup=admin_back_button(f"edit_promotion_{promo_id}")
        )
        await callback.answer()
        return
    elif field == "discount_value":
        await state.set_state(PromotionManagement.edit_discount_value)
        current_value = promotion.discount_value
        field_name = "значения скидки"
    elif field == "start_date":
        await state.set_state(PromotionManagement.edit_start_date)
        current_value = promotion.start_date.strftime("%d-%m-%Y") if promotion.start_date else "Не задана"
        field_name = "даты начала"
    elif field == "end_date":
        await state.set_state(PromotionManagement.edit_end_date)
        current_value = promotion.end_date.strftime("%d-%m-%Y") if promotion.end_date else "Не задана"
        field_name = "даты окончания"
    else:
        await callback.answer("Неизвестное поле", show_alert=True)
        return
    
    # Обновляем данные состояния
    await state.update_data(promo_id=promo_id, field=field)
    
    # Выводим текущее значение и просим ввести новое
    await callback.message.edit_text(
        f"Редактирование {field_name} акции\n\n"
        f"Текущее значение: {current_value}\n\n"
        f"Введите новое значение для {field_name}:",
        reply_markup=admin_back_button(f"edit_promotion_{promo_id}")
    )
    await callback.answer()

# Обработчики редактирования каждого поля
@admin_promotion_router.message(PromotionManagement.edit_name)
async def process_edit_name(message: Message, state: FSMContext, repo: PromotionRepo):
    """
    Обрабатывает ввод нового названия акции.
    """
    new_name = message.text.strip()
    
    if not new_name or len(new_name) > 100:
        await message.answer("❌ Название должно быть от 1 до 100 символов. Попробуйте снова.")
        return
    
    # Получаем данные из состояния
    data = await state.get_data()
    promo_id = data.get("promo_id")
    
    # Обновляем название акции
    try:
        updated = await repo.update_promotion(promo_id, {"name": new_name})
        if updated:
            await message.answer(f"✅ Название акции успешно изменено на '{new_name}'")
        else:
            await message.answer("❌ Не удалось обновить название акции. Попробуйте позже.")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
    
    # Отображаем акцию после обновления
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(message=message, promo_id=promo_id, promotion=promotion, repo=repo)
    await state.clear()

@admin_promotion_router.message(PromotionManagement.edit_description)
async def process_edit_description(message: Message, state: FSMContext, repo: PromotionRepo):
    """
    Обрабатывает ввод нового описания акции.
    """
    new_description = message.text.strip()
    
    # Получаем данные из состояния
    data = await state.get_data()
    promo_id = data.get("promo_id")
    
    # Обновляем описание акции
    try:
        updated = await repo.update_promotion(promo_id, {"description": new_description})
        if updated:
            await message.answer(f"✅ Описание акции успешно изменено")
        else:
            await message.answer("❌ Не удалось обновить описание акции. Попробуйте позже.")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
    
    # Отображаем акцию после обновления
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(message=message, promo_id=promo_id, promotion=promotion, repo=repo)
    await state.clear()

@admin_promotion_router.message(PromotionManagement.edit_discount_type)
async def process_edit_discount_type(message: Message, state: FSMContext, repo: PromotionRepo):
    """
    Обрабатывает ввод нового типа скидки.
    """
    selection = message.text.strip()
    
    if selection == "1":
        discount_type = DiscountType.PERCENTAGE.value
    elif selection == "2":
        discount_type = DiscountType.FIXED.value
    else:
        await message.answer("❌ Пожалуйста, выберите 1 для процентной скидки или 2 для фиксированной.")
        return
    
    # Получаем данные из состояния
    data = await state.get_data()
    promo_id = data.get("promo_id")
    
    # Обновляем тип скидки
    try:
        updated = await repo.update_promotion(promo_id, {"discount_type": discount_type})
        if updated:
            type_name = "процентную" if discount_type == DiscountType.PERCENTAGE.value else "фиксированную"
            await message.answer(f"✅ Тип скидки успешно изменен на {type_name}")
        else:
            await message.answer("❌ Не удалось обновить тип скидки. Попробуйте позже.")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
    
    # Отображаем акцию после обновления
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(message=message, promo_id=promo_id, promotion=promotion, repo=repo)
    await state.clear()

@admin_promotion_router.message(PromotionManagement.edit_discount_value)
async def process_edit_discount_value(message: Message, state: FSMContext, repo: PromotionRepo):
    """
    Обрабатывает ввод нового значения скидки.
    """
    try:
        new_value = float(message.text.strip())
        if new_value <= 0:
            raise ValueError("Скидка должна быть положительным числом")
        
        # Получаем данные из состояния
        data = await state.get_data()
        promo_id = data.get("promo_id")
        
        # Получаем текущую акцию для проверки типа скидки
        promotion = await repo.get_promotion_by_id(promo_id)
        if promotion.discount_type == DiscountType.PERCENTAGE.value and new_value > 100:
            await message.answer("❌ Процент скидки не может быть больше 100%. Пожалуйста, введите корректное значение.")
            return
        
        # Обновляем значение скидки
        updated = await repo.update_promotion(promo_id, {"discount_value": new_value})
        if updated:
            await message.answer(f"✅ Значение скидки успешно изменено на {new_value}")
        else:
            await message.answer("❌ Не удалось обновить значение скидки. Попробуйте позже.")
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное числовое значение для скидки.")
        return
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
        return
    
    # Отображаем акцию после обновления
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(message=message, promo_id=promo_id, promotion=promotion, repo=repo)
    await state.clear()

@admin_promotion_router.message(PromotionManagement.edit_start_date)
async def process_edit_start_date(message: Message, state: FSMContext, repo: PromotionRepo):
    """
    Обрабатывает ввод новой даты начала акции.
    """
    date_text = message.text.strip()
    
    # Получаем данные из состояния
    data = await state.get_data()
    promo_id = data.get("promo_id")
    
    if not date_text:
        # Используем текущую дату, если ничего не введено
        new_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        try:
            new_date = datetime.strptime(date_text, "%d-%m-%Y")
        except ValueError:
            await message.answer("❌ Неверный формат даты. Пожалуйста, используйте формат ДД-ММ-ГГГГ.")
            return
    
    # Обновляем дату начала акции
    try:
        updated = await repo.update_promotion(promo_id, {"start_date": new_date})
        if updated:
            await message.answer(f"✅ Дата начала акции успешно изменена на {new_date.strftime('%d-%m-%Y')}")
        else:
            await message.answer("❌ Не удалось обновить дату начала акции. Попробуйте позже.")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
    
    # Отображаем акцию после обновления
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(message=message, promo_id=promo_id, promotion=promotion, repo=repo)
    await state.clear()

@admin_promotion_router.message(PromotionManagement.edit_end_date)
async def process_edit_end_date(message: Message, state: FSMContext, repo: PromotionRepo):
    """
    Обрабатывает ввод новой даты окончания акции.
    """
    date_text = message.text.strip()
    
    # Получаем данные из состояния
    data = await state.get_data()
    promo_id = data.get("promo_id")
    
    # Получаем акцию для проверки даты начала
    promotion = await repo.get_promotion_by_id(promo_id)
    
    if not date_text:
        # Устанавливаем None, если ничего не введено (бессрочная акция)
        new_date = None
    else:
        try:
            new_date = datetime.strptime(date_text, "%d-%m-%Y")
            # Проверяем, что дата окончания после даты начала
            if promotion.start_date and new_date < promotion.start_date:
                await message.answer("❌ Дата окончания не может быть раньше даты начала.")
                return
        except ValueError:
            await message.answer("❌ Неверный формат даты. Пожалуйста, используйте формат ДД-ММ-ГГГГ.")
            return
    
    # Обновляем дату окончания акции
    try:
        updated = await repo.update_promotion(promo_id, {"end_date": new_date})
        if updated:
            date_str = new_date.strftime('%d-%m-%Y') if new_date else "бессрочно"
            await message.answer(f"✅ Дата окончания акции успешно изменена на {date_str}")
        else:
            await message.answer("❌ Не удалось обновить дату окончания акции. Попробуйте позже.")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
    
    # Отображаем акцию после обновления
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(message=message, promo_id=promo_id, promotion=promotion, repo=repo)
    await state.clear()

# Обработчик для изменения статуса акции
@admin_promotion_router.callback_query(F.data.regexp(r"^toggle_promo_status_(\d+)$"))
async def toggle_promotion_status(callback: CallbackQuery, repo: PromotionRepo):
    """
    Изменяет статус акции (активна/неактивна).
    """
    promo_id = int(callback.data.split('_')[-1])
    
    # Получаем текущую акцию
    promotion = await repo.get_promotion_by_id(promo_id)
    if not promotion:
        await callback.answer("Акция не найдена", show_alert=True)
        return
    
    # Инвертируем статус
    new_status = not promotion.is_active
    
    # Обновляем статус акции
    try:
        updated = await repo.update_promotion(promo_id, {"is_active": new_status})
        if updated:
            status_str = "активной" if new_status else "неактивной"
            await callback.answer(f"Акция теперь {status_str}", show_alert=True)
        else:
            await callback.answer("Не удалось обновить статус акции", show_alert=True)
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    
    # Обновляем информацию о акции
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(callback=callback, promo_id=promo_id, promotion=promotion, repo=repo)

# Обработчик для удаления акции
@admin_promotion_router.callback_query(F.data.regexp(r"^delete_promotion_(\d+)$"))
async def confirm_delete_promotion(callback: CallbackQuery, state: FSMContext):
    """
    Запрашивает подтверждение удаления акции.
    """
    promo_id = int(callback.data.split('_')[-1])
    
    # Сохраняем ID акции в состоянии
    await state.update_data(promo_id=promo_id)
    await state.set_state(PromotionManagement.delete_confirm)
    
    # Создаем клавиатуру для подтверждения
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Да, удалить",
            callback_data=f"confirm_delete_{promo_id}"
        ),
        InlineKeyboardButton(
            text="❌ Нет, отмена",
            callback_data=f"promotion_{promo_id}"
        )
    )
    
    await callback.message.edit_text(
        "⚠️ Вы уверены, что хотите удалить эту акцию?\n"
        "Это действие нельзя будет отменить.",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@admin_promotion_router.callback_query(PromotionManagement.delete_confirm, F.data.regexp(r"^confirm_delete_(\d+)$"))
async def delete_promotion(callback: CallbackQuery, state: FSMContext, repo: PromotionRepo):
    """
    Удаляет акцию после подтверждения.
    """
    promo_id = int(callback.data.split('_')[-1])
    
    # Удаляем акцию
    try:
        deleted = await repo.delete_promotion(promo_id)
        if deleted:
            await callback.answer("✅ Акция успешно удалена", show_alert=True)
        else:
            await callback.answer("❌ Не удалось удалить акцию", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
    
    # Возвращаемся к списку акций
    await state.clear()
    
    promotions = await repo.get_all_promotions()
    if promotions:
        await callback.message.edit_text(
            "Список доступных акций:",
            reply_markup=promotion_list_keyboard(promotions)
        )
    else:
        await callback.message.edit_text(
            "В системе нет акций.",
            reply_markup=promotion_management_keyboard()
        )

# Обработчик для управления товарами в акции
@admin_promotion_router.callback_query(F.data.regexp(r"^manage_promo_products_(\d+)$"))
async def manage_promotion_products(callback: CallbackQuery, state: FSMContext, repo: PromotionRepo, product_repo: ProductsRepo):
    """
    Отображает интерфейс для управления товарами в акции.
    """
    promo_id = int(callback.data.split('_')[-1])
    
    # Получаем товары в акции
    promotion = await repo.get_promotion_by_id(promo_id)
    if not promotion:
        await callback.answer("Акция не найдена", show_alert=True)
        return
    
    # Получаем все товары
    all_products = await product_repo.get_all_products()
    
    # Получаем товары в акции
    promoted_products = await repo.get_promotion_products(promo_id)
    selected_product_ids = [p.product_id for p in promoted_products]
    
    # Сохраняем данные в состоянии
    await state.update_data(promo_id=promo_id, selected_products=selected_product_ids)
    await state.set_state(PromotionManagement.manage_products)
    
    await callback.message.edit_text(
        f"Управление товарами для акции '{promotion.name}'\n\n"
        "Выберите товары, которые должны участвовать в акции:",
        reply_markup=product_selection_keyboard(all_products, selected_product_ids)
    )
    await callback.answer()

@admin_promotion_router.callback_query(PromotionManagement.manage_products, F.data.regexp(r"^select_product_(\d+)$"))
async def toggle_product_selection(callback: CallbackQuery, state: FSMContext, product_repo: ProductsRepo):
    """
    Переключает выбор товара при управлении товарами акции.
    """
    product_id = int(callback.data.split('_')[-1])
    
    # Получаем текущий список выбранных товаров из состояния
    data = await state.get_data()
    promo_id = data.get("promo_id")
    selected_products = data.get("selected_products", [])
    
    # Переключаем товар (добавляем/удаляем)
    if product_id in selected_products:
        selected_products.remove(product_id)
    else:
        selected_products.append(product_id)
    
    # Обновляем данные состояния
    await state.update_data(selected_products=selected_products)
    
    # Получаем все товары для обновления клавиатуры
    all_products = await product_repo.get_all_products()
    
    # Обновляем сообщение с новой клавиатурой
    await callback.message.edit_text(
        f"Управление товарами для акции (ID: {promo_id})\n\n"
        "Выберите товары, которые должны участвовать в акции:",
        reply_markup=product_selection_keyboard(all_products, selected_products)
    )
    await callback.answer()

@admin_promotion_router.callback_query(PromotionManagement.manage_products, F.data == "confirm_product_selection")
async def confirm_product_selection(callback: CallbackQuery, state: FSMContext, repo: PromotionRepo):
    """
    Подтверждает выбор товаров для акции.
    """
    # Получаем данные из состояния
    data = await state.get_data()
    promo_id = data.get("promo_id")
    selected_products = data.get("selected_products", [])
    
    # Обновляем товары в акции
    try:
        updated = await repo.update_promotion_products(promo_id, selected_products)
        if updated:
            await callback.answer("✅ Список товаров в акции обновлен", show_alert=True)
        else:
            await callback.answer("❌ Не удалось обновить список товаров", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
    
    # Очищаем состояние
    await state.clear()
    
    # Показываем детали акции
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(callback=callback, promo_id=promo_id, promotion=promotion, repo=repo)

async def show_promotion_details(callback: CallbackQuery = None, message: Message = None, promo_id: int = None, promotion = None, repo: PromotionRepo = None):
    """
    Вспомогательная функция для отображения деталей акции.
    """
    # Если не передан promotion, получаем его
    if not promotion:
        promotion = await repo.get_promotion_by_id(promo_id)
    
    if not promotion:
        text = "❌ Акция не найдена"
        reply_markup = promotion_management_keyboard()
    else:
        # Форматируем даты
        start_date = promotion.start_date.strftime("%d-%m-%Y") if promotion.start_date else "Не указана"
        end_date = promotion.end_date.strftime("%d-%m-%Y") if promotion.end_date else "Бессрочно"
        
        # Определяем тип скидки
        discount_type = "Процентная" if promotion.discount_type == DiscountType.PERCENTAGE.value else "Фиксированная"
        discount_value = f"{promotion.discount_value}%" if promotion.discount_type == DiscountType.PERCENTAGE.value else f"{promotion.discount_value}₽"
        
        # Формируем текст с информацией об акции
        text = (
            f"🏷️ *Акция: {promotion.name}*\n"
            f"📝 Описание: {promotion.description}\n"
            f"💰 Скидка: {discount_type}, {discount_value}\n"
            f"📅 Период: с {start_date} по {end_date}\n"
            f"Статус: {'✅ Активна' if promotion.is_active else '❌ Неактивна'}\n\n"
        )
        
        # Получаем товары в акции
        promoted_products = await repo.get_promotion_products(promo_id)
        
        # Добавляем информацию о товарах
        text += "📦 *Товары в акции:*\n"
        if promoted_products:
            for i, product in enumerate(promoted_products[:5], 1):
                text += f"{i}. {product.name} - {product.price}₽\n"
            
            if len(promoted_products) > 5:
                text += f"... и еще {len(promoted_products) - 5} товаров\n"
        else:
            text += "Нет товаров в акции.\n"
        
        reply_markup = promotion_edit_keyboard(promo_id)
    
    # Отправляем или редактируем сообщение
    if callback:
        await callback.message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    elif message:
        await message.answer(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )