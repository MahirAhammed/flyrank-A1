from typing import List

from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Task model
class Task(BaseModel):
    id: int | None = None
    title: str
    done: bool = False

# Task request DTO
class TaskRequest(BaseModel):
    title: str | None = None
    done: bool | None = None

# data
tasks: List[Task] = [
    Task(id= 1, title= "Complete assignment A1", done= False),
    Task(id= 2, title= "Watch lecture 2A", done= True),
    Task(id= 3, title= "Water the plants", done= False )
]

id_counter = 4

# Helper function
def find_task(id: int) -> Task:
    """Return the task with given id."""
    for t in tasks:
        if t.id == id:
            return t
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {id} not found")


# FastAPI instance
app = FastAPI()

# Initial endpoint
@app.get("/hello")
async def test():
    """Sanity check."""
    return {"message": "Hello World"}

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
async def get_all_tasks():
    """Return the full list of tasks."""
    return tasks

@app.get("/tasks/{id}", response_model= Task)
async def get_task(id: int):
    """Return a single task by its id if exists."""
    return find_task(id)

@app.post("/tasks", response_model= Task, status_code= status.HTTP_201_CREATED)
async def create_task(req: TaskRequest):
    """Creates a new task from a title"""
    global id_counter
    
    reqTitle = req.title
    if not reqTitle or not reqTitle.strip():
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "Title is required"
        )  

    new_task = Task(id= id_counter, title= reqTitle, done= False)
    tasks.append(new_task)
    id_counter += 1

    return new_task

@app.put("/tasks/{id}", response_model= Task)
async def update_task(id: int, req: TaskRequest):
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
