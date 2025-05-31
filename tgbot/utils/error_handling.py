"""
Utility functions for standardized error handling across handlers and repositories
"""
import logging
from typing import Optional, Any, Callable, Awaitable, TypeVar, Coroutine, Union, Dict
from functools import wraps
from aiogram.types import CallbackQuery, Message
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RepositoryError(Exception):
    """Base exception for repository operations"""
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(message)

class NotFoundError(RepositoryError):
    """Exception raised when an entity is not found"""
    pass

class ValidationError(RepositoryError):
    """Exception raised when input validation fails"""
    pass

class DatabaseError(RepositoryError):
    """Exception raised for database-related errors"""
    pass

async def handle_repository_errors(
    callback_or_message: Union[CallbackQuery, Message],
    error: Exception,
    user_message: str = "Произошла ошибка при выполнении операции",
    log_message: str = "Repository operation error",
    show_alert: bool = True
) -> None:
    """
    Standard error handler for repository operations.
    
    Args:
        callback_or_message: CallbackQuery or Message to respond to
        error: The exception that occurred
        user_message: Message to display to the user
        log_message: Message to log
        show_alert: Whether to show an alert (for CallbackQuery)
    """
    error_details = str(error)
    logger.error(f"{log_message}: {error_details}")
    
    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.answer(
            user_message, 
            show_alert=show_alert
        )
    else:
        await callback_or_message.answer(user_message)

def safe_db_operation(error_message: str = "Database operation failed"):
    """
    Decorator for repository methods to handle database errors consistently.
    
    Args:
        error_message: Message to include in the exception
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)
            except NotFoundError:
                # Re-raise not found errors
                raise
            except ValidationError:
                # Re-raise validation errors
                raise
            except SQLAlchemyError as e:
                # Log SQLAlchemy errors with details
                logger.error(f"Database error in {func.__name__}: {e}")
                raise DatabaseError(error_message, str(e))
            except Exception as e:
                # Log unexpected errors
                logger.exception(f"Unexpected error in {func.__name__}:")
                raise RepositoryError(error_message, str(e))
        return wrapper
    return decorator

async def handle_callback_error(
    callback: CallbackQuery,
    error: Exception,
    user_message: str = "Произошла ошибка при обработке запроса",
    show_alert: bool = True
) -> None:
    """
    Handles errors from callback handlers consistently.
    
    Args:
        callback: CallbackQuery to respond to
        error: The exception that occurred
        user_message: Message to display to the user
        show_alert: Whether to show an alert
    """
    error_type = type(error).__name__
    error_details = str(error)
    
    # Log detailed error information
    logger.error(f"Error handling callback {callback.data}: {error_type} - {error_details}")
    
    # Customize message based on error type
    if isinstance(error, NotFoundError):
        user_message = "Запрашиваемый объект не найден"
    elif isinstance(error, ValidationError):
        user_message = f"Ошибка валидации: {error.message}"
    elif isinstance(error, DatabaseError):
        user_message = "Ошибка базы данных. Пожалуйста, попробуйте позже."
    
    # Answer callback with appropriate message
    await callback.answer(user_message, show_alert=show_alert)

async def handle_message_error(
    message: Message,
    error: Exception,
    user_message: str = "Произошла ошибка при обработке вашего запроса"
) -> None:
    """
    Handles errors from message handlers consistently.
    
    Args:
        message: Message to respond to
        error: The exception that occurred
        user_message: Message to display to the user
    """
    error_type = type(error).__name__
    error_details = str(error)
    
    # Log detailed error information
    logger.error(f"Error handling message: {error_type} - {error_details}")
    
    # Customize message based on error type
    if isinstance(error, NotFoundError):
        user_message = "Запрашиваемый объект не найден"
    elif isinstance(error, ValidationError):
        user_message = f"Ошибка валидации: {error.message}"
    elif isinstance(error, DatabaseError):
        user_message = "Ошибка базы данных. Пожалуйста, попробуйте позже."
    
    # Answer message with appropriate text
    await message.answer(user_message)