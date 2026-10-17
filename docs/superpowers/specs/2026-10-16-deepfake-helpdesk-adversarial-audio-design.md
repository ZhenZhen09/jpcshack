# Deepfake Help Desk: Adversarial Audio CTF Design

## Goal

Replace the scripted help-desk exercise with a hard, story-driven adversarial machine-learning challenge. Players investigate a fraudulent executive account reset, reverse engineer a downloadable lightweight audio detector, and modify a captured synthetic call so the detector classifies it as genuine without exceeding a distortion limit.

## Audience and learning outcomes

The challenge targets advanced beginner to intermediate CTF players who are comfortable with Python and basic numeric analysis. It teaches that machine-learning confidence is not proof of authenticity, exposed model artifacts reveal decision boundaries, and input validation must be separate from model output.

Players should finish able to:

- inspect a compact model artifact and recover its normalization and classifier parameters;
- reproduce a deterministic audio-feature pipeline;
- reason about how a perturbation changes both extracted features and classifier score;
- construct and validate a targeted adversarial audio example;
- explain why a detector-only identity check is an unsafe help-desk control.

## Story

Northstar Systems uses an internal voice-authentication service during executive account recovery. A caller sounding like CFO Elena Marquez convinced the help desk to reset her account, and a high-value transfer is now pending. The security team recovered the submitted call and the exact detector artifact deployed during the incident.

The player is the incident responder. Their task is to reproduce the bypass by creating a modified version of the recovered call that the detector accepts as genuine. A successful reproduction unlocks the incident evidence vault and reveals the mock flag `THM{confidence_is_not_identity}`.

All people, organizations, phone numbers, recordings, and flags are fictional. The supplied audio is generated for the challenge and contains no real person's voice.

## Player flow

1. Start the local challenge and read the incident briefing.
2. Download `intercepted_call.wav`, `detector_model.npz`, and `deployment_notes.txt`.
3. Inspect the model archive to recover the ordered feature names, normalization mean and scale, linear weights, bias, and decision threshold.
4. Reproduce the feature extractor described by the deployment note and confirmed by the model metadata.
5. Measure the captured call, calculate which feature changes raise the genuine score, and generate a low-amplitude perturbation.
6. Upload a mono 16-bit PCM WAV with the required sample rate and frame count.
7. Use the returned score and distortion measurements to refine the sample.
8. Cross the genuine threshold while remaining under the distortion budget to reveal the flag.

The normal application never serves the author solver or solution walkthrough.

## Challenge mechanics

### Audio contract

The canonical recording uses these fixed properties:

- mono signed 16-bit PCM WAV;
- 16,000 Hz sample rate;
- exactly 64,000 frames, for a duration of four seconds;
- normalized floating-point samples in `[-1.0, 1.0]` during analysis;
- a maximum request body of 1 MiB;
- a maximum root-mean-square perturbation of `0.018` relative to the canonical recording.

Uploads with different channel count, sample width, sample rate, frame count, compression type, non-finite calculations, or excessive distortion are rejected before classification. The uploaded bytes and decoded samples must differ from the original so a replay is not accepted as a solve.

### Feature pipeline

`audio_features.py` owns the only production feature implementation. It extracts this ordered `float64` vector from the complete waveform:

1. `rms`: square root of mean squared amplitude;
2. `zero_crossing_rate`: sign changes divided by `sample_count - 1`;
3. `spectral_centroid`: magnitude-weighted frequency from an `rfft`;
4. `spectral_rolloff_85`: frequency below which 85 percent of spectral magnitude accumulates;
5. `spectral_flatness`: geometric mean divided by arithmetic mean of spectral magnitude with a fixed epsilon;
6. `high_frequency_ratio`: squared spectral magnitude at or above 4,000 Hz divided by total squared spectral magnitude;
7. `crest_factor`: maximum absolute amplitude divided by RMS with a fixed epsilon.

The module exposes the feature names and extraction function so asset generation, the detector, tests, and the reference solver cannot silently disagree on ordering.

### Detector artifact

`detector_model.npz` is a NumPy archive containing:

- `feature_names`: the exact ordered Unicode names;
- `mean`: seven normalization means;
- `scale`: seven positive normalization scales;
- `weights`: seven linear classifier weights;
- `bias`: one scalar;
- `threshold`: one scalar probability threshold;
- `sample_rate`, `frame_count`, and `max_rms_delta`: validation metadata;
- `format_version`: integer `1`.

Prediction standardizes the feature vector, calculates `logit = weights @ standardized + bias`, and applies the sigmoid function. The model returns `genuine` only when the probability is greater than or equal to the stored threshold.

The artifact is intentionally downloadable. Its exposure is the initial foothold, following the model-extraction style of the Fourtune challenge in `Machine_Learning_CTF_Challenges`.

### Intended adversarial path

The generated baseline call is classified as synthetic. A quiet high-frequency sinusoid, with amplitude and frequency selected by inspecting the weight vector and iterating locally, increases the genuine score enough to cross the threshold. The generator fixes a random seed and writes all artifacts deterministically so the intended solution remains reproducible.

The reference solver performs a bounded search over sinusoid frequency and amplitude, checks the RMS perturbation budget, and writes `solution/adversarial_call.wav`. Tests run that solver and submit its result through the same HTTP validation path used by players.

There is no alternate flag path through filenames, static files, error messages, malformed archives, or client-side state.

## Application architecture

### `audio_features.py`

Defines audio constants, `FEATURE_NAMES`, PCM conversion helpers, strict WAV decoding, feature extraction, and RMS perturbation measurement. It has no Flask dependency.

### `detector.py`

Loads and validates the `.npz` schema, rejects incompatible or non-finite arrays, computes probabilities, and returns a small prediction object containing the probability, classification, and extracted feature values.

### `generate_assets.py`

Creates a deterministic fictional speech-like waveform, a small synthetic training corpus, and the linear detector. It exports the canonical WAV, downloadable model archive, deployment note, and the private server copy of the model. Generation is a development and packaging step, not a runtime requirement.

### `app.py`

Creates the Flask application, serves the challenge page and three allowlisted public artifacts, accepts one uploaded WAV, applies size and audio validation, compares it with the canonical waveform, invokes the detector, and returns JSON. It reveals the flag only when every validation rule passes and the classifier accepts the sample.

The server binds to `127.0.0.1:8010` by default. It stores no player files or personal data. Upload bytes remain in memory for one request and are discarded afterward.

### Browser interface

The page resembles a Northstar incident-response console. It contains the case briefing, attack timeline, evidence downloads, upload area, detector result, distortion meter, and a short objective. It does not reveal the feature weights, perturbation strategy, or solution sequence beyond what exists in the downloadable artifacts.

All server strings are rendered with `textContent`. Upload controls remain keyboard accessible, result changes use an `aria-live` region, focus is visible, and the page has no horizontal overflow at 320 CSS pixels.

### Solution materials

`solution/solve.py` imports the shared feature contract but independently reads the public model artifact and performs a bounded search. `solution/README.md` explains the model equations, feature influence, perturbation search, and final upload. The normal server does not route anything under `solution/`.

## HTTP interface

### `GET /`

Returns the application shell.

### `GET /static/<allowlisted asset>`

Returns only the application stylesheet and JavaScript through Flask's static handling.

### `GET /evidence/<name>`

Allows exactly `intercepted_call.wav`, `detector_model.npz`, and `deployment_notes.txt`. Unknown names and encoded traversal attempts return a generic 404.

### `POST /api/analyze`

Accepts `multipart/form-data` with exactly one field named `audio`. It returns:

```json
{
  "accepted": false,
  "probability": 0.731245,
  "threshold": 0.92,
  "rms_delta": 0.009814,
  "max_rms_delta": 0.018,
  "message": "Detector rejected the sample.",
  "flag": null
}
```

The flag is non-null only when `accepted` is true and all validation rules pass. Validation failures return status 400 or 413 with a generic JSON error and no classifier measurements when those measurements could help bypass structural checks.

Unsupported methods return 405. Unknown routes return 404. Responses set `X-Content-Type-Options: nosniff`, `Cache-Control: no-store`, and a restrictive content security policy suitable for same-origin assets.

## Dependencies and resource limits

- Python 3.11 or newer;
- Flask 3.x;
- NumPy 2.x;
- SciPy 1.14 or newer;
- scikit-learn 1.5 or newer for asset generation; runtime prediction uses exported NumPy arrays and does not require loading a pickle or joblib object;
- no TensorFlow, PyTorch, librosa, GPU runtime, external API, database, or LLM;
- expected steady-state memory below 1 GiB on Windows;
- expected model archive below 100 KiB and evidence bundle below 2 MiB.

`requirements.txt` pins compatible major and minor versions. `run.bat` creates or reuses `.venv`, installs missing requirements, generates absent artifacts, starts the server, and opens the browser only after binding. README instructions also provide explicit command-line setup for users who do not want the launcher to install packages automatically.

## Error handling and security boundaries

- Reject requests by declared and actual byte size before expensive processing.
- Decode uploads from memory and never use the submitted filename as a filesystem path.
- Reject malformed RIFF/WAV data and unsupported PCM layouts without stack traces.
- Reject NaN or infinite features, model parameters, logits, probabilities, and distortion values.
- Compare decoded canonical and candidate arrays with identical shape and dtype semantics.
- Use explicit artifact and route allowlists; never expose Python source, the flag, or solution files.
- Keep the mock flag in server configuration and out of public HTML, JavaScript, model metadata, notes, and error messages.
- Disable Flask debug mode in the launcher.
- Do not persist uploads, IP addresses, filenames, or analysis results.

## Testing strategy

Use `pytest` with temporary in-memory WAV data and Flask's test client.

### Audio tests

- canonical WAV decoding accepts only the exact PCM contract;
- each feature matches hand-calculated fixtures or independently derived numeric expectations;
- silence and degenerate spectra produce finite values;
- channel count, sample width, rate, frame count, compression, truncation, and non-WAV data are rejected;
- perturbation distance is zero for identical arrays and matches a hand-derived constant offset.

### Detector tests

- the model schema and feature ordering are enforced;
- prediction matches a hand-calculated standardized vector and sigmoid result;
- incompatible shapes, non-positive scales, unsupported versions, and non-finite parameters are rejected;
- the canonical sample is classified synthetic;
- deterministic generation produces byte-identical metadata and numerically identical arrays.

### HTTP tests

- only the three evidence files are downloadable;
- source, flag, solution, absolute, and encoded traversal paths are inaccessible;
- missing, duplicate, empty, oversized, malformed, and structurally invalid uploads fail without a flag;
- the original sample and over-budget perturbations never solve;
- a valid but rejected sample returns bounded measurements and no flag;
- the intended adversarial sample reveals the flag;
- public assets omit the flag and avoid unsafe HTML insertion.

### End-to-end validation

- create a clean virtual environment and install pinned dependencies;
- regenerate all artifacts from a clean directory;
- run the complete test suite;
- run the reference solver and upload its output through the live server;
- launch from `run.bat` on Windows;
- verify keyboard navigation and layout at 320, 375, and desktop widths;
- confirm peak process memory remains below 1 GiB during generation, solving, and analysis.

## Documentation

The root README contains the story, learning objectives, prerequisites, launcher instructions, manual setup, resource estimate, player rules, and spoiler-free hints. The solution walkthrough lives only under `solution/`. It states that the detector is intentionally simplified and that real identity verification must use independent factors rather than model confidence alone.

## Success criteria

- A player can install and run the challenge locally on Windows without Docker or external services.
- The downloadable model is sufficient to reproduce the detector offline.
- The supplied call fails verification before modification.
- The reference attack generates a distinct WAV that passes the detector within the distortion budget.
- Random replay, malformed data, path traversal, and client-side manipulation cannot reveal the flag.
- The server processes uploads in memory and remains below 1 GiB RAM.
- The story and interface give the player an investigative objective without exposing the solve path.

## Out of scope

- neural speech synthesis, voice cloning, speaker recognition, speech-to-text, or realistic production deepfake detection;
- training or running a deep neural network;
- remote hosting, multi-user scoring, accounts, leaderboards, or persistent progress;
- defending the flag from a user with local source-code access;
- guaranteeing that the adversarial recording sounds natural to a human listener.
