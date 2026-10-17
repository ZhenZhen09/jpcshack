"""Shared image validation and inference for Sigma Tech."""

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
MODEL_PATH = DATA_DIR / "model.json"
BASELINE_PATH = DATA_DIR / "baseline.json"
IMAGE_SIZE = 32
PIXEL_COUNT = IMAGE_SIZE * IMAGE_SIZE


def validate_pixels(pixels):
    if not isinstance(pixels, list) or len(pixels) != IMAGE_SIZE:
        raise ValueError("pixels must contain exactly 32 rows")

    normalized = []
    for row in pixels:
        if not isinstance(row, list) or len(row) != IMAGE_SIZE:
            raise ValueError("each pixel row must contain exactly 32 values")
        if any(type(pixel) is not int or pixel not in (0, 1) for pixel in row):
            raise ValueError("pixel values must be the integers 0 or 1")
        normalized.append(row[:])
    return normalized


def load_model(path=MODEL_PATH):
    try:
        model = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"could not load model artifact: {error}") from error

    if not isinstance(model, dict):
        raise ValueError("model artifact has an invalid format")
    classes = model.get("classes")
    if (
        model.get("format_version") != 1
        or not isinstance(classes, list)
        or len(classes) != 2
        or not all(isinstance(label, str) for label in classes)
        or len(set(classes)) != 2
    ):
        raise ValueError("model artifact has an invalid format")
    try:
        coefficients = np.asarray(model.get("coefficients"), dtype=np.float64)
        intercepts = np.asarray(model.get("intercepts"), dtype=np.float64)
    except (TypeError, ValueError) as error:
        raise ValueError("model artifact has an invalid format") from error
    if (
        model.get("image_shape") != [IMAGE_SIZE, IMAGE_SIZE]
        or model.get("feature_order") != "row-major"
        or model.get("target_class") not in classes
        or coefficients.shape != (2, PIXEL_COUNT)
        or intercepts.shape != (2,)
        or not np.isfinite(coefficients).all()
        or not np.isfinite(intercepts).all()
    ):
        raise ValueError("model artifact has an invalid format")
    return model


def count_edits(pixels, baseline):
    candidate = validate_pixels(pixels)
    original = validate_pixels(baseline)
    return sum(
        candidate[row][column] != original[row][column]
        for row in range(IMAGE_SIZE)
        for column in range(IMAGE_SIZE)
    )


def predict_pixels(pixels, model=None):
    validated = validate_pixels(pixels)
    model = load_model() if model is None else model
    vector = np.asarray(validated, dtype=np.float64).reshape(PIXEL_COUNT)
    coefficients = np.asarray(model["coefficients"], dtype=np.float64)
    intercepts = np.asarray(model["intercepts"], dtype=np.float64)
    logits = coefficients @ vector + intercepts
    logits -= np.max(logits)
    probabilities = np.exp(logits)
    probabilities /= probabilities.sum()
    classes = model["classes"]
    winner = int(np.argmax(probabilities))
    return {
        "label": classes[winner],
        "confidence": float(probabilities[winner]),
        "scores": {label: float(probabilities[index]) for index, label in enumerate(classes)},
    }
