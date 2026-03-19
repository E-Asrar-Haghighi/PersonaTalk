import sqlite3
from contextlib import contextmanager

from .config import get_settings


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS personas (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    system_prompt TEXT NOT NULL,
    temperature REAL NOT NULL DEFAULT 0.7,
    voice_preference TEXT NOT NULL DEFAULT 'female',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    persona_id TEXT,
    persona_name TEXT,
    persona_snapshot TEXT NOT NULL,
    llm_provider TEXT NOT NULL DEFAULT 'openai',
    temperature REAL NOT NULL,
    voice_preference TEXT NOT NULL,
    mode TEXT NOT NULL DEFAULT 'text',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content_text TEXT NOT NULL,
    audio_path TEXT,
    transcript_source TEXT NOT NULL DEFAULT 'text',
    created_at TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    db_path = get_settings().database_path
    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def db_cursor():
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database() -> None:
    with db_cursor() as connection:
        connection.executescript(SCHEMA)
        _ensure_column(connection, "conversations", "llm_provider", "TEXT NOT NULL DEFAULT 'openai'")


def _ensure_column(connection: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
    existing = {row["name"] for row in rows}
    if column not in existing:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
