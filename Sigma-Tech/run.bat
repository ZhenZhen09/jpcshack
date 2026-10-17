@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    if errorlevel 1 goto error
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto error
)

".venv\Scripts\python.exe" -m pip show Flask >nul 2>&1
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto error
)

".venv\Scripts\python.exe" -m pip show scikit-learn >nul 2>&1
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto error
)

if not exist "data\baseline.png" goto generate
if not exist "data\baseline.json" goto generate
if not exist "data\model.json" goto generate
goto launch

:generate
    ".venv\Scripts\python.exe" train_model.py
    if errorlevel 1 goto error

:launch

".venv\Scripts\python.exe" app.py
pause
goto end

:error
echo Setup failed. Check that Python 3 is installed and available on PATH.
pause

:end
