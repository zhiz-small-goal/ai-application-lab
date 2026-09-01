import logging
import sys
import csv

from main import main, run_file_processing


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


def test_run_processing_writes_manifest(
        tmp_path,
        caplog,
):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"

    input_dir.mkdir()

    (input_dir / "hello.txt").write_text(
        "hello python",
        encoding="utf-8",
    )
    (input_dir / "image.jpg").write_text(
        "Fake image data",
        encoding="utf-8",
    )
    (input_dir / "subfolder").mkdir()

    with caplog.at_level(logging.INFO):
        records = run_file_processing(
            input_dir=input_dir,
            output_dir=output_dir
        )

    assert records is not None
    assert len(records) == 3

    manifest_file = output_dir / "manifest.csv"

    assert manifest_file.is_file()

    with manifest_file.open(
        mode="r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        rows = list(csv.DictReader(csv_file))

    rows_by_filename = {
        row["filename"]: row
        for row in rows
    }

    assert len(rows) == 3

    assert rows_by_filename["hello.txt"]["status"] == "success"
    assert rows_by_filename["hello.txt"]["reason"] == ""
    assert rows_by_filename["hello.txt"]["modified_time"] != ""

    assert rows_by_filename["image.jpg"]["status"] == "skipped"
    assert (
        rows_by_filename["image.jpg"]["reason"]
        == "Unsupported file type"
    )

    assert rows_by_filename["subfolder"]["status"] == "skipped"
    assert rows_by_filename["subfolder"]["reason"] == "Not a file"

    assert ("Processing complete. Generated 3 records"
            in caplog.text
    )