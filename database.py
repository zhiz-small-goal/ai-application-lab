from contextlib import closing
from pathlib import Path
import sqlite3


DEFAULT_DATABASE_PATH = Path("data") / "app.db"


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS processing_tasks (
id TEXT PRIMARY KEY,
created_at TEXT NOT NULL,
input_type TEXT NOT NULL
    CHECK (input_type IN ('directory', 'upload'))
    );

CREATE TABLE IF NOT EXISTS file_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    extension TEXT NOT NULL,
    size_bytes INTEGER NOT NULL
        CHECK (size_bytes >= 0),
    modified_time TEXT,
    status TEXT NOT NULL
        CHECK (status IN ('success', 'failed', 'skipped')),
    reason TEXT NOT NULL,
    
    FOREIGN KEY (task_id)
        REFERENCES processing_tasks(id)
        ON DELETE CASCADE
        );    
"""


def open_database(
        db_path: Path = DEFAULT_DATABASE_PATH,
) -> sqlite3.Connection:
    """Open a configured SQLite database connection."""
    connection = sqlite3.connect(db_path)

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def initialize_database(
        db_path: Path = DEFAULT_DATABASE_PATH,
) -> None:
    """Create the database and reqired tables."""
    db_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with closing(open_database(db_path)) as connection:
        connection.executescript(SCHEMA_SQL)
        connection.commit()