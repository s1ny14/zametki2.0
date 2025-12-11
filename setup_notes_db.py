"""
Настройка базы данных PostgreSQL для менеджера заметок.
"""

import psycopg2
import getpass


def setup_database():
    """Создает базу данных и таблицы для заметок."""
    print("=== НАСТРОЙКА БАЗЫ ДАННЫХ ДЛЯ МЕНЕДЖЕРА ЗАМЕТОК ===\n")

    # Запрашиваем данные подключения
    print("Введите параметры подключения к PostgreSQL:")
    host = input("Хост [localhost]: ") or "localhost"
    port = input("Порт [5432]: ") or "5432"
    user = input("Пользователь [postgres]: ") or "postgres"
    password = getpass.getpass("Пароль: ")

    try:
        # Подключаемся к системной базе данных
        print("\nПодключение к PostgreSQL...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database="postgres",
            user=user,
            password=password
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Проверяем существование базы данных
        db_name = "notes_db"
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))

        if cursor.fetchone():
            print(f"База данных '{db_name}' уже существует.")
            choice = input("Пересоздать? (y/N): ").lower()
            if choice == 'y':
                cursor.execute(f"DROP DATABASE {db_name}")
                cursor.execute(f"CREATE DATABASE {db_name}")
                print(f"База данных '{db_name}' пересоздана.")
        else:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"База данных '{db_name}' создана.")

        cursor.close()
        conn.close()

        # Теперь создаем таблицы в новой базе данных
        print("\nСоздание таблиц...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=db_name,
            user=user,
            password=password
        )
        cursor = conn.cursor()

        # Создаем таблицу notes
        create_table_query = """
        CREATE TABLE IF NOT EXISTS notes (
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
        """

        cursor.execute(create_table_query)
        conn.commit()

        print("Таблицы успешно созданы!")

        # Выводим строку подключения для .env файла
        print("\n" + "=" * 60)
        print("Добавьте в файл .env следующие параметры:")
        print("=" * 60)
        print(f"DATABASE_URL=postgresql://{user}:{password}@{host}:{port}/{db_name}")
        print("\nИли запускайте приложение с параметром:")
        print(f'python main.py --db-url "postgresql://{user}:{password}@{host}:{port}/{db_name}"')
        print("=" * 60)

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\nОшибка: {e}")
        print("\nВозможные причины:")
        print("1. PostgreSQL не установлен или не запущен")
        print("2. Неправильный пароль")
        print("3. Порт занят другим приложением")
        print("4. Нет прав на создание баз данных")


if __name__ == "__main__":
    setup_database()