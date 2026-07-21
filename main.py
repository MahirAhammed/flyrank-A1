from typing import List, Optional

from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from models import Task, TaskCreate, TaskUpdate
import database_psql as db

# FastAPI instance
app = FastAPI()
db.init_db()

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(req, exc: HTTPException) -> JSONResponse:
    """Return errors in the consistent format: {"error": "<message>"}."""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

# Helper functions
def to_task(row: dict) -> Task:
    return Task(id=row["id"], title=row["title"], done=bool(row["done"]))

def fetch_task(id: int):
    """fetch task from db by id."""
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s", (id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_valid_task(id: int) -> Task:
    """Return the Task for id, or raise exception."""
    row = fetch_task(id)
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return to_task(row)

# Root endpoint
@app.get("/")
async def root():
    """Provide API info."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

# Health check
@app.get("/health")
async def health():
    """Health check"""
    return { "status": "ok" }


@app.get("/tasks", response_model=List[Task])
async def get_all_tasks(done: Optional[bool] = None, search: Optional[str]= None):
    """Return the full list of tasks, with optional filtering."""
    
    conn = db.get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if done is not None:
        query += " AND done = %s"
        params.append(done)
    
    if search:
        query += " AND LOWER(title) LIKE %s"
        params.append(f"%{search.lower()}%")

    query += " ORDER BY title"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return [to_task(row) for row in rows]

@app.get("/tasks/{id}", response_model= Task)
async def get_task(id: int):
    """Return a single task by its id if exists."""
    return get_valid_task(id)

@app.post("/tasks", response_model= Task, status_code= status.HTTP_201_CREATED)
async def create_task(req: TaskCreate):
    """Creates a new task from a title"""
    reqTitle = req.title
    if not reqTitle or not reqTitle.strip():
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST,detail= "Title is required")  
    
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (req.title, 0))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return Task(id=new_id, title=reqTitle, done=False)

@app.put("/tasks/{id}", response_model= Task)
async def update_task(id: int, req: TaskUpdate):
    """Updates task title and/or done status."""
    if req.title is None and req.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Request body must include title and/or done"
        )
    
    if req.title is not None and not req.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Title cannot be empty"
        )
    
    current_task = get_valid_task(id)

    new_title = req.title if req.title is not None else current_task.title
    new_done = req.done if req.done is not None else bool(current_task.done)

    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, 1 if new_done else 0, id),
    )
    conn.commit()
    conn.close()

    return Task(id= id, title= new_title, done= new_done)

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int):
    """Delete a task by id."""
    get_valid_task(id)

    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()

@app.get("/stats", status_code= 200)
async def stats():
    """Return counts of total, done and open tasks."""
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM tasks")
    total = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS done_count FROM tasks WHERE done = 1")
    done = cur.fetchone()["done_count"]
    conn.close()

    return {"total": total, "done": done, "open": total - done}