from models import TextAnalysisResult

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
