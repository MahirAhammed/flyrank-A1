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
| GET    | `/tasks/{id}`| Get a single task by id                   | 200     | 404            |
| POST   | `/tasks`     | Create a new task                         | 201     | 400            |
| PUT    | `/tasks/{id}`| Replace a task's title and/or done status | 200     | 400, 404       |
| DELETE | `/tasks/{id}`| Delete a task by id                       | 204     | 404            |

## Example request

```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk"}'
```

## Swagger-UI
![Swagger UI](./image.png)