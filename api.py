from pathlib import Path
from shutil import copyfileobj
from tempfile import TemporaryDirectory
from typing import Annotated

from fastapi import (
    FastAPI, 
    File,
    HTTPException,
    UploadFile,
)
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
                "Input directory does not exist "
                "or is not a directory"
            ),
        )

    return ProcessFileResponse(
        total=len(records),
        records=records,
    )



@app.post(
    "/process-upload",
    response_model=ProcessFileResponse,
)
def process_uploaded_file(
    files: Annotated[
        list[UploadFile],
        File(description="Files to precess"),
    ],
) -> ProcessFileResponse:
    with TemporaryDirectory() as temporary_directory:
        task_directory = Path(temporary_directory)
        input_dir = task_directory / "input"
        output_dir = task_directory / "output"

        input_dir.mkdir()

        saved_filenames: set[str] = set()

        for uploaded_file in files:
            filename= Path(
                uploaded_file.filename or ""
            ).name

            if not filename:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file must have a filename",
                )

            if filename in saved_filenames:
                raise HTTPException(
                    status_code=400,
                    detail=f"Duplicate filiename: {filename}",
                )

            saved_filenames.add(filename)

            destination_file = input_dir / filename

            with destination_file.open("wb") as output_file:
                copyfileobj(
                    uploaded_file.file,
                    output_file,
                )

        records = run_file_processing(
            input_dir=input_dir,
            output_dir=output_dir,
        )

        if records is None:
            raise HTTPException(
                status_code=500,
                detail="File processing did not start",
            )

        return ProcessFileResponse(
            total=len(records),
            records=records,
        )