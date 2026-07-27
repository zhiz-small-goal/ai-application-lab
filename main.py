from pathlib import Path
from datetime import datetime, UTC
import csv
import logging

from models import FileRecord, FileProcessingStatus


INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
MANIFEST_FILE = OUTPUT_DIR / "manifest.csv"

SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".csv",
    ".json"
}

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)


def timestamp_to_utc_datetime(
        timestamp: float,
) -> datetime:
    """Convert a POSIX timestamp to a UTC datetime"""

    return datetime.fromtimestamp(
        timestamp,
        tz=UTC
    )


def scan_files(input_dir: Path) -> list[FileRecord]:
    """Scan the input directory and collect file records"""

    records: list[FileRecord] = []

    for file_path in sorted(input_dir.iterdir()):
        record = process_file(file_path)
        records.append(record)

    return records


def process_file(
        file_path: Path,
) -> FileRecord:
    """Process one path and return its processing record."""

    try:
        if not file_path.is_file():
            logging.warning(
                "SKipping non-file path: %s",
                file_path.name,
            )

            return FileRecord(
                filename=file_path.name,
                extension="",
                size_bytes=0,
                modified_time=None,
                status=FileProcessingStatus.SKIPPED,
                reason="Not a file"
            )

        extension = file_path.suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            logging.warning(
                "Skipping unsupported file type: %s",
                file_path.name,
            )

            return FileRecord(
                filename=file_path.name,
                extension=extension,
                size_bytes=0,
                modified_time=None,
                status=FileProcessingStatus.SKIPPED,
                reason="Unsupported file type",
            )

        file_info = file_path.stat()

        return FileRecord(
            filename=file_path.name,
            extension=extension,
            size_bytes=file_info.st_size,
            modified_time=timestamp_to_utc_datetime(
                file_info.st_mtime
            ),
            status=FileProcessingStatus.SUCCESS,
            reason="",
        )

    except OSError as error:
        logging.error(
            "Failed to process file: %s: %s",
            file_path.name,
            error,
        )

        return FileRecord(
            filename=file_path.name,
            extension=file_path.suffix.lower(),
            size_bytes=0,
            modified_time=None,
            status=FileProcessingStatus.FAILED,
            reason=str(error),
        )


def summarize_records(
        records: list[FileRecord]
) -> dict[str, int]:

    success: int = 0
    failed: int = 0
    skipped: int = 0

    for record in records:
        if record.status is FileProcessingStatus.SUCCESS:
            success += 1
        elif record.status is FileProcessingStatus.FAILED:
            failed += 1
        elif record.status is FileProcessingStatus.SKIPPED:
            skipped += 1

    result = {
        "success": success,
        "failed": failed,
        "skipped": skipped,
    }

    logging.info(
        "Processed successfully: %s 个, failed: %s 个, skipped %s 个", 
        result["success"], 
        result["failed"], 
        result["skipped"]
    )

    return result


def save_manifest(
        records: list[FileRecord],
) -> None:
    """Write file records to a CSV manifest."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    fieldnames = [
        "filename",
        "extension",
        "size_bytes",
        "modified_time",
        "status",
        "reason",
    ]

    with MANIFEST_FILE.open(
        mode="w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(
            record.model_dump(mode="json")
            for record in records
        )


def main() -> None:
    """Run the file processing workflow."""
    if not INPUT_DIR.exists():
        logging.error(
            "Input directory does not exist: %s",
            INPUT_DIR.resolve(),
        )
        return

    records = scan_files(INPUT_DIR)
    save_manifest(records)
    summarize_records(records)

    logging.info(
        "Processing complete. Generated %s records",
        len(records),
    )
    logging.info(
        "Manifest file: %s",
        MANIFEST_FILE.resolve(),
    )


if __name__ == "__main__":
    main()
    