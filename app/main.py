from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.api.routes import tasks, root
from app.database.factory import db

app = FastAPI(title="Task API", version="1.0", description="A simple task management API")
app.include_router(tasks.router)
app.include_router(root.router)

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
