from typing import TypedDict


class FileRecord(TypedDict):
    filename: str
    extension: str
    size_bytes: int
    modified_time: str
    status: str
    reason: str
