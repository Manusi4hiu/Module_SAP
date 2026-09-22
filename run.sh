#!/bin/bash
# Launcher script untuk SAP Simulator

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -q -r requirements.txt
fi

echo "Starting SAP Simulator..."
.venv/bin/python main.py
