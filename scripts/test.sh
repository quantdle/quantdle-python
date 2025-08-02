#!/usr/bin/env bash

# Filter out the --release argument since pytest doesn't recognize it
args=()
for arg in "$@"; do
    if [[ "$arg" != "--release" ]]; then
        args+=("$arg")
    fi
done

poetry run pytest tests/ --cov=quantdle --cov-report=term-missing --cov-report=html --cov-report=xml "${args[@]}"