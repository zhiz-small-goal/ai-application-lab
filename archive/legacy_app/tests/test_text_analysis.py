from models import TextAnalysisResult
from text_analysis import summarize_text, summarize_text_file


def test_text_analysis_result_accepts_summary():
    result = TextAnalysisResult(
        summary="This is a summary."
    )

    assert result.summary == "This is a summary."


def test_summarize_text_returns_structured_result():
    source_text = "Zhiz is learning AI application development"
    expected_summary = "zhiz learning AI"

    def fake_summarizer(text: str) -> str:
        assert text == source_text
        return expected_summary

    result = summarize_text(
        text=source_text,
        summarizer=fake_summarizer,
    )

    assert isinstance(result, TextAnalysisResult)
    assert result.summary == expected_summary


def test_summarize_text_file_returns_expected_summary(
        tmp_path,
):
    file_path = tmp_path / "hello.txt"

    source_text = "Zhiz is a baby"
    expected_summary = "Zhiz is very good"

    file_path.write_text(
        data=source_text,
        encoding="utf-8",
    )

    def fake_summarizer(text: str) -> str:
        assert text == source_text
        return expected_summary

    result = summarize_text_file(
        file_path=file_path,
        summarizer=fake_summarizer,
    )

    assert result.summary == expected_summary