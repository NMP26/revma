import os
import sqlite3
from pathlib import Path

from fastapi import FastAPI

app = FastAPI(title="REVMA V2 API", version="0.1.0")


def initialize_database() -> None:
    database_path = Path(os.environ.get("DATABASE_PATH", "/data/revma.sqlite3"))
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "REVMA V2 API"}
