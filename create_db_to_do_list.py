import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('todo.db')
cursor = conn.cursor()

# Создание таблицы lists
cursor.execute('''
CREATE TABLE IF NOT EXISTS lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
''')

# Создание таблицы tasks
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER,
    description TEXT NOT NULL,
    completed INTEGER DEFAULT 0,
    deadline TEXT,
    priority TEXT,
    category TEXT,
    FOREIGN KEY (list_id) REFERENCES lists (id)
)
''')

# Сохранение изменений
conn.commit()

# Закрытие соединения
conn.close()