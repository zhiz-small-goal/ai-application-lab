from content_reader import read_text_content


def test_read_text_content_returns_file_text(
        tmp_path,
):
    file_path = tmp_path / "hello.txt"

    file_path.write_text(
        "hello AI application",
        encoding="utf-8",
    )

    result = read_text_content(file_path)

    assert result == "hello AI application"