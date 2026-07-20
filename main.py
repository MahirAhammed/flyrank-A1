from typing import List, Optional

from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from models import Task, TaskCreate, TaskUpdate
import database as db

# data
tasks: List[Task] = [
    Task(id= 1, title= "Complete assignment A1", done= False),
    Task(id= 2, title= "Watch lecture 2A", done= True),
    Task(id= 3, title= "Water the plants", done= False )
]

id_counter = 4
default_tasks = tasks # store the default tasks for reset

# Helper function
def find_task(id: int) -> Task:
    """Return the task with given id."""
    for t in tasks:
        if t.id == id:
            return t
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {id} not found")



# FastAPI instance
app = FastAPI()
db.init_db()

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(req, exc: HTTPException) -> JSONResponse:
    """Return errors in the consistent format: {"error": "<message>"}."""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

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
        query += " AND done = ?"
        params.append(1 if done else 0)
    
    if search:
        query += " AND LOWER(title) LIKE ?"
        params.append(f"%{search.lower()}%")

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return [
        {"id": row["id"], "title": row["title"], "done": bool(row["done"])} for row in rows
    ]

@app.get("/tasks/{id}", response_model= Task)
async def get_task(id: int):
    """Return a single task by its id if exists."""
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return Task(id= row["id"], title= row["title"], done= bool(row["done"]))

@app.post("/tasks", response_model= Task, status_code= status.HTTP_201_CREATED)
async def create_task(req: TaskCreate):
    """Creates a new task from a title"""
    
    reqTitle = req.title
    if not reqTitle or not reqTitle.strip():
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST,detail= "Title is required")  
    
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks VALUES (?, ?)", (req.title, 0))
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
    
    task = find_task(id)
    if req.title is not None:
        task.title = req.title
    if req.done is not None:
        task.done = req.done

    return task

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int):
    """Delete a task by id."""
    task = find_task(id)
    tasks.remove(task)

@app.get("/stats")
async def get_stats():
    """Return counts of total, done, and open tasks."""
    total = len(tasks)
    done = 0
    for t in tasks:
        if t.done:
            done += 1

    return {"total": total, "done": done, "open": total - done}

@app.post("/reset")
async def reset():
    global tasks, id_counter
    tasks = default_tasks
    id_counter = 4
    return {"message": "tasks reset"}