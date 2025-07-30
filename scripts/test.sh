#!/usr/bin/env bash
python3 -m poetry run pytest tests/ --cov=quantdle --cov-report=term-missing --cov-report=html --cov-report=xml "$@"