@echo off
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 goto python_missing

if not exist ".venv\Scripts\python.exe" (
  echo Creating a local Python environment...
  python -m venv .venv
  if errorlevel 1 goto venv_failed
)

echo Starting Dolos Lab at http://127.0.0.1:8100/
echo Press Ctrl+C to stop the challenge.
.venv\Scripts\python.exe server.py
if errorlevel 1 goto launch_failed
goto done

:python_missing
echo Python 3 is required. Install Python and make sure it is available on PATH.
goto done

:launch_failed
echo Dolos Lab could not start. Check that port 8100 is available and try again.
goto done

:venv_failed
echo Could not create the local Python environment. Check your Python installation.

:done
pause
