from fastapi import FastAPI

# FastAPI instance
app = FastAPI()

# Initial endpoint
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

# Root endpoint
@app.get("/")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

# Health check
@app.get("/health")
async def health():
    return { "status": "ok" }