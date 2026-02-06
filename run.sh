#!/usr/bin/env bash
set -e
export PYTHONUNBUFFERED=1
export TZ="Europe/Amsterdam"
source .venv/bin/activate
echo "Stoic Daily Bot — разработано aggel008"
python main.py
