import sqlite3

def get_connection():
    conn = sqlite3.connect("tasks.db")
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)
    
    cur.execute("SELECT COUNT(*) FROM tasks")
    count = cur.fetchone()[0]

    if count == 0:
        seed_tasks = ["Complete assignment A2", "Watch lecture 2B", "Water the plants"]
        cur.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, 0)", [(title, ) for title in seed_tasks]
        )
    
    conn.commit()
    conn.close()