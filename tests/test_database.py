from contextlib import closing
import sqlite3

import pytest

from datetime import datetime, UTC

from database import (
    initialize_database,
    open_database,
    save_processing_task
)
from models import FileProcessingStatus, FileRecord


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


def test_save_processing_task_saves_task_and_records(
        tmp_path,
):
    db_path = tmp_path / "test.db"

    records = [
        FileRecord(
            filename="hello.txt",
            extension=".txt",
            size_bytes=12,
            modified_time=datetime(
                2026,
                7,
                29,
                10,
                0,
                tzinfo=UTC,
            ),
            status=FileProcessingStatus.SUCCESS,
            reason="",
        ),
        FileRecord(
            filename="image.jpg",
            extension=".jpg",
            size_bytes=0,
            modified_time=None,
            status=FileProcessingStatus.SKIPPED,
            reason="Unsupported file type",
        ),
    ]

    task_id = save_processing_task(
        records=records,
        input_type="upload",
        db_path=db_path,
    )

    with closing(open_database(db_path)) as connection:
        task_row = connection.execute(
            """
            SELECT input_type
            FROM processing_tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

        record_rows = connection.execute(
            """
            SELECT
                filename,
                status,
                reason
            FROM file_records
            WHERE task_id = ?
            ORDER BY id
            """,
            (task_id,),
        ).fetchall()

    assert task_row == ("upload",)

    assert record_rows == [
        (
            "hello.txt",
            "success",
            "",
        ),
        (
            "image.jpg",
            "skipped",
            "Unsupported file type"
        ),
    ]