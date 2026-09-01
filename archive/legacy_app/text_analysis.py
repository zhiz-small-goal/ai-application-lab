from models import TextAnalysisResult
from pathlib import Path

from content_reader import read_text_content

from collections.abc import Callable


def summarize_text(
        text: str,
        summarizer: Callable[[str], str],
) -> TextAnalysisResult:
    """Summarize text and return a validated result."""
    
    summary_text = summarizer(text)
    return TextAnalysisResult(
        summary=summary_text
        )


def summarize_text_file(
        file_path: Path,
        summarizer: Callable[[str], str],
) -> TextAnalysisResult:
    """Read a text file and return its structured summary."""

    text = read_text_content(file_path=file_path)

    return summarize_text(
        text=text, 
        summarizer=summarizer
    )