from datetime import datetime
from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, Field, model_validator


SizeBytes = Annotated[int, Field(ge=0)]


class FileProcessingStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class FileRecord(BaseModel):
    filename: str
    extension: str
    size_bytes: SizeBytes
    modified_time: datetime | None
    status: FileProcessingStatus
    reason: str


    @model_validator(mode="after")
    def validate_status_consistency(self) -> Self:
        """Validate consistency between status and related fields."""

        reason = self.reason.strip()

        if self.status is FileProcessingStatus.SUCCESS:
            if self.modified_time is None:
                raise ValueError(
                    "Successful records must include a modified time"
                )
            if reason:
                raise ValueError(
                    "Successful records must have an empty reason"
                )

        elif not reason:
            raise ValueError(
                "Failed or skipped records must provide a reason"
            )

        return  self


class ProcessingTask(BaseModel):
    task_id: str
    created_at: datetime
    input_type: str
    records: list[FileRecord]