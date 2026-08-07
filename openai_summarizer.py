def summarize_with_openai(
        text: str,
        client,
        model: str,
) -> str:
    """Summarize text with OpenAI client."""

    response = client.responses.create(
        input_text=text,
        model=model,
    )

    return response.output_text