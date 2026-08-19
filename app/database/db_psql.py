import psycopg
from psycopg.rows import dict_row
from app.database.base import Database
import redis

rs = redis.Redis(host= "redis", port= 6379, decode_responses= True)

class PostgresDatabase(Database):
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def get_placeholder(self) -> str:
        return "%s"
    
    def get_connection(self):
        return psycopg.connect(
            self.database_url,
            row_factory= dict_row,
        )

    def init_db(self) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done)"
        )

        cursor.execute("SELECT COUNT(*) AS count FROM tasks")
        count = cursor.fetchone()["count"]

        if count == 0:
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (%s, FALSE)",
                [
                    ("Complete assignment A3",),
                    ("Watch lecture 2C",),
                    ("Water the plants",),
                ],
            )

        conn.commit()
        conn.close()

    def ping(self):
        super().ping()
        rs.ping()