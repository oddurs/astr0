# Starward Development Makefile
# ==============================

.PHONY: help install test test-cov test-allure allure-serve allure-report lint typecheck clean

help:
	@echo "Starward Development Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install package with dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run tests (default)"
	@echo "  make test-cov      Run tests with coverage report"
	@echo "  make test-allure   Run tests and clean allure results"
	@echo ""
	@echo "Allure Reports:"
	@echo "  make allure-serve  Start Allure server to view results"
	@echo "  make allure-report Generate static HTML report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          Run ruff linter"
	@echo "  make typecheck     Run mypy type checker"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         Remove build artifacts and caches"

# Setup
install:
	pip install -e ".[dev]"

# Testing
test:
	pytest

test-cov:
	pytest --cov --cov-report=term-missing

test-allure:
	pytest --clean-alluredir

# Allure Reports (requires Allure CLI: brew install allure)
allure-serve:
	allure serve allure-results

allure-report:
	allure generate allure-results -o allure-report --clean
	@echo ""
	@echo "Report generated: allure-report/index.html"

# Code Quality
lint:
	ruff check src/ tests/

typecheck:
	mypy src/

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf allure-results/
	rm -rf allure-report/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
