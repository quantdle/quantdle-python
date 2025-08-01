#!/usr/bin/env bash
poetry run pytest tests/ --cov=quantdle --cov-report=term-missing --cov-report=html --cov-report=xml "$@"