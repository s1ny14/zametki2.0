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
