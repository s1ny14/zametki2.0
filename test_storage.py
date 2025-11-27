"""
Тесты для модуля storage.py
"""

import unittest
import sys
import os
import tempfile
import shutil
from notebook.storage import Storage
from notebook.models import Note

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestStorage(unittest.TestCase):


    """Тесты для класса Storage"""

    def setUp(self):
        """Создание временной директории для тестовых файлов"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_notes.json")
        self.storage = Storage(self.test_file)

    def tearDown(self):
        """Очистка временной директории после тестов"""
        shutil.rmtree(self.test_dir)

    def test_storage_initialization(self):
        """Тест инициализации хранилища"""
        self.assertEqual(self.storage.file_path, self.test_file)

    def test_save_and_get_all_notes(self):
        """Тест сохранения и получения всех заметок"""
        note = Note("Тест 1", "Содержание 1")
        result = self.storage.save(note)
        self.assertTrue(result)
        self.assertEqual(note.id, 1)

        notes = self.storage.get_all()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "Тест 1")
        self.assertEqual(notes[0].id, 1)

    def test_save_multiple_notes(self):
        """Тест сохранения нескольких заметок"""
        note1 = Note("Тест 1", "Содержание 1")
        note2 = Note("Тест 2", "Содержание 2")

        self.storage.save(note1)
        self.storage.save(note2)

        notes = self.storage.get_all()
        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0].id, 1)
        self.assertEqual(notes[1].id, 2)

    def test_update_existing_note(self):
        """Тест обновления существующей заметки"""
        note = Note("Старый заголовок", "Старое содержание")
        self.storage.save(note)

        note.title = "Новый заголовок"
        note.content = "Новое содержание"
        self.storage.save(note)

        notes = self.storage.get_all()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "Новый заголовок")
        self.assertEqual(notes[0].content, "Новое содержание")

    def test_delete_note(self):