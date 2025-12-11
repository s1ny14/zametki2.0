"""
Главный модуль приложения "Менеджер заметок" с PostgreSQL.

Использование:
    python main.py [--db-url СТРОКА_ПОДКЛЮЧЕНИЯ] [--migrate] [--debug]
"""

import tkinter as tk
import argparse
import os
from dotenv import load_dotenv
from gui.app import NoteApp
from notebook.models import PostgresStorage

# Загружаем переменные окружения из .env файла
load_dotenv()


def parse_arguments():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Менеджер заметок с PostgreSQL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py
  python main.py --db-url "postgresql://user:pass@localhost:5432/notes_db"
  python main.py --migrate
  python main.py --debug
  
Параметры подключения по умолчанию берутся из .env файла:
  DB_HOST=localhost
  DB_PORT=5432
  DB_NAME=checkers_db  # или notes_db
  DB_USER=postgres
  DB_PASSWORD=s1ny14
        """
    )

    parser.add_argument(
        '--db-url',
        type=str,
        default=None,
        help="""Строка подключения к PostgreSQL.
Пример: postgresql://user:password@localhost:5432/dbname
По умолчанию берется из .env файла или используется:
postgresql://postgres:s1ny14@localhost:5432/checkers_db"""
    )

    parser.add_argument(
        '--migrate',
        action='store_true',
        help="Мигрировать данные из JSON файлов в PostgreSQL перед запуском"
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help="Включить режим отладки"
    )

    return parser.parse_args()


def main():
    """Основная функция запуска приложения."""
    args = parse_arguments()

    try:
        # Создаем хранилище PostgreSQL
        print("=" * 60)
        print("Подключение к PostgreSQL...")

        # Показываем параметры подключения
        print(f"Host: {os.getenv('DB_HOST', 'localhost')}")
        print(f"Port: {os.getenv('DB_PORT', '5432')}")
        print(f"Database: {os.getenv('DB_NAME', 'checkers_db')}")
        print(f"User: {os.getenv('DB_USER', 'postgres')}")
        print("=" * 60)

        storage = PostgresStorage(connection_string=args.db_url)

        # Запускаем GUI приложение
        root = tk.Tk()

        # Изменение здесь: передаем storage как именованный аргумент
        # Или убираем storage, если NoteApp создает его сам
        try:
            # Попробуем создать с storage
            app = NoteApp(root, storage=storage, debug=args.debug)
        except TypeError:
            # Если конструктор не принимает storage, создаем без него
            print("NoteApp не принимает storage в конструкторе")
            app = NoteApp(root, debug=args.debug)

        root.mainloop()

    except Exception as e:
        print(f"\nОшибка при запуске приложения: {e}")
        print("\nПроверьте:")
        print("1. Запущен ли PostgreSQL сервер")
        print("2. Правильность строки подключения --db-url")
        print(f"3. Существует ли база данных {os.getenv('DB_NAME', 'checkers_db')}")
        print("4. Правильность параметров в .env файле")
        print("\nСоздать базу данных можно командой:")
        print(f"  createdb -U postgres {os.getenv('DB_NAME', 'checkers_db')}")
        print("\nИли через psql:")
        print("  sudo -u postgres psql")
        print(f"  CREATE DATABASE {os.getenv('DB_NAME', 'checkers_db')};")
        print("  \\q")


if __name__ == "__main__":
    main()