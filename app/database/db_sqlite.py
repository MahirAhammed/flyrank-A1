from app.database.base import Database
import sqlite3

class SQLiteDatabase(Database):
    def __init__(self, filename: str = "tasks.db"):
        self.filename = filename

    def get_placeholder(self) -> str:
        return "?"

    def get_connection(self):
        conn = sqlite3.connect(self.filename)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
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