from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import  BaseModel

from main import run_file_processing
from models import FileRecord


app = FastAPI(
    title="File Processing API",
)


class ProcessFileRequest(BaseModel):
    input_dir: Path
    output_dir: Path


class ProcessFileResponse(BaseModel):
    total: int
    records: list[FileRecord]


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
    }


@app.post(
    "/process",
    response_model=ProcessFileResponse,
)
def process_files(
    request: ProcessFileRequest,
) -> ProcessFileResponse:
    records = run_file_processing(
        input_dir=request.input_dir,
        output_dir=request.output_dir,
    )

    if records is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Input directory does not exist"
                "or is not directory"
            ),
        )

    return ProcessFileResponse(
        total=len(records),
        records=records,
    )