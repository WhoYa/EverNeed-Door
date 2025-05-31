"""
Handlers for editing and deleting promotions
"""
import logging
import re
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from infrastructure.database.models.promotions import DiscountType
from infrastructure.database.repositories.promotion_repo import PromotionRepo
from tgbot.keyboards.admin_promotion import (
    admin_back_button,
    promotion_list_keyboard,
    promotion_management_keyboard,
)
from .base import PromotionManagement, show_promotion_details

logger = logging.getLogger(__name__)

def register_edit_handlers(router: Router):
    """
    Register all handlers related to editing promotions
    """
    # Start editing promotion
    router.callback_query.register(
        start_edit_promotion,
        F.data.regexp(r"^edit_promotion_(\d+)$")
    )
    
    # Edit field selection
    router.callback_query.register(
        edit_promotion_field,
        PromotionManagement.edit_select_field,
        F.data.regexp(r"^edit_field_(\w+)_(\d+)$")
    )
    
    # Field editing handlers
    router.message.register(process_edit_name, PromotionManagement.edit_name)
    router.message.register(process_edit_description, PromotionManagement.edit_description)
    router.message.register(process_edit_discount_type, PromotionManagement.edit_discount_type)
    router.message.register(process_edit_discount_value, PromotionManagement.edit_discount_value)
    router.message.register(process_edit_start_date, PromotionManagement.edit_start_date)
    router.message.register(process_edit_end_date, PromotionManagement.edit_end_date)
    
    # Toggle promotion status
    router.callback_query.register(
        toggle_promotion_status,
        F.data.regexp(r"^toggle_promo_status_(\d+)$")
    )
    
    # Delete promotion handlers
    router.callback_query.register(
        confirm_delete_promotion,
        F.data.regexp(r"^delete_promotion_(\d+)$")
    )
    
    router.callback_query.register(
        delete_promotion,
        PromotionManagement.delete_confirm,
        F.data.regexp(r"^confirm_delete_(\d+)$")
    )

def edit_field_keyboard(promo_id: int) -> InlineKeyboardMarkup:
    """
    Creates a keyboard for selecting a field to edit.
    """
    builder = InlineKeyboardBuilder()
    
    # Add buttons for each field
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
    
    # Back button
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=f"promotion_{promo_id}"
        )
    )
    
    return builder.as_markup()

async def start_edit_promotion(callback: CallbackQuery, state: FSMContext):
    """
    Starts the process of editing a promotion.
    """
    promo_id = int(callback.data.split('_')[-1])
    
    await state.update_data(promo_id=promo_id)
    
    await callback.message.edit_text(
        "Выберите, что именно вы хотите изменить:",
        reply_markup=edit_field_keyboard(promo_id)
    )
    await state.set_state(PromotionManagement.edit_select_field)
    await callback.answer()

async def edit_promotion_field(callback: CallbackQuery, state: FSMContext, repo: PromotionRepo):
    """
    Handles field selection for editing.
    """
    field, promo_id = callback.data.split('_')[2:4]
    promo_id = int(promo_id)
    
    # Get current promotion data
    promotion = await repo.get_promotion_by_id(promo_id)
    if not promotion:
        await callback.answer("Акция не найдена", show_alert=True)
        await state.clear()
        return
    
    # Set appropriate state based on field
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
    
    # Update state data
    await state.update_data(promo_id=promo_id, field=field)
    
    # Show current value and prompt for new one
    await callback.message.edit_text(
        f"Редактирование {field_name} акции\n\n"
        f"Текущее значение: {current_value}\n\n"
        f"Введите новое значение для {field_name}:",
        reply_markup=admin_back_button(f"edit_promotion_{promo_id}")
    )
    await callback.answer()

async def process_edit_name(message: Message, state: FSMContext, repo: PromotionRepo):
    """
    Processes editing the promotion name.
    """
    new_name = message.text.strip()
    
    if not new_name or len(new_name) > 100:
        await message.answer("❌ Название должно быть от 1 до 100 символов. Попробуйте снова.")
        return
    
    # Get promotion ID from state
    data = await state.get_data()
    promo_id = data.get("promo_id")
    
    # Update promotion name
    try:
        updated = await repo.update_promotion(promo_id, {"name": new_name})
        if updated:
            await message.answer(f"✅ Название акции успешно изменено на '{new_name}'")
        else:
            await message.answer("❌ Не удалось обновить название акции. Попробуйте позже.")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
    
    # Show updated promotion
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(message=message, promo_id=promo_id, promotion=promotion, repo=repo)
    await state.clear()

async def process_edit_description(message: Message, state: FSMContext, repo: PromotionRepo):
    """
    Processes editing the promotion description.
    """
    new_description = message.text.strip()
    
    # Get promotion ID from state
    data = await state.get_data()
    promo_id = data.get("promo_id")
    
    # Update promotion description
    try:
        updated = await repo.update_promotion(promo_id, {"description": new_description})
        if updated:
            await message.answer(f"✅ Описание акции успешно изменено")
        else:
            await message.answer("❌ Не удалось обновить описание акции. Попробуйте позже.")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
    
    # Show updated promotion
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(message=message, promo_id=promo_id, promotion=promotion, repo=repo)
    await state.clear()

async def process_edit_discount_type(message: Message, state: FSMContext, repo: PromotionRepo):
    """
    Processes editing the promotion discount type.
    """
    selection = message.text.strip()
    
    if selection == "1":
        discount_type = DiscountType.PERCENTAGE.value
    elif selection == "2":
        discount_type = DiscountType.FIXED.value
    else:
        await message.answer("❌ Пожалуйста, выберите 1 для процентной скидки или 2 для фиксированной.")
        return
    
    # Get promotion ID from state
    data = await state.get_data()
    promo_id = data.get("promo_id")
    
    # Update discount type
    try:
        updated = await repo.update_promotion(promo_id, {"discount_type": discount_type})
        if updated:
            type_name = "процентную" if discount_type == DiscountType.PERCENTAGE.value else "фиксированную"
            await message.answer(f"✅ Тип скидки успешно изменен на {type_name}")
        else:
            await message.answer("❌ Не удалось обновить тип скидки. Попробуйте позже.")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
    
    # Show updated promotion
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(message=message, promo_id=promo_id, promotion=promotion, repo=repo)
    await state.clear()

async def process_edit_discount_value(message: Message, state: FSMContext, repo: PromotionRepo):
    """
    Processes editing the promotion discount value.
    """
    try:
        new_value = float(message.text.strip())
        if new_value <= 0:
            raise ValueError("Скидка должна быть положительным числом")
        
        # Get promotion ID from state
        data = await state.get_data()
        promo_id = data.get("promo_id")
        
        # Get current promotion for discount type check
        promotion = await repo.get_promotion_by_id(promo_id)
        if promotion.discount_type == DiscountType.PERCENTAGE.value and new_value > 100:
            await message.answer("❌ Процент скидки не может быть больше 100%. Пожалуйста, введите корректное значение.")
            return
        
        # Update discount value
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
    
    # Show updated promotion
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(message=message, promo_id=promo_id, promotion=promotion, repo=repo)
    await state.clear()

async def process_edit_start_date(message: Message, state: FSMContext, repo: PromotionRepo):
    """
    Processes editing the promotion start date.
    """
    date_text = message.text.strip()
    
    # Get promotion ID from state
    data = await state.get_data()
    promo_id = data.get("promo_id")
    
    if not date_text:
        # Use current date if empty
        new_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        try:
            new_date = datetime.strptime(date_text, "%d-%m-%Y")
        except ValueError:
            await message.answer("❌ Неверный формат даты. Пожалуйста, используйте формат ДД-ММ-ГГГГ.")
            return
    
    # Update start date
    try:
        updated = await repo.update_promotion(promo_id, {"start_date": new_date})
        if updated:
            await message.answer(f"✅ Дата начала акции успешно изменена на {new_date.strftime('%d-%m-%Y')}")
        else:
            await message.answer("❌ Не удалось обновить дату начала акции. Попробуйте позже.")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
    
    # Show updated promotion
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(message=message, promo_id=promo_id, promotion=promotion, repo=repo)
    await state.clear()

async def process_edit_end_date(message: Message, state: FSMContext, repo: PromotionRepo):
    """
    Processes editing the promotion end date.
    """
    date_text = message.text.strip()
    
    # Get promotion ID from state
    data = await state.get_data()
    promo_id = data.get("promo_id")
    
    # Get current promotion for start date check
    promotion = await repo.get_promotion_by_id(promo_id)
    
    if not date_text:
        # Set to None if empty (indefinite promotion)
        new_date = None
    else:
        try:
            new_date = datetime.strptime(date_text, "%d-%m-%Y")
            # Validate end date is after start date
            if promotion.start_date and new_date < promotion.start_date:
                await message.answer("❌ Дата окончания не может быть раньше даты начала.")
                return
        except ValueError:
            await message.answer("❌ Неверный формат даты. Пожалуйста, используйте формат ДД-ММ-ГГГГ.")
            return
    
    # Update end date
    try:
        updated = await repo.update_promotion(promo_id, {"end_date": new_date})
        if updated:
            date_str = new_date.strftime('%d-%m-%Y') if new_date else "бессрочно"
            await message.answer(f"✅ Дата окончания акции успешно изменена на {date_str}")
        else:
            await message.answer("❌ Не удалось обновить дату окончания акции. Попробуйте позже.")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
    
    # Show updated promotion
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(message=message, promo_id=promo_id, promotion=promotion, repo=repo)
    await state.clear()

async def toggle_promotion_status(callback: CallbackQuery, repo: PromotionRepo):
    """
    Toggles the active status of a promotion.
    """
    promo_id = int(callback.data.split('_')[-1])
    
    # Get current promotion
    promotion = await repo.get_promotion_by_id(promo_id)
    if not promotion:
        await callback.answer("Акция не найдена", show_alert=True)
        return
    
    # Toggle status
    new_status = not promotion.is_active
    
    # Update promotion status
    try:
        updated = await repo.update_promotion(promo_id, {"is_active": new_status})
        if updated:
            status_str = "активной" if new_status else "неактивной"
            await callback.answer(f"Акция теперь {status_str}", show_alert=True)
        else:
            await callback.answer("Не удалось обновить статус акции", show_alert=True)
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    
    # Show updated promotion
    promotion = await repo.get_promotion_by_id(promo_id)
    await show_promotion_details(callback=callback, promo_id=promo_id, promotion=promotion, repo=repo)

async def confirm_delete_promotion(callback: CallbackQuery, state: FSMContext):
    """
    Asks for confirmation before deleting a promotion.
    """
    promo_id = int(callback.data.split('_')[-1])
    
    # Save promotion ID in state
    await state.update_data(promo_id=promo_id)
    await state.set_state(PromotionManagement.delete_confirm)
    
    # Create confirmation keyboard
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

async def delete_promotion(callback: CallbackQuery, state: FSMContext, repo: PromotionRepo):
    """
    Deletes a promotion after confirmation.
    """
    promo_id = int(callback.data.split('_')[-1])
    
    # Delete promotion
    try:
        deleted = await repo.delete_promotion(promo_id)
        if deleted:
            await callback.answer("✅ Акция успешно удалена", show_alert=True)
        else:
            await callback.answer("❌ Не удалось удалить акцию", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
    
    # Back to promotion list
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