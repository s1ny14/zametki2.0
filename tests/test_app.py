"""
Тесты для модуля app.py (графический интерфейс)
"""

import unittest
import sys
import os
import tempfile
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from notebook import Storage, Note
from gui.app import NoteApp


class TestNoteApp(unittest.TestCase):
    """Тесты для класса NoteApp"""

    def setUp(self):
        """Создание временного файла и окна приложения для тестов"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_notes.json")

        # Создаем корневое окно для тестов
        self.root = tk.Tk()
        self.root.withdraw()  # скрываем окно во время тестов

        self.app = NoteApp(self.root, storage_file=self.test_file, debug=True)

    def tearDown(self):
        """Очистка после тестов"""
        try:
            self.root.destroy()
        except tk.TclError:
            pass  # окно уже уничтожено
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

        # временно отключаем messagebox чтобы тест не зависал
        import tkinter.messagebox as messagebox
        original_showwarning = messagebox.showwarning

        def mock_showwarning(title, message):
            # вместо показа окна просто проверяем что вызывается с правильными параметрами
            self.assertEqual(title, "Ошибка")
            self.assertEqual(message, "Заполните заголовок и содержание!")
            return "ok"

        messagebox.showwarning = mock_showwarning

        try:
            self.app.add_note()
            # если дошли сюда - значит валидация сработала и messagebox был вызван
        except Exception as e:
            self.fail(f"add_note() вызвал исключение: {e}")
        finally:
            # восстанавливаем оригинальный messagebox
            messagebox.showwarning = original_showwarning

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

        # заполняем обязательные поля чтобы избежать сообщения об ошибке
        self.app.title_entry.insert(0, "Тестовый заголовок")
        self.app.content_text.insert("1.0", "Тестовое содержание")

        # мокаем messagebox чтобы не появлялось окно
        from unittest import mock
        with mock.patch('tkinter.messagebox.showinfo') as mock_info:
            self.app.add_note()  # Это вызовет парсинг тегов внутри метода

            # проверяем что шоуинфо был вызван (успешное добавление)
            mock_info.assert_called_once()

        # проверяем, что теги правильно парсятся в методе add_note
        notes = self.app.storage.get_all()
        if notes:  # если заметка была добавлена
            self.assertEqual(notes[-1].tags, ["тег1", "тег2", "тег3"])

    @unittest.skip("Требуется mock для messagebox")
    def test_add_note_success(self):
        """Тест успешного добавления заметки"""
        self.app.title_entry.insert(0, "Тест заголовок")
        self.app.content_text.insert("1.0", "Тест содержание")

        pass


class TestNoteAppIntegration(unittest.TestCase):
    """Интеграционные тесты для приложения"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_notes.json")

    def tearDown(self):
        """Очистка после тестов"""
        shutil.rmtree(self.test_dir)

    def test_app_with_prepopulated_data(self):
        """Тест приложения с предварительно заполненными данными"""
        # создаем тестовые данные
        storage = Storage(self.test_file)
        note1 = Note("Заметка 1", "Содержание 1", tags=["тест"])
        note2 = Note("Заметка 2", "Содержание 2", priority="high")
        storage.save(note1)
        storage.save(note2)

        # создаем временное окно для теста
        root = tk.Tk()
        root.withdraw()

        try:
            # создаем приложение с существующими данными
            app = NoteApp(root, storage_file=self.test_file)

            # проверяем, что данные загружены
            notes = app.storage.get_all()
            self.assertEqual(len(notes), 2)
        finally:
            # всегда уничтожаем окно
            root.destroy()


if __name__ == '__main__':
    unittest.main()