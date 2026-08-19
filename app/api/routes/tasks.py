from fastapi import APIRouter, status
from typing import Optional
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.services import task_service

router = APIRouter(prefix= "/tasks")

@router.get("", response_model= list[Task])
async def get_all_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    return task_service.get_tasks(done, search)


@router.get("/{task_id}", response_model= Task)
async def get_task(task_id: int):
    return task_service.get_valid_task(task_id)


@router.post("", response_model=Task, status_code= 201)
async def create_task(req: TaskCreate):
    return task_service.create_task(req)


@router.put("/{task_id}", response_model= Task)
async def update_task(task_id: int, req: TaskUpdate):
    return task_service.update_task(task_id, req)


@router.delete("/{task_id}", status_code= 204)
async def delete_task(task_id: int):
    task_service.delete_task(task_id)