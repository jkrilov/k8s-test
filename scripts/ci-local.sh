#!/usr/bin/env bash
# Local CI test script

set -e

echo "Running local CI tests..."

echo "1. Installing dependencies..."
uv sync --all-extras --dev

echo "2. Running linting..."
uv run black --check src/ tests/
uv run isort --check-only src/ tests/

echo "3. Running tests..."
uv run pytest tests/ -v --cov=src

echo "4. Running security scan..."
uv run bandit -r src/ -s B104

echo "5. Testing Docker build..."
docker build -t k8s-test-app:latest .

echo "✅ All local CI tests passed!"
