from fastapi import HTTPException
from app.repositories import task_repository
from app.schemas.task import Task, TaskCreate, TaskUpdate

def to_task(row: dict) -> Task:
    return Task(id= row["id"], title= row["title"], done= bool(row["done"]))


def get_valid_task(task_id: int) -> Task:
    row = task_repository.fetch_task(task_id)
    if row is None:
        raise HTTPException(
            status_code= 404,
            detail="Task not found",
        )

    return to_task(row)


def get_tasks(done: bool | None = None, search: str | None = None) -> list[Task]:
    return [to_task(row) for row in task_repository.fetch_all_tasks(done, search)]


def create_task(request: TaskCreate) -> Task:
    if not request.title or not request.title.strip():
        raise HTTPException(
            status_code= 400,
            detail="Title is required",
        )

    return to_task(task_repository.create_task(request.title.strip()))


def update_task(task_id: int, req: TaskUpdate) -> Task:

    if req.title is None and req.done is None:
        raise HTTPException(
            status_code= 400,
            detail= "Request body must include title and/or done"
        )

    if req.title is not None and not req.title.strip():
        raise HTTPException(
            status_code= 400,
            detail="Title cannot be empty",
        )
    
    current = get_valid_task(task_id)
    new_title = req.title if req.title is not None else current.title
    new_done = req.done if req.done is not None else bool(current.done)
    
    row = task_repository.update_task(task_id, new_title, new_done)
    return to_task(row)


def delete_task(task_id: int) -> None:
    get_valid_task(task_id)
    task_repository.delete_task(task_id)
     