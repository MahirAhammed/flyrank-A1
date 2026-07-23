# Task Manager API

FastAPI task manager backed by PostgreSQL, fully containerized with Docker Compose.

## Run it

```bash
docker compose up
```

That's it — this single command builds the API image, starts Postgres with a
named volume for persistent storage, waits for the database to be healthy,
then starts the API. The table is created (if missing) and seeded with 3
example tasks (only if empty) automatically on startup.

API available at: http://localhost:8000
Interactive docs: http://localhost:8000/docs

To stop: `docker compose down` (data persists).
To stop and wipe data: `docker compose down -v`.

## Configuration

Connection details live in `.env` (already populated with working defaults
for local development — change `POSTGRES_PASSWORD` before using this
anywhere real). `.env.example` is provided as a template; `.env` itself is
git-ignored.

## API

| Method | Path          | Description                              |
|--------|---------------|-------------------------------------------|
| GET    | /tasks        | List all tasks                            |
| GET    | /tasks/{id}   | Get one task (404 if missing)             |
| POST   | /tasks        | Create a task (400 if title missing/blank)|
| PUT    | /tasks/{id}   | Update title and/or done (400 if neither given, 400 if title blank, 404 if missing) |
| DELETE | /tasks/{id}   | Delete a task (404 if missing, 204 on success) |

All errors are returned as `{"error": "<message>"}`.

## Project layout

```
.
├── app/
│   ├── __init__.py
│   ├── main.py       # FastAPI app, routes, error handling
│   ├── db.py          # connection pool, table creation/seeding
│   └── models.py       # Pydantic schemas
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── .env                # actual config (git-ignored)
└── .env.example
```

## Local development without Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://taskuser:change_me_please@localhost:5432/taskmanager
uvicorn app.main:app --reload
```
