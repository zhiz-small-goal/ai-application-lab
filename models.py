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
                    "成功记录必须包含修改时间"
                )
            if reason:
                raise ValueError(
                    "成功记录的 reason 必须为空"
                )

        elif not reason:
            raise ValueError(
                "失败或跳过记录必须提供 reason"
            )

        return  self