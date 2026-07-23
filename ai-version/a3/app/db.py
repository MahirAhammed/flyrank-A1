import os
from contextlib import contextmanager

from psycopg_pool import ConnectionPool

DATABASE_URL = os.environ["DATABASE_URL"]

SEED_TASKS = [
    ("Buy groceries", False),
    ("Write project report", False),
    ("Schedule dentist appointment", True),
]

pool: ConnectionPool | None = None


def init_pool() -> None:
    """Create the connection pool. Called once at app startup."""
    global pool
    pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=10, open=True)


def close_pool() -> None:
    """Close the connection pool. Called once at app shutdown."""
    if pool is not None:
        pool.close()


@contextmanager
def get_conn():
    """Borrow a connection from the pool for the duration of a request."""
    with pool.connection() as conn:
        yield conn


def init_db() -> None:
    """
    Create the tasks table if it doesn't already exist, and seed it with
    example rows only if it is currently empty. Safe to call on every
    startup/restart.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                )
                """
            )

            cur.execute("SELECT COUNT(*) FROM tasks")
            (row_count,) = cur.fetchone()

            if row_count == 0:
                cur.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                    SEED_TASKS,
                )
        conn.commit()
