# Sigma Tech Author Solution

> **AUTHOR ONLY — do not publish this file with player-facing challenge materials.** Flask does not serve this document.

The baseline badge is classified as `EMPLOYEE`; the target class in `data/model.json` is `VISITOR`. Coefficients use row-major order, so each flat feature index is `row * 32 + column`. Compare the target and baseline class coefficient rows, then account for the direction of each binary pixel toggle.

For the generated model, change these two pixels from `0` (black) to `1` (white):

- Row 9, column 22
- Row 6, column 22

Coordinates are zero-based. These edits make the shared classifier predict `VISITOR`, within the five-pixel limit.

From the `Sigma-Tech` folder, verify the solution with:

```powershell
.\.venv\Scripts\python.exe solve.py
```

Expected result: `Target prediction: VISITOR` and the two coordinates above. The solver intentionally does not print the flag; submit its candidate through the page to exercise the server-side flag gate.
