"""
Handlers for creating new promotions
"""
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from infrastructure.database.models.promotions import DiscountType
from infrastructure.database.repositories.promotion_repo import PromotionRepo
from infrastructure.database.repositories.products import ProductsRepo
from tgbot.keyboards.admin_promotion import admin_back_button, product_selection_keyboard
from .base import PromotionManagement, show_promotion_details

logger = logging.getLogger(__name__)

def register_create_handlers(router: Router):
    """
    Register all handlers related to creating promotions
    """
    # Start promotion creation
    router.callback_query.register(
        add_promotion_start, 
        F.data == "add_promotion"
    )
    
    # Process name input
    router.message.register(
        process_promotion_name, 
        PromotionManagement.add_name
    )
    
    # Process description input
    router.message.register(
        process_promotion_description, 
        PromotionManagement.add_description
    )
    
    # Process discount type input
    router.message.register(
        process_discount_type, 
        PromotionManagement.add_discount_type
    )
    
    # Process discount value input
    router.message.register(
        process_discount_value, 
        PromotionManagement.add_discount_value
    )
    
    # Process start date input
    router.message.register(
        process_start_date, 
        PromotionManagement.add_start_date
    )
    
    # Process end date input
    router.message.register(
        process_end_date, 
        PromotionManagement.add_end_date
    )
    
    # Process product selection
    router.callback_query.register(
        process_product_selection, 
        PromotionManagement.add_select_products, 
        F.data.regexp(r"^select_product_(\d+)$")
    )
    
    # Confirm product selection
    router.callback_query.register(
        confirm_products, 
        PromotionManagement.add_select_products, 
        F.data == "confirm_product_selection"
    )
    
    # Final confirmation
    router.callback_query.register(
        confirm_add_promotion, 
        PromotionManagement.add_confirm, 
        F.data == "confirm_add_promotion"
    )
    
    # Cancel creation
    router.callback_query.register(
        cancel_add_promotion, 
        PromotionManagement.add_confirm, 
        F.data == "cancel_add_promotion"
    )

async def add_promotion_start(callback: CallbackQuery, state: FSMContext):
    """
    Starts the process of adding a new promotion.
    """
    await callback.message.edit_text(
        "Давайте создадим новую акцию!\n\n"
        "Введите название акции:",
        reply_markup=admin_back_button("manage_promotions"),
        parse_mode="Markdown"
    )
    await state.set_state(PromotionManagement.add_name)
    await callback.answer()

async def process_promotion_name(message: Message, state: FSMContext):
    """
    Processes the promotion name input and requests description.
    """
    name = message.text.strip()
    
    # Verify name validity
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

async def process_promotion_description(message: Message, state: FSMContext):
    """
    Processes the promotion description and requests discount type.
    """
    description = message.text.strip()
    
    await state.update_data(description=description)
    await message.answer(
        "Выберите тип скидки:\n"
        "1. Процентная скидка (например, 10% от цены)\n"
        "2. Фиксированная скидка (например, 500₽)"
    )
    await state.set_state(PromotionManagement.add_discount_type)

async def process_discount_type(message: Message, state: FSMContext):
    """
    Processes the discount type selection and requests discount value.
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

async def process_discount_value(message: Message, state: FSMContext):
    """
    Processes the discount value and requests start date.
    """
    try:
        value = float(message.text.strip())
        if value <= 0:
            raise ValueError("Скидка должна быть положительным числом")
        
        data = await state.get_data()
        discount_type = data.get("discount_type")
        
        # Validate percentage is not over 100%
        if discount_type == DiscountType.PERCENTAGE.value and value > 100:
            await message.answer(
                "❌ Процент скидки не может быть больше 100%. Пожалуйста, введите корректное значение:"
            )
            return
            
        await state.update_data(discount_value=value)
        
        # Request start date (default is today)
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

async def process_start_date(message: Message, state: FSMContext):
    """
    Processes start date and requests end date.
    """
    date_text = message.text.strip()
    
    if not date_text:
        # Use today as default
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
    
    # Request end date (optional)
    await message.answer(
        "Введите дату окончания акции в формате ДД-ММ-ГГГГ:\n"
        "Или оставьте пустым, если акция бессрочная."
    )
    await state.set_state(PromotionManagement.add_end_date)

async def process_end_date(message: Message, state: FSMContext, product_repo: ProductsRepo):
    """
    Processes end date and shows product selection.
    """
    date_text = message.text.strip()
    data = await state.get_data()
    start_date = data.get("start_date")
    
    if not date_text:
        # No end date, promotion is indefinite
        end_date = None
    else:
        try:
            end_date = datetime.strptime(date_text, "%d-%m-%Y")
            
            # Validate end date is after start date
            if end_date < start_date:
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
    
    # Request product selection
    products = await product_repo.get_all_products()
    
    if not products:
        await message.answer(
            "❌ В системе нет товаров, к которым можно применить акцию. Сначала добавьте товары."
        )
        await state.clear()
        return
    
    await message.answer(
        "Выберите товары, к которым применяется акция:",
        reply_markup=product_selection_keyboard(products)
    )
    await state.update_data(selected_products=[])
    await state.set_state(PromotionManagement.add_select_products)

async def process_product_selection(callback: CallbackQuery, state: FSMContext, product_repo: ProductsRepo):
    """
    Handles product selection for the promotion.
    """
    product_id = int(callback.data.split('_')[-1])
    
    # Get current selected products
    data = await state.get_data()
    selected_products = data.get("selected_products", [])
    
    # Toggle product selection
    if product_id in selected_products:
        selected_products.remove(product_id)
    else:
        selected_products.append(product_id)
    
    # Update state data
    await state.update_data(selected_products=selected_products)
    
    # Refresh product selection display
    products = await product_repo.get_all_products()
    
    await callback.message.edit_text(
        "Выберите товары, к которым применяется акция:",
        reply_markup=product_selection_keyboard(products, selected_products)
    )
    await callback.answer()

async def confirm_products(callback: CallbackQuery, state: FSMContext):
    """
    Confirms product selection and shows final promotion summary.
    """
    # Get all promotion data
    data = await state.get_data()
    
    # Format dates for display
    start_date = data['start_date'].strftime("%d-%m-%Y")
    end_date = data['end_date'].strftime("%d-%m-%Y") if data.get('end_date') else "бессрочно"
    
    # Format discount for display
    discount_type = "Процентная" if data['discount_type'] == DiscountType.PERCENTAGE.value else "Фиксированная"
    discount_value = f"{data['discount_value']}%" if data['discount_type'] == DiscountType.PERCENTAGE.value else f"{data['discount_value']}₽"
    
    # Create confirmation keyboard
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_add_promotion"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_add_promotion")
    )
    
    # Show promotion summary
    await callback.message.edit_text(
        f"Проверьте данные акции перед созданием:\n\n"
        f"Название: {data['name']}\n"
        f"Описание: {data['description']}\n"
        f"Тип скидки: {discount_type}\n"
        f"Значение скидки: {discount_value}\n"
        f"Период: с {start_date} по {end_date}\n"
        f"Выбрано товаров: {len(data['selected_products'])}\n\n"
        f"Всё верно?",
        reply_markup=builder.as_markup()
    )
    
    await state.set_state(PromotionManagement.add_confirm)
    await callback.answer()

async def confirm_add_promotion(callback: CallbackQuery, state: FSMContext, repo: PromotionRepo):
    """
    Creates the new promotion with all the collected data.
    """
    # Get all promotion data
    data = await state.get_data()
    
    try:
        # Create the promotion
        promo_id = await repo.create_promotion(
            name=data['name'],
            description=data['description'],
            discount_type=data['discount_type'],
            discount_value=data['discount_value'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            is_active=True
        )
        
        if promo_id:
            # Associate products with the promotion
            if data['selected_products']:
                await repo.update_promotion_products(promo_id, data['selected_products'])
            
            await callback.answer("✅ Акция успешно создана!", show_alert=True)
            
            # Show the created promotion
            promotion = await repo.get_promotion_by_id(promo_id)
            await show_promotion_details(callback=callback, promotion=promotion, promo_id=promo_id, repo=repo)
        else:
            await callback.answer("❌ Не удалось создать акцию. Пожалуйста, попробуйте позже.", show_alert=True)
            await callback.message.edit_text(
                "Произошла ошибка при создании акции. Вернитесь в меню управления акциями.",
                reply_markup=admin_back_button("manage_promotions")
            )
    except Exception as e:
        logger.error(f"Error creating promotion: {e}")
        await callback.answer("❌ Ошибка при создании акции.", show_alert=True)
        await callback.message.edit_text(
            f"Произошла ошибка при создании акции: {str(e)}",
            reply_markup=admin_back_button("manage_promotions")
        )
    
    # Clear state
    await state.clear()

async def cancel_add_promotion(callback: CallbackQuery, state: FSMContext):
    """
    Cancels promotion creation and returns to the promotion management menu.
    """
    from tgbot.keyboards.admin_promotion import promotion_management_keyboard
    
    await state.clear()
    await callback.answer("❌ Создание акции отменено", show_alert=True)
    
    await callback.message.edit_text(
        "Создание акции отменено. Вернитесь в меню управления акциями:",
        reply_markup=promotion_management_keyboard()
    )