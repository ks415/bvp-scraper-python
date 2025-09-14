# BVP Scraper Python

A Python library for scraping boatrace official website data including programs, previews, odds, and results.

**This is a Python port of the original PHP library [bvp-scraper](https://github.com/shimomo/bvp-scraper) by shimomo.**

The original PHP implementation can be found at: https://github.com/shimomo/bvp-scraper

## Installation

### Using uv (recommended)

```bash
uv add bvp-scraper-python
```

### Using pip

```bash
pip install bvp-scraper-python
```

## Quick Start

```python
from bvp_scraper import Scraper

# Get race programs
programs = Scraper.scrape_programs('2024-01-01')

# Get odds for specific race
odds = Scraper.scrape_odds('2024-01-01', 1, 1)

# Get race results
results = Scraper.scrape_results('2024-01-01')
```

## Development Setup

### Using uv

```bash
# Clone the repository
git clone https://github.com/shimomo/bvp-scraper-python
cd bvp-scraper-python

# Install dependencies with uv
uv sync --dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=bvp_scraper

# Format and lint code
uv run ruff format .
uv run ruff check .

# Fix linting issues automatically
uv run ruff check . --fix
```

### Alternative: Using Makefile

```bash
# Install dependencies
make install

# Run tests
make test

# Run all quality checks
make check

# Build package
make build
```

## Usage

```python
from bvp_scraper import Scraper
from datetime import date

# Get race programs
programs = Scraper.scrape_programs('2024-01-01')

# Get odds for specific race
odds = Scraper.scrape_odds('2024-01-01', 1, 1)

# Get race results
results = Scraper.scrape_results('2024-01-01')
```

## Features

- **Program Scraping**: Get race programs with boat and racer information
- **Preview Scraping**: Get pre-race information and weather conditions
- **Odds Scraping**: Get all betting odds (Win, Place, Exacta, Quinella, etc.)
- **Result Scraping**: Get race results and payouts
- **Stadium Scraping**: Get stadium information

## PHP vs Python Comparison

This Python port maintains API compatibility with the original PHP library while leveraging Python-specific improvements:

| Feature               | Original PHP               | Python Port                         |
| --------------------- | -------------------------- | ----------------------------------- |
| **Core Architecture** | ✅ Same design patterns    | ✅ Maintained with Python idioms    |
| **API Methods**       | ✅ `scrapePrograms()` etc. | ✅ `scrape_programs()` (snake_case) |
| **Error Handling**    | ✅ Exception based         | ✅ Enhanced with type hints         |
| **HTTP Client**       | Symfony BrowserKit         | `requests` + `BeautifulSoup4`       |
| **Date Handling**     | Carbon                     | `datetime` + `dateutil`             |
| **Retry Logic**       | Custom implementation      | `tenacity` library                  |
| **Type Safety**       | PHP DocBlocks              | Python type hints                   |
| **Testing**           | PHPUnit                    | pytest                              |

## Equivalent Usage

**Original PHP:**

```php
use BVP\Scraper\Scraper;

$programs = Scraper::scrapePrograms('2024-01-01', 1, 1);
$odds = Scraper::scrapeOdds('2024-01-01', 1, 1);
```

**Python Port:**

```python
from bvp_scraper import Scraper

programs = Scraper.scrape_programs('2024-01-01', 1, 1)
odds = Scraper.scrape_odds('2024-01-01', 1, 1)
```

## Requirements

- Python 3.8.1+
- Dependencies managed via uv/pyproject.toml:
  - requests
  - beautifulsoup4
  - lxml
  - python-dateutil
  - tenacity

## License

MIT License
