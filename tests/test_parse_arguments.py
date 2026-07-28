import sys
from pathlib import Path

from main import(
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    parse_arguments,
)


def test_parse_arguments_uses_default_dirctories():
    args = parse_arguments([])

    assert args.input_dir == DEFAULT_INPUT_DIR
    assert args.output_dir == DEFAULT_OUTPUT_DIR


def test_parse_arguments_accepts_custom_directories():
    args = parse_arguments(
        [
            "--input-dir",
            "source-files",
            "--output-dir",
            "generated-reports",
        ]
    )

    assert args.input_dir == Path("source-files")
    assert args.output_dir == Path("generated-reports")