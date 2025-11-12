"""
Модуль models - определение структуры данных заметки.

Содержит класс Note для представления заметок с различными атрибутами:
заголовок, содержание, приоритет, статус, теги и временные метки.
"""

from datetime import datetime
from typing import Optional, List


class Note:
    """Класс, представляющий заметку с метаданными.

    Attributes:
        id (Optional[int]): Уникальный идентификатор заметки
        title (str): Заголовок заметки
        content (str): Содержание заметки
        priority (str): Уровень приоритета (low/medium/high)
        status (str): Статус заметки (active/done/archived)
        tags (List[str]): Список тегов заметки
        created_at (str): Временная метка создания в формате ISO
    """

    def __init__(self, title: str, content: str,
                 priority: str = "medium", status: str = "active",
                 tags: List[str] = None):
        """Инициализирует новую заметку.

        Args:
            title (str): Заголовок заметки
            content (str): Содержание заметки
            priority (str, optional): Уровень приоритета. Defaults to "medium".
            status (str, optional): Статус заметки. Defaults to "active".
            tags (List[str], optional): Список тегов. Defaults to None.
        """
        self.id: Optional[int] = None
        self.title = title.strip()
        self.content = content.strip()
        self.priority = priority.lower()
        self.status = status.lower()
        self.tags = [t.strip().lower() for t in (tags or []) if t.strip()]
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Преобразует объект заметки в словарь.

        Returns:
            dict: Словарь с данными заметки
        """
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "priority": self.priority,
            "status": self.status,
            "tags": self.tags,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data: dict) -> 'Note':
        """Создает объект Note из словаря.

        Args:
            data (dict): Словарь с данными заметки

        Returns:
            Note: Объект заметки
        """
        note = Note(
            title=data["title"],
            content=data["content"],
            priority=data["priority"],
            status=data["status"],
            tags=data.get("tags", [])
        )
        note.id = data["id"]
        note.created_at = data["created_at"]
        return note