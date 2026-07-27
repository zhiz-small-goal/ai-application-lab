import logging
import sys

from main import main


def test_main_stops_when_input_directory_is_missing(
        tmp_path,
        monkeypatch,
        caplog,
):
    missing_input_dir = tmp_path / "missing-input"
    output_dir = tmp_path / "output"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--input-dir",
            str(missing_input_dir),
            "--output-dir",
            str(output_dir),
        ],
    )

    with caplog.at_level(logging.ERROR):
        main()

    assert (
        "Input directory does not exist or is not a directory"
        in caplog.text
    )
    assert not output_dir.exists()