@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    if errorlevel 1 goto setup_failed
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto setup_failed
)
".venv\Scripts\python.exe" server.py
pause
exit /b

:setup_failed
echo Setup failed. Check that Python and network access are available, then try again.
pause
exit /b 1
