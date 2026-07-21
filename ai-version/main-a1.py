"""
Simple in-memory Task Manager REST API built with FastAPI.
"""

from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="Task Manager API",
    description="A simple in-memory task manager.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class Task(BaseModel):
    """A single task."""
    id: int
    title: str
    done: bool = False


class TaskCreate(BaseModel):
    """Payload for creating a task."""
    title: Optional[str] = None


class TaskUpdate(BaseModel):
    """Payload for updating a task. Both fields are optional."""
    title: Optional[str] = None
    done: Optional[bool] = None


# ---------------------------------------------------------------------------
# In-memory data store
# ---------------------------------------------------------------------------
tasks: list[Task] = []
_next_id: int = 1


def _seed_tasks() -> None:
    """Populate the store with example tasks on startup."""
    global _next_id
    seed_titles = [
        "Buy groceries",
        "Write project report",
        "Schedule dentist appointment",
    ]
    for title in seed_titles:
        tasks.append(Task(id=_next_id, title=title, done=False))
        _next_id += 1

_seed_tasks()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_task_or_404(task_id: int) -> Task:
    """Return the task with the given id, or raise a 404 HTTPException."""
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


def _next_task_id() -> int:
    """Return the next available task id and advance the counter."""
    global _next_id
    new_id = _next_id
    _next_id += 1
    return new_id


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException) -> JSONResponse:
    """Return errors in the consistent format: {"error": "<message>"}."""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/tasks", response_model=list[Task], summary="List all tasks")
def list_tasks() -> list[Task]:
    """Return every task currently stored."""
    return tasks


@app.get("/tasks/{task_id}", response_model=Task, summary="Get a single task by id")
def get_task(task_id: int) -> Task:
    """Return the task matching the given id, or 404 if it doesn't exist."""
    return _get_task_or_404(task_id)


@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(payload: TaskCreate) -> Task:
    """Create a task from a title, auto-assigning its id and defaulting done to false."""
    if payload.title is None:
        raise HTTPException(status_code=400, detail="title is missing")
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="title is empty")

    task = Task(id=_next_task_id(), title=payload.title, done=False)
    tasks.append(task)
    return task


@app.put("/tasks/{task_id}", response_model=Task, summary="Update a task's title and/or done status")
def update_task(task_id: int, payload: TaskUpdate) -> Task:
    """Update title and/or done for an existing task. At least one field is required."""
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=400, detail="at least one of title or done must be provided"
        )
    if payload.title is not None and not payload.title.strip():
        raise HTTPException(status_code=400, detail="title is empty")

    task = _get_task_or_404(task_id)

    if payload.title is not None:
        task.title = payload.title
    if payload.done is not None:
        task.done = payload.done

    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task by id",
)
def delete_task(task_id: int) -> None:
    """Remove the task matching the given id, or 404 if it doesn't exist."""
    task = _get_task_or_404(task_id)
    tasks.remove(task)