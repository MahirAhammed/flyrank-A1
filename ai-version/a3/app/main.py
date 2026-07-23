from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.db import close_pool, get_conn, init_db, init_pool
from app.models import TaskCreate, TaskUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_pool()
    init_db()
    yield
    close_pool()


app = FastAPI(title="Task Manager API", lifespan=lifespan)

# --- Error handling -------------------------------------------------------
# Force every error response (including FastAPI/Starlette defaults) into
# {"error": "<message>"} instead of the default {"detail": ...} shape.

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Invalid request data"})


# --- Helpers ----------------------------------------------------------------

def row_to_task(row) -> dict:
    task_id, title, done = row
    return {"id": task_id, "title": title, "done": done}


# --- Endpoints ----------------------------------------------------------------

@app.get("/tasks")
def list_tasks():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
        rows = cur.fetchall()
    return [row_to_task(r) for r in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
        row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return row_to_task(row)


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    if payload.title is None or not payload.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
            (payload.title.strip(), False),
        )
        row = cur.fetchone()
        conn.commit()

    return row_to_task(row)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=400, detail="At least one of title or done is required"
        )
    if payload.title is not None and not payload.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be blank")

    # Field names below are fixed literals (never user input), so building
    # this clause is safe; all values are still passed as placeholders.
    set_clauses = []
    values: list = []
    if payload.title is not None:
        set_clauses.append("title = %s")
        values.append(payload.title.strip())
    if payload.done is not None:
        set_clauses.append("done = %s")
        values.append(payload.done)
    values.append(task_id)

    query = f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = %s RETURNING id, title, done"

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query, values)
        row = cur.fetchone()
        conn.commit()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return row_to_task(row)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,))
        row = cur.fetchone()
        conn.commit()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return None
