from models import FileProcessingStatus, FileRecord
from main import summarize_records

from datetime import UTC, datetime


def test_summarize_records():
    records = [
        FileRecord(
            filename="success.txt",
            extension=".txt",
            size_bytes=100,
            modified_time=datetime(2026, 7, 27, tzinfo=UTC),
            status=FileProcessingStatus.SUCCESS,
            reason="",
        ),
        FileRecord(
            filename="failed.txt",
            extension=".txt",
            size_bytes=0,
            modified_time=None,
            status=FileProcessingStatus.FAILED,
            reason="Failed to read file",
        ),
        FileRecord(
            filename="skipped.jpg",
            extension=".jpg",
            size_bytes=0,
            modified_time=None,
            status=FileProcessingStatus.SKIPPED,
            reason="Unsupported file type",
        ),
    ]

    result = summarize_records(records)


    assert result == {
        "success": 1,
        "failed": 1,
        "skipped": 1,
    }