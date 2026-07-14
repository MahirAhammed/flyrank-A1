from typing import List

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Task model
class Task(BaseModel):
    id: int
    title: str
    done: bool = False

# data
tasks: List[Task] = [
    Task(id= 1, title= "Complete assignment A1", done= False),
    Task(id= 2, title= "Watch lecture 2A", done= True),
    Task(id= 3, title= "Water the plants", done= False )
]

# FastAPI instance
app = FastAPI()

# Initial endpoint
@app.get("/hello")
async def test():
    return {"message": "Hello World"}

# Root endpoint
@app.get("/")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

# Health check
@app.get("/health")
async def health():
    return { "status": "ok" }


# Get all tasks
@app.get("/tasks", response_model=List[Task])
async def get_all_tasks():
    return tasks

# Get a specific task
@app.get("/tasks/{id}", response_model= Task)
async def get_task(id: int):
    
    for t in tasks:
        if t.id == id:
            return t
    
    return JSONResponse(
        status_code= status.HTTP_404_NOT_FOUND,
        content= {"error": f"Task {id} not found"}
    )