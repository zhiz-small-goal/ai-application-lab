import time

from httpx import Client


url = "https://api.github.com/repos/python/cpython"

with Client() as client:
    
    MAX_RETRIES = 3
    retry_count = 0

    while True:
        if retry_count == MAX_RETRIES:
            break
        response = client.get(url)

        status_code = response.status_code

        if status_code == 200:
            print(response.json())
            break

        elif status_code == 429:
            print("Rate Limited")
            retry_count += 1
            time.sleep(10)
            continue

        elif status_code == 403:
            print("Forbidden")
            break

        elif status_code in {500, 502, 503, 504}:
            print("Server Error")
            time.sleep(2)
            retry_count += 1
            continue

        else:
            print("Unknown Status")
            break

