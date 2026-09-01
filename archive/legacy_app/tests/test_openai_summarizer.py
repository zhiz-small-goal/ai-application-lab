from openai_summarizer import summarize_with_openai


def test_summarize_with_openai_returns_expected_summary():
    source_text = "zhiz is learning AI application"
    expected_summary = "zhiz is learning AI"
    model = "test-model"
    expected_instructions = "Summarize the input text in one concise sentence."

    class FakeResponse:
        output_text = expected_summary

    class FakeResponses:
        def create(
                self,
                *,
                model: str,
                input: str,
                instructions: str

        ):
            assert model == "test-model"
            assert input == source_text
            assert instructions == expected_instructions

            return FakeResponse()

    class FakeClient:
        responses = FakeResponses()

    result = summarize_with_openai(
        text=source_text,
        client=FakeClient(),
        model=model,
    )

    assert result == expected_summary



