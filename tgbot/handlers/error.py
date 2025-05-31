import logging
from typing import Dict, Any, Union

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ErrorEvent
from aiogram.exceptions import TelegramAPIError

error_router = Router()
logger = logging.getLogger(__name__)

# Catch all unhandled messages with low priority
@error_router.message(F.text)
async def error_message(message: Message):
    """
    Handle unprocessed text messages from users.
    Suggests using the bot's interface.
    """
    await message.answer(
        text="Я не понял :(\nПожалуйста, воспользуйтесь кнопками меню"
    )

# Handle Telegram API errors
@error_router.error()
async def error_handler(event: ErrorEvent, bot_data: Dict[str, Any] = None) -> Any:
    """
    Global error handler for the bot.
    Catches exceptions from handlers and logs them.
    
    Args:
        event: Error event containing the update and exception
        bot_data: Bot data containing configuration
    """
    update = event.update
    exception = event.exception
    
    # Get event source
    if update.message:
        user_id = update.message.from_user.id if update.message.from_user else "Unknown"
        chat = update.message.chat.id
        event_type = "message"
    elif update.callback_query:
        user_id = update.callback_query.from_user.id
        chat = update.callback_query.message.chat.id if update.callback_query.message else "Unknown"
        event_type = "callback_query"
    else:
        user_id = "Unknown"
        chat = "Unknown"
        event_type = str(type(update))
    
    # Log the error
    logger.error(
        f"Error handling {event_type} from user {user_id} in chat {chat}: {exception}",
        exc_info=True
    )
    
    # Handle Telegram API errors specifically
    if isinstance(exception, TelegramAPIError):
        # Try to notify the user if possible
        try:
            # Determine the right object to reply to
            if update.message:
                await update.message.answer(
                    "Произошла ошибка при обработке вашего запроса. "
                    "Пожалуйста, попробуйте позже."
                )
            elif update.callback_query:
                await update.callback_query.answer(
                    "Ошибка при обработке запроса. Попробуйте еще раз.", 
                    show_alert=True
                )
        except Exception as e:
            logger.error(f"Error while sending error message: {e}")
    
    return True  # Prevent exception propagation
