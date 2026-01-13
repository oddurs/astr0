# Starward Development Cheatsheet

Quick reference for common development commands.

## Pipenv Commands

```bash
# Install dependencies (first time setup)
pipenv install --dev

# Activate virtual environment
pipenv shell

# Run a command in the virtual environment (without activating)
pipenv run <command>

# Install a new package
pipenv install <package>

# Install a dev package
pipenv install --dev <package>

# Update all packages
pipenv update

# Show dependency graph
pipenv graph

# Check for security vulnerabilities
pipenv check

# Remove virtual environment
pipenv --rm

# Show path to virtual environment
pipenv --venv
```

## Running the CLI

```bash
# Inside pipenv shell
starward --help
starward time now
starward sun position
starward moon phase

# Without activating shell
pipenv run starward --help
```

## Testing

```bash
# Run all tests
pipenv run pytest

# Run with verbose output
pipenv run pytest -v

# Run with coverage report
pipenv run pytest --cov=starward

# Run coverage with HTML report
pipenv run pytest --cov=starward --cov-report=html

# Run specific test file
pipenv run pytest tests/core/test_sun.py

# Run specific test function
pipenv run pytest tests/core/test_sun.py::test_sun_position

# Run tests matching a keyword
pipenv run pytest -k "moon"

# Run tests excluding slow ones
pipenv run pytest -m "not slow"

# Show print statements during tests
pipenv run pytest -s
```

## Linting & Type Checking

```bash
# Run ruff linter
pipenv run ruff check src/

# Run ruff with auto-fix
pipenv run ruff check --fix src/

# Format code with ruff
pipenv run ruff format src/

# Run mypy type checker
pipenv run mypy src/starward/
```

## Development Install

```bash
# Install package in editable mode (already configured in Pipfile)
pipenv install -e .

# Or with pip directly
pip install -e ".[dev]"
```

## Git Shortcuts

```bash
# Check status
git status

# Create feature branch
git checkout -b feature/my-feature

# Stage all changes
git add .

# Commit with message
git commit -m "feat: add new feature"

# Push branch
git push -u origin feature/my-feature

# Pull latest changes
git pull origin master

# Rebase on master
git rebase master
```

## Common Starward CLI Examples

```bash
# Time
starward time now                          # Current time
starward time convert 2451545.0            # JD to calendar
starward time lst 2460000.5 -74.0          # Local sidereal time

# Sun
starward sun position                      # Current sun position
starward sun rise --lat 51.5 --lon -0.1    # Sunrise
starward sun set --lat 51.5 --lon -0.1     # Sunset

# Moon
starward moon phase                        # Current phase
starward moon next full                    # Next full moon

# Planets
starward planets position mars             # Mars position
starward planets all                       # All planets

# Coordinates
starward coord convert "18h36m56s +38d47m01s" galactic
starward angle sep "00h42m44s +41d16m09s" "01h33m51s +30d39m37s"

# Visibility
starward vis altitude "00h42m44s" "+41d16m09s" --lat 40.7 --lon -74.0

# Observer
starward observer add "Home" 40.7128 -74.0060
starward observer list

# Output formats
starward --json time now                   # JSON output
starward --verbose sun rise --lat 51.5 --lon -0.1  # Show work
```

## Command Shortcuts

| Full | Short |
|------|-------|
| `starward time` | `starward t` |
| `starward angle` | `starward a` |
| `starward coord` | `starward c` |
| `starward const` | `starward k` |
| `starward sun` | `starward s` |
| `starward moon` | `starward m` |
| `starward planets` | `starward p` |
| `starward observer` | `starward o` |
| `starward vis` | `starward v` |

## Useful One-Liners

```bash
# Run tests and linting in one go
pipenv run pytest && pipenv run ruff check src/ && pipenv run mypy src/starward/

# Quick test of a specific module
pipenv run pytest tests/core/test_sun.py -v

# Check what would be published
pipenv run python -m build --sdist

# See installed packages
pipenv run pip list
```
