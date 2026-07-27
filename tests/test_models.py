from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from models import FileProcessingStatus, FileRecord


VALID_MODIFIED_TIME = datetime(
    2026,
    7,
    25,
    12,
    0,
    tzinfo=UTC,
)


def make_record(**overrides: Any) -> FileRecord:
    """Create a valid file record with optional field overrides."""

    data = {
        "filename": "hello.txt",
        "extension": ".txt",
        "size_bytes": 100,
        "modified_time": VALID_MODIFIED_TIME,
        "status": FileProcessingStatus.SUCCESS,
        "reason": "",
    }

    data.update(overrides)

    return FileRecord(**data)


def test_create_valid_success_record():
    record = make_record()

    assert record.status is FileProcessingStatus.SUCCESS
    assert record.modified_time == VALID_MODIFIED_TIME
    assert record.reason == ""


@pytest.mark.parametrize(
    "status",
    [
        FileProcessingStatus.FAILED,
        FileProcessingStatus.SKIPPED,
    ],
)
def test_create_valid_non_success_record(
    status: FileProcessingStatus,
):
    record = make_record(
        modified_time=None,
        status=status,
        reason="Processing was not successful",
    )

    assert record.status is status
    assert record.modified_time is None
    assert record.reason == "Processing was not successful"


def test_reject_negative_size():
    with pytest.raises(ValidationError):
        make_record(size_bytes=-1)


def test_reject_success_without_modified_time():
    with pytest.raises(
        ValidationError,
        match="Successful records must include a modified time",
    ):
        make_record(modified_time=None)


def test_reject_success_with_reason():
    with pytest.raises(
        ValidationError,
        match="Successful records must have an empty reason",
    ):
        make_record(reason="Unexpected error")


@pytest.mark.parametrize(
    "status",
    [
        FileProcessingStatus.FAILED,
        FileProcessingStatus.SKIPPED,
    ],
)
def test_reject_non_success_without_reason(
    status:FileProcessingStatus,
):
    with pytest.raises(
        ValidationError,
        match="Failed or skipped records must provide a reason",
    ):
        make_record(
            modified_time=None,
            status=status,
            reason="",
        )