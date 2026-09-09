import time

from httpx import Client


url = "https://api.github.com/repos/python/cpython"

MAX_RETRIES = 3

with Client() as client:
    for attempt in range(MAX_RETRIES + 1):
        response = client.get(url)

        status_code = response.status_code

        if status_code == 200:
            print(response.json())
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