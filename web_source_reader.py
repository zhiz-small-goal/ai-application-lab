from bs4 import BeautifulSoup


def read_web_source(
        url: str,
        client,
) -> str:
    "Get source text form URL."

    response = client.get(url)

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    return soup.get_text(
        separator="\n",
        strip=True
    )


def select_candidate_text(
        raw_text: str,
) -> str:
    """Select candidate paragraphs for LLM evidence extraction."""

    candidate_keywords = [
        "AI",
        "大模型",
        "人工智能",
    ]

    selected_paragraphs = []

    paragraphs = raw_text.split("\n")

    for paragraph in paragraphs:
        if any(
            keyword in paragraph
            for keyword in candidate_keywords
        ):
            selected_paragraphs.append(paragraph)
            
    return "\n".join(selected_paragraphs)
