# Deepfake Help Desk Adversarial Audio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `deepfake_helpdesk` with a hard, story-driven CTF in which players reverse engineer a lightweight audio classifier and submit a low-distortion adversarial WAV to recover `THM{confidence_is_not_identity}`.

**Architecture:** A deterministic asset generator produces a fictional four-second WAV and a transparent NumPy model archive. Shared audio code validates PCM WAV input and extracts seven signal features; a small detector standardizes those features and applies a linear sigmoid classifier. A Flask application serves the incident console and evidence, analyzes uploads entirely in memory, and releases the flag only when a distinct candidate crosses the model threshold within the RMS distortion budget.

**Tech Stack:** Python 3.11+, Flask 3.x, NumPy 2.x, SciPy 1.14+, scikit-learn 1.5+ for deterministic training, pytest, vanilla HTML/CSS/JavaScript, Windows batch launcher.

**Spec:** `docs/superpowers/specs/2026-10-16-deepfake-helpdesk-adversarial-audio-design.md`

## Global Constraints

- Bind to `127.0.0.1:8010` by default and never enable Flask debug mode in the launcher.
- Accept only mono signed 16-bit PCM WAV at 16,000 Hz with exactly 64,000 frames.
- Limit request bodies to 1 MiB and candidate RMS perturbation to `0.018`.
- Keep uploads in memory; do not persist filenames, samples, IP addresses, or results.
- Keep `THM{confidence_is_not_identity}` out of public HTML, JavaScript, evidence, model metadata, deployment notes, and error details.
- Use the single feature order `rms`, `zero_crossing_rate`, `spectral_centroid`, `spectral_rolloff_85`, `spectral_flatness`, `high_frequency_ratio`, `crest_factor` everywhere.
- Do not use TensorFlow, PyTorch, librosa, an external API, a database, an LLM, or unsafe pickle/joblib model loading.
- Generate fictional audio deterministically with no real person's voice.
- Render server-provided browser text with `textContent`; never use `innerHTML`.
- Keep expected peak memory below 1 GiB.
- This workspace is not a Git repository, so do not add commit steps. Record task completion in the plan ledger instead.

## Review Focus

- A valid WAV containing trailing chunks or unusual RIFF chunk ordering must either decode safely under the exact PCM contract or fail with a controlled 400, never crash or bypass validation; Task 1 tests this.
- A model archive with correct array shapes but duplicate, reordered, or Unicode-confusable feature names must be rejected before prediction; Task 2 tests this.
- A candidate whose decoded samples match the original but whose container bytes differ must be rejected as a replay; Task 4 tests decoded equality rather than byte equality alone.
- Multipart requests with duplicate `audio` fields or extra fields must fail without classification or flag disclosure; Task 4 tests the exact request shape.
- Concurrent analyses must not mutate shared model or baseline arrays or leak one request's result into another; Task 4 runs parallel accepted and rejected requests.

---

## File structure

Replace the existing challenge files with these responsibilities:

- `deepfake_helpdesk/audio_features.py`: strict WAV decoding, PCM conversion, seven-feature extraction, and RMS distance.
- `deepfake_helpdesk/detector.py`: safe `.npz` schema loading and linear sigmoid prediction.
- `deepfake_helpdesk/generate_assets.py`: deterministic fictional waveform, training corpus, classifier fitting, and public evidence generation.
- `deepfake_helpdesk/app.py`: Flask application factory, evidence allowlist, upload validation, classification, and flag gate.
- `deepfake_helpdesk/public/index.html`: incident-response application shell.
- `deepfake_helpdesk/public/style.css`: responsive incident-console presentation.
- `deepfake_helpdesk/public/app.js`: upload workflow and text-only result rendering.
- `deepfake_helpdesk/evidence/`: generated public call, model, and deployment note.
- `deepfake_helpdesk/private/`: generated server model copy and canonical waveform.
- `deepfake_helpdesk/solution/solve.py`: bounded adversarial sinusoid search.
- `deepfake_helpdesk/solution/README.md`: author walkthrough.
- `deepfake_helpdesk/tests/`: focused audio, detector, generator, solver, and HTTP tests.
- `deepfake_helpdesk/requirements.txt`: pinned runtime, generation, and test dependencies.
- `deepfake_helpdesk/run.bat`: Windows setup and launch.
- `deepfake_helpdesk/README.md`: spoiler-free player and operator documentation.

Delete obsolete `server.py` and its old state-machine tests only after the replacement app has a passing startup/API test.

### Task 1: Build the strict audio boundary and feature pipeline

**Files:**
- Create: `deepfake_helpdesk/audio_features.py`
- Create: `deepfake_helpdesk/tests/test_audio_features.py`
- Create: `deepfake_helpdesk/requirements.txt`

**Interfaces:**
- Produces `AudioValidationError(ValueError)`.
- Produces `AudioSample(sample_rate: int, samples: numpy.ndarray)` where `samples` is one-dimensional `float64` in `[-1, 1]`.
- Produces `decode_wav(data: bytes, *, expected_rate: int = 16000, expected_frames: int = 64000) -> AudioSample`.
- Produces `encode_wav(samples: numpy.ndarray, sample_rate: int = 16000) -> bytes`.
- Produces `extract_features(samples: numpy.ndarray, sample_rate: int = 16000) -> numpy.ndarray` with shape `(7,)`.
- Produces `rms_delta(candidate: numpy.ndarray, reference: numpy.ndarray) -> float`.
- Produces constants `FEATURE_NAMES`, `SAMPLE_RATE`, `FRAME_COUNT`, and `MAX_RMS_DELTA`.

- [ ] **Step 1: Add pinned dependencies**

Create `requirements.txt` with compatible exact versions available for Python 3.11:

```text
Flask==3.1.2
numpy==2.1.3
scipy==1.14.1
scikit-learn==1.5.2
pytest==8.3.5
```

- [ ] **Step 2: Write failing decode and encode tests**

Add tests that build WAV bytes with `wave.Wave_write` and prove the boundary accepts exactly mono, 16-bit PCM, 16 kHz, 64,000 frames. Include stereo, 8-bit, wrong rate, wrong frame count, truncated bytes, random bytes, and a valid RIFF containing a harmless trailing `LIST` chunk. Name each mutation in a parametrized test.

```python
@pytest.mark.parametrize(
    ("channels", "width", "rate", "frames", "reason"),
    [
        (2, 2, 16000, 64000, "mono"),
        (1, 1, 16000, 64000, "16-bit"),
        (1, 2, 8000, 64000, "16000 Hz"),
        (1, 2, 16000, 63999, "64000 frames"),
    ],
)
def test_decode_wav_rejects_audio_outside_contract(channels, width, rate, frames, reason):
    with pytest.raises(AudioValidationError, match=reason):
        decode_wav(make_wav(channels=channels, width=width, rate=rate, frames=frames))
```

- [ ] **Step 3: Run the boundary tests and verify RED**

Run from `deepfake_helpdesk`:

```powershell
python -m pytest tests/test_audio_features.py -q
```

Expected: collection fails because `audio_features` does not exist.

- [ ] **Step 4: Implement strict in-memory PCM decoding and encoding**

Use `wave.open(io.BytesIO(data), "rb")`, inspect all format fields before reading frames, require `getcomptype() == "NONE"`, require no missing or extra decoded frames, convert little-endian `int16` to `float64 / 32768.0`, copy arrays before returning, and translate `wave.Error`, `EOFError`, and structural `OSError` into `AudioValidationError("Invalid WAV file.")`. Encoding clips only at the serialization boundary and returns bytes from `io.BytesIO`.

```python
SAMPLE_RATE = 16_000
FRAME_COUNT = 64_000
MAX_RMS_DELTA = 0.018
FEATURE_NAMES = (
    "rms", "zero_crossing_rate", "spectral_centroid",
    "spectral_rolloff_85", "spectral_flatness",
    "high_frequency_ratio", "crest_factor",
)

@dataclass(frozen=True)
class AudioSample:
    sample_rate: int
    samples: np.ndarray
```

- [ ] **Step 5: Run decode and encode tests and verify GREEN**

Run the same pytest command. Expected: boundary tests pass, including the safe trailing-chunk fixture.

- [ ] **Step 6: Write failing feature and distance tests**

Use hand-derived fixtures: all-zero samples, a constant `0.25` waveform, an alternating-sign waveform, and a bin-centered `1000 Hz` sine. Assert exact RMS/ZCR cases, centroid within one FFT bin, all seven values finite, stable feature order, shape `(7,)`, zero distance for equal arrays, `0.01` distance for a constant `0.01` offset, and a shape mismatch error.

```python
def test_constant_offset_has_hand_derived_rms_delta():
    reference = np.zeros(8, dtype=np.float64)
    candidate = np.full(8, 0.01, dtype=np.float64)
    assert rms_delta(candidate, reference) == pytest.approx(0.01)
```

- [ ] **Step 7: Run feature tests and verify RED**

Expected: failures name missing `extract_features` and `rms_delta`.

- [ ] **Step 8: Implement the seven deterministic features**

Use `np.fft.rfft`, `np.fft.rfftfreq`, magnitude for centroid/rolloff/flatness, squared magnitude for the high-frequency ratio, epsilon `np.finfo(np.float64).tiny`, and explicit finite checks. Treat silent spectra as zero for centroid, rolloff, flatness, and high-frequency ratio; return crest factor zero when RMS is zero. Reject non-one-dimensional, empty, or non-finite arrays.

- [ ] **Step 9: Run Task 1 tests and record completion**

Run:

```powershell
python -m pytest tests/test_audio_features.py -q
```

Expected: all Task 1 tests pass with no warnings.

### Task 2: Generate and load the transparent detector artifact

**Files:**
- Create: `deepfake_helpdesk/detector.py`
- Create: `deepfake_helpdesk/generate_assets.py`
- Create: `deepfake_helpdesk/tests/test_detector.py`
- Create: `deepfake_helpdesk/tests/test_generate_assets.py`
- Generate: `deepfake_helpdesk/evidence/intercepted_call.wav`
- Generate: `deepfake_helpdesk/evidence/detector_model.npz`
- Generate: `deepfake_helpdesk/evidence/deployment_notes.txt`
- Generate: `deepfake_helpdesk/private/canonical_call.wav`
- Generate: `deepfake_helpdesk/private/detector_model.npz`

**Interfaces:**
- Consumes all Task 1 constants and functions.
- Produces `ModelValidationError(ValueError)`.
- Produces immutable `DetectorModel` fields `feature_names`, `mean`, `scale`, `weights`, `bias`, `threshold`, `sample_rate`, `frame_count`, and `max_rms_delta`.
- Produces `load_model(path_or_file) -> DetectorModel` using `numpy.load(..., allow_pickle=False)`.
- Produces `Prediction(probability: float, accepted: bool, features: numpy.ndarray)`.
- Produces `predict(model: DetectorModel, samples: numpy.ndarray) -> Prediction`.
- Produces `generate(output_root: pathlib.Path) -> GeneratedAssets` and deterministic command `python generate_assets.py`.

- [ ] **Step 1: Write failing model-schema tests**

Create `.npz` files in `tmp_path` and assert successful loading of the exact schema. Parametrize wrong shapes, missing fields, format version other than `1`, zero/negative scales, threshold outside `(0, 1)`, non-finite numbers, reordered names, duplicate names, and the confusable name `spectral_rolloff_８５`.

```python
def test_model_rejects_reordered_feature_names(tmp_path):
    arrays = valid_model_arrays()
    arrays["feature_names"] = np.array((*FEATURE_NAMES[1:], FEATURE_NAMES[0]))
    path = save_npz(tmp_path, arrays)
    with pytest.raises(ModelValidationError, match="feature names"):
        load_model(path)
```

- [ ] **Step 2: Run detector tests and verify RED**

Run `python -m pytest tests/test_detector.py -q`. Expected: import failure for `detector`.

- [ ] **Step 3: Implement safe model loading and prediction**

Load with `allow_pickle=False`, copy arrays as `float64`, mark them read-only with `setflags(write=False)`, compare feature names by exact tuple equality, and validate every scalar and array. Compute a numerically stable sigmoid by branching on the sign of the logit. Return a copied, read-only feature vector from `predict`.

```python
@dataclass(frozen=True)
class Prediction:
    probability: float
    accepted: bool
    features: np.ndarray

def predict(model: DetectorModel, samples: np.ndarray) -> Prediction:
    features = extract_features(samples, model.sample_rate)
    standardized = (features - model.mean) / model.scale
    logit = float(model.weights @ standardized + model.bias)
    probability = stable_sigmoid(logit)
    return Prediction(probability, probability >= model.threshold, readonly_copy(features))
```

- [ ] **Step 4: Add hand-calculated prediction tests and verify GREEN**

Monkeypatch only `detector.extract_features` to return a fixed literal vector, then compare standardization, logit, sigmoid, and threshold against hand-calculated numeric expectations. Also assert calls cannot mutate model arrays. Run detector tests and expect all pass.

- [ ] **Step 5: Write failing deterministic-generation tests**

Call `generate()` into two temporary roots. Assert the same relative files exist, both models contain numerically identical arrays, both WAVs decode identically, notes contain the format contract, public files omit the flag, the canonical call is rejected by the detector, and the artifact sizes meet the spec. Do not require ZIP container bytes to be identical because `.npz` timestamps may vary; require identical contents.

- [ ] **Step 6: Run generator tests and verify RED**

Run `python -m pytest tests/test_generate_assets.py -q`. Expected: `generate_assets` or `generate` is missing.

- [ ] **Step 7: Implement deterministic fictional signal and training**

Use `np.random.default_rng(2048)`. Build four-second speech-like signals from amplitude envelopes, several harmonics between 90 and 320 Hz, controlled noise, and optional high-frequency components. Generate labeled feature rows for synthetic and genuine-like classes, fit `StandardScaler` and `LogisticRegression(random_state=2048, solver="liblinear")`, then export only numeric arrays. Select and store a threshold that rejects the canonical call while leaving a feasible adversarial solution below `0.018` RMS.

Write `deployment_notes.txt` with only the WAV contract, feature names, equation form, and artifact field descriptions. It must not state the successful frequency/amplitude or include the flag.

- [ ] **Step 8: Generate checked-in challenge assets**

Run:

```powershell
python generate_assets.py
```

Expected: the three evidence files and two private files are created; the command prints the canonical probability, threshold, and artifact paths without printing the flag.

- [ ] **Step 9: Run Task 2 tests and record completion**

Run:

```powershell
python -m pytest tests/test_audio_features.py tests/test_detector.py tests/test_generate_assets.py -q
```

Expected: all Task 1–2 tests pass.

### Task 3: Build and prove the intended adversarial attack

**Files:**
- Create: `deepfake_helpdesk/solution/solve.py`
- Create: `deepfake_helpdesk/solution/README.md`
- Create: `deepfake_helpdesk/tests/test_solution.py`

**Interfaces:**
- Consumes the public `intercepted_call.wav` and `detector_model.npz` plus Task 1–2 APIs.
- Produces `find_adversarial(call_path: Path, model_path: Path) -> AttackResult`.
- Produces `AttackResult(samples: numpy.ndarray, frequency: float, amplitude: float, prediction: Prediction, rms_delta: float)`.
- Produces CLI output `solution/adversarial_call.wav` without importing private server files.

- [ ] **Step 1: Write the failing intended-solve test**

Generate assets in a temporary root, call `find_adversarial` using only the two public artifacts, and assert the result differs from the original, remains within the model's RMS budget, is accepted, and round-trips through `encode_wav`/`decode_wav` without losing acceptance.

```python
def test_public_artifacts_are_sufficient_to_build_a_passing_wav(tmp_path):
    assets = generate(tmp_path)
    result = find_adversarial(assets.public_call, assets.public_model)
    original = decode_wav(assets.public_call.read_bytes()).samples
    assert not np.array_equal(result.samples, original)
    assert result.rms_delta <= MAX_RMS_DELTA
    assert predict(load_model(assets.public_model), result.samples).accepted
```

- [ ] **Step 2: Run the solution test and verify RED**

Run `python -m pytest tests/test_solution.py -q`. Expected: import failure for `solution.solve`.

- [ ] **Step 3: Implement a bounded sinusoid search**

Search integer FFT-bin frequencies from 4,000 through 7,500 Hz and amplitudes from `0.001` through the largest value under the RMS budget. Keep the accepted candidate with the smallest RMS delta, break deterministic ties by lower frequency then lower amplitude, clip to the representable PCM range before evaluating the serialized round trip, and raise a clear `RuntimeError` if no candidate exists.

The CLI accepts optional `--call`, `--model`, and `--output` paths with defaults pointing at the packaged challenge files.

- [ ] **Step 4: Run the solution test and tune generation, not the validator**

Run the solution test. If no feasible candidate exists, adjust the Task 2 generated training distribution, weights, or threshold while preserving the fixed validation budget and feature definitions. Regenerate assets and rerun all Task 1–3 tests. Record every generator ruling in the plan ledger.

- [ ] **Step 5: Write the author walkthrough**

Document how to inspect `.npz` fields with NumPy, reproduce the feature equation, rank standardized feature influence as `weights * standardized_features`, search perturbations, run `solve.py`, and upload the resulting WAV. Include the exact commands but keep this file outside all served paths.

- [ ] **Step 6: Run Task 3 tests and record completion**

Run:

```powershell
python -m pytest tests/test_audio_features.py tests/test_detector.py tests/test_generate_assets.py tests/test_solution.py -q
```

Expected: the intended attack produces a passing, under-budget WAV deterministically.

### Task 4: Replace the scripted server with the secure Flask analysis API

**Files:**
- Create: `deepfake_helpdesk/app.py`
- Create: `deepfake_helpdesk/tests/test_app.py`
- Delete after GREEN: `deepfake_helpdesk/server.py`
- Delete after GREEN: `deepfake_helpdesk/tests/test_server.py`

**Interfaces:**
- Consumes `decode_wav`, `rms_delta`, `load_model`, and `predict`.
- Produces `create_app(config: dict | None = None) -> flask.Flask`.
- Produces `GET /`, `GET /static/<allowlisted asset>`, `GET /evidence/<name>`, and `POST /api/analyze`.
- Produces JSON `{accepted, probability, threshold, rms_delta, max_rms_delta, message, flag}` for structurally valid candidates.

- [ ] **Step 1: Write failing application-shell and evidence tests**

Create an app with generated temporary asset paths and a test flag. Assert `/` returns HTML; the three evidence names return non-empty files; unknown, source, solution, absolute, backslash, double-encoded, and encoded traversal paths return 404; evidence and public assets omit the flag; unsupported methods return 405; and security/cache headers exist.

- [ ] **Step 2: Run the application tests and verify RED**

Run `python -m pytest tests/test_app.py -q`. Expected: import failure for `app`.

- [ ] **Step 3: Implement the application factory and allowlisted reads**

Load the baseline and model once during `create_app`, copy and mark baseline samples read-only, set `MAX_CONTENT_LENGTH = 1_048_576`, configure `SEND_FILE_MAX_AGE_DEFAULT = 0`, and use a dictionary mapping public evidence names to resolved paths. Never join a request path onto a directory.

Add `after_request` headers for `nosniff`, `no-store`, frame denial, referrer policy, and a same-origin content security policy.

- [ ] **Step 4: Write failing upload-gate tests**

Cover missing file, empty filename with bytes, empty body, extra form field, duplicate `audio` fields, oversized request, malformed WAV, every invalid PCM property, original decoded samples in a rewritten container, accepted classifier result over the RMS budget, ordinary rejected sample, and the Task 3 intended adversarial sample. Assert errors never include the flag or numeric feature vector.

For duplicate fields, construct `werkzeug.datastructures.MultiDict` containing two file tuples. For decoded replay, decode and re-encode the canonical samples so the container differs while samples remain equal.

- [ ] **Step 5: Run upload tests and verify RED**

Expected: route missing or placeholder analysis responses fail the exact assertions.

- [ ] **Step 6: Implement exact multipart and solve validation**

Require `request.mimetype == "multipart/form-data"`, `set(request.form) == set()`, `set(request.files) == {"audio"}`, and `len(request.files.getlist("audio")) == 1`. Read at most `MAX_CONTENT_LENGTH + 1` bytes, reject empty or oversized content, decode, reject `np.array_equal(candidate, baseline)`, compute RMS delta, reject over-budget samples before calling `predict`, and return rounded measurements only for structurally valid, within-budget candidates.

Use a server-only flag from `app.config["FLAG"]`, defaulting to `THM{confidence_is_not_identity}`. The solve condition is one expression combining distinct decoded samples, budget compliance, and `prediction.accepted`.

- [ ] **Step 7: Add concurrent isolation test**

Use `ThreadPoolExecutor(max_workers=8)` with a fresh Flask test client inside each worker. Alternate the intended adversarial WAV and a rejected WAV for at least 32 requests. Assert every response matches its input and model/baseline arrays remain unchanged after the run.

- [ ] **Step 8: Run Task 4 tests and verify GREEN**

Run:

```powershell
python -m pytest tests/test_app.py -q
```

Expected: all HTTP, bypass, and concurrency tests pass.

- [ ] **Step 9: Remove the obsolete state-machine server**

Delete `server.py` and `tests/test_server.py`. Search the challenge folder for imports or documentation that still names `server.py`, the old callback-number flow, or `THM{verify_out_of_band}` and remove those references.

- [ ] **Step 10: Run the complete backend suite and record completion**

Run `python -m pytest -q`. Expected: every Task 1–4 test passes.

### Task 5: Build the incident-response interface and Windows launcher

**Files:**
- Replace: `deepfake_helpdesk/public/index.html`
- Replace: `deepfake_helpdesk/public/style.css`
- Replace: `deepfake_helpdesk/public/app.js`
- Replace: `deepfake_helpdesk/run.bat`
- Replace: `deepfake_helpdesk/README.md`
- Modify: `deepfake_helpdesk/tests/test_app.py`

**Interfaces:**
- Consumes the Task 4 routes and JSON response shape.
- Sends exactly one multipart field named `audio` to `/api/analyze`.
- Displays accepted state, probability, threshold, RMS delta, budget, message, and nullable flag using text nodes.

- [ ] **Step 1: Write failing public-source and semantic-shell tests**

Assert the served page contains one `h1`, incident timeline, evidence download links, an associated `.wav` file input, submit button, status region with `aria-live`, and result fields. Assert public sources omit both flag literals, `innerHTML`, inline scripts, remote URLs, and solution terms such as the winning frequency or amplitude.

- [ ] **Step 2: Run the interface contract tests and verify RED**

Run `python -m pytest tests/test_app.py -q`. Expected: old help-desk markup fails the new semantic and source assertions.

- [ ] **Step 3: Replace the page with the Northstar incident console**

Create sections for the urgent briefing, incident timeline, three evidence downloads, mission objective, upload drop area, analysis progress, score versus threshold, distortion versus budget, and flag panel. Use native links, label/input/button elements, a skip link, and a polite live region. Keep instructions spoiler-free: tell players to inspect the model and submit a distinct, low-distortion WAV without naming the perturbation.

- [ ] **Step 4: Replace styles with a responsive forensic-console layout**

Use the existing dark visual direction but make the evidence and analysis workflow primary. Provide visible `:focus-visible`, a minimum 44px interactive height, status colors that also have text labels, `overflow-wrap` for values, responsive single-column layout below 760px, and no fixed widths that overflow 320px. Respect `prefers-reduced-motion`.

- [ ] **Step 5: Replace client logic with safe multipart analysis**

On submit, require a selected `.wav`, create `FormData`, append exactly `audio`, disable the button, and fetch `/api/analyze`. Validate the response's booleans and finite numeric fields before display. Set every dynamic field with `textContent`; hide and clear the flag panel when `flag` is null. Show retryable network and validation messages and restore controls in `finally`.

- [ ] **Step 6: Run interface tests and static safety searches**

Run:

```powershell
python -m pytest tests/test_app.py -q
rg -n "innerHTML|THM\{|https?://" public
```

Expected: tests pass and `rg` returns no matches.

- [ ] **Step 7: Write the launcher**

Replace `run.bat` with a script that changes to its directory, creates `.venv` when absent, installs `requirements.txt` only on first setup, generates assets when any required artifact is absent, and starts `app.py`. Preserve failures with `if errorlevel 1` and `pause`; do not hide dependency or generation errors.

Add an `if __name__ == "__main__"` block to `app.py` that binds before opening the browser. Use `werkzeug.serving.make_server`, print the URL, call `webbrowser.open`, then serve until Ctrl+C and close cleanly.

- [ ] **Step 8: Write spoiler-free player documentation**

Document the fictional incident, prerequisites, approximate RAM/disk use, double-click setup, manual virtual-environment commands, URL, stopping the service, evidence list, player objective, allowed offline analysis, reset/regeneration commands, and the simplified educational nature of the detector. Link to `solution/README.md` under a clearly marked spoiler heading.

- [ ] **Step 9: Run Task 5 tests and record completion**

Run `python -m pytest -q`. Expected: the full automated suite passes.

### Task 6: Validate packaging, intended solve, browser behavior, and resources

**Files:**
- Review all files under `deepfake_helpdesk/`
- Create during validation only: `deepfake_helpdesk/.validation/` logs and screenshots, then remove this directory after recording results in the ledger.

**Interfaces:**
- Consumes the complete challenge.
- Produces a clean local player experience and a repeatable author solve.

- [ ] **Step 1: Test a clean environment**

Move any existing `.venv` aside using a temporary path, create a new virtual environment, install `requirements.txt`, and run `python generate_assets.py`. Compare generated arrays and decoded audio to the checked-in artifacts with the Task 2 tests. Restore or retain the clean environment only after confirming setup succeeds.

- [ ] **Step 2: Run all automated tests**

Run:

```powershell
python -m pytest -q
```

Expected: exit code 0, no failures, and no unexpected warnings.

- [ ] **Step 3: Run the author attack from public artifacts only**

Run:

```powershell
python solution\solve.py
```

Expected: `solution/adversarial_call.wav` is distinct, within `0.018` RMS, and accepted above the stored threshold.

- [ ] **Step 4: Exercise the live HTTP flow**

Start the server without debug mode. Download all three evidence files over HTTP, run the solver against those downloaded copies, upload its output, and confirm the response reveals exactly `THM{confidence_is_not_identity}`. Upload the original and an over-budget candidate and confirm neither response contains a flag.

- [ ] **Step 5: Check browser accessibility and responsive behavior**

At desktop, 375px, and 320px widths, verify no horizontal overflow, readable evidence cards, visible upload results, and no clipped flag. Tab from the address bar through every link, file input, and button; verify the skip link and focus ring. Trigger rejection, validation error, connection error, and success states and confirm the live region announces each meaningful result.

- [ ] **Step 6: Measure peak memory**

Measure the Python process while generating assets, running the solver, and analyzing an upload. Record the highest working set in the ledger. Expected: each operation stays below 1 GiB. If generation exceeds the limit, reduce corpus size before changing model behavior or validation rules.

- [ ] **Step 7: Audit the delivered folder**

Run searches proving public artifacts contain neither flag, private paths, nor solution values; no route exposes source or solution files; no upload file remains after requests; and no obsolete help-desk state-machine files or cache directories are part of the deliverable.

- [ ] **Step 8: Record final completion**

Record exact test counts, generated model probability/threshold, reference solution probability/RMS delta, browser viewport results, and peak memory in the plan ledger. Keep the ledger because the workspace has no Git history.

---

## Execution notes

- Use TDD for every production behavior: write the focused test, observe the expected failure, implement the smallest behavior, then run the focused and cumulative suites.
- Never weaken the sample contract, threshold, or RMS limit merely to make the solver pass. Tune deterministic asset generation so the documented attack exists within the fixed rules.
- The model is intentionally simple and transparent. Do not add neural frameworks, audio playback, speech recognition, authentication, scoring, persistence, or multiple levels.
- Preserve the existing challenge folder name and default port so local links remain stable.
