#!/usr/bin/env python3
"""
Скрипт для исправления таблицы favorites - добавления первичного ключа.
"""

import asyncio
import asyncpg
import sys
import os

# Добавляем корневую директорию в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tgbot.config import load_config

async def fix_favorites_table():
    """Исправляет структуру таблицы favorites."""
    
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
        # Проверяем, есть ли первичный ключ у таблицы favorites
        result = await conn.fetchval("""
            SELECT COUNT(*)
            FROM information_schema.table_constraints 
            WHERE table_name = 'favorites' 
            AND constraint_type = 'PRIMARY KEY'
        """)
        
        if result == 0:
            print("Первичный ключ не найден. Добавляем...")
            
            # Проверяем, есть ли constraint на колонку id
            constraint_exists = await conn.fetchval("""
                SELECT COUNT(*)
                FROM information_schema.table_constraints 
                WHERE table_name = 'favorites' 
                AND constraint_name = 'favorites_pkey'
            """)
            
            if constraint_exists == 0:
                await conn.execute("ALTER TABLE favorites ADD CONSTRAINT favorites_pkey PRIMARY KEY (id);")
                print("✅ Первичный ключ успешно добавлен!")
            else:
                print("Первичный ключ уже существует.")
        else:
            print("Первичный ключ уже установлен.")
            
        # Проверяем автоинкремент
        sequence_exists = await conn.fetchval("""
            SELECT COUNT(*)
            FROM information_schema.sequences 
            WHERE sequence_name = 'favorites_id_seq'
        """)
        
        if sequence_exists == 0:
            print("Создаем sequence для автоинкремента...")
            await conn.execute("""
                CREATE SEQUENCE favorites_id_seq;
                ALTER TABLE favorites ALTER COLUMN id SET DEFAULT nextval('favorites_id_seq');
                SELECT setval('favorites_id_seq', COALESCE(MAX(id), 0) + 1, false) FROM favorites;
            """)
            print("✅ Sequence создан!")
        else:
            print("Sequence уже существует.")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_favorites_table())