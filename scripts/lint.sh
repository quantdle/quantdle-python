#!/usr/bin/env bash
echo "Running $(python3 -m poetry run mypy --version)..."
python3 -m poetry run mypy .