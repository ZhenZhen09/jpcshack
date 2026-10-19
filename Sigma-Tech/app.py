"""Local Flask server for the Sigma Tech image-classifier challenge."""

import json
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge

from classifier import BASELINE_PATH, MODEL_PATH, count_edits, load_model, predict_pixels, validate_pixels


FLAG_DEFAULT = "flag{pixel_confidence_is_not_identity}"
MAX_PIXEL_EDITS = 5


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        TESTING=False,
        MAX_CONTENT_LENGTH=32 * 1024,
        BASELINE_PATH=BASELINE_PATH,
        MODEL_PATH=MODEL_PATH,
        SIGMA_TECH_FLAG=os.environ.get("SIGMA_TECH_FLAG", FLAG_DEFAULT),
    )
    if config:
        app.config.update(config)
    app.config["BASELINE_PATH"] = Path(app.config["BASELINE_PATH"])
    app.config["MODEL_PATH"] = Path(app.config["MODEL_PATH"])

    def challenge_assets():
        try:
            baseline = validate_pixels(
                json.loads(app.config["BASELINE_PATH"].read_text(encoding="utf-8"))
            )
            model = load_model(app.config["MODEL_PATH"])
            return baseline, model
        except (OSError, json.JSONDecodeError, ValueError) as error:
            raise RuntimeError("challenge model files are missing or invalid") from error

    @app.get("/")
    def home():
        try:
            baseline, model = challenge_assets()
        except RuntimeError as error:
            return render_template("index.html", baseline=None, error=str(error)), 503
        return render_template(
            "index.html",
            baseline=baseline,
            classes=model["classes"],
            model_file="/model.json",
        )

    @app.get("/model.json")
    def model_artifact():
        try:
            load_model(app.config["MODEL_PATH"])
            response = app.response_class(
                app.config["MODEL_PATH"].read_text(encoding="utf-8"), mimetype="application/json"
            )
            response.headers["Cache-Control"] = "no-store"
            return response
        except (OSError, ValueError):
            return jsonify({"error": "Classifier unavailable. Run python train_model.py and retry."}), 503

    @app.get("/baseline.png")
    def baseline_image():
        image_path = app.config["BASELINE_PATH"].with_name("baseline.png")
        if not image_path.is_file():
            return jsonify({"error": "Starting image unavailable. Run python train_model.py and retry."}), 503
        return send_file(image_path, mimetype="image/png", download_name="sigma-tech-badge.png")

    @app.post("/api/predict")
    def predict():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or set(payload) != {"pixels"}:
            return jsonify({"error": "Send a JSON object containing only a pixels matrix."}), 400

        try:
            pixels = validate_pixels(payload["pixels"])
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

        try:
            baseline, model = challenge_assets()
        except RuntimeError:
            return jsonify({"error": "Classifier unavailable. Run python train_model.py and retry."}), 503

        edits = count_edits(pixels, baseline)
        if edits > MAX_PIXEL_EDITS:
            return jsonify({"error": f"The challenge allows at most {MAX_PIXEL_EDITS} changed pixels."}), 400

        result = predict_pixels(pixels, model)
        solved = result["label"] == model["target_class"]
        response = {
            "prediction": result["label"],
            "confidence": result["confidence"],
            "edits": edits,
            "solved": solved,
        }
        if solved:
            response["flag"] = app.config["SIGMA_TECH_FLAG"]
        return jsonify(response)

    @app.errorhandler(RequestEntityTooLarge)
    def request_too_large(_error):
        return jsonify({"error": "The submitted image data is too large."}), 413

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5001")), debug=False)
