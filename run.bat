@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 goto python_missing

python "%~dp0local_portal.py"
exit /b %errorlevel%

:python_missing
echo Python 3 is required and must be available on PATH.
pause
exit /b 1
