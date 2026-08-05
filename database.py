from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
import sqlite3
from uuid import uuid4

from models import FileRecord, ProcessingTask, FileProcessingStatus


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


def save_processing_task(
        records: list[FileRecord],
        input_type: str,
        db_path: Path = DEFAULT_DATABASE_PATH,
) -> str:
    """Save one processing task and its file records."""
    initialize_database(db_path)

    task_id = str(uuid4())
    created_at = datetime.now(UTC).isoformat()

    with closing(open_database(db_path)) as connection:
        with connection:
            connection.execute(
                """
                INSERT INTO processing_tasks (
                    id,
                    created_at,
                    input_type
                )
                VALUES (?, ?, ?)
                """,
                (
                    task_id,
                    created_at,
                    input_type,
                ),
            )

            for record in records:
                modified_time = (
                    record.modified_time.isoformat()
                    if record.modified_time is not None
                    else None
                )

                connection.execute(
                    """
                    INSERT INTO file_records (
                        task_id,
                        filename,
                        extension,
                        size_bytes,
                        modified_time,
                        status,
                        reason
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task_id,
                        record.filename,
                        record.extension,
                        record.size_bytes,
                        modified_time,
                        record.status.value,
                        record.reason,
                    ),
                )

    return task_id


def get_processing_task(
        task_id: str,
        db_path: Path = DEFAULT_DATABASE_PATH,
)-> ProcessingTask | None:
    """Get one processing task by its ID"""

    with closing(open_database(db_path)) as connection:
        task_row = connection.execute(
            """
            SELECT
                id,
                created_at,
                input_type
            FROM processing_tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

    if task_row is None:
        return None

    stored_task_id, created_at_text, input_type = task_row

    records = []
        
    with closing(open_database(db_path)) as connection:
        task_row = connection.execute(
                    """
                    SELECT
                        id,
                        created_at,
                        input_type
                    FROM processing_tasks
                    WHERE id = ?
                    """,
                    (task_id,),
                ).fetchone()
        for record in task_row["records"]:
            filename = record["filename"]
            extension = record["extension"]
            size_bytes = record["size_bytes"]
            modified_time = record["modified_time"]
            status = record["status"]
            reason = record["reason"]

            record_list = (
                str(filename),
                str(extension),
                int(size_bytes),
                datetime.fromisoformat(modified_time) if modified_time is not None else None,
                FileProcessingStatus(status),
                str(reason)
            )

            records.append(record_list)


    return ProcessingTask(
        task_id=stored_task_id,
        created_at=datetime.fromisoformat(
            created_at_text
        ),
        input_type=input_type,
        records=records,
    )

