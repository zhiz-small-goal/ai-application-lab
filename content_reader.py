from pathlib import Path


def read_text_content(
        file_path: Path,
) -> str:
    """Read UTF-8 text content from a file"""
    return file_path.read_text(
        encoding="utf-8",
    )