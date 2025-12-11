"""
Пакет notebook - модуль для управления заметками с PostgreSQL.

Этот пакет предоставляет функциональность для создания, хранения
и управления заметками с поддержкой тегов и метаданными в PostgreSQL.

Modules:
    models: Классы Note и PostgresStorage для работы с заметками
    migrate: Миграция данных из JSON в PostgreSQL

Classes:
    Note: Класс, представляющий заметку
    PostgresStorage: Класс для работы с PostgreSQL хранилищем
"""

from .models import Note, PostgresStorage

__all__ = ["Note", "PostgresStorage"]