from httpx import Client


url = "https://api.github.com/repos/python/cpython"

with Client() as client:

    response = client.get(url)

    print("\n")
    print(response.status_code)
    print("\n")
    print(response.headers.get("x-ratelimit-remaining"))

    data = response.json()

    print(
        "\n",
        data["name"],
        "\n",
        data["full_name"]
    )