from models import TextAnalysisResult


def test_text_analysis_result_accepts_summary():
    result = TextAnalysisResult(
        summary="This is a summary."
    )

    assert result.summary == "This is a summary."
