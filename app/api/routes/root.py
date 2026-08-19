from fastapi import APIRouter, HTTPException
from app.database.factory import db
from app.repositories import task_repository

router = APIRouter()

@router.get("/")
async def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/stats"],
    }


@router.get("/health")
async def health():
    try:
        db.ping()
        return {"status": "ok", "db": "ok"}
    except Exception:
        raise HTTPException(
            status_code= 503,
            detail="Database unreachable",
        )

@router.get("/stats")
async def stats():
    return task_repository.stats()