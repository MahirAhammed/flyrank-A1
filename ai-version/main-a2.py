import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

DB_FILE = "tasks.db"

app = FastAPI()

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()

        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            seed = [
                ("Buy groceries", 0),
                ("Write report", 0),
                ("Walk the dog", 1),
            ]
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)", seed
            )
            conn.commit()
    finally:
        conn.close()


init_db()


# ---------------------------------------------------------------------------
# Error handling: always return {"error": "<message>"}
# ---------------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Invalid request body"})


# ---------------------------------------------------------------------------
# Models (fields kept optional so we control validation/status codes manually)
# ---------------------------------------------------------------------------
class TaskCreate(BaseModel):
    title: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def row_to_task(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


def fetch_task(conn: sqlite3.Connection, task_id: int) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/tasks")
def list_tasks():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
        return [row_to_task(r) for r in rows]
    finally:
        conn.close()


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_connection()
    try:
        row = fetch_task(conn, task_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return row_to_task(row)
    finally:
        conn.close()


@app.post("/tasks", status_code=201)
def create_task(payload: TaskCreate):
    if payload.title is None or payload.title.strip() == "":
        raise HTTPException(status_code=400, detail="Title is required")

    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (payload.title, 0),
        )
        conn.commit()
        row = fetch_task(conn, cursor.lastrowid)
        return row_to_task(row)
    finally:
        conn.close()


@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=400, detail="At least one of title or done is required"
        )

    if payload.title is not None and payload.title.strip() == "":
        raise HTTPException(status_code=400, detail="Title cannot be blank")

    conn = get_connection()
    try:
        row = fetch_task(conn, task_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")

        new_title = payload.title if payload.title is not None else row["title"]
        new_done = int(payload.done) if payload.done is not None else row["done"]

        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, new_done, task_id),
        )
        conn.commit()

        updated = fetch_task(conn, task_id)
        return row_to_task(updated)
    finally:
        conn.close()


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_connection()
    try:
        row = fetch_task(conn, task_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")

        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return Response(status_code=204)
    finally:
        conn.close()