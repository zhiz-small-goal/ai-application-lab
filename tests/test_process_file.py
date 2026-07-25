from pathlib import Path

from models import FileProcessingStatus

from main import process_file



def test_process_supported_file(tmp_path: Path):
    test_file = tmp_path / "hello.txt"

    test_file.write_text(
        "hello python",
        encoding="utf-8",
    )

    result = process_file(test_file)

    assert result.status is FileProcessingStatus.SUCCESS
    assert result.filename == "hello.txt"
    assert result.extension == ".txt"


def test_process_unsupported_file(tmp_path: Path):
    test_file = tmp_path / "image.jpg"

    test_file.write_text(
        "fake image",
        encoding="utf-8",
    )

    result = process_file(test_file)

    assert result.status is FileProcessingStatus.SKIPPED
    assert result.reason == "不支持的文件类型"


def test_process_directory(tmp_path: Path):
    test_dir = tmp_path / "folder"

    test_dir.mkdir()

    result = process_file(test_dir)

    assert result.status is FileProcessingStatus.SKIPPED
    assert result.reason == "不是文件"


def test_process_missing_file(tmp_path: Path):
    missing_file = tmp_path / "missing.txt"

    result = process_file(missing_file)

    assert result.status is FileProcessingStatus.SKIPPED
    assert result.reason == "不是文件"