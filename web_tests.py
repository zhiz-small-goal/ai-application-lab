from pathlib import Path
import time

from trafilatura import extract

from httpx import Client


url = "https://api.github.com/repos/python/cpython/readme"

MAX_RETRIES = 3

raw_path = Path("data/raw/cpython_readme.html")

with Client(
    headers={
        "Accept": "application/vnd.github.html+json"
    }
) as client:
    for attempt in range(MAX_RETRIES + 1):
        response = client.get(url)

        status_code = response.status_code

        if status_code == 200:
            raw_html = response.text
            raw_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            raw_path.write_text(
                raw_html,
                encoding="utf-8",
            )

            print(f"Saved: {raw_path}")

            parser_input_html = (
                "<!DOCTYPE html>"
                "<html>"
                "<body>"
                f"{raw_html}"
                "</body>"
                "</html>"
            )

            parser_text = extract(parser_input_html)

            if parser_text is None:
                print("Parser failed")
                break

            print(parser_text[:1000])
            break

        elif status_code == 403:
            print("Forbidden")
            break

        retryable = (
            status_code == 429
            or status_code in {500, 502, 503, 504}
        )

        if not retryable:
            print("Unknown Status")
            break

        if attempt == MAX_RETRIES:
            print("Max retries reached")
            break

        time.sleep(2)
