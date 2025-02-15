import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import csv
from datetime import datetime
import sqlite3

class Task:
    def __init__(self, description, completed=False, deadline=None, priority="средний", category=None):
        self.description = description
        self.completed = completed
        self.deadline = deadline
        self.priority = priority
        self.category = category

    def __str__(self):
        status = "✓" if self.completed else "✗"
        deadline_info = f", Дедлайн: {self.deadline}" if self.deadline else ""
        priority_info = f", Приоритет: {self.priority}" if self.priority else ""
        category_info = f", Категория: {self.category}" if self.category else ""
        return f"[{status}] {self.description}{deadline_info}{priority_info}{category_info}"

class ToDoList:
    def __init__(self, name):
        self.name = name
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        conn = sqlite3.connect('todo.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM lists WHERE name = ?", (self.name,))
        list_id = cursor.fetchone()
        if list_id:
            list_id = list_id[0]
            cursor.execute("SELECT description, completed, deadline, priority, category FROM tasks WHERE list_id = ?", (list_id,))
            self.tasks = [Task(task[0], task[1], task[2], task[3], task[4]) for task in cursor.fetchall()]
        conn.close()

    def add_task(self, description, deadline=None, priority="средний", category=None):
        conn = sqlite3.connect('todo.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM lists WHERE name = ?", (self.name,))
        list_id = cursor.fetchone()
        if not list_id:
            cursor.execute("INSERT INTO lists (name) VALUES (?)", (self.name,))
            list_id = cursor.lastrowid
        else:
            list_id = list_id[0]
        cursor.execute("INSERT INTO tasks (list_id, description, deadline, priority, category) VALUES (?, ?, ?, ?, ?)",
                       (list_id, description, deadline, priority, category))
        conn.commit()
        conn.close()
        self.tasks.append(Task(description, False, deadline, priority, category))

    def view_tasks(self):
        return [str(task) for task in self.tasks]

    def mark_task_completed(self, task_number):
        if 1 <= task_number <= len(self.tasks):
            self.tasks[task_number - 1].completed = True
            self.save_tasks()

    def delete_task(self, task_number):
        if 1 <= task_number <= len(self.tasks):
            task = self.tasks.pop(task_number - 1)
            conn = sqlite3.connect('todo.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE description = ?", (task.description,))
            conn.commit()
            conn.close()

    def edit_task(self, task_number, new_description):
        if 1 <= task_number <= len(self.tasks):
            self.tasks[task_number - 1].description = new_description

    def set_deadline(self, task_number, deadline):
        if 1 <= task_number <= len(self.tasks):
            self.tasks[task_number - 1].deadline = deadline

    def set_priority(self, task_number, priority):
        if 1 <= task_number <= len(self.tasks):
            self.tasks[task_number - 1].priority = priority

    def set_category(self, task_number, category):
        if 1 <= task_number <= len(self.tasks):
            self.tasks[task_number - 1].category = category

    def sort_tasks(self, completed_first=True):
        self.tasks.sort(key=lambda task: task.completed == completed_first, reverse=True)

    def save_to_file(self, filename=None):
        if not filename:
            filename = f"{self.name}.json"
        with open(filename, "w", encoding="utf-8") as file:
            tasks_data = [{"description": task.description, "completed": task.completed, "deadline": task.deadline, "priority": task.priority, "category": task.category} for task in self.tasks]
            json.dump(tasks_data, file, indent=4, ensure_ascii=False)

    def load_from_file(self, filename=None):
        if not filename:
            filename = f"{self.name}.json"
        try:
            with open(filename, "r", encoding="utf-8") as file:
                tasks_data = json.load(file)
                self.tasks = [Task(task["description"], task["completed"], task["deadline"], task["priority"], task["category"]) for task in tasks_data]
        except FileNotFoundError:
            pass

    def export_to_csv(self, filename=None):
        if not filename:
            filename = f"{self.name}.csv"
        with open(filename, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Описание", "Статус", "Дедлайн", "Приоритет", "Категория"])
            for task in self.tasks:
                status = "Выполнена" if task.completed else "Не выполнена"
                writer.writerow([task.description, status, task.deadline, task.priority, task.category])

    def check_deadlines(self):
        today = datetime.today().date()
        reminders = []
        for task in self.tasks:
            if task.deadline:
                deadline_date = datetime.strptime(task.deadline, "%Y-%m-%d").date()
                if deadline_date == today:
                    reminders.append(f"Напоминание: задача '{task.description}' должна быть выполнена сегодня.")
                elif deadline_date < today:
                    reminders.append(f"Напоминание: задача '{task.description}' просрочена.")
        return reminders
    
    def save_tasks(self):
        conn = sqlite3.connect('todo.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM lists WHERE name = ?", (self.name,))
        list_id = cursor.fetchone()[0]
        for task in self.tasks:
            cursor.execute("UPDATE tasks SET completed = ?, deadline = ?, priority = ?, category = ? WHERE description = ? AND list_id = ?",
                           (task.completed, task.deadline, task.priority, task.category, task.description, list_id))
        conn.commit()
        conn.close()

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ToDo List App")
        self.lists = self.load_lists()
        self.current_list = None

        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(pady=10)

        self.list_label = tk.Label(self.list_frame, text="Списки задач:")
        self.list_label.pack()

        self.listbox = tk.Listbox(self.list_frame, width=50)
        self.listbox.pack()

        self.task_frame = tk.Frame(self.root)
        self.task_frame.pack(pady=10)

        self.task_label = tk.Label(self.task_frame, text="Задачи:")
        self.task_label.pack()

        self.task_listbox = tk.Listbox(self.task_frame, width=50)
        self.task_listbox.pack()

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.create_list_button = tk.Button(self.button_frame, text="Создать список", command=self.create_list)
        self.create_list_button.grid(row=0, column=0, padx=5)

        self.select_list_button = tk.Button(self.button_frame, text="Выбрать список", command=self.select_list)
        self.select_list_button.grid(row=0, column=1, padx=5)

        self.add_task_button = tk.Button(self.button_frame, text="Добавить задачу", command=self.add_task)
        self.add_task_button.grid(row=0, column=2, padx=5)

        self.mark_completed_button = tk.Button(self.button_frame, text="Отметить выполненной", command=self.mark_completed)
        self.mark_completed_button.grid(row=0, column=3, padx=5)

        self.delete_task_button = tk.Button(self.button_frame, text="Удалить задачу", command=self.delete_task)
        self.delete_task_button.grid(row=0, column=4, padx=5)

        self.edit_task_button = tk.Button(self.button_frame, text="Редактировать задачу", command=self.edit_task)
        self.edit_task_button.grid(row=1, column=0, padx=5)

        self.set_deadline_button = tk.Button(self.button_frame, text="Установить дедлайн", command=self.set_deadline)
        self.set_deadline_button.grid(row=1, column=1, padx=5)

        self.set_priority_button = tk.Button(self.button_frame, text="Установить приоритет", command=self.set_priority)
        self.set_priority_button.grid(row=1, column=2, padx=5)

        self.set_category_button = tk.Button(self.button_frame, text="Установить категорию", command=self.set_category)
        self.set_category_button.grid(row=1, column=3, padx=5)

        self.sort_tasks_button = tk.Button(self.button_frame, text="Сортировать задачи", command=self.sort_tasks)
        self.sort_tasks_button.grid(row=1, column=4, padx=5)

        self.save_tasks_button = tk.Button(self.button_frame, text="Сохранить задачи", command=self.save_tasks)
        self.save_tasks_button.grid(row=2, column=0, padx=5)

        self.export_csv_button = tk.Button(self.button_frame, text="Экспорт в CSV", command=self.export_csv)
        self.export_csv_button.grid(row=2, column=1, padx=5)

        self.delete_list_button = tk.Button(self.button_frame, text="Удалить список", command=self.delete_list)
        self.delete_list_button.grid(row=2, column=2, padx=5)

        self.check_deadlines_button = tk.Button(self.button_frame, text="Проверить дедлайны", command=self.check_deadlines)
        self.check_deadlines_button.grid(row=2, column=3, padx=5)

        self.exit_button = tk.Button(self.button_frame, text="Выйти", command=self.root.quit)
        self.exit_button.grid(row=2, column=4, padx=5)

        self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for list_name in self.lists:
            self.listbox.insert(tk.END, list_name)

    def update_task_listbox(self):
        self.task_listbox.delete(0, tk.END)
        if self.current_list:
            for task in self.current_list.view_tasks():
                self.task_listbox.insert(tk.END, task)

    def create_list(self):
        list_name = simpledialog.askstring("Создать список", "Введите название списка задач:")
        if list_name:
            self.lists[list_name] = ToDoList(list_name)
            self.current_list = self.lists[list_name]
            self.update_listbox()

    def select_list(self):
        selected = self.listbox.curselection()
        if selected:
            list_name = self.listbox.get(selected)
            self.current_list = self.lists[list_name]
            self.current_list.load_tasks()
            self.update_task_listbox()

    def add_task(self):
        if self.current_list:
            description = simpledialog.askstring("Добавить задачу", "Введите описание задачи:")
            if description:
                deadline = simpledialog.askstring("Добавить задачу", "Введите дедлайн (опционально, формат ГГГГ-ММ-ДД):")
                priority = simpledialog.askstring("Добавить задачу", "Введите приоритет (высокий, средний, низкий):")
                category = simpledialog.askstring("Добавить задачу", "Введите категорию (опционально):")
                self.current_list.add_task(description, deadline if deadline else None, priority, category if category else None)
                self.update_task_listbox()

    def mark_completed(self):
        if self.current_list:
            selected = self.task_listbox.curselection()
            if selected:
                task_number = selected[0] + 1
                self.current_list.mark_task_completed(task_number)
                self.update_task_listbox()

    def delete_task(self):
        if self.current_list:
            selected = self.task_listbox.curselection()
            if selected:
                task_number = selected[0] + 1
                self.current_list.delete_task(task_number)
                self.update_task_listbox()

    def edit_task(self):
        if self.current_list:
            selected = self.task_listbox.curselection()
            if selected:
                task_number = selected[0] + 1
                new_description = simpledialog.askstring("Редактировать задачу", "Введите новое описание задачи:")
                if new_description:
                    self.current_list.edit_task(task_number, new_description)
                    self.update_task_listbox()

    def set_deadline(self):
        if self.current_list:
            selected = self.task_listbox.curselection()
            if selected:
                task_number = selected[0] + 1
                deadline = simpledialog.askstring("Установить дедлайн", "Введите дедлайн (формат ГГГГ-ММ-ДД):")
                if deadline:
                    self.current_list.set_deadline(task_number, deadline)
                    self.update_task_listbox()

    def set_priority(self):
        if self.current_list:
            selected = self.task_listbox.curselection()
            if selected:
                task_number = selected[0] + 1
                priority = simpledialog.askstring("Установить приоритет", "Введите приоритет (высокий, средний, низкий):")
                if priority:
                    self.current_list.set_priority(task_number, priority)
                    self.update_task_listbox()

    def set_category(self):
        if self.current_list:
            selected = self.task_listbox.curselection()
            if selected:
                task_number = selected[0] + 1
                category = simpledialog.askstring("Установить категорию", "Введите категорию:")
                if category:
                    self.current_list.set_category(task_number, category)
                    self.update_task_listbox()

    def set_category(self):
        if self.current_list:
            selected = self.task_listbox.curselection()
            if selected:
                task_number = selected[0] + 1
                category = simpledialog.askstring("Установить категорию", "Введите категорию:")
                if category:
                    self.current_list.set_category(task_number, category)
                    self.update_task_listbox()

    def save_tasks(self):
        if self.current_list:
            self.current_list.save_to_file()

    def export_csv(self):
        if self.current_list:
            self.current_list.export_to_csv()

    def delete_list(self):
        selected = self.listbox.curselection()
        if selected:
            list_name = self.listbox.get(selected)
            del self.lists[list_name]
            self.update_listbox()
            self.current_list = None
            self.task_listbox.delete(0, tk.END)

    def check_deadlines(self):
        if self.current_list:
            reminders = self.current_list.check_deadlines()
            if reminders:
                messagebox.showinfo("Напоминания", "\n".join(reminders))
            else:
                messagebox.showinfo("Напоминания", "Нет задач с дедлайнами на сегодня или просроченных задач.")

    def load_lists(self):
        conn = sqlite3.connect('todo.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM lists")
        lists = {row[0]: ToDoList(row[0]) for row in cursor.fetchall()}
        conn.close()
        return lists

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
