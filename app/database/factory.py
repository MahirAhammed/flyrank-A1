import os
from dotenv import load_dotenv
from app.database.base import Database
from app.database.db_sqlite import SQLiteDatabase
from app.database.db_psql import PostgresDatabase

load_dotenv()

def create_database() -> Database:
    db_type = os.getenv("DB_BACKEND", "sqlite")

    if db_type.lower() == "sqlite":
        return SQLiteDatabase("tasks.db")

    if db_type.lower() == "postgres":
        database_url = os.environ["DATABASE_URL"]
        if not database_url:
            raise RuntimeError("Database URL missing")

        return PostgresDatabase(database_url)

    raise RuntimeError(f"Unsupported Database: {db_type}")

db = create_database()