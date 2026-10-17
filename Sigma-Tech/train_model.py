"""Create Sigma Tech's original synthetic image data and classifier artifact."""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.linear_model import LogisticRegression

from classifier import IMAGE_SIZE


SEED = 20261017
CLASSES = ("EMPLOYEE", "VISITOR")
TARGET_CLASS = "VISITOR"
SIGNATURE_COORDINATES = ((6, 22), (7, 22), (8, 22), (9, 22), (10, 22))


def _badge_template():
    image = np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.uint8)
    image[4, 4:28] = 1
    image[27, 4:28] = 1
    image[4:28, 4] = 1
    image[4:28, 27] = 1
    image[7, 9:23] = 1
    image[7:16, 9] = 1
    image[15, 9:23] = 1
    image[15:24, 22] = 1
    image[23, 9:23] = 1
    return image


def _training_data(rng, samples_per_class=120):
    template = _badge_template()
    signature = set(SIGNATURE_COORDINATES)
    features = []
    labels = []

    for label in CLASSES:
        for _ in range(samples_per_class):
            sample = template.copy()
            if label == TARGET_CLASS:
                for row, column in SIGNATURE_COORDINATES:
                    sample[row, column] = 1
            else:
                for row, column in SIGNATURE_COORDINATES:
                    sample[row, column] = 0

            # Mild label-independent sensor noise keeps the synthetic data varied.
            noise = rng.random(sample.shape) < 0.002
            for row, column in signature:
                noise[row, column] = False
            sample[noise] = 1 - sample[noise]
            features.append(sample.reshape(-1))
            labels.append(label)

    return np.asarray(features, dtype=np.uint8), np.asarray(labels)


def generate_assets(output_dir: Path):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    features, labels = _training_data(rng)
    classifier = LogisticRegression(C=2.0, max_iter=1000, random_state=SEED)
    classifier.fit(features, labels)

    baseline = _badge_template()
    baseline_path = output_dir / "baseline.json"
    model_path = output_dir / "model.json"
    baseline_path.write_text(
        json.dumps(baseline.tolist(), separators=(",", ":")) + "\n", encoding="utf-8"
    )
    Image.fromarray(baseline * 255).resize((320, 320), Image.Resampling.NEAREST).save(
        output_dir / "baseline.png"
    )
    # Binary LogisticRegression stores one decision row; expand it into an
    # equivalent symmetric two-logit form for the shared JSON inference path.
    binary_coefficients = classifier.coef_[0]
    binary_intercept = float(classifier.intercept_[0])
    model = {
        "format_version": 1,
        "image_shape": [IMAGE_SIZE, IMAGE_SIZE],
        "feature_order": "row-major",
        "classes": [str(value) for value in classifier.classes_],
        "target_class": TARGET_CLASS,
        "coefficients": np.stack((-binary_coefficients / 2, binary_coefficients / 2)).tolist(),
        "intercepts": [-binary_intercept / 2, binary_intercept / 2],
        "training_seed": SEED,
    }
    model_path.write_text(
        json.dumps(model, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8"
    )
    return baseline_path, model_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "data")
    arguments = parser.parse_args()
    baseline, model = generate_assets(arguments.output_dir)
    print(f"Generated {baseline} and {model}")
