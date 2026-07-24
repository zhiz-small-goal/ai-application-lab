from pathlib import Path
from datetime import datetime
import csv
import logging

from models import FileRecord


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


def format_modified_time(timestamp: float) -> str:
    """把文件时间戳转换为可读时间"""
    modified_time = datetime.fromtimestamp(timestamp)
    return modified_time.strftime("%Y-%m-%d %H:%M:%S")


def scan_files(input_dir: Path) -> list[FileRecord]:
    """扫描输入目录并收集文件信息"""

    records: list[FileRecord] = []

    for file_path in sorted(input_dir.iterdir()):
        record = process_file(file_path)
        records.append(record)

    return records


def process_file(
        file_path: Path,
) -> FileRecord:
    """处理单个文件, 返回文件记录"""

    if not file_path.is_file():
        logging.warning(
            "跳过非文件路径: %s",
            file_path.name,
        )
        return FileRecord(
            filename=file_path.name,
            extension="",
            size_bytes=0,
            modified_time="",
            status="skipped",
            reason="不是文件"
        )

    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        logging.warning(
            "跳过不支持的文件类型: %s",
            file_path.name,
        )
        return FileRecord(
            filename=file_path.name,
            extension=extension,
            size_bytes=0,
            modified_time="",
            status="skipped",
            reason="不支持的文件类型",
        )

    try:
        file_info = file_path.stat()

        return FileRecord(
            filename=file_path.name,
            extension=extension,
            size_bytes=file_info.st_size,
            modified_time=format_modified_time(
                file_info.st_mtime
            ),
            status="success",
            reason="",
        )
    

    except Exception as error:
        logging.error(
            "处理失败: %s: %s",
            file_path.name,
            error,
        )

        return FileRecord(
            filename=file_path.name,
            extension=extension,
            size_bytes=0,
            modified_time="",
            status="failed",
            reason=str(error),
        )


def summarize_records(
        records: list[FileRecord]
) -> dict[str, int]:

    success: int = 0
    failed: int = 0
    skip: int = 0

    for summarize in records:
        if summarize.status == "success":
            success += 1
        elif summarize.status == "failed":
            failed += 1
        elif summarize.status == "skipped":
            skip += 1

    result = {
        "success": success,
        "failed": failed,
        "skipped": skip
    }

    logging.info(
        "成功处理 %s 个, 处理失败 %s 个, 跳过 %s 个", 
        result["success"], 
        result["failed"], 
        result["skipped"]
    )

    return result


def save_manifest(
        records: list[FileRecord],
) -> None:
    """把文件信息写入 CSV"""
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
            record.model_dump()
            for record in records
        )


def main() -> None:
    """程序入口"""
    if not INPUT_DIR.exists():
        logging.error(
            "输入目录不存在：%s",
            INPUT_DIR.resolve(),
        )
        return

    records = scan_files(INPUT_DIR)
    save_manifest(records)
    summarize_records(records)

    logging.info(
        "处理完成，共生成 %s 条记录",
        len(records),
    )
    logging.info(
        "结果文件： %s",
        MANIFEST_FILE.resolve(),
    )


if __name__ == "__main__":
    main()
    