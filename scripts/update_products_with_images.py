#!/usr/bin/env python3
"""
Скрипт для обновления товаров с реальными изображениями из папки imgs.
"""

import asyncio
import asyncpg
import sys
import os
from decimal import Decimal

# Добавляем корневую директорию в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tgbot.config import load_config

# Данные товаров с соответствующими изображениями
PRODUCTS_DATA = [
    # Деревянные двери
    {
        "name": "Дверь деревянная «Классика»",
        "description": "Элегантная деревянная дверь из массива дуба. Идеально подходит для создания уютной атмосферы в доме.",
        "type": "дверь",
        "material": "дерево",
        "price": Decimal("25000.00"),
        "image_path": "imgs/Wood_door_1.jpg"
    },
    {
        "name": "Дверь деревянная «Модерн»",
        "description": "Современная деревянная дверь с минималистичным дизайном. Изготовлена из качественной сосны.",
        "type": "дверь",
        "material": "дерево",
        "price": Decimal("22000.00"),
        "image_path": "imgs/Wood_door_2.jpg"
    },
    {
        "name": "Дверь деревянная «Премиум»",
        "description": "Роскошная деревянная дверь из массива ясеня с декоративными элементами.",
        "type": "дверь",
        "material": "дерево",
        "price": Decimal("35000.00"),
        "image_path": "imgs/Wood_door_3.webp"
    },
    # Металлические двери
    {
        "name": "Дверь металлическая «Страж»",
        "description": "Надежная металлическая входная дверь с усиленной конструкцией. Отличная защита для вашего дома.",
        "type": "дверь",
        "material": "металл",
        "price": Decimal("45000.00"),
        "image_path": "imgs/Metal_door_1.jpeg"
    },
    {
        "name": "Дверь металлическая «Форт»",
        "description": "Бронированная металлическая дверь с многоточечным замком. Максимальная безопасность.",
        "type": "дверь",
        "material": "металл",
        "price": Decimal("55000.00"),
        "image_path": "imgs/Metal_door_2.webp"
    },
    {
        "name": "Дверь металлическая «Защитник»",
        "description": "Современная металлическая дверь с терморазрывом и качественной отделкой.",
        "type": "дверь",
        "material": "металл",
        "price": Decimal("48000.00"),
        "image_path": "imgs/Metal_door_3.jpg"
    },
    # Замки
    {
        "name": "Замок врезной «Секьюрити Про»",
        "description": "Высококачественный врезной замок с цилиндровым механизмом. Повышенная стойкость к взлому.",
        "type": "аксессуар",
        "material": "металл",
        "price": Decimal("8500.00"),
        "image_path": "imgs/Door_locker_1.jpg"
    },
    {
        "name": "Замок накладной «Гарант»",
        "description": "Надежный накладной замок с ригельным механизмом. Простота установки и надежность.",
        "type": "аксессуар",
        "material": "металл",
        "price": Decimal("6200.00"),
        "image_path": "imgs/Door_locker_2.jpg"
    },
    {
        "name": "Замок электронный «Смарт Лок»",
        "description": "Современный электронный замок с кодовой панелью. Открытие по коду или карте.",
        "type": "аксессуар",
        "material": "металл",
        "price": Decimal("15000.00"),
        "image_path": "imgs/Door_locker_3.jpeg"
    }
]

async def update_products_with_images():
    """Обновляет товары с реальными изображениями."""
    
    # Загружаем конфигурацию из переменных окружения
    config = load_config(".env")
    
    # Подключаемся к базе данных
    conn = await asyncpg.connect(
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password,
        database=config.db.database
    )
    
    try:
        print("🔄 Начинаем обновление товаров...")
        
        # Сначала удаляем связанные записи
        await conn.execute("DELETE FROM favorites;")
        await conn.execute("DELETE FROM orders;")
        print("🧹 Очищены связанные таблицы (favorites, orders)")
        
        # Удаляем все старые товары
        deleted_count = await conn.execute("DELETE FROM products;")
        print(f"❌ Удалено старых товаров: {deleted_count.split()[1]}")
        
        # Сбрасываем sequence для product_id
        await conn.execute("ALTER SEQUENCE products_product_id_seq RESTART WITH 1;")
        print("🔄 Sequence для product_id сброшен")
        
        # Добавляем новые товары
        for i, product_data in enumerate(PRODUCTS_DATA, 1):
            # Проверяем, существует ли файл изображения
            image_path = product_data["image_path"]
            if not os.path.exists(image_path):
                print(f"⚠️ Файл изображения не найден: {image_path}")
                continue
            
            # Вставляем товар в базу данных
            await conn.execute("""
                INSERT INTO products (name, description, type, material, price, stock_quantity, is_in_stock, image_url)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, 
            product_data["name"],
            product_data["description"], 
            product_data["type"],
            product_data["material"],
            product_data["price"],
            50,  # stock_quantity
            True,  # is_in_stock
            image_path  # Сохраняем путь к локальному файлу
            )
            
            print(f"✅ Добавлен товар {i}: {product_data['name']}")
        
        # Показываем итоговую статистику
        total_products = await conn.fetchval("SELECT COUNT(*) FROM products;")
        print(f"\n📊 Итого товаров в базе: {total_products}")
        
        # Показываем все товары
        products = await conn.fetch("SELECT product_id, name, type, material, price, image_url FROM products ORDER BY product_id;")
        print("\n📦 Список всех товаров:")
        for product in products:
            print(f"ID: {product['product_id']}, Название: {product['name']}")
            print(f"    Тип: {product['type']}, Материал: {product['material']}")
            print(f"    Цена: {product['price']}₽, Изображение: {product['image_url']}")
            print()
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(update_products_with_images())