"""
Главный модуль приложения "Менеджер заметок".

Этот модуль запускает графическое приложение для управления заметками.
Приложение позволяет создавать, просматривать, редактировать и удалять заметки
с поддержкой тегов, приоритетов и статусов.
Поддерживает аргументы командной строки через argparse

Attributes:
    root (tk.Tk): Корневое окно приложения
    app (NoteApp): Основной класс приложения
"""

import tkinter as tk
import argparse
from gui.app import NoteApp

def parse_arguments():
    """Парсит аргументы ком-ой строки"""
    parser = argparse.ArgumentParser(
        description="Менеджер заметок",
        epilog="Описание или примеры использ-я"
    )

    parser.add_argument(
        '-f', '--file', # работа с разными файлами
        type=str,
        default="notes.json",
        help="Путь к файлу notes.json"
    )

    parser.add_argument(
        '--debug', # удобная отладка
        action='store_true',
        help="Включить режим отладки"
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    root = tk.Tk()
    app = NoteApp(root, storage_file=args.file, debug=args.debug) # передаём режим отладки
    root.mainloop()