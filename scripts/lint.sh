#!/usr/bin/env bash
echo "Running $(poetry run mypy --version)..."
poetry run mypy quantdle/ --exclude examples --exclude tests