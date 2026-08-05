from datetime import UTC, datetime

from fastapi.testclient import TestClient

from api import app

from contextlib  import closing

import api

from database import get_processing_task, initialize_database, open_database, save_processing_task
from models import FileProcessingStatus, FileRecord


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


def test_process_files_returns_records_and_writes_manifest(
        tmp_path,
):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"

    input_dir.mkdir()

    (input_dir / "hello.txt").write_text(
        "hello python",
        encoding="utf-8",
    )

    response = client.post(
        "/process",
        json={
            "input_dir": str(input_dir),
            "output_dir": str(output_dir)
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["total"] == 1
    assert len(response_data["records"]) == 1
    assert response_data["records"][0]["filename"] == "hello.txt"
    assert response_data["records"][0]["status"] == "success"

    assert (output_dir / "manifest.csv").is_file()


def test_process_files_returns_400_for_missing_input(
        tmp_path,
):
    missing_input_dir = tmp_path / "missing-input"
    output_dir = tmp_path / "output"

    response = client.post(
        "/process",
        json={
            "input_dir": str(missing_input_dir),
            "output_dir": str(output_dir),
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "Input directory does not exist "
            "or is not a directory"
        ),
    }

    assert not output_dir.exists()


def test_process_uploaded_files_returns_records(
        tmp_path,
        monkeypatch,
):
    db_path = tmp_path / "test.db"

    monkeypatch.setattr(
        api,
        "DATABASE_PATH",
        db_path,
    )

    response = client.post(
        "/process-upload",
        files=[
            (
                "files",
                (
                    "hello.txt",
                    b"hello python",
                    "text/plain",
                ),
            ),
            (
                "files",
                (
                    "image.jpg",
                    b"fack image data",
                    "image/jpeg",
                ),
            ),
        ],
    )

    assert response.status_code == 200

    response_data = response.json()

    task_id = response_data["task_id"]

    assert task_id
    assert response_data["total"] == 2

    with closing(open_database(db_path)) as connection:
        task_row = connection.execute(
            """
            SELECT input_type
            FROM processing_tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

        record_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM file_records
            WHERE task_id = ?
            """,
            (task_id,)
        ).fetchone()[0]

    assert task_row == ("upload",)
    assert record_count == 2

    records_by_filename = {
        record["filename"]: record
        for record in response_data["records"]
    }

    assert (
        records_by_filename["hello.txt"]["status"]
        == "success"
    )
    assert (
        records_by_filename["image.jpg"]["status"]
        == "skipped"
    )
    assert (
        records_by_filename["image.jpg"]["reason"]
        == "Unsupported file type"
    )


def test_get_processing_task_returns_save_task(
        tmp_path,
        monkeypatch,
):
    db_path = tmp_path / "test.db"

    monkeypatch.setattr(
        api,
        "DATABASE_PATH",
        db_path,
    )

    records = [
        FileRecord(
            filename="hello.txt",
            extension=".txt",
            size_bytes=20,
            modified_time=datetime(
                2026,
                7,
                20,
                20,
                10,
                tzinfo=UTC,
            ),
            status=FileProcessingStatus.SUCCESS,
            reason="",
        ),
    ]

    task_id = save_processing_task(
        records=records,
        db_path=db_path,
        input_type="upload",
    )

    response = client.get(
        f"/tasks/{task_id}"
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["task_id"] == task_id
    assert response_data["input_type"] == "upload"
    assert len(response_data["records"]) == 1
    assert (
        response_data["records"][0]["filename"] 
        == "hello.txt"
    )


def test_get_processing_task_returns_404_for_missing_task(
        tmp_path,
        monkeypatch,
):
    db_path = tmp_path / "test.db"

    monkeypatch.setattr(
        api,
        "DATABASE_PATH",
        db_path,
    )

    initialize_database(
        db_path=db_path
    )

    response = client.get(
        "/tasks/missing-task"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Processing task not found"
    }

