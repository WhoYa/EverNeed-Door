"""
Utility functions for creating commonly used keyboards across the bot
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Union, Optional, Dict, Any

def create_back_button(callback_data: str = "go_back", text: str = "🔙 Назад") -> InlineKeyboardMarkup:
    """
    Creates a keyboard with a single back button.
    
    Args:
        callback_data: Callback data for the button, default "go_back"
        text: Button text, default "🔙 Назад"
        
    Returns:
        InlineKeyboardMarkup with a back button
    """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=text, callback_data=callback_data))
    return builder.as_markup()

def create_pagination_keyboard(
    current_page: int, 
    total_pages: int, 
    page_prefix: str = "page_",
    add_back_button: bool = True,
    back_callback_data: str = "main_menu"
) -> InlineKeyboardMarkup:
    """
    Creates a pagination keyboard with previous/next buttons and page indicators.
    
    Args:
        current_page: Current page number (1-based)
        total_pages: Total number of pages
        page_prefix: Prefix for page callback data
        add_back_button: Whether to add a back button below pagination
        back_callback_data: Callback data for the back button
        
    Returns:
        InlineKeyboardMarkup with pagination buttons
    """
    builder = InlineKeyboardBuilder()
    
    # Add pagination buttons if there are multiple pages
    if total_pages > 1:
        pagination_buttons = []
        
        # Previous page button
        if current_page > 1:
            pagination_buttons.append(
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data=f"{page_prefix}{current_page-1}"
                )
            )
            
        # Page indicator
        pagination_buttons.append(
            InlineKeyboardButton(
                text=f"📄 {current_page}/{total_pages}",
                callback_data="current_page"  # No action
            )
        )
        
        # Next page button
        if current_page < total_pages:
            pagination_buttons.append(
                InlineKeyboardButton(
                    text="Вперёд ▶️",
                    callback_data=f"{page_prefix}{current_page+1}"
                )
            )
            
        builder.row(*pagination_buttons)
    
    # Add back button
    if add_back_button:
        builder.row(InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=back_callback_data
        ))
    
    return builder.as_markup()

def create_confirmation_keyboard(
    confirm_text: str = "✅ Да",
    cancel_text: str = "❌ Нет",
    confirm_callback: str = "confirm",
    cancel_callback: str = "cancel"
) -> InlineKeyboardMarkup:
    """
    Creates a confirmation keyboard with yes/no buttons.
    
    Args:
        confirm_text: Text for confirmation button
        cancel_text: Text for cancel button
        confirm_callback: Callback data for confirmation
        cancel_callback: Callback data for cancellation
        
    Returns:
        InlineKeyboardMarkup with confirmation buttons
    """
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=confirm_text, callback_data=confirm_callback),
        InlineKeyboardButton(text=cancel_text, callback_data=cancel_callback)
    )
    
    return builder.as_markup()

def build_list_keyboard(
    items: List[Dict[str, Any]],
    text_key: str,
    callback_prefix: str,
    id_key: str = "id",
    page: int = 1,
    items_per_page: int = 5,
    back_button_callback: str = "main_menu",
    status_key: Optional[str] = None,
    active_marker: str = "✅",
    inactive_marker: str = "❌"
) -> InlineKeyboardMarkup:
    """
    Creates a keyboard with a list of items and pagination.
    
    Args:
        items: List of items to display
        text_key: Key in item dict to use for button text
        callback_prefix: Prefix for callback data
        id_key: Key in item dict to use for item ID
        page: Current page number (1-based)
        items_per_page: Number of items per page
        back_button_callback: Callback data for back button
        status_key: Optional key for item status
        active_marker: Marker for active items
        inactive_marker: Marker for inactive items
        
    Returns:
        InlineKeyboardMarkup with list items and pagination
    """
    builder = InlineKeyboardBuilder()
    
    # Calculate pagination
    total_items = len(items)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Add item buttons
    page_items = items[start_idx:end_idx]
    for item in page_items:
        # Add status marker if status_key provided
        text = item[text_key]
        if status_key is not None:
            marker = active_marker if item.get(status_key) else inactive_marker
            text = f"{text} {marker}"
            
        builder.row(InlineKeyboardButton(
            text=text,
            callback_data=f"{callback_prefix}{item[id_key]}"
        ))
    
    # Add pagination buttons
    if total_pages > 1:
        pagination_row = []
        
        if page > 1:
            pagination_row.append(InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"page_{callback_prefix}{page-1}"
            ))
            
        pagination_row.append(InlineKeyboardButton(
            text=f"📄 {page}/{total_pages}",
            callback_data="current_page"
        ))
        
        if page < total_pages:
            pagination_row.append(InlineKeyboardButton(
                text="Вперёд ▶️",
                callback_data=f"page_{callback_prefix}{page+1}"
            ))
            
        builder.row(*pagination_row)
    
    # Add back button
    builder.row(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data=back_button_callback
    ))
    
    return builder.as_markup()

def create_menu_keyboard(
    options: List[Dict[str, str]],
    columns: int = 1,
    add_back_button: bool = True,
    back_button_callback: str = "main_menu"
) -> InlineKeyboardMarkup:
    """
    Creates a menu keyboard with multiple options.
    
    Args:
        options: List of dicts with 'text' and 'callback_data' keys
        columns: Number of buttons per row
        add_back_button: Whether to add a back button
        back_button_callback: Callback data for back button
        
    Returns:
        InlineKeyboardMarkup with menu options
    """
    builder = InlineKeyboardBuilder()
    
    # Add option buttons
    buttons = []
    for option in options:
        buttons.append(InlineKeyboardButton(
            text=option["text"],
            callback_data=option["callback_data"]
        ))
    
    # Adjust buttons layout
    builder.adjust(columns)
    builder.add(*buttons)
    
    # Add back button in a separate row if needed
    if add_back_button:
        builder.row(InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=back_button_callback
        ))
    
    return builder.as_markup()