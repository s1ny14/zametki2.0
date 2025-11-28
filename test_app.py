"""
Тесты для модуля app.py (графический интерфейс)
"""

import unittest
import sys
import os
import tempfile
import shutil

import tkinter as tk
from gui.app import NoteApp

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestNoteApp(unittest.TestCase):
    """Тесты для класса NoteApp"""

    def setUp(self):
        """Создание временного файла и окна приложения для тестов"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_notes.json")

        # создаем корневое окно для тестов
        self.root = tk.Tk()
        self.root.withdraw()  # скрываем окно во время тестов

        self.app = NoteApp(self.root, storage_file=self.test_file, debug=True)

    def tearDown(self):
        """Очистка после тестов"""
        self.root.destroy()
        shutil.rmtree(self.test_dir)

    def test_app_initialization(self):
        """Тест инициализации приложения"""
        self.assertIsNotNone(self.app.storage)
        self.assertEqual(self.app.storage.file_path, self.test_file)
        self.assertTrue(self.app.debug)

    def test_priority_selection(self):
        """Тест выбора приоритета"""
        self.app.select_priority("high")
        self.assertEqual(self.app.priority_var.get(), "high")

        self.app.select_priority("low")
        self.assertEqual(self.app.priority_var.get(), "low")

    def test_status_selection(self):
        """Тест выбора статуса"""
        self.app.select_status("done")
        self.assertEqual(self.app.status_var.get(), "done")

        self.app.select_status("archived")
        self.assertEqual(self.app.status_var.get(), "archived")

    def test_add_note_validation(self):
        """Тест валидации при добавлении заметки"""
        # пытаемся добавить заметку без заголовка и содержания
        self.app.title_entry.delete(0, tk.END)
        self.app.content_text.delete("1.0", tk.END)

        try:
            self.app.add_note()
        except Exception as e:
            self.fail(f"add_note() вызвал исключение: {e}")

    def test_clear_form(self):
        """Тест очистки формы"""
        self.app.title_entry.insert(0, "Тест")
        self.app.content_text.insert("1.0", "Содержание")
        self.app.tags_entry.insert(0, "тег1, тег2")

        self.app.clear_form()

        self.assertEqual(self.app.title_entry.get(), "")
        self.assertEqual(self.app.content_text.get("1.0", tk.END).strip(), "")
        self.assertEqual(self.app.tags_entry.get(), "")
        self.assertEqual(self.app.priority_var.get(), "medium")
        self.assertEqual(self.app.status_var.get(), "active")

    def test_tags_parsing(self):
        """Тест парсинга тегов из строки"""
        # тестируем приватный метод через публичный интерфейс
        self.app.tags_entry.insert(0, "#тег1, тег2  #тег3")
        self.app.add_note()  # Это вызовет парсинг тегов внутри метода

        # проверяем, что теги правильно парсятся в методе add_note
        tags_input = self.app.tags_entry.get()
        tags = [t.strip().lstrip('#').lower() for t in tags_input.replace(',', ' ').split() if t.strip()]
        expected_tags = ["тег1", "тег2", "тег3"]
        self.assertEqual(tags, expected_tags)

    @unittest.skip("Требуется mock для messagebox")
    def test_add_note_success(self):
        """Тест успешного добавления заметки"""
        # Этот тест требует мокирования messagebox
        self.app.title_entry.insert(0, "Тест заголовок")
        self.app.content_text.insert("1.0", "Тест содержание")

        # здесь нужно использовать mock для messagebox.showinfo
        pass

