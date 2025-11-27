"""
Тесты для модуля storage.py
"""

import unittest
import sys
import os
import tempfile
import shutil
from notebook.storage import Storage

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