# tgbot/handlers/users/user_feedback.py

import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from tgbot.keyboards.user_feedback import feedback_keyboard
from tgbot.misc.states import FeedbackStates
from infrastructure.database.repositories.feedback import FeedbackRepo

# Инициализация роутера
user_feedback_router = Router()

# Настройка логирования для данного модуля
logger = logging.getLogger(__name__)

@user_feedback_router.callback_query(F.data == "start_feedback")
async def start_feedback(callback: CallbackQuery, state: FSMContext):
    """
    Начало процесса обратной связи.
    """
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} инициировал обратную связь.")
    
    await callback.message.edit_text(
        "Пожалуйста, введите ваш отзыв или предложение:",
        reply_markup=feedback_keyboard()
    )
    await state.set_state(FeedbackStates.waiting_for_feedback)
    await callback.answer()

@user_feedback_router.message(FeedbackStates.waiting_for_feedback)
async def process_feedback(message: Message, state: FSMContext, repo: FeedbackRepo):
    """
    Обработка полученного отзыва.
    """
    user_id = message.from_user.id
    feedback_text = message.text.strip()
    
    # Проверка наличия текста отзыва
    if not feedback_text:
        logger.warning(f"Пользователь {user_id} отправил пустой отзыв.")
        await message.answer("❌ Отзыв не может быть пустым. Пожалуйста, введите ваш отзыв или предложение:")
        return

    # Ограничение длины отзыва (например, максимум 1000 символов)
    if len(feedback_text) > 1000:
        logger.warning(f"Пользователь {user_id} отправил отзыв длиной {len(feedback_text)} символов, что превышает допустимый лимит.")
        await message.answer("❌ Отзыв слишком длинный. Пожалуйста, сократите ваш отзыв до 1000 символов.")
        return

    try:
        # Сохраняем отзыв в базе данных
        feedback = await repo.create_feedback(user_id=user_id, message=feedback_text)
        logger.info(f"Пользователь {user_id} отправил отзыв (ID: {feedback.id}).")
    
        await message.answer("✅ Спасибо за ваш отзыв!")
    except Exception as e:
        logger.error(f"Ошибка при сохранении отзыва от пользователя {user_id}: {e}")
        await message.answer("❌ Произошла ошибка при сохранении вашего отзыва. Пожалуйста, попробуйте позже.")
    finally:
        await state.clear()

@user_feedback_router.callback_query(
    (F.data == "cancel_feedback") & (F.state == FeedbackStates.waiting_for_feedback)
)
async def cancel_feedback(callback: CallbackQuery, state: FSMContext):
    """
    Отмена процесса обратной связи.
    """
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} отменил процесс обратной связи.")
    
    await callback.message.edit_text(
        "✅ Обратная связь отменена.",
        reply_markup=None
    )
    await state.clear()
    await callback.answer()
