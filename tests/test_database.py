from contextlib import closing
import sqlite3

import pytest

from database import (
    initialize_database,
    open_database,
)


def test_initialize_database_creates_required_tables(
        tmp_path,
):
    db_path = tmp_path / "test.db"

    initialize_database(db_path)

    assert db_path.is_file()

    with closing(open_database(db_path)) as connection:
        table_names = {
            row[0]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            )
        }

    assert "processing_tasks" in table_names
    assert "file_records" in table_names


def test_file_record_requires_existing_task(
        tmp_path,
):
    db_path = tmp_path / "test.db"

    initialize_database(db_path)

    with closing(open_database(db_path)) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO file_records(
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
                    "missing-task",
                    "hello.txt",
                    ".txt",
                    12,
                    None,
                    "success",
                    "",
                ),
            )