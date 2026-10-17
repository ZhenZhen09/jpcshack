import json

import pytest

from app import create_app
from solve import find_solution
from train_model import generate_assets


@pytest.fixture
def client(tmp_path):
    baseline_path, model_path = generate_assets(tmp_path)
    app = create_app(
        {
            "TESTING": True,
            "BASELINE_PATH": baseline_path,
            "MODEL_PATH": model_path,
            "SIGMA_TECH_FLAG": "flag{test_only}",
        }
    )
    return app.test_client()


def _baseline(client):
    path = client.application.config["BASELINE_PATH"]
    return json.loads(path.read_text(encoding="utf-8"))


def test_home_serves_the_sigma_tech_editor(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Sigma Tech" in response.data
    assert b"pixel-grid" in response.data


def test_model_and_starting_image_are_available_for_inspection(client):
    model = client.get("/model.json")
    image = client.get("/baseline.png")

    assert model.status_code == 200
    assert model.get_json()["target_class"] == "VISITOR"
    assert image.status_code == 200
    assert image.mimetype == "image/png"


def test_sigma_tech_favicon_is_available(client):
    response = client.get("/static/favicon.svg")

    assert response.status_code == 200
    assert response.mimetype == "image/svg+xml"


def test_author_solution_is_not_served(client):
    response = client.get("/SOLUTION.md")

    assert response.status_code == 404
    assert b"flag{pixel_confidence_is_not_identity}" not in response.data


def test_baseline_prediction_does_not_reveal_flag(client):
    response = client.post("/api/predict", json={"pixels": _baseline(client)})
    result = response.get_json()

    assert response.status_code == 200
    assert result["prediction"] == "EMPLOYEE"
    assert result["edits"] == 0
    assert result["solved"] is False
    assert "flag" not in result


def test_verified_target_candidate_returns_configured_flag(client, tmp_path):
    baseline_path, model_path = generate_assets(tmp_path)
    candidate, _ = find_solution(model_path, baseline_path, max_edits=5)

    response = client.post("/api/predict", json={"pixels": candidate})
    result = response.get_json()

    assert response.status_code == 200
    assert result["prediction"] == "VISITOR"
    assert result["solved"] is True
    assert result["flag"] == "flag{test_only}"


def test_over_budget_image_is_rejected_without_flag(client):
    pixels = _baseline(client)
    changed = 0
    for row in range(32):
        for column in range(32):
            if pixels[row][column] == 0:
                pixels[row][column] = 1
                changed += 1
                if changed == 6:
                    break
        if changed == 6:
            break

    response = client.post("/api/predict", json={"pixels": pixels})

    assert response.status_code == 400
    assert "flag" not in response.get_json()


@pytest.mark.parametrize(
    "payload",
    [
        {"pixels": [[0]]},
        {"pixels": [[0] * 32 for _ in range(31)]},
        {"pixels": [[False] * 32 for _ in range(32)]},
        {"pixels": [[2] * 32 for _ in range(32)]},
        {"pixels": [[0] * 32 for _ in range(32)], "flag": "flag{guess}"},
    ],
)
def test_invalid_payload_is_rejected_without_flag(client, payload):
    response = client.post("/api/predict", json=payload)

    assert response.status_code == 400
    assert "flag" not in response.get_json()


def test_invalid_json_is_rejected_without_flag(client):
    response = client.post("/api/predict", data="not-json", content_type="application/json")

    assert response.status_code == 400
    assert "flag" not in response.get_json()


def test_missing_model_shows_recoverable_error(tmp_path):
    baseline_path, _ = generate_assets(tmp_path)
    app = create_app(
        {
            "TESTING": True,
            "BASELINE_PATH": baseline_path,
            "MODEL_PATH": tmp_path / "missing.json",
        }
    )

    response = app.test_client().post("/api/predict", json={"pixels": json.loads(baseline_path.read_text())})

    assert response.status_code == 503
    assert "python train_model.py" in response.get_json()["error"]
