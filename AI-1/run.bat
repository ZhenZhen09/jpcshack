@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    if errorlevel 1 goto error
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto error
)

".venv\Scripts\python.exe" app.py
pause
goto end

:error
echo Setup failed. Check that Python 3 is installed and available on PATH.
pause

:end
