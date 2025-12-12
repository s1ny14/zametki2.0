"""Тест подключения к PostgreSQL"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

try:
    print("Тест подключения к PostgreSQL...")

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "checkers_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "s1ny14")
    )

    cursor = conn.cursor()

    # Проверяем существование таблицы
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'notes'
        );
    """)

    table_exists = cursor.fetchone()[0]

    if table_exists:
        print("Таблица 'notes' существует")

        # Показываем структуру
        cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'notes'")
        columns = cursor.fetchall()

        print("\nСтруктура таблицы:")
        for col_name, data_type in columns:
            print(f"  {col_name}: {data_type}")

        # Показываем количество записей
        cursor.execute("SELECT COUNT(*) FROM notes")
        count = cursor.fetchone()[0]
        print(f"\nКоличество заметок: {count}")
    else:
        print("✗ Таблица 'notes' не существует")
        print("\nСоздаю таблицу")

        cursor.execute("""
            CREATE TABLE notes (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                priority VARCHAR(20) DEFAULT 'medium',
                status VARCHAR(20) DEFAULT 'active',
                tags TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX idx_notes_title ON notes(title);
            CREATE INDEX idx_notes_status ON notes(status);
            CREATE INDEX idx_notes_priority ON notes(priority);
            CREATE INDEX idx_notes_created_at ON notes(created_at DESC);
        """)

        conn.commit()
        print("Таблица создана успешно")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Ошибка: {e}")