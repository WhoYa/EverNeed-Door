#!/usr/bin/env python3
"""
Скрипт для создания таблицы feedbacks в базе данных.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
from infrastructure.database.setup import create_engine, create_session_pool
from tgbot.config import load_config

async def create_feedbacks_table():
    """Создает таблицу feedbacks если её нет."""
    
    config = load_config(".env")
    
    # Создаем движок базы данных
    engine = create_engine(config.db, echo=True)
    
    try:
        # Создаем соединение с базой данных напрямую
        password = config.db.password
        if hasattr(password, 'get_secret_value'):
            password = password.get_secret_value()
            
        conn = await asyncpg.connect(
            host=config.db.host,
            port=config.db.port,
            user=config.db.user,
            password=password,
            database=config.db.database
        )
        
        # Проверяем, существует ли таблица feedbacks
        table_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'feedbacks')"
        )
        
        if table_exists:
            print("✅ Таблица feedbacks уже существует")
        else:
            print("📝 Создаем таблицу feedbacks...")
            
            # Создаем таблицу feedbacks
            await conn.execute("""
                CREATE TABLE feedbacks (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
                );
            """)
            
            print("✅ Таблица feedbacks успешно создана!")
            
        await conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при создании таблицы feedbacks: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_feedbacks_table())