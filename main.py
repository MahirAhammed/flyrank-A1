from fastapi import FastAPI

# FastAPI instance
app = FastAPI()

# Initial endpoint
@app.get("/")
async def root():
    return {"message": "Hello World"}