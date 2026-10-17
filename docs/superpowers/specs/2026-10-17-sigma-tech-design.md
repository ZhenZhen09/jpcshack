# Sigma Tech: Image Classifier Challenge Design

## Goal

Create an original adversarial image-classification CTF challenge in a new standalone `Sigma-Tech/` folder beside `AI-1/`. Players inspect a small image, reason about a classifier's behavior, change no more than five pixels, and submit an image that makes the classifier predict the target class to reveal the mock flag.

## Audience and learning outcomes

The challenge is for beginner-to-intermediate CTF players with basic Python familiarity. It teaches that image classifiers can be fooled by small, targeted input changes and that a model's prediction should not be treated as proof of identity or authorization.

Players should learn to inspect a small model and its input representation, compare predictions as input pixels change, construct a targeted adversarial example within a strict edit budget, and distinguish the model's prediction from the server's flag-unlock validation.

## Scope and placement

- Create a new `Sigma-Tech/` directory at the project root. Do not modify or import runtime code from `AI-1/`.
- Keep the challenge self-contained: Flask app, templates/static files, original dataset and image assets, deterministic training/model-generation code, tests, dependency list, README, and a non-player-facing solution walkthrough.
- Include a Windows `run.bat` beside the app. It creates a local virtual environment and installs dependencies on first launch, generates missing model assets, then starts Flask.
- Use an original fictional company story, generated images/data, and a mock flag. Do not reuse assets, model files, code, or flag material from the referenced challenge.
- Do not require Groq, an LLM, external API calls, credentials, or network access at runtime.

## Player experience

1. Read a short Sigma Tech incident brief explaining that an image-based access check accepted a suspicious badge.
2. View/download the supplied small image and inspect the exposed model or challenge notes.
3. Use the page's pixel editor to change up to five distinct pixels. Show the current edit count and latest predicted class after each submission.
4. Submit the candidate image. Return the predicted class and concise feedback; reveal the flag only when the server-side classifier predicts the target class and the candidate respects the edit budget.
5. If the candidate fails, preserve the image and edits so the player can refine their attempt.

The interface must work with keyboard controls as well as pointer interaction, label the pixel-edit controls, expose prediction/status feedback to assistive technology, and keep the image legible at mobile sizes.

## Classifier and challenge assets

Use a small scikit-learn image classifier trained on an original, deterministic synthetic dataset. Images have a fixed 32-by-32 grayscale format. The model's preprocessing, class labels, and inference behavior must be shared by the Flask app, model-generation tool, tests, and author solver through one implementation so they cannot drift.

The model and notes should provide enough evidence for a player to reason about the decision boundary. The source dataset and generation script stay inside `Sigma-Tech/`. A deterministic author-side solver searches legal candidates with at most five changed pixels and verifies a winning example by calling the same inference and validation functions used by the server. The solver and exact solution are not exposed by the player route.

Before implementation is considered complete, the solver must find a valid winning sample from the published starting image, and the server test must confirm that sample unlocks the mock flag. If this cannot be achieved with the initial model/data, adjust the original synthetic dataset or training configuration rather than weakening the server's edit-budget checks.

## Application boundaries and validation

- The Flask route handles the player request, validates its shape and edits, calls the shared classifier, and decides whether the flag is earned.
- The model module owns model loading, preprocessing, prediction, class names, and validation metadata.
- The author tooling owns deterministic data/model creation and solution search; it is not imported as a player-facing endpoint.
- Reject malformed JSON, invalid dimensions, out-of-range coordinates/pixel values, duplicate coordinates counted as multiple edits, and requests with more than five distinct changed pixels. Do not return the flag for invalid input or a target prediction produced by an invalid candidate.
- Keep the flag in server-side configuration with a harmless local mock default; never place it in client assets, model metadata, or normal prediction responses.
- Return clear client errors for invalid input and a recoverable message when the model artifact is missing or invalid. Do not run in Flask debug mode by default.

## Setup and solve documentation

`Sigma-Tech/README.md` will state the supported Python version, virtual-environment commands, dependency installation, model/data generation (if needed), local launch command, URL, and a player-oriented solve outline. `Sigma-Tech/run.bat` will provide the matching one-double-click Windows startup flow. `Sigma-Tech/SOLUTION.md` will be explicitly marked author-only and contain the exact winning pixel edits, the reasoning that derives them, and a verification command. It must not be served by Flask or included in the player page.

## Testing and acceptance

Tests will cover deterministic model/data generation, fixed input shape and pixel range, valid and invalid edit counts, repeated coordinates, ordinary predictions, the verified winning sample, flag secrecy on failure and malformed input, and static/template wiring. A local smoke check will start the app and exercise the page and submission endpoint without external services.

Acceptance requires that Sigma Tech runs independently from `AI-1/`, installs from its own dependency file, makes predictions without an LLM/API key/network, accepts a solver-verified candidate within five edits, rejects invalid or over-budget candidates, and returns the flag only for a valid target-class prediction.
