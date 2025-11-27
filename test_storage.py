"""
Тесты для модуля storage.py
"""

import unittest
import sys
import os
import tempfile
import shutil
import json
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
        """Тест удаления заметки"""
        note1 = Note("Тест 1", "Содержание 1")
        note2 = Note("Тест 2", "Содержание 2")

        self.storage.save(note1)
        self.storage.save(note2)

        result = self.storage.delete(1)
        self.assertTrue(result)

        notes = self.storage.get_all()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].id, 2)

    def test_delete_nonexistent_note(self):
        """Тест удаления несуществующей заметки"""
        note = Note("Тест", "Содержание")
        self.storage.save(note)

        result = self.storage.delete(999)
        self.assertFalse(result)

        notes = self.storage.get_all()
        self.assertEqual(len(notes), 1)

    def test_load_from_nonexistent_file(self):
        """Тест загрузки из несуществующего файла"""
        storage = Storage("nonexistent_file.json")
        notes = storage.get_all()
        self.assertEqual(notes, [])

    def test_save_with_invalid_path(self):
        """Тест сохранения с невалидным путем"""
        storage = Storage("/invalid/path/notes.json")
        note = Note("Тест", "Содержание")
        result = storage.save(note)
        self.assertFalse(result)

    def test_file_content_structure(self):
        """Тест структуры сохраняемого файла"""
        note = Note("Тест", "Содержание", tags=["тег1", "тег2"])
        self.storage.save(note)

        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Тест")
        self.assertEqual(data[0]["content"], "Содержание")
        self.assertEqual(data[0]["tags"], ["тег1", "тег2"])
        self.assertEqual(data[0]["id"], 1)


if __name__ == '__main__':
    unittest.main()