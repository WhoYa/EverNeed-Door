#!/usr/bin/env python3
"""
Скрипт для пополнения товаров на складе.
"""

import asyncio
import asyncpg
import sys
import os

# Добавляем корневую директорию в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tgbot.config import load_config

async def update_product_stock():
    """Пополняет товары на складе."""
    
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
        # Получаем все товары
        products = await conn.fetch("SELECT product_id, name, stock_quantity FROM products;")
        
        if not products:
            print("❌ Товары не найдены в базе данных.")
            return
        
        print(f"Найдено {len(products)} товаров:")
        for product in products:
            print(f"ID: {product['product_id']}, Название: {product['name']}, Текущее количество: {product['stock_quantity']}")
        
        print("\n🔄 Пополняем склад...")
        
        # Устанавливаем количество товаров в наличии = 50 для всех товаров
        updated_count = await conn.execute("""
            UPDATE products 
            SET stock_quantity = 50, is_in_stock = true 
            WHERE stock_quantity < 50 OR is_in_stock = false
        """)
        
        print(f"✅ Обновлено товаров: {updated_count.split()[1]} из {len(products)}")
        
        # Показываем обновленные данные
        updated_products = await conn.fetch("SELECT product_id, name, stock_quantity, is_in_stock FROM products;")
        print("\n📦 Обновленное состояние склада:")
        for product in updated_products:
            status = "✅ В наличии" if product['is_in_stock'] else "❌ Нет в наличии"
            print(f"ID: {product['product_id']}, Название: {product['name']}, Количество: {product['stock_quantity']}, Статус: {status}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(update_product_stock())