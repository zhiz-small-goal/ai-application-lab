from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


def test_process_files_returns_records_and_writes_manifest(
        tmp_path,
):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"

    input_dir.mkdir()

    (input_dir / "hello.txt").write_text(
        "hello python",
        encoding="utf-8",
    )

    response = client.post(
        "/process",
        json={
            "input_dir": str(input_dir),
            "output_dir": str(output_dir)
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["total"] == 1
    assert len(response_data["records"]) == 1
    assert response_data["records"][0]["filename"] == "hello.txt"
    assert response_data["records"][0]["status"] == "success"

    assert (output_dir / "manifest.csv").is_file()


def test_process_files_returns_400_for_missing_input(
        tmp_path,
):
    missing_input_dir = tmp_path / "missing-input"
    output_dir = tmp_path / "output"

    response = client.post(
        "/process",
        json={
            "input_dir": str(missing_input_dir),
            "output_dir": str(output_dir),
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "Input directory does not exist "
            "or is not a directory"
        ),
    }

    assert not output_dir.exists()
    