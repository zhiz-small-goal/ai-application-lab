from trafilatura import extract
from bs4 import BeautifulSoup


def extract_text_from_html(
        html: str,
) -> str | None:
    """Extract main text from a full HTML document or HTML fragment."""

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    if soup.html is None:
        parser_text = extract(
            "<!DOCTYPE html>"
            "<html>"
            "<body>"
            f"{html}"
            "</body>"
            "</html>"
        )

    else:
        parser_text = extract(html)

    if parser_text is None:
        return parser_text

    return None

        