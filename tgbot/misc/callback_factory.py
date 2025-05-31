# tgbot/misc/callback_factory.py

from aiogram.filters.callback_data import CallbackData

# CallbackData для действий, связанных с просмотром продукта
class ProductViewCallback(CallbackData, prefix="product"):
    product_id: int

# CallbackData для действий, связанных с избранным
class FavoriteActionCallback(CallbackData, prefix="favorite"):
    action: str  # Возможные значения: "add", "remove", "view"
    product_id: int

# CallbackData для действий, связанных с обратной связью
class FeedbackCallback(CallbackData, prefix="feedback"):
    action: str  # Возможные значения: "start", "cancel"

# CallbackData для действий, связанных с заказами (если необходимо)
class OrderActionCallback(CallbackData, prefix="order"):
    order_id: int
    action: str  # Возможные значения: "view", "update", "cancel"
    
# CallbackData для действий, связанных с фильтрацией товаров
class FilterCallback(CallbackData, prefix="filter"):
    action: str  # Возможные значения: "material", "type", "price", "apply", "reset"

# CallbackData для действий, связанных с покупкой
class PurchaseCallback(CallbackData, prefix="purchase"):
    product_id: int
    action: str  # Возможные значения: "buy", "confirm", "cancel"
