import os



def summarize_with_openai(
        text: str,
        client,
        model: str,
) -> str:
    """Summarize text with OpenAI-compatible client."""

    response = client.responses.create(
        input=text,
        instructions="Summarize the input text in one concise sentence.",
        model=model,
    )

    return response.output_text