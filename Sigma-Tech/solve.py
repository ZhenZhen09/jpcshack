"""Author-only bounded search for a five-pixel adversarial example."""

import argparse
import itertools
import json
from pathlib import Path

import numpy as np

from classifier import IMAGE_SIZE, count_edits, load_model, predict_pixels, validate_pixels


def find_solution(model_path, image_path, max_edits=5):
    model = load_model(model_path)
    baseline = validate_pixels(json.loads(Path(image_path).read_text(encoding="utf-8")))
    prediction = predict_pixels(baseline, model)
    target = model["target_class"]
    if prediction["label"] == target:
        return baseline, []

    classes = model["classes"]
    target_index = classes.index(target)
    source_index = classes.index(prediction["label"])
    coefficients = np.asarray(model["coefficients"], dtype=np.float64)
    target_delta = coefficients[target_index] - coefficients[source_index]
    values = np.asarray(baseline, dtype=np.uint8).reshape(-1)
    toggle_delta = target_delta * (1 - (2 * values))
    candidates = np.argsort(toggle_delta)[-18:][::-1]
    if max_edits < 1 or max_edits > 5:
        raise ValueError("max_edits must be between 1 and 5")

    for edit_count in range(1, max_edits + 1):
        for chosen in itertools.combinations(candidates.tolist(), edit_count):
            candidate = values.copy()
            candidate[list(chosen)] = 1 - candidate[list(chosen)]
            matrix = candidate.reshape((IMAGE_SIZE, IMAGE_SIZE)).astype(int).tolist()
            if (
                count_edits(matrix, baseline) <= max_edits
                and predict_pixels(matrix, model)["label"] == target
            ):
                coordinates = [(index // IMAGE_SIZE, index % IMAGE_SIZE) for index in chosen]
                return matrix, coordinates

    raise RuntimeError("no target-class candidate found within the edit budget")


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=root / "data" / "model.json")
    parser.add_argument("--image", type=Path, default=root / "data" / "baseline.json")
    parser.add_argument("--max-edits", type=int, default=5)
    arguments = parser.parse_args()
    pixels, coordinates = find_solution(arguments.model, arguments.image, arguments.max_edits)
    print(f"Target prediction: {predict_pixels(pixels, load_model(arguments.model))['label']}")
    print(f"Changed pixels (row, column): {coordinates}")
