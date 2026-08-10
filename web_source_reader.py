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

    paragraphs = raw_text.split("\n")

    selected_indexes = set()

    for index, paragraph in enumerate(paragraphs):
        if any(
            keyword in paragraph
            for keyword in candidate_keywords
        ):
            if index > 0:
                selected_indexes.add(index - 1)

            selected_indexes.add(index)

            if index < (len(paragraphs) - 1):
                selected_indexes.add(index + 1)

    selected_paragraphs = [
        paragraph
        for index, paragraph in enumerate(paragraphs)
        if index in selected_indexes
    ]

    return "\n".join(selected_paragraphs)
