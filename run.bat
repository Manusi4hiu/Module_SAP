@echo off
REM Windows launcher untuk SAP Simulator

cd /d "%~dp0"

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    .venv\Scripts\pip install -q -r requirements.txt
)

echo Starting SAP Simulator...
.venv\Scripts\python.exe main.py
