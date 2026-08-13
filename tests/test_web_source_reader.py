from web_source_reader import read_web_source


def test_read_web_source_returns_page_text():
    url = "https://test-url"

    html = """
    <html>
        <body>
            <h1>Zhiz</h1>
            <p>Zhiz is learning AI.</p>
        </body>
    </html>
    """
    expected_page_text = (
        "Zhiz\n"
        "Zhiz is learning AI."
    )

    class FakeResponse:
        text = html

    class FakeClient:
        def get(
                self,
                url: str,
        ):
            assert url == "https://test-url"
            return FakeResponse()

    page_text = read_web_source(
        url=url,
        client=FakeClient(),
    )

    assert page_text == expected_page_text





