"""
Модуль models - модели данных и классы для работы с PostgreSQL.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


class Note:
    """Класс, представляющий заметку."""

    def __init__(self, id: Optional[int] = None, title: str = "", content: str = "",
                 priority: str = "medium", status: str = "active",
                 tags: List[str] = None, created_at: Optional[str] = None):
        self.id = id
        self.title = title.strip()
        self.content = content.strip()
        self.priority = priority.lower()
        self.status = status.lower()
        self.tags = [t.strip().lower() for t in (tags or []) if t.strip()]
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Преобразует объект заметки в словарь."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "priority": self.priority,
            "status": self.status,
            "tags": self.tags,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Note':
        """Создает объект Note из словаря."""
        note = cls(
            id=data.get("id"),
            title=data.get("title", ""),
            content=data.get("content", ""),
            priority=data.get("priority", "medium"),
            status=data.get("status", "active"),
            tags=data.get("tags", []),
            created_at=data.get("created_at")
        )
        return note


class PostgresStorage:
    """Класс для работы с PostgreSQL хранилищем заметок."""

    def __init__(self, connection_string: Optional[str] = None):
        """
        Инициализирует подключение к PostgreSQL.

        Args:
            connection_string: Строка подключения к PostgreSQL.
                Если не указана, берется из переменной окружения DATABASE_URL
                или отдельных переменных DB_* из .env файла.
        """
        if connection_string is None:
            # Пробуем сначала взять DATABASE_URL
            connection_string = os.getenv("DATABASE_URL")

            if not connection_string:
                # Если нет DATABASE_URL, используем отдельные переменные из .env
                host = os.getenv("DB_HOST", "localhost")
                port = os.getenv("DB_PORT", "5432")
                database = os.getenv("DB_NAME", "notes_db")  # по умолчанию notes_db
                user = os.getenv("DB_USER", "postgres")
                password = os.getenv("DB_PASSWORD", "s1ny14")

                # Формируем строку подключения
                connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        # Преобразуем строку подключения в параметры для psycopg2
        self.connection_params = self._parse_connection_string(connection_string)
        self._create_tables_if_not_exists()

    def _parse_connection_string(self, connection_string: str) -> dict:
        """Парсит строку подключения PostgreSQL."""
        import urllib.parse

        result = urllib.parse.urlparse(connection_string)

        return {
            "host": result.hostname or os.getenv("DB_HOST", "localhost"),
            "port": result.port or int(os.getenv("DB_PORT", 5432)),
            "database": result.path[1:] if result.path else os.getenv("DB_NAME", "notes_db"),
            "user": result.username or os.getenv("DB_USER", "postgres"),
            "password": result.password or os.getenv("DB_PASSWORD", "s1ny14")
        }

    def _get_connection(self):
        """Создает подключение к базе данных."""
        try:
            conn = psycopg2.connect(
                host=self.connection_params["host"],
                port=self.connection_params["port"],
                database=self.connection_params["database"],
                user=self.connection_params["user"],
                password=self.connection_params["password"]
            )
            return conn
        except Exception as e:
            print(f"Ошибка подключения к PostgreSQL: {e}")
            raise

    def _create_tables_if_not_exists(self):
        """Создает таблицы в базе данных, если они не существуют."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Создаем таблицу notes
            create_table_query = """
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                priority VARCHAR(20) DEFAULT 'medium',
                status VARCHAR(20) DEFAULT 'active',
                tags TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Создаем индексы для быстрого поиска
            CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title);
            CREATE INDEX IF NOT EXISTS idx_notes_status ON notes(status);
            CREATE INDEX IF NOT EXISTS idx_notes_priority ON notes(priority);
            CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at DESC);
            """

            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            conn.close()

            print(f"Таблицы успешно созданы в PostgreSQL (база: {self.connection_params['database']})")

        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")

    def get_all_notes(self) -> List[dict]:
        """Возвращает все заметки из базы данных."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
            SELECT id, title, content, priority, status, tags, 
                   created_at AT TIME ZONE 'UTC' as created_at
            FROM notes 
            ORDER BY created_at DESC
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            notes = []
            for row in rows:
                note = Note(
                    id=row['id'],
                    title=row['title'],
                    content=row['content'],
                    priority=row['priority'],
                    status=row['status'],
                    tags=row['tags'].split(',') if row['tags'] else [],
                    created_at=row['created_at'].isoformat() if row['created_at'] else None
                )
                notes.append(note.to_dict())

            cursor.close()
            conn.close()

            return notes

        except Exception as e:
            print(f"Ошибка при получении заметок: {e}")
            return []

    def get_note_by_id(self, note_id: int) -> Optional[dict]:
        """Возвращает заметку по ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
            SELECT id, title, content, priority, status, tags, 
                   created_at AT TIME ZONE 'UTC' as created_at
            FROM notes 
            WHERE id = %s
            """

            cursor.execute(query, (note_id,))
            row = cursor.fetchone()

            if row:
                note = Note(
                    id=row['id'],
                    title=row['title'],
                    content=row['content'],
                    priority=row['priority'],
                    status=row['status'],
                    tags=row['tags'].split(',') if row['tags'] else [],
                    created_at=row['created_at'].isoformat() if row['created_at'] else None
                )

                cursor.close()
                conn.close()
                return note.to_dict()

            cursor.close()
            conn.close()
            return None

        except Exception as e:
            print(f"Ошибка при получении заметки: {e}")
            return None

    def create_note(self, title: str, content: str, priority: str = "medium",
                    status: str = "active", tags: List[str] = None) -> Optional[dict]:
        """Создает новую заметку в базе данных."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            tags_str = ",".join([t.strip().lower() for t in (tags or []) if t.strip()])

            query = """
            INSERT INTO notes (title, content, priority, status, tags, created_at)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id, created_at AT TIME ZONE 'UTC' as created_at
            """

            cursor.execute(query, (title.strip(), content.strip(), priority.lower(),
                                   status.lower(), tags_str))

            result = cursor.fetchone()
            note_id = result['id']
            created_at = result['created_at'].isoformat() if result['created_at'] else None

            conn.commit()

            # Создаем объект заметки
            note = Note(
                id=note_id,
                title=title,
                content=content,
                priority=priority,
                status=status,
                tags=tags or [],
                created_at=created_at
            )

            cursor.close()
            conn.close()

            return note.to_dict()

        except Exception as e:
            print(f"Ошибка при создании заметки: {e}")
            return None

    def update_note(self, note_id: int, **kwargs) -> Optional[dict]:
        """Обновляет существующую заметку."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Получаем текущие данные заметки
            current_note = self.get_note_by_id(note_id)
            if not current_note:
                return None

            # Обновляем только переданные поля
            title = kwargs.get('title', current_note['title'])
            content = kwargs.get('content', current_note['content'])
            priority = kwargs.get('priority', current_note['priority'])
            status = kwargs.get('status', current_note['status'])
            tags = kwargs.get('tags', current_note['tags'])

            tags_str = ",".join([t.strip().lower() for t in tags if t.strip()])

            query = """
            UPDATE notes 
            SET title = %s, content = %s, priority = %s, status = %s, tags = %s
            WHERE id = %s
            RETURNING created_at AT TIME ZONE 'UTC' as created_at
            """

            cursor.execute(query, (title.strip(), content.strip(), priority.lower(),
                                   status.lower(), tags_str, note_id))

            result = cursor.fetchone()
            created_at = result['created_at'].isoformat() if result['created_at'] else None

            conn.commit()

            # Создаем обновленный объект заметки
            note = Note(
                id=note_id,
                title=title,
                content=content,
                priority=priority,
                status=status,
                tags=tags,
                created_at=created_at
            )

            cursor.close()
            conn.close()

            return note.to_dict()

        except Exception as e:
            print(f"Ошибка при обновлении заметки: {e}")
            return None

    def delete_note(self, note_id: int) -> bool:
        """Удаляет заметку из базы данных."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = "DELETE FROM notes WHERE id = %s"
            cursor.execute(query, (note_id,))

            rows_deleted = cursor.rowcount
            conn.commit()

            cursor.close()
            conn.close()

            return rows_deleted > 0

        except Exception as e:
            print(f"Ошибка при удалении заметки: {e}")
            return False

    def search_notes(self, query: str) -> List[dict]:
        """Ищет заметки по тексту или тегам."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            search_term = f"%{query.lower()}%"

            search_query = """
            SELECT id, title, content, priority, status, tags, 
                   created_at AT TIME ZONE 'UTC' as created_at
            FROM notes 
            WHERE LOWER(title) LIKE %s 
               OR LOWER(content) LIKE %s 
               OR LOWER(tags) LIKE %s
            ORDER BY created_at DESC
            """

            cursor.execute(search_query, (search_term, search_term, search_term))
            rows = cursor.fetchall()

            notes = []
            for row in rows:
                note = Note(
                    id=row['id'],
                    title=row['title'],
                    content=row['content'],
                    priority=row['priority'],
                    status=row['status'],
                    tags=row['tags'].split(',') if row['tags'] else [],
                    created_at=row['created_at'].isoformat() if row['created_at'] else None
                )
                notes.append(note.to_dict())

            cursor.close()
            conn.close()

            return notes

        except Exception as e:
            print(f"Ошибка при поиске заметок: {e}")
            return []

    def get_stats(self) -> dict:
        """Получает статистику по заметкам."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Общее количество заметок
            cursor.execute("SELECT COUNT(*) as total FROM notes")
            total = cursor.fetchone()['total']

            # Количество по статусам
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM notes 
                GROUP BY status
            """)
            by_status = {row['status']: row['count'] for row in cursor.fetchall()}

            # Количество по приоритетам
            cursor.execute("""
                SELECT priority, COUNT(*) as count 
                FROM notes 
                GROUP BY priority
            """)
            by_priority = {row['priority']: row['count'] for row in cursor.fetchall()}

            cursor.close()
            conn.close()

            return {
                "total": total,
                "by_status": by_status,
                "by_priority": by_priority
            }

        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            return {"total": 0, "by_status": {}, "by_priority": {}}