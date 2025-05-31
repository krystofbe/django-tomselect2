# Modern task runner (alternative to Makefile)
default:
    @just --list

# Development setup
setup:
    uv sync --extra dev
    uv run pre-commit install

# Run all checks
check:
    uv run ruff check .
    uv run ruff format --check .

# Fix formatting
fix:
    uv run ruff check --fix .
    uv run ruff format .

# Run tests
test:
    uv run pytest

# Run tests with coverage
test-cov:
    uv run pytest --cov=django_tomselect2 --cov-report=html

# Build package
build:
    uv build

# Serve docs locally
docs:
    uv run sphinx-autobuild docs docs/_build
