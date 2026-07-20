from typing import Optional
from pydantic import BaseModel

# Task model
class Task(BaseModel):
    id: int | None = None
    title: str
    done: bool = False

class TaskCreate(BaseModel):
    """Payload for creating a task."""
    title: Optional[str] = None


class TaskUpdate(BaseModel):
    """Payload for updating a task."""
    title: Optional[str] = None
    done: Optional[bool] = None