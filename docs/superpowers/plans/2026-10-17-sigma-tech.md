# Sigma Tech Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an original, standalone adversarial image-classification CTF in `Sigma-Tech/` where a player edits at most five pixels to make a classifier predict the target class and earn a flag.

**Architecture:** A deterministic generator creates a small original synthetic dataset and trains a scikit-learn classifier, saving the baseline image and model metadata/weights as project-local artifacts. A shared classifier module validates and predicts; Flask exposes the UI and a guarded JSON prediction route; an author-only solver finds a verified candidate.

**Tech Stack:** Python 3.11+, Flask, NumPy, Pillow, scikit-learn, pytest, HTML/CSS/vanilla JavaScript.

**Spec:** `docs/superpowers/specs/2026-10-17-sigma-tech-design.md`

## Global Constraints

- Create the self-contained challenge in a new root-level `Sigma-Tech/`; leave `AI-1/` unchanged.
- Use original fictional story, generated image/data, and mock flag; reuse none of the referenced challenge's code, assets, model, or flag.
- Require no Groq, LLM, external API, credentials, or runtime network access.
- Images are fixed at 32-by-32 grayscale pixels; players may change no more than five distinct pixels.
- Keep the exact solution out of routes, client assets, and model metadata.
- The author solver must verify a target-class candidate within the same five-pixel budget enforced by the server.
- Reject malformed input, invalid dimensions, out-of-range values/coordinates, duplicate edit accounting, and edits over budget; never return a flag for invalid input.
- Do not start Flask in debug mode by default; keep accessible keyboard interaction and responsive image scaling.
- This workspace has no Git metadata; do not include or attempt Git commit/worktree steps.

## Review Focus

- Five pixel edits that include unchanged values must be counted as actual changed pixels; the server must compare against the baseline.
- Duplicate coordinates and malformed/ragged matrices must be rejected deterministically rather than bypassing the budget or causing a server error.
- The exact flag must not appear in static assets, model artifacts, failed prediction responses, or malformed-request responses.
- The author solver and server must use the same preprocessing and prediction implementation so a solver result cannot disagree with runtime behavior.
- A missing or invalid model artifact must produce a clear startup/runtime failure instead of silently substituting a different model.

---

## File Map

- `Sigma-Tech/app.py`: Flask routes, request validation boundary, flag decision.
- `Sigma-Tech/classifier.py`: fixed image contract, model loading, shared inference, baseline edit counting.
- `Sigma-Tech/train_model.py`: deterministic synthetic dataset generation and scikit-learn training; writes the starting image and inspectable model artifact.
- `Sigma-Tech/solve.py`: bounded deterministic author search using the trained model; prints candidate pixels and prediction.
- `Sigma-Tech/data/`: generated original starting image and model metadata/weights.
- `Sigma-Tech/run.bat`: Windows first-run environment/dependency setup, asset generation, and app launch.
- `Sigma-Tech/templates/index.html`: incident story, pixel editor, prediction and status output.
- `Sigma-Tech/static/app.css`: responsive accessible dark challenge styling.
- `Sigma-Tech/static/app.js`: 32-by-32 keyboard/pointer editor and `/api/predict` client.
- `Sigma-Tech/static/favicon.svg`: local vector app icon.
- `Sigma-Tech/tests/test_classifier.py`: model format, image contract, inference, and solver behavior.
- `Sigma-Tech/tests/test_app.py`: route validation, budget enforcement, flag gating, and HTML route.
- `Sigma-Tech/requirements.txt`: app and author/test dependency versions.
- `Sigma-Tech/README.md`: installation, generation, launch, and player solve outline.
- `Sigma-Tech/SOLUTION.md`: author-only exact edit set and reproducible verification command; never served.

## Interfaces

- `classifier.load_model(path: Path = MODEL_PATH) -> dict`: load and validate the generated artifact.
- `classifier.validate_pixels(pixels: object) -> list[list[int]]`: return a 32-by-32 binary matrix or raise `ValueError`.
- `classifier.count_edits(pixels: list[list[int]], baseline: list[list[int]]) -> int`: count coordinates that differ.
- `classifier.predict_pixels(pixels: list[list[int]], model: dict | None = None) -> dict`: return `{label: str, confidence: float, scores: dict[str, float]}`.
- `train_model.generate_assets(output_dir: Path) -> tuple[Path, Path]`: deterministically write baseline image and model artifact.
- `solve.find_solution(model_path: Path, image_path: Path, max_edits: int = 5) -> tuple[list[list[int]], list[tuple[int, int]]]`: return a model-verified target candidate and changed coordinates or raise `RuntimeError` if none exists.
- `POST /api/predict` accepts `{"pixels": [[0, 1, ...], ...]}` and returns `{"prediction": str, "confidence": float, "edits": int, "solved": bool}` plus `flag` only when solved.

## Task 1: Deterministic classifier, generated assets, and solver

**Files:**
- Create: `Sigma-Tech/classifier.py`
- Create: `Sigma-Tech/train_model.py`
- Create: `Sigma-Tech/solve.py`
- Create: `Sigma-Tech/tests/test_classifier.py`
- Generate: `Sigma-Tech/data/baseline.json`, `Sigma-Tech/data/baseline.png`
- Generate: `Sigma-Tech/data/model.json`
- Create: `Sigma-Tech/requirements.txt`

**Interfaces:**
- Consumes: Python 3.11+, NumPy, Pillow, scikit-learn.
- Produces: the classifier and solver signatures listed above; the server consumes `load_model`, `validate_pixels`, `count_edits`, and `predict_pixels`.

- [ ] **Step 1: Write behavior tests first.** Cover deterministic asset generation, matrix shape/value validation, identical predictions for repeated calls, and that `find_solution` produces no more than five distinct edits and is predicted as the target by `predict_pixels`.
- [ ] **Step 2: Run the focused tests and confirm they fail because the classifier/trainer/solver modules do not yet exist.**

Run: `python -m pytest Sigma-Tech/tests/test_classifier.py -q`

Expected: collection fails because the new `classifier` module is missing.

- [ ] **Step 3: Implement the fixed image and model contract.** Accept only JSON-compatible 32-by-32 matrices containing integer `0` or `1`; reject booleans and floats. Load only the known JSON artifact format. Convert pixels to a one-row NumPy feature vector in row-major order; compute class scores/probabilities with the stored trained logistic-regression coefficients and return the highest scoring label.
- [ ] **Step 4: Generate original deterministic synthetic images and train a two-class `LogisticRegression` model with a fixed random seed.** Serialize only class labels, dimensions, feature ordering, coefficients, intercepts, and seed as JSON; do not use pickle/joblib. Store the baseline as a 32-by-32 matrix. Tune the generated examples until the bounded author search finds a target candidate within five toggled pixels.
- [ ] **Step 5: Implement author search.** Rank candidate coordinates by the signed model coefficient for moving the baseline pixel toward the target class, exhaustively search subsets of the strongest 18 candidates up to `max_edits`, and return only a candidate that passes `predict_pixels`. Raise `RuntimeError` if no candidate wins.
- [ ] **Step 6: Run the focused tests and inspect solver output.**

Run: `python -m pytest Sigma-Tech/tests/test_classifier.py -q`

Expected: all classifier and solver tests pass; the winning sample differs from baseline at between one and five unique coordinates.

- [ ] **Step 7: Review the generated artifact diff and confirm it contains only original challenge assets and JSON model parameters.**

## Task 2: Guarded Flask API and player interface

**Files:**
- Create: `Sigma-Tech/app.py`
- Create: `Sigma-Tech/templates/index.html`
- Create: `Sigma-Tech/static/app.css`
- Create: `Sigma-Tech/static/app.js`
- Create: `Sigma-Tech/tests/test_app.py`

**Interfaces:**
- Consumes: Task 1 classifier functions and generated assets.
- Produces: `GET /` serving the editor and `POST /api/predict` implementing the JSON contract above.

- [ ] **Step 1: Write route tests first.** Test page status/title, a normal prediction, a solver-generated winning image returning the configured flag, over-budget rejection, malformed/ragged matrix rejection, invalid pixel rejection, and no flag in any unsuccessful response.
- [ ] **Step 2: Run the route tests and confirm they fail because `app` does not exist.**

Run: `python -m pytest Sigma-Tech/tests/test_app.py -q`

Expected: collection fails because the new `app` module is missing.

- [ ] **Step 3: Implement Flask routes.** `GET /` renders the interface. `POST /api/predict` requires a JSON object with only a `pixels` matrix, invokes `validate_pixels`, loads the same model, compares changed coordinates to the baseline, rejects more than five with HTTP 400, and predicts. Return the configured `SIGMA_TECH_FLAG` (default `flag{pixel_confidence_is_not_identity}`) only for a valid target prediction; otherwise omit the flag. Handle malformed JSON and model-loading errors with bounded, non-secret error JSON. Set Flask `debug=False` in the direct-run entry point.
- [ ] **Step 4: Implement the accessible pixel editor.** Render the supplied matrix as a crisp 32-by-32 grid using canvas or a CSS grid scaled responsively. Pointer clicks toggle binary pixels; keyboard focus and arrow/space controls provide equivalent editing. Show changed-pixel count, disable further edits at five, submit JSON to `/api/predict`, and announce prediction/result through a polite live region. Use explicit labels, visible focus, high-contrast dark surfaces, and reduced-motion-safe transitions.
- [ ] **Step 5: Add `run.bat` following the local challenge launcher convention.** Run from its own directory; create `.venv` with `python -m venv .venv` when missing; install `requirements.txt`; install again if the existing venv lacks Flask; run `train_model.py` when `data/model.json` is missing; then start `app.py` and pause after exit. Route setup errors to a message that Python must be installed and on PATH.
- [ ] **Step 6: Run focused route tests and the full Sigma Tech suite.**

Run: `python -m pytest Sigma-Tech/tests -q`

Expected: all API, flag secrecy, validation, and UI route tests pass.

- [ ] **Step 7: Review the route and static-file diff; confirm no file under `AI-1/` changed.**

## Task 3: Setup and solve documentation

**Files:**
- Create: `Sigma-Tech/README.md`
- Create: `Sigma-Tech/SOLUTION.md`

**Interfaces:**
- Consumes: app routes, `requirements.txt`, `train_model.py`, and `solve.py` from Tasks 1-2.
- Produces: reproducible local setup and an author-only verified solve guide.

- [ ] **Step 1: Document Windows PowerShell setup.** Include `py -3 -m venv .venv`, activation, `python -m pip install -r requirements.txt`, `python train_model.py`, and `python app.py`; identify `http://127.0.0.1:5000`, `run.bat` first-run behavior, and the no-Groq/no-network runtime requirement.
- [ ] **Step 2: Document the player solve path.** Explain how to read the fictional incident clue, inspect the starting bitmap and model JSON class coefficients, identify promising target-class pixels, toggle candidates while watching the edit counter and prediction, and submit a candidate at five or fewer edits. Keep the exact coordinates in `SOLUTION.md`, not the player README or UI.
- [ ] **Step 3: Record the exact solver result and verification command in `SOLUTION.md`.** The document must state that it is author-only and reproduce the coordinates printed by `python solve.py`; confirm the same image receives the target label through the shared classifier.
- [ ] **Step 4: Review documentation commands against actual file names and routes, then run the complete Sigma Tech test suite.**

Run: `python -m pytest Sigma-Tech/tests -q`

Expected: all tests pass; documentation commands refer only to files and endpoints that exist.

- [ ] **Step 5: Review both documents for exact author solution leakage in player-facing content.**

## Completion checks

- `Sigma-Tech/` runs independently; no files under `AI-1/` are modified.
- `python train_model.py` deterministically regenerates the starting image and JSON model artifact.
- `python solve.py` finds a legal target-class candidate and prints no flag.
- The Flask route returns the flag only for a validated candidate within the five-pixel limit.
- The normal UI, model artifacts, and prediction failures do not expose the exact solution or flag.
- `python -m pytest Sigma-Tech/tests -q` passes.
