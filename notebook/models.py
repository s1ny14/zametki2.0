"""
модуль models - модели данных и классы для работы с postgresql.
"""
# импортируем библиотеку для работы с postgresql
import psycopg2

# импортируем специальный курсор, который возвращает результаты в виде словарей
from psycopg2.extras import RealDictCursor
from datetime import datetime

# импортируем типы для аннотаций (указания типов данных)
from typing import Optional, List
import os
from dotenv import load_dotenv

# загружаем переменные окружения из .env файла
load_dotenv()


class Note:
    """класс, представляющий заметку."""

    def __init__(self, id: Optional[int] = None, title: str = "", content: str = "",
                 priority: str = "medium", status: str = "active",
                 tags: List[str] = None, created_at: Optional[str] = None):
        # уникальный идентификатор заметки (может быть None для новой заметки)
        self.id = id

        # заголовок заметки, убираем лишние пробелы
        self.title = title.strip()

        # содержимое заметки, убираем лишние пробелы
        self.content = content.strip()

        # приоритет заметки, приводим к нижнему регистру
        self.priority = priority.lower()

        # статус заметки, приводим к нижнему регистру
        self.status = status.lower()

        # список тегов, обрабатываем каждый тег (убираем пробелы, приводим к нижнему регистру)
        # если tags = None, используем пустой список
        self.tags = [t.strip().lower() for t in (tags or []) if t.strip()]

        # дата создания, если не указана - используем текущее время
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> dict:
        """преобразует объект заметки в словарь."""
        # возвращаем словарь со всеми полями заметки
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
        """создает объект note из словаря."""
        # создаем новый объект Note из словаря
        note = cls(
            id=data.get("id"),                    # получаем id или None
            title=data.get("title", ""),          # получаем title или пустую строку
            content=data.get("content", ""),      # получаем content или пустую строку
            priority=data.get("priority", "medium"),  # получаем priority или "medium"
            status=data.get("status", "active"),  # получаем status или "active"
            tags=data.get("tags", []),            # получаем tags или пустой список
            created_at=data.get("created_at")     # получаем created_at или None
        )
        return note


class PostgresStorage:
    """класс для работы с postgresql хранилищем заметок."""

    def __init__(self, connection_string: Optional[str] = None):
        """
        инициализирует подключение к postgresql.

        args:
            connection_string: строка подключения к postgresql.
                если не указана, берется из переменной окружения database_url
                или отдельных переменных db_* из .env файла.
        """
        # если строка подключения не передана явно
        if connection_string is None:
            # пробуем сначала взять DATABASE_URL из переменных окружения
            connection_string = os.getenv("DATABASE_URL")

            # если DATABASE_URL не найден
            if not connection_string:

                host = os.getenv("DB_HOST", "localhost")
                port = os.getenv("DB_PORT", "5432")
                database = os.getenv("DB_NAME", "notes_db")
                user = os.getenv("DB_USER", "postgres")
                password = os.getenv("DB_PASSWORD", "s1ny14")

                # формируем строку подключения в формате URL
                connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        # преобразуем строку подключения в параметры для psycopg2
        self.connection_params = self._parse_connection_string(connection_string)

        # создаем таблицы, если они еще не существуют
        self._create_tables_if_not_exists()

    def _parse_connection_string(self, connection_string: str) -> dict:
        """парсит строку подключения postgresql."""
        # импортируем модуль для парсинга URL
        import urllib.parse

        # разбираем строку подключения на компоненты
        result = urllib.parse.urlparse(connection_string)

        # возвращаем словарь с параметрами подключения
        return {
            # хост из URL или значение по умолчанию
            "host": result.hostname or os.getenv("DB_HOST", "localhost"),
            "port": result.port or int(os.getenv("DB_PORT", 5432)),
            "database": result.path[1:] if result.path else os.getenv("DB_NAME", "notes_db"),
            "user": result.username or os.getenv("DB_USER", "postgres"),
            "password": result.password or os.getenv("DB_PASSWORD", "s1ny14")
        }

    def _get_connection(self):
        """создает подключение к базе данных."""
        try:
            # создаем подключение к PostgreSQL с использованием параметров
            conn = psycopg2.connect(
                host=self.connection_params["host"],          # адрес сервера
                port=self.connection_params["port"],          # порт подключения
                database=self.connection_params["database"],  # имя базы данных
                user=self.connection_params["user"],          # имя пользователя
                password=self.connection_params["password"]   # пароль
            )
            return conn
        except Exception as e:
            # выводим сообщение об ошибке и пробрасываем исключение дальше
            print(f"ошибка подключения к postgresql: {e}")
            raise

    def _create_tables_if_not_exists(self):
        """создает таблицы в базе данных, если они не существуют."""
        try:
            # получаем подключение к базе данных
            conn = self._get_connection()

            # создаем курсор для выполнения SQL команд
            cursor = conn.cursor()

            # SQL запрос для создания таблицы notes
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

            CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title);               
            CREATE INDEX IF NOT EXISTS idx_notes_status ON notes(status);             
            CREATE INDEX IF NOT EXISTS idx_notes_priority ON notes(priority);        
            CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at DESC); 
            """

            # выполняем SQL запрос создания таблицы
            cursor.execute(create_table_query)

            # фиксируем изменения в базе данных
            conn.commit()

            # закрываем курсор для освобождения ресурсов
            cursor.close()

            # закрываем подключение к базе данных
            conn.close()

            # выводим сообщение об успешном создании таблиц
            print(f"таблицы успешно созданы в postgresql (база: {self.connection_params['database']})")

        except Exception as e:
            print(f"ошибка при создании таблиц: {e}")

    def get_all_notes(self) -> List[dict]:
        """возвращает все заметки из базы данных."""
        try:
            # получаем подключение к базе данных
            conn = self._get_connection()

            # создаем курсор, который возвращает результаты как словари
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # SQL запрос для получения всех заметок
            query = """
            SELECT id, title, content, priority, status, tags, 
                   created_at AT TIME ZONE 'UTC' as created_at  
            FROM notes 
            ORDER BY created_at DESC  
            """

            # выполняем SQL запрос
            cursor.execute(query)

            # получаем все строки результата
            rows = cursor.fetchall()

            # создаем пустой список для заметок
            notes = []

            # обрабатываем каждую строку результата
            for row in rows:
                # создаем объект Note из данных строки
                note = Note(
                    id=row['id'],                                          # идентификатор
                    title=row['title'],                                    # заголовок
                    content=row['content'],                                # содержимое
                    priority=row['priority'],                              # приоритет
                    status=row['status'],                                  # статус
                    # преобразуем строку тегов в список (разделяем по запятой)
                    tags=row['tags'].split(',') if row['tags'] else [],
                    # конвертируем datetime в строку ISO формата
                    created_at=row['created_at'].isoformat() if row['created_at'] else None
                )
                # добавляем заметку в список в виде словаря
                notes.append(note.to_dict())

            # закрываем курсор
            cursor.close()

            # закрываем подключение
            conn.close()

            # возвращаем список заметок
            return notes

        except Exception as e:
            # выводим сообщение об ошибке и возвращаем пустой список
            print(f"ошибка при получении заметок: {e}")
            return []

    def get_note_by_id(self, note_id: int) -> Optional[dict]:
        """возвращает заметку по ID."""
        try:
            # получаем подключение к базе данных
            conn = self._get_connection()

            # создаем курсор, который возвращает результаты как словари
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # SQL запрос для получения заметки по ID
            query = """
            SELECT id, title, content, priority, status, tags, 
                   created_at AT TIME ZONE 'UTC' as created_at
            FROM notes 
            WHERE id = %s 
            """

            # выполняем SQL запрос с параметром (note_id)
            cursor.execute(query, (note_id,))

            # получаем одну строку результата
            row = cursor.fetchone()

            # если строка найдена
            if row:
                # создаем объект Note из данных строки
                note = Note(
                    id=row['id'],
                    title=row['title'],
                    content=row['content'],
                    priority=row['priority'],
                    status=row['status'],
                    tags=row['tags'].split(',') if row['tags'] else [],
                    created_at=row['created_at'].isoformat() if row['created_at'] else None
                )

                # закрываем курсор
                cursor.close()

                # закрываем подключение
                conn.close()

                # возвращаем заметку в виде словаря
                return note.to_dict()

            # если заметка не найдена, закрываем ресурсы и возвращаем None
            cursor.close()
            conn.close()
            return None

        except Exception as e:
            # выводим сообщение об ошибке и возвращаем None
            print(f"ошибка при получении заметки: {e}")
            return None

    def create_note(self, title: str, content: str, priority: str = "medium",
                    status: str = "active", tags: List[str] = None) -> Optional[dict]:
        """создает новую заметку в базе данных."""
        try:
            # получаем подключение к базе данных
            conn = self._get_connection()

            # создаем курсор, который возвращает результаты как словари
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # преобразуем список тегов в строку, разделенную запятыми
            # обрабатываем каждый тег: убираем пробелы, приводим к нижнему регистру
            tags_str = ",".join([t.strip().lower() for t in (tags or []) if t.strip()])

            # SQL запрос для создания новой заметки
            # используем RETURNING для получения ID и даты создания новой записи
            query = """
            INSERT INTO notes (title, content, priority, status, tags, created_at)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)  
            RETURNING id, created_at AT TIME ZONE 'UTC' as created_at
            """

            # выполняем SQL запрос с параметрами
            cursor.execute(query, (title.strip(), content.strip(), priority.lower(),
                                   status.lower(), tags_str))

            # получаем результат выполнения INSERT (возвращенный ID и created_at)
            result = cursor.fetchone()

            # извлекаем ID новой заметки
            note_id = result['id']

            # извлекаем дату создания и конвертируем в строку
            created_at = result['created_at'].isoformat() if result['created_at'] else None
            conn.commit()

            # создаем объект заметки с полученными данными
            note = Note(
                id=note_id,                  # ID из базы данных
                title=title,                 # переданный заголовок
                content=content,             # переданное содержимое
                priority=priority,           # переданный приоритет
                status=status,               # переданный статус
                tags=tags or [],             # переданные теги или пустой список
                created_at=created_at        # дата создания из базы данных
            )

            # закрываем курсор
            cursor.close()

            # закрываем подключение
            conn.close()

            # возвращаем созданную заметку в виде словаря
            return note.to_dict()

        except Exception as e:
            # выводим сообщение об ошибке и возвращаем None
            print(f"ошибка при создании заметки: {e}")
            return None

    def update_note(self, note_id: int, **kwargs) -> Optional[dict]:
        """обновляет существующую заметку."""
        try:
            # получаем подключение к базе данных
            conn = self._get_connection()

            # создаем курсор, который возвращает результаты как словари
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # получаем текущие данные заметки по ID
            current_note = self.get_note_by_id(note_id)

            # если заметка не найдена, возвращаем None
            if not current_note:
                return None

            # обновляем только переданные поля, остальные берем из текущей заметки
            # kwargs.get('ключ', значение_по_умолчанию)
            title = kwargs.get('title', current_note['title'])
            content = kwargs.get('content', current_note['content'])
            priority = kwargs.get('priority', current_note['priority'])
            status = kwargs.get('status', current_note['status'])
            tags = kwargs.get('tags', current_note['tags'])

            # преобразуем список тегов в строку, разделенную запятыми
            tags_str = ",".join([t.strip().lower() for t in tags if t.strip()])

            # SQL запрос для обновления заметки
            query = """
            UPDATE notes 
            SET title = %s, content = %s, priority = %s, status = %s, tags = %s
            WHERE id = %s  
            RETURNING created_at AT TIME ZONE 'UTC' as created_at  
            """

            # выполняем SQL запрос с параметрами
            cursor.execute(query, (title.strip(), content.strip(), priority.lower(),
                                   status.lower(), tags_str, note_id))

            # получаем результат выполнения UPDATE
            result = cursor.fetchone()

            # извлекаем дату создания и конвертируем в строку
            created_at = result['created_at'].isoformat() if result['created_at'] else None

            # фиксируем изменения в базе данных
            conn.commit()

            # создаем обновленный объект заметки
            note = Note(
                id=note_id,          # ID остается прежним
                title=title,         # обновленный заголовок
                content=content,     # обновленное содержимое
                priority=priority,   # обновленный приоритет
                status=status,       # обновленный статус
                tags=tags,           # обновленные теги
                created_at=created_at  # дата создания (может обновиться триггером)
            )

            # закрываем курсор
            cursor.close()

            # закрываем подключение
            conn.close()

            # возвращаем обновленную заметку в виде словаря
            return note.to_dict()

        except Exception as e:
            # выводим сообщение об ошибке и возвращаем None
            print(f"ошибка при обновлении заметки: {e}")
            return None

    def delete_note(self, note_id: int) -> bool:
        """удаляет заметку из базы данных."""
        try:
            # получаем подключение к базе данных
            conn = self._get_connection()

            # создаем обычный курсор (не нужен RealDictCursor для DELETE)
            cursor = conn.cursor()

            # SQL запрос для удаления заметки
            query = "DELETE FROM notes WHERE id = %s"

            # выполняем SQL запрос с параметром
            cursor.execute(query, (note_id,))

            # получаем количество удаленных строк
            rows_deleted = cursor.rowcount

            # фиксируем изменения в базе данных
            conn.commit()

            # закрываем курсор
            cursor.close()

            # закрываем подключение
            conn.close()

            # возвращаем True если удалили хотя бы одну строку, иначе False
            return rows_deleted > 0

        except Exception as e:
            # выводим сообщение об ошибке и возвращаем False
            print(f"ошибка при удалении заметки: {e}")
            return False

    def search_notes(self, query: str) -> List[dict]:
        """ищет заметки по тексту или тегам."""
        try:
            # получаем подключение к базе данных
            conn = self._get_connection()

            # создаем курсор, который возвращает результаты как словари
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # подготавливаем поисковый терм (добавляем % для LIKE)
            search_term = f"%{query.lower()}%"

            # SQL запрос для поиска заметок
            search_query = """
            SELECT id, title, content, priority, status, tags, 
                   created_at AT TIME ZONE 'UTC' as created_at
            FROM notes 
            WHERE LOWER(title) LIKE %s        
               OR LOWER(content) LIKE %s      
               OR LOWER(tags) LIKE %s         
            ORDER BY created_at DESC          
            """

            # выполняем SQL запрос с параметрами
            cursor.execute(search_query, (search_term, search_term, search_term))

            # получаем все строки результата
            rows = cursor.fetchall()

            # создаем пустой список для найденных заметок
            notes = []

            # обрабатываем каждую найденную строку
            for row in rows:
                # создаем объект Note из данных строки
                note = Note(
                    id=row['id'],
                    title=row['title'],
                    content=row['content'],
                    priority=row['priority'],
                    status=row['status'],
                    tags=row['tags'].split(',') if row['tags'] else [],
                    created_at=row['created_at'].isoformat() if row['created_at'] else None
                )
                # добавляем заметку в список в виде словаря
                notes.append(note.to_dict())

            # закрываем курсор
            cursor.close()

            # закрываем подключение
            conn.close()

            # возвращаем список найденных заметок
            return notes

        except Exception as e:
            # выводим сообщение об ошибке и возвращаем пустой список
            print(f"ошибка при поиске заметок: {e}")
            return []

    def get_stats(self) -> dict:
        """получает статистику по заметкам."""
        try:
            # получаем подключение к базе данных
            conn = self._get_connection()

            # создаем курсор, который возвращает результаты как словари
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # общее количество заметок
            cursor.execute("SELECT COUNT(*) as total FROM notes")

            # получаем результат (одну строку с одним полем)
            total = cursor.fetchone()['total']

            # количество заметок по статусам
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM notes 
                GROUP BY status 
            """)

            # создаем словарь {статус: количество}
            by_status = {row['status']: row['count'] for row in cursor.fetchall()}

            # количество заметок по приоритетам
            cursor.execute("""
                SELECT priority, COUNT(*) as count 
                FROM notes 
                GROUP BY priority  
            """)

            # создаем словарь {приоритет: количество}
            by_priority = {row['priority']: row['count'] for row in cursor.fetchall()}

            # закрываем курсор
            cursor.close()

            # закрываем подключение
            conn.close()

            # возвращаем словарь со статистикой
            return {
                "total": total,          # общее количество заметок
                "by_status": by_status,  # распределение по статусам
                "by_priority": by_priority  # распределение по приоритетам
            }

        except Exception as e:
            # выводим сообщение об ошибке и возвращаем словарь с нулевыми значениями
            print(f"ошибка при получении статистики: {e}")
            return {"total": 0, "by_status": {}, "by_priority": {}}