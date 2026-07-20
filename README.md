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

## AI vs me

### My prompt

Build a REST API for a simple task manager using Python and FastAPI, with data stored in memory (a Python list, no database). Include automatic interactive API docs via Swagger UI (FastAPI gives this for free at `/docs`).
Define a Task object with attributes: `id` (integer), `title` (string), `done` (boolean, defaults to false).
Seed the in-memory store with 3 example tasks on startup.
The API should consist of the following endpoints:

1. GET /tasks -> return all tasks. 
2. GET /tasks/{id} -> return a single task by id. Return 404 with a JSON error body in the format { "error": "Task 99 not found" } if the id doesn't exist.
3.  POST /tasks -> create a task from a JSON body containing `title`. Assign the next available id automatically, set `done` to false, add it to the list, and return the created task with status 201. If `title` is missing or blank/whitespace-only, return 400 with a JSON error body explaining whether title is missing or empty.
4. PUT /tasks -> update a task's `title` and/or `done` from a JSON body. Both fields are optional but at least one must be provided. Return the updated task. Return 404 if the id doesn't exist. Return 400 if the body is empty/has neither field, or if `title` is provided but blank.
5. DELETE /tasks -> remove a task by id. Return 404 if the id doesn't exist. Return 204 (no body) on success.

Give each endpoint a one-line description so it shows up nicely in Swagger UI. Keep the code in a single `main.py` file, runnable with `uvicorn main:app --reload`. Follow best coding practice and avoid unnecessary code repetition.

##### What the AI did better

- Centralized error formatting: a single @app.exception_handler(HTTPException) converts every HTTPException into {"error": "<message>"}, instead of repeating in each route.
- Split TaskCreate/TaskUpdate models instead of one shared DTO, makes the accepted fields for POST vs. PUT self-documenting in Swagger.
- ID generation defined in a _next_task_id() helper rather than direct global variable manipulation.

The AI implementation follows a clear structure to understand it well enough to explain: seed -> route -> Pydantic validates shape -> manual checks -> helper does lookup/id-assignment -> exception handler normalizes any error before it reaches the client.

##### What it got wrong or quietly ignored

It didn't fully follow its own naming-repetition instruction. My prompt named two specific things to factor out: "looking up a task by id" and "validating a title." It did factor out task lookup (`_get_task_or_404`), but title validation, the "missing" check and the "blank" check, is written out inline, separately, in both `create_task` and `update_task`, instead of behind one shared helper.

##### What my prompt forgot to specify, and what the AI decided for me

- My prompt never mentioned the need of defining Task object as a Pydantic model, as well as the creation of seperate DTOs for each request.
- The 3 seed tasks were never specified, the AI invented generic ones ("Buy groceries"). In addition, the seeding process by the AI follows best practice, and also makes it easy to reset tasks, which was never mentioned