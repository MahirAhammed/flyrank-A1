# Task API

A simple RESTful API for managing a to-do list, built with FastAPI.

## Install & Run

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

## Endpoints

| Method | Path         | Description                              | Success | Errors        |
|--------|--------------|-------------------------------------------|---------|----------------|
| GET    | `/`          | Get API info                            | 200     | –              |
| GET    | `/health`     | Health check                            | 200     | –              |
| GET    | `/tasks`     | List all tasks                            | 200     | –              |
| GET    | `/tasks?done=true`    | Filter tasks by done status                | 200     | –              |
| GET    | `/tasks?search=milk`  | Search tasks by a term in title  | 200     | –              |
| GET    | `/tasks/{id}`| Get a single task by id                   | 200     | 404            |
| POST   | `/tasks`     | Create a new task                         | 201     | 400            |
| PUT    | `/tasks/{id}`| Replace a task's title and/or done status | 200     | 400, 404       |
| DELETE | `/tasks/{id}`| Delete a task by id                       | 204     | 404            |
| DELETE | `/tasks/{id}`| Delete a task by id                       | 204     | 404            |
| GET    | `/stats`              | Return counts of total, done, open           | 200     | –              |
| POST   | `/reset`              | Restore the 3 seed tasks                   | 200     | –              |


## Example request

```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk"}'
```

## Mortality experiment
Restarting the server means running the server from the start, which is why all previous tasks stored are not persisted. The current implementation uses Python's `list` which is a variable in memory that exists only when the program is running.

## Swagger-UI
![Swagger UI](./image.png)