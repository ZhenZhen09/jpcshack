# Sigma Tech

Sigma Tech is a standalone adversarial image-classification CTF challenge. Investigate a suspicious lobby badge, inspect a small image classifier, and edit at most five pixels to change its prediction. The original synthetic images and model are generated locally; the app does not call Groq, an LLM, or any network service while it runs.

## Run on Windows

1. Install Python 3.11 or newer and make sure `python` works in Command Prompt.
2. Double-click `run.bat`. On first launch it creates `.venv`, installs the dependencies in `requirements.txt`, generates the model files if they are missing, and starts the local Flask server.
3. Open <http://127.0.0.1:5001>.
4. Stop the server with Ctrl+C in its console.

For a manual setup in PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python train_model.py
$env:PORT = "5001"
python app.py
```

The mock flag can be changed for a local session with `$env:SIGMA_TECH_FLAG = "flag{your_local_value}"` before launching the app. Keep a real competition flag in server-side environment configuration; do not put it in browser code or model artifacts.

## Player solve outline

1. Read the incident bulletin and note the fixed 32-by-32 binary image and five-pixel edit budget.
2. Download the starting PNG and inspect `sigma-tech-model.json`. The artifact gives the class labels, row-major pixel order, and per-class model coefficients.
3. Compare the classifier coefficients for the desired label with the current predicted label. Pixels with a large positive score change are useful candidates; account for whether toggling each pixel changes it from 0 to 1 or from 1 to 0.
4. Toggle candidate pixels in the editor. Watch the changed-pixel counter and submit the image to observe the classifier's predicted class and confidence.
5. Refine the edits until the model predicts the target class while the counter stays at five or fewer. A valid prediction reveals the local mock flag.

The exact successful edit coordinates are in the author-only `SOLUTION.md`. Flask does not serve that file.

## Author commands

Regenerate the deterministic data and model:

```powershell
.\.venv\Scripts\python.exe train_model.py
```

Find and print a valid solution without printing the flag:

```powershell
.\.venv\Scripts\python.exe solve.py
```

Run the challenge checks:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

The app listens on `127.0.0.1` in Flask's non-debug mode. No API key or runtime internet connection is required.
