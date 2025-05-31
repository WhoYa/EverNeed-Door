#!/usr/bin/env python
"""
Test data generator for the EverDoor_Need bot.
This script populates the database with sample products.
"""

import asyncio
import sys
import os
from decimal import Decimal
import random
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, project_root)

from tgbot.config import load_config
from infrastructure.database.setup import create_engine, create_session_pool
from infrastructure.database.repositories.requests import RequestsRepo
from infrastructure.database.models.products import ProductType

# Sample product data
PRODUCT_NAMES = [
    "Дверь Классика", "Дверь Модерн", "Дверь Стандарт", "Дверь Премиум",
    "Дверь Эконом", "Дверь Люкс", "Дверь Комфорт", "Дверь Элит",
    "Ручка дверная классическая", "Ручка дверная современная",
    "Замок цилиндровый", "Замок врезной", "Петли дверные",
    "Доводчик дверной", "Глазок дверной"
]

PRODUCT_TYPES = [
    ProductType.DOOR.value, ProductType.DOOR.value, ProductType.DOOR.value, ProductType.DOOR.value,
    ProductType.DOOR.value, ProductType.DOOR.value, ProductType.DOOR.value, ProductType.DOOR.value,
    ProductType.ACCESSORY.value, ProductType.ACCESSORY.value,
    ProductType.ACCESSORY.value, ProductType.ACCESSORY.value, ProductType.ACCESSORY.value,
    ProductType.ACCESSORY.value, ProductType.ACCESSORY.value
]

PRODUCT_MATERIALS = [
    "Дерево", "Металл", "Стекло", "Пластик", "МДФ", "ДСП", 
    "Сталь", "Алюминий", "Комбинированный", "Шпон", "Ламинат"
]

PRODUCT_DESCRIPTIONS = [
    "Прочная и надежная дверь для вашего дома или офиса.",
    "Стильная дверь с современным дизайном.",
    "Классический дизайн, который подойдет для любого интерьера.",
    "Современный дизайн с использованием качественных материалов.",
    "Экономичный вариант для тех, кто ценит соотношение цены и качества.",
    "Роскошная дверь для престижных помещений.",
    "Комфортная дверь с дополнительной шумоизоляцией.",
    "Элитная дверь для тех, кто ценит эксклюзивность.",
    "Качественная ручка, которая прослужит долгие годы.",
    "Стильная ручка, которая подчеркнет дизайн вашей двери.",
    "Надежный цилиндровый замок для защиты вашего дома.",
    "Прочный врезной замок с высоким уровнем защиты.",
    "Надежные петли, выдерживающие большие нагрузки.",
    "Доводчик для плавного закрывания двери.",
    "Глазок с широким углом обзора для вашей безопасности."
]

# Sample price ranges for products
PRICE_RANGES = {
    ProductType.DOOR.value: (5000, 50000),
    ProductType.ACCESSORY.value: (500, 5000),
    ProductType.OTHER.value: (1000, 10000)
}

# Telegram media IDs for sample images (placeholder URLs for testing)
DOOR_IMAGE_IDS = [
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64", 
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"
]

ACCESSORY_IMAGE_IDS = [
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64", 
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"
]

async def generate_test_products(repo, count=15):
    """Generate and save test products to the database"""
    
    products_created = 0
    
    for i in range(count):
        # Choose product type
        product_type = PRODUCT_TYPES[i % len(PRODUCT_TYPES)]
        
        # Generate product data
        product_data = {
            "name": PRODUCT_NAMES[i % len(PRODUCT_NAMES)],
            "description": PRODUCT_DESCRIPTIONS[i % len(PRODUCT_DESCRIPTIONS)],
            "type": product_type,
            "material": random.choice(PRODUCT_MATERIALS),
            "price": Decimal(str(random.randint(*PRICE_RANGES[product_type]))),
            "stock_quantity": random.randint(0, 50),
        }
        
        # Add image URL (Telegram media ID)
        if product_type == ProductType.DOOR.value:
            product_data["image_url"] = random.choice(DOOR_IMAGE_IDS)
        elif product_type == ProductType.ACCESSORY.value:
            product_data["image_url"] = random.choice(ACCESSORY_IMAGE_IDS)
            
        # Add discount price to some products
        if random.random() < 0.3:  # 30% chance to have a discount
            original_price = product_data["price"]
            discount_percent = random.choice([5, 10, 15, 20, 25])
            discount_price = original_price * (100 - discount_percent) / 100
            product_data["discount_price"] = discount_price.quantize(Decimal('0.01'))
        
        # Create the product
        product = await repo.products.create_product(product_data)
        
        if product:
            products_created += 1
            print(f"Created product: {product.name}, price: {product.price}")
        else:
            print(f"Failed to create product: {product_data['name']}")
    
    return products_created

async def generate_test_logs(repo, count=100):
    """Generate and save test user logs to the database"""
    
    logs_created = 0
    user_ids = [100001, 100002, 100003, 100004, 100005]  # Fake user IDs
    
    # Get all products to reference in logs
    products = await repo.products.get_all_products()
    
    if not products:
        print("No products found to create logs for. Please generate products first.")
        return 0
    
    # Possible log actions
    actions = [
        "view_product", 
        "add_favorite", 
        "remove_favorite",
        "create_order",
        "filter_products",
        "search_products",
        "view_catalog"
    ]
    
    # Generate logs with weighted distribution (more views than orders)
    action_weights = [0.6, 0.15, 0.05, 0.1, 0.05, 0.03, 0.02]
    
    from datetime import timedelta
    import random
    
    now = datetime.now()
    
    for i in range(count):
        # Select random user
        user_id = random.choice(user_ids)
        
        # Select random action based on weights
        action = random.choices(actions, weights=action_weights)[0]
        
        # Generate appropriate details based on action
        details = None
        
        if action == "view_product":
            product = random.choice(products)
            details = f"Просмотр товара с ID {product.product_id}"
        elif action == "add_favorite":
            product = random.choice(products)
            details = f"Добавление в избранное товара с ID {product.product_id}"
        elif action == "remove_favorite":
            product = random.choice(products)
            details = f"Удаление из избранного товара с ID {product.product_id}"
        elif action == "create_order":
            product = random.choice(products)
            details = f"Создание заказа товара с ID {product.product_id}"
        elif action == "filter_products":
            filter_type = random.choice(["по цене", "по материалу", "по типу"])
            details = f"Фильтрация товаров {filter_type}"
        elif action == "search_products":
            search_terms = ["дверь", "металл", "дерево", "ручка", "замок"]
            details = f"Поиск товаров по запросу: {random.choice(search_terms)}"
        
        # Generate random timestamp within the last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        mins_ago = random.randint(0, 59)
        timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=mins_ago)
        
        # Create log with custom timestamp for testing
        log_data = {
            "user_id": user_id,
            "action": action,
            "details": details,
            "timestamp": timestamp
        }
        
        log = await repo.logs.create_with_timestamp(log_data)
        
        if log:
            logs_created += 1
            if logs_created % 20 == 0:
                print(f"Created {logs_created} logs...")
    
    return logs_created

async def main():
    print("Generating test data for EverDoor_Need bot...")
    
    # Load configuration
    config = load_config(".env")
    
    # Create database engine and session pool
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)
    
    # Create products
    async with session_pool() as session:
        repo = RequestsRepo(session)
        
        # Ask user what to generate
        generate_products = input("Generate test products? (y/n): ").lower() == 'y'
        generate_logs = input("Generate test logs? (y/n): ").lower() == 'y'
        
        if generate_products:
            count = await generate_test_products(repo, count=15)
            print(f"Successfully created {count} test products.")
            
        if generate_logs:
            count = await generate_test_logs(repo, count=100)
            print(f"Successfully created {count} test logs.")

if __name__ == "__main__":
    asyncio.run(main())