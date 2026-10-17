import json

import pytest

from classifier import count_edits, load_model, predict_pixels, validate_pixels
from solve import find_solution
from train_model import generate_assets


def test_generated_assets_are_deterministic(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"

    generate_assets(first)
    generate_assets(second)

    assert (first / "baseline.json").read_bytes() == (second / "baseline.json").read_bytes()
    assert (first / "model.json").read_bytes() == (second / "model.json").read_bytes()


def test_pixel_validation_accepts_only_a_32_by_32_binary_integer_matrix():
    pixels = [[0 for _ in range(32)] for _ in range(32)]

    assert validate_pixels(pixels) == pixels

    with pytest.raises(ValueError):
        validate_pixels([[0] * 31 for _ in range(32)])
    with pytest.raises(ValueError):
        validate_pixels([[False] * 32 for _ in range(32)])
    with pytest.raises(ValueError):
        validate_pixels([[0.0] * 32 for _ in range(32)])
    with pytest.raises(ValueError):
        validate_pixels([[2] * 32 for _ in range(32)])


def test_edit_count_compares_pixel_values_to_the_baseline():
    baseline = [[0 for _ in range(32)] for _ in range(32)]
    candidate = [row[:] for row in baseline]
    candidate[2][3] = 1
    candidate[5][8] = 1

    assert count_edits(candidate, baseline) == 2


def test_generated_model_predicts_baseline_as_employee(tmp_path):
    generate_assets(tmp_path)
    model = load_model(tmp_path / "model.json")
    baseline = json.loads((tmp_path / "baseline.json").read_text(encoding="utf-8"))

    result = predict_pixels(baseline, model)

    assert result["label"] == "EMPLOYEE"
    assert set(result["scores"]) == {"EMPLOYEE", "VISITOR"}
    assert 0.0 <= result["confidence"] <= 1.0


def test_malformed_model_artifact_raises_value_error(tmp_path):
    artifact = tmp_path / "model.json"
    artifact.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid format"):
        load_model(artifact)


def test_model_artifact_rejects_invalid_class_labels_and_versions(tmp_path):
    artifact = tmp_path / "model.json"
    artifact.write_text(
        json.dumps({
            "format_version": 1,
            "image_shape": [32, 32],
            "feature_order": "row-major",
            "classes": [[], []],
            "target_class": "VISITOR",
            "coefficients": [[0] * 1024, [0] * 1024],
            "intercepts": [0, 0],
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid format"):
        load_model(artifact)

    artifact.write_text(
        json.dumps({
            "format_version": 999,
            "image_shape": [32, 32],
            "feature_order": "row-major",
            "classes": ["EMPLOYEE", "VISITOR"],
            "target_class": "VISITOR",
            "coefficients": [[0] * 1024, [0] * 1024],
            "intercepts": [0, 0],
        }),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="invalid format"):
        load_model(artifact)


def test_author_solver_finds_a_target_sample_with_at_most_five_edits(tmp_path):
    generate_assets(tmp_path)
    candidate, coordinates = find_solution(
        tmp_path / "model.json", tmp_path / "baseline.json", max_edits=5
    )
    model = load_model(tmp_path / "model.json")

    assert 1 <= len(coordinates) <= 5
    assert len(set(coordinates)) == len(coordinates)
    assert count_edits(candidate, json.loads((tmp_path / "baseline.json").read_text())) == len(coordinates)
    assert predict_pixels(candidate, model)["label"] == "VISITOR"
