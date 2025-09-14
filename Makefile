.PHONY: install test lint format type-check clean build

# Install dependencies
install:
	uv sync --dev

# Run tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run pytest --cov=bvp_scraper --cov-report=html --cov-report=term

# Lint and type check code
lint:
	uv run ruff check bvp_scraper tests examples

# Format code
format:
	uv run ruff format bvp_scraper tests examples

# Fix linting issues automatically
lint-fix:
	uv run ruff check bvp_scraper tests examples --fix

# Type checking (using ruff)
type-check:
	uv run ruff check bvp_scraper tests examples --select=TCH

# Run all quality checks
check: lint type-check test

# Clean build artifacts
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	uv build

# Install in development mode
dev-install:
	uv pip install -e .

# Run examples
example-basic:
	uv run python examples/basic_usage.py

example-advanced:
	uv run python examples/advanced_usage.py

# Help
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Lint and type check code"
	@echo "  lint-fix     - Fix linting issues automatically"
	@echo "  format       - Format code"
	@echo "  type-check   - Run type checking"
	@echo "  check        - Run all quality checks"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  dev-install  - Install in development mode"
	@echo "  example-*    - Run example scripts"
