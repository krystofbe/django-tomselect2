# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

django-tomselect2 is a Django integration library for TomSelect, a jQuery-based replacement for select boxes. It provides autocomplete widgets and form fields with three main widget types:

- **Light widgets**: For small option sets, all pre-rendered in HTML
- **Heavy widgets**: For large option sets requiring Ajax queries
- **Model widgets**: Specialized Heavy widgets with built-in Ajax handling

## Development Commands

### Setup
```bash
# Install dependencies and setup development environment
uv sync --extra dev
uv run pre-commit install
```

### Code Quality
```bash
# Check code formatting and linting
uv run ruff check .
uv run ruff format --check .

# Auto-fix formatting and linting issues
uv run ruff check --fix .
uv run ruff format .
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage report
uv run pytest --cov=django_tomselect2 --cov-report=html

# Run specific test markers
uv run pytest -m "not slow"           # Skip slow tests
uv run pytest -m integration         # Run only integration tests
uv run pytest -m playwright          # Run only browser automation tests
```

### Building and Documentation
```bash
# Build the package
uv build

# Serve documentation locally with auto-reload
uv run sphinx-autobuild docs docs/_build
```

### Alternative Task Runner (Just)
The project includes a `justfile` for common tasks:
```bash
just setup      # Development setup
just check      # Run all checks
just fix        # Fix formatting
just test       # Run tests
just test-cov   # Run tests with coverage
just build      # Build package
just docs       # Serve docs locally
```

## Architecture

### Core Components

- **`forms.py`**: Main widget implementations (Light, Heavy, Model widgets)
- **`views.py`**: Ajax response views for Heavy/Model widgets
- **`conf.py`**: Configuration management using django-appconf
- **`cache.py`**: Caching utilities for widget data
- **`urls.py`**: URL patterns for Ajax endpoints

### Widget Architecture

The library implements a three-tier widget system:

1. **Light widgets**: Direct HTML rendering, suitable for <100 options
2. **Heavy widgets**: Ajax-powered, requires custom view implementation
3. **Model widgets**: Self-registering Ajax widgets with built-in queryset handling

### Static Assets

- **`static/django_tomselect2/`**: Contains TomSelect JavaScript and CSS files
- Widgets automatically include necessary static files

### Test Structure

- **`tests/`**: Main test directory
- **`tests/testapp/`**: Django test application
- **`tests/conftest.py`**: Pytest configuration and fixtures
- Browser automation tests use Playwright

### Example Application

- **`example/`**: Full Django application demonstrating widget usage
- Contains models, forms, and views showing different widget implementations
- SQLite database included for quick testing

## Key Configuration

- Uses modern Python tooling: `uv` for dependency management, `ruff` for linting/formatting
- Supports Django 4.2+ and Python 3.10+
- Pre-commit hooks enforce code quality
- Comprehensive test coverage with pytest and playwright for browser testing

## Development Notes

- Widget registration happens automatically for Model widgets
- Heavy widgets require implementing custom Ajax views
- The library maintains backward compatibility with django-select2 patterns
- Uses django-appconf for configuration management with `TOMSELECT2_` prefix
