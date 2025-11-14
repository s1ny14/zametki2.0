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
    """"""
    parser = argparse.ArgumentParser(
        description="Менеджер заметок",
        epilog="Пример: python main.py --file my_notes.json"
    )

    parser.add_argument(
        '-f', '--file',
        type=str,
        default="notes.json",
        help="Путь к файлу notes.json"
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help="Включить режим отладки"
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    root = tk.Tk()
    app = NoteApp(root, storage_file=args.file, debug=args.debug)
    root.mainloop()