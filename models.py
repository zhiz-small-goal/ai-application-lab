from pydantic import BaseModel


class FileRecord(BaseModel):
    filename: str
    extension: str
    size_bytes: int
    modified_time: str
    status: str
    reason: str
