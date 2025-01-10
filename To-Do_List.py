import json
from tkinter import Tk, Label, Entry, Button, Listbox, messagebox, StringVar, OptionMenu

# Имя файла для хранения задач
TASKS_FILE = 'tasks.json'

######

def load_tasks():
    """Загружает задачи из файла"""
    try:
        with open(TASKS_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        messagebox.showwarning("Предупреждение", "Файл задач не найден или поврежден. Создан новый список задач.")
        return []
    
def save_tasks(tasks):
    """Сохраняет задачи в файл"""
    with open(TASKS_FILE, 'w') as file:
        json.dump(tasks, file)

def add_task(tasks, task_text, priority):
    """Добавляет новую задачу"""
    if not task_text.strip():
        messagebox.showerror("Ошибка", "Текст задачи не может быть пустым.")
        return
    task = {"text": task_text, "priority": priority, "completed": False}
    tasks.append(task)
    save_tasks(tasks)
    messagebox.showinfo("Успех", f"Задача '{task_text}' добавлена")

def remove_task(tasks, index):
    """Удаляет задачу по индексу."""
    if 0 <= index < len(tasks):
        removed_task = tasks.pop(index)
        messagebox.showinfo("Успех", f"Задача '{removed_task['text']}' удалена.")
    else:
        messagebox.showerror("Ошибка", "Неверный номер задачи.")

def mark_task_completed(tasks, index):
    """Помечает задачу как выполненную."""
    if 0 <= index < len(tasks):
        tasks[index]["completed"] = True
        save_tasks(tasks)
        messagebox.showinfo("Успех", f"Задача '{tasks[index]['text']}' помечена как выполненная.")
    else:
        messagebox.showerror("Ошибка", "Неверный номер задачи.")

def view_tasks(tasks, filter_completed=None):
    """Отображает задачи с учетом фильтрации по статусу."""
    filtered_tasks = tasks
    if filter_completed is not None:
        filtered_tasks = [task for task in tasks if task["completed"] == filter_completed]
    return filtered_tasks

def edit_task(tasks, index, new_text, new_priority):
    """Редактирует задачу по индексу."""
    if 0 <= index < len(tasks):
        tasks[index]["text"] = new_text
        tasks[index]["priority"] = new_priority
        save_tasks(tasks)
        messagebox.showinfo("Успех", f"Задача '{new_text}' отредактирована.")
    else:
        messagebox.showerror("Ошибка", "Неверный номер задачи.")

def sort_tasks_by_priority(tasks):
    """Сортирует задачи по приоритету."""
    priority_order = {"Низкий": 1, "Средний": 2, "Высокий": 3}
    tasks.sort(key=lambda x: priority_order[x["priority"]], reverse=True)

######

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер задач")

        self.tasks = load_tasks()

        Label(root, text="Список задач").pack(pady=5)
        self.task_listbox = Listbox(root, width=50, height=15)
        self.task_listbox.pack(pady=10)

        Label(root, text="Текст задачи").pack(pady=5)
        self.task_entry = Entry(root, width=40)
        self.task_entry.pack(pady=5)
        
        Label(root, text="Приоритет").pack(pady=5)
        self.priority_var = StringVar(root)
        self.priority_var.set("Низкий")
        self.priority_menu = OptionMenu(root, self.priority_var, "Низкий", "Средний", "Высокий")
        self.priority_menu.pack(pady=5)

        self.add_button = Button(root, text="Добавить задачу", command=add_task)
        self.add_button.pack(pady=5)

        self.remove_button = Button(root, text="Удалить задачу", command=remove_task)
        self.remove_button.pack(pady=5)

        self.complete_button = Button(root, text="Пометить как выполненную", command=mark_task_completed)
        self.complete_button.pack(pady=5)

        Label(root, text="Фильтр задач").pack(pady=5)
        self.filter_var = StringVar(root)
        self.filter_var.set("Все")
        self.filter_menu = OptionMenu(root, self.filter_var, "Все", "Выполненные", "Невыполненные", command=self.filter_tasks)
        self.filter_menu.pack(pady=5)

        self.edit_button = Button(root, text="Редактировать задачу", command=self.edit_task)
        self.edit_button.pack(pady=5)

        self.sort_button = Button(root, text="Сортировать по приоритету", command=self.sort_tasks)
        self.sort_button.pack(pady=5)

        self.update_task_list()

    def update_task_list(self):
        """Обновляет список задач в интерфейсе."""
        self.task_listbox.delete(0, 'end')
        filter_value = self.filter_var.get()
        if filter_value == "Выполненные":
            tasks_to_show = view_tasks(self.tasks, True)
        elif filter_value == "Невыполненные":
            tasks_to_show = view_tasks(self.tasks, False)
        else:
            tasks_to_show = self.tasks

        if len(tasks_to_show):
            for task in tasks_to_show:
                status = "✓" if task["completed"] else "✗"
                self.task_listbox.insert('end', f"{task['text']} [Приоритет: {task['priority']}] [{status}]")

    def remove_task(self):
        """Удаляет задачу через интерфейс."""
        try:
            selected_task_index = self.task_listbox.curselection()[0]
            remove_task(self.tasks, selected_task_index)
            self.update_task_list()
        except IndexError:
            messagebox.showerror("Ошибка", "Выберите задачу для удаления.")

    def mark_task_completed(self):
        """Помечает задачу как выполненную через интерфейс."""
        try:
            selected_task_index = self.task_listbox.curselection()[0]
            mark_task_completed(self.tasks, selected_task_index)
            self.update_task_list()
        except IndexError:
            messagebox.showerror("Ошибка", "Выберите задачу для отметки.")

    def filter_tasks(self, *args):
        """Фильтрует задачи по статусу."""
        self.update_task_list()

    def edit_task(self):
        """Редактирует задачу через интерфейс."""
        try:
            selected_task_index = self.task_listbox.curselection()[0]
            new_text = self.task_entry.get()
            new_priority = self.priority_var.get()
            if not new_text.strip():
                messagebox.showerror("Ошибка", "Текст задачи не может быть пустым.")
                return
            edit_task(self.tasks, selected_task_index, new_text, new_priority)
            self.update_task_list()
        except IndexError:
            messagebox.showerror("Ошибка", "Выберите задачу для редактирования.")

    def sort_tasks(self):
        """Сортирует задачи по приоритету и обновляет список."""
        sort_tasks_by_priority(self.tasks)
        self.update_task_list()

######

if __name__ == "__main__":
    root = Tk()
    app = TaskManagerApp(root)
    root.mainloop()