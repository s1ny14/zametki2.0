"""
Модуль app - графический интерфейс приложения "Менеджер заметок".

Содержит класс NoteApp с Tkinter интерфейсом для управления заметками.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from notebook import Storage, Note

# === РОЗОВАЯ ТЕМА ===
BG_COLOR = "#FFF0F5"
PINK = "#FFC1CC"
DARK_PINK = "#FF69B4"
WHITE = "#FFFFFF"
TEXT_COLOR = "#333333"


class NoteApp:
    """Главный класс графического приложения для управления заметками.

    Attributes:
        root (tk.Tk): Корневое окно приложения
        storage (Storage): Объект для работы с хранилищем
        priority_buttons (dict): Кнопки выбора приоритета
        status_buttons (dict): Кнопки выбора статуса
    """

    def __init__(self, root):
        """Инициализирует приложение.

        Args:
            root (tk.Tk): Корневое окно Tkinter
        """
        self.root = root
        self.root.title("Менеджер заметок — #хэштеги")
        self.root.geometry("950x650")
        self.root.minsize(850, 550)
        self.root.configure(bg=BG_COLOR)
        self.storage = Storage()

        self.priority_buttons = {}
        self.status_buttons = {}

        self.setup_styles()
        self.setup_ui()
        self.refresh_notes()

    def setup_styles(self):
        """Настраивает стили для Tkinter виджетов."""
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Pink.TButton',
                        background=PINK,
                        foreground=TEXT_COLOR,
                        font=('Segoe UI', 10, 'bold'),
                        padding=6)
        style.map('Pink.TButton',
                  background=[('active', DARK_PINK)],
                  foreground=[('active', 'white')])

        style.configure('P.TLabelframe',
                        background=BG_COLOR,
                        foreground=DARK_PINK,
                        font=('Segoe UI', 12, 'bold'))
        style.configure('P.TLabelframe.Label',
                        background=BG_COLOR,
                        foreground=DARK_PINK)

        style.configure('Treeview',
                        background=WHITE,
                        fieldbackground=WHITE,
                        font=('Segoe UI', 10),
                        rowheight=28)
        style.configure('Treeview.Heading',
                        background=PINK,
                        foreground=TEXT_COLOR,
                        font=('Segoe UI', 10, 'bold'))
        style.map('Treeview',
                  background=[('selected', DARK_PINK)])

    def setup_ui(self):
        """Создает пользовательский интерфейс приложения."""
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === ЛЕВАЯ ЧАСТЬ: форма ===
        form_frame = ttk.Labelframe(main_frame, text=" Новая заметка ", style='P.TLabelframe', padding=12)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        # Заголовок
        ttk.Label(form_frame, text="Заголовок:", background=BG_COLOR, font=('Segoe UI', 10)).pack(anchor="w",
                                                                                                  pady=(0, 3))
        self.title_entry = ttk.Entry(form_frame, width=38, font=('Segoe UI', 11))
        self.title_entry.pack(fill=tk.X, pady=2)

        # Содержание
        ttk.Label(form_frame, text="Содержание:", background=BG_COLOR, font=('Segoe UI', 10)).pack(anchor="w",
                                                                                                   pady=(10, 3))
        self.content_text = scrolledtext.ScrolledText(form_frame, width=38, height=9, wrap=tk.WORD,
                                                      font=('Segoe UI', 11))
        self.content_text.pack(fill=tk.X, pady=2)

        # ХЭШТЕГИ
        ttk.Label(form_frame, text="Хэштеги (#учеба #работа #дом):", background=BG_COLOR, font=('Segoe UI', 10)).pack(
            anchor="w", pady=(12, 3))
        self.tags_entry = ttk.Entry(form_frame, font=('Segoe UI', 11))
        self.tags_entry.pack(fill=tk.X, pady=2)
        ttk.Label(form_frame, text="Пиши через пробел или запятую", background=BG_COLOR, font=('Segoe UI', 9),
                  foreground="gray").pack(anchor="w")

        # Приоритет
        ttk.Label(form_frame, text="Приоритет:", background=BG_COLOR, font=('Segoe UI', 10)).pack(anchor="w",
                                                                                                  pady=(12, 3))
        priority_frame = ttk.Frame(form_frame)
        priority_frame.pack(fill=tk.X, pady=2)
        self.priority_var = tk.StringVar(value="medium")
        for text, value in [("Низкий", "low"), ("Средний", "medium"), ("Высокий", "high")]:
            btn = tk.Button(priority_frame, text=text, bg=PINK, fg=TEXT_COLOR, font=('Segoe UI', 9, 'bold'),
                            relief='flat', command=lambda v=value: self.select_priority(v))
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
            self.priority_buttons[value] = btn
        self.select_priority("medium")

        # Статус
        ttk.Label(form_frame, text="Статус:", background=BG_COLOR, font=('Segoe UI', 10)).pack(anchor="w", pady=(12, 3))
        status_frame = ttk.Frame(form_frame)
        status_frame.pack(fill=tk.X, pady=2)
        self.status_var = tk.StringVar(value="active")
        for text, value in [("В работе", "active"), ("Готово", "done"), ("Архив", "archived")]:
            btn = tk.Button(status_frame, text=text, bg=PINK, fg=TEXT_COLOR, font=('Segoe UI', 9, 'bold'),
                            relief='flat', command=lambda v=value: self.select_status(v))
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
            self.status_buttons[value] = btn
        self.select_status("active")

        # Кнопка добавления
        ttk.Button(form_frame, text="Добавить заметку", style='Pink.TButton', command=self.add_note).pack(pady=20,
                                                                                                          fill=tk.X)

        # === ПРАВАЯ ЧАСТЬ: список ===
        list_frame = ttk.Labelframe(main_frame, text=" Мои заметки ", style='P.TLabelframe', padding=12)
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Поиск
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(search_frame, text="Поиск (текст или #тег):", background=BG_COLOR, font=('Segoe UI', 10)).pack(
            side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, font=('Segoe UI', 11))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_notes())
        clear_btn = tk.Button(search_frame, text="Очистить", bg=DARK_PINK, fg="white", font=('Segoe UI', 9, 'bold'),
                              relief='flat',
                              command=lambda: self.search_entry.delete(0, tk.END) or self.refresh_notes())
        clear_btn.pack(side=tk.RIGHT)

        # Таблица
        columns = ("id", "title", "tags", "priority", "status", "date")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", style='Treeview')
        widths = [50, 280, 180, 90, 90, 100]
        texts = ["ID", "Заголовок", "Хэштеги", "Приоритет", "Статус", "Дата"]
        for col, text, width in zip(columns, texts, widths):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.show_details)
        self.tree.bind("<Delete>", self.delete_selected)

        # Кнопки
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="Удалить выбранное", style='Pink.TButton', command=self.delete_selected).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить список", style='Pink.TButton', command=self.refresh_notes).pack(
            side=tk.LEFT)

    def select_priority(self, value: str):
        """Выбирает приоритет заметки.

        Args:
            value (str): Значение приоритета (low/medium/high)
        """
        self.priority_var.set(value)
        for val, btn in self.priority_buttons.items():
            btn.configure(bg=DARK_PINK if val == value else PINK, fg="white" if val == value else TEXT_COLOR)

    def select_status(self, value: str):
        """Выбирает статус заметки.

        Args:
            value (str): Значение статуса (active/done/archived)
        """
        self.status_var.set(value)
        for val, btn in self.status_buttons.items():
            btn.configure(bg=DARK_PINK if val == value else PINK, fg="white" if val == value else TEXT_COLOR)

    def add_note(self):
        """Добавляет новую заметку на основе данных из формы."""
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        if not title or not content:
            messagebox.showwarning("Ошибка", "Заполните заголовок и содержание!")
            return

        tags_input = self.tags_entry.get()
        tags = [t.strip().lstrip('#').lower() for t in tags_input.replace(',', ' ').split() if t.strip()]

        note = Note(
            title=title,
            content=content,
            priority=self.priority_var.get(),
            status=self.status_var.get(),
            tags=tags
        )
        if self.storage.save(note):
            messagebox.showinfo("Готово!", f"Заметка добавлена (ID: {note.id})")
            self.clear_form()
            self.refresh_notes()
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить")

    def clear_form(self):
        """Очищает форму ввода новой заметки."""
        self.title_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)
        self.tags_entry.delete(0, tk.END)
        self.select_priority("medium")
        self.select_status("active")

    def refresh_notes(self):
        """Обновляет список заметок в таблице с учетом поискового запроса."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        search = self.search_entry.get().lower().lstrip('#')
        notes = self.storage.get_all()

        for note in notes:
            tags_str = ", ".join([f"#{t}" for t in note.tags]) if note.tags else "—"
            priority_text = {"low": "Низкий", "medium": "Средний", "high": "Высокий"}[note.priority]
            status_text = {"active": "В работе", "done": "Готово", "archived": "Архив"}[note.status]

            # Поиск по заголовку, содержимому или тегам
            if search:
                if (search in note.title.lower() or
                        search in note.content.lower() or
                        search in " ".join(note.tags)):
                    self.tree.insert("", tk.END, values=(
                        note.id, note.title, tags_str, priority_text, status_text, note.created_at[:10]
                    ))
            else:
                self.tree.insert("", tk.END, values=(
                    note.id, note.title, tags_str, priority_text, status_text, note.created_at[:10]
                ))

    def show_details(self, event=None):
        """Показывает детали выбранной заметки.

        Args:
            event: Событие двойного клика (опционально)
        """
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        note_id = int(item["values"][0])
        note = next((n for n in self.storage.get_all() if n.id == note_id), None)
        if note:
            self.open_detail_window(note)

    def open_detail_window(self, note: Note):
        """Открывает окно с деталями заметки.

        Args:
            note (Note): Объект заметки для отображения
        """
        win = tk.Toplevel(self.root)
        win.title(f"Заметка #{note.id}")
        win.geometry("600x500")
        win.configure(bg=BG_COLOR)
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text=note.title, font=("Segoe UI", 16, "bold"), background=BG_COLOR, foreground=DARK_PINK).pack(
            pady=15, anchor="w", padx=20)
        meta = f"Приоритет: {note.priority} | Статус: {note.status} | {note.created_at[:10]}"
        ttk.Label(win, text=meta, background=BG_COLOR, foreground="gray").pack(anchor="w", padx=20)
        if note.tags:
            tags_str = " • ".join([f"#{t}" for t in note.tags])
            ttk.Label(win, text=tags_str, background=BG_COLOR, foreground=DARK_PINK, font=('Segoe UI', 11)).pack(
                anchor="w", padx=20, pady=5)

        text = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Segoe UI", 11), bg=WHITE, relief='flat', padx=10,
                                         pady=10)
        text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        text.insert(tk.END, note.content)
        text.config(state=tk.DISABLED)

    def delete_selected(self, event=None):
        """Удаляет выбранную заметку.

        Args:
            event: Событие нажатия клавиши Delete (опционально)
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Выберите", "Выберите заметку для удаления")
            return
        if messagebox.askyesno("Удалить?", "Удалить выбранную заметку?"):
            note_id = int(self.tree.item(selected[0], "values")[0])
            if self.storage.delete(note_id):
                self.refresh_notes()
                messagebox.showinfo("Удалено", f"Заметка ID {note_id} удалена")
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить")