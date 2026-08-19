from app.database.base import Database
from app.database.factory import db
from typing import Optional

placeholder = db.get_placeholder()

def fetch_all_tasks(done: Optional[bool] = None, search: Optional[str]= None):
    """Return the full list of tasks, with optional filtering."""
        
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if done is not None:
        query += f" AND done = {placeholder}"
        params.append(done)
    
    if search:
        query += f" AND LOWER(title) LIKE {placeholder}"
        params.append(f"%{search.lower()}%")

    query += " ORDER BY title"

    conn = db.get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def fetch_task(task_id: int):
    """Return a task by id."""
    conn = db.get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            f"SELECT * FROM tasks WHERE id = {placeholder}",
            (task_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_task(title: str):
    """Creates a new task from a title"""

    conn = db.get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            f"""
            INSERT INTO tasks (title, done) 
            VALUES ({placeholder}, FALSE)
            RETURNING *
            """,
            (title,)
        )
        row = cur.fetchone()
        conn.commit()
        return dict(row)
    
    finally:
        conn.close()


def update_task(task_id: int, title: str, done: bool):
    """Updates task title and/or done status."""

    conn = db.get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            f"""
            UPDATE tasks
            SET title = {placeholder}, done = {placeholder}
            WHERE id = {placeholder}
            RETURNING *
            """,
            (title, done, task_id),
        )
        row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_task(task_id: int):
    """Delete a task by id."""

    conn = db.get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM tasks WHERE id = {placeholder}", (task_id,))
        conn.commit()

    finally:
        conn.close()


def stats():
    conn = db.get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM tasks")
        total = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(*) AS done_count FROM tasks WHERE done IS TRUE")
        done = cur.fetchone()["done_count"]
    finally:
        conn.close()

    return {"total": total, "done": done, "open": total - done}