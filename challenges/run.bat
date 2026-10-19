@echo off
cd /d "%~dp0"
python -u server.py
if defined CTF_LAUNCHED_BY_PORTAL exit /b
pause
