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


