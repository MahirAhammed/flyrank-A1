from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.routes import tasks, root
from app.database.factory import db
from task_analyzer.src.routes import task_analyzer

import logging
from pathlib import Path

logging.basicConfig(
    level= logging.INFO, 
    format="%(message)s", 
    handlers= [
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent.parent / "task_analyzer" / "logs" / "calls.jsonl")
    ])

app = FastAPI(title="Task API", version="1.0", description="A simple task management API")
app.include_router(tasks.router)
app.include_router(root.router)

# Endpoint for use of LLM
app.include_router(task_analyzer.router)

db.init_db()
db.ping()

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(req, exc: HTTPException) -> JSONResponse:
    """Return errors in the consistent format: {"error": "<message>"}."""

    return JSONResponse(
        status_code= exc.status_code, 
        content= {"error": exc.detail}
    )

# Exception Handler invalid request for /task-analyzer
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(req, exc: RequestValidationError):
    """Return status 400 for Pydantic's default 422 invalid model request"""
    first = exc.errors()[0] if exc.errors() else {}
    field = first.get("loc", ("unknown",))[-1]
    return JSONResponse(
        status_code= 400,
        content= {
            "error": "validation_failed", 
            "field": field, 
            "message": first.get("msg", "Invalid input")},
    )
