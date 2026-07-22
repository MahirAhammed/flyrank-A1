import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]

def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done)")

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()["count"]

    if count == 0:
        seed_tasks = ["Complete assignment A3", "Watch lecture 2C", "Water the plants"]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (%s, FALSE)",
            [(t,) for t in seed_tasks],
        )

    conn.commit()
    conn.close()