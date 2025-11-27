"""
Тесты для модуля models.py
"""

import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notebook.models import Note


class TestNote(unittest.TestCase):
    """Тесты для класса Note"""

    def test_note_creation(self):
        """Тест создания заметки с минимальными параметрами"""
        note = Note("Тест", "Содержание теста")
        self.assertEqual(note.title, "Тест")
        self.assertEqual(note.content, "Содержание теста")
        self.assertEqual(note.priority, "medium")
        self.assertEqual(note.status, "active")
        self.assertEqual(note.tags, [])
        self.assertIsNone(note.id)

    def test_note_creation_with_all_params(self):
        """Тест создания заметки со всеми параметрами"""
        note = Note(
            title="  Важная заметка  ",
            content="  Содержание  ",
            priority="HIGH",
            status="DONE",
            tags=["#работа", " #срочно "]
        )
        self.assertEqual(note.title, "Важная заметка")
        self.assertEqual(note.content, "Содержание")
        self.assertEqual(note.priority, "high")
        self.assertEqual(note.status, "done")
        self.assertEqual(note.tags, ["работа", "срочно"])

    def test_note_to_dict(self):
        """Тест преобразования заметки в словарь"""
        note = Note("Тест", "Содержание")
        note.id = 1
        note_dict = note.to_dict()

        expected = {
            "id": 1,
            "title": "Тест",
            "content": "Содержание",
            "priority": "medium",
            "status": "active",
            "tags": [],
            "created_at": note.created_at
        }
        self.assertEqual(note_dict, expected)

    def test_note_from_dict(self):
        """Тест создания заметки из словаря"""
        data = {
            "id": 1,
            "title": "Тест",
            "content": "Содержание",
            "priority": "high",
            "status": "done",
            "tags": ["тест"],
            "created_at": "2024-01-01T00:00:00"
        }
        note = Note.from_dict(data)

        self.assertEqual(note.id, 1)
        self.assertEqual(note.title, "Тест")
        self.assertEqual(note.content, "Содержание")
        self.assertEqual(note.priority, "high")
        self.assertEqual(note.status, "done")
        self.assertEqual(note.tags, ["тест"])
        self.assertEqual(note.created_at, "2024-01-01T00:00:00")

