from openai import OpenAI

from openai_summarizer import summarize_with_openai


def test_summarize_with_openai_returns_result(
    tmp_path,
) -> str:
    source_text = "Zhiz is learning AI application development."
    expected_summary = "zhiz is learning AI."
    model = "test-model"

    file_path = tmp_path / "hello.txt"

    file_path.wirte_text(
        data=source_text,
        encoding="utf-8",
    )

    text_content = summarize_with_openai(
        file_path=file_path,
        summarizer=OpenAI(model)
    )

    assert text_content == expected_summary



