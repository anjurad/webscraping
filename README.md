# Webscraping Project

Repository: [https://github.com/anjurad/webscraping/](https://github.com/anjurad/webscraping/)

A Python 3.11+ command-line tool for scraping tables and downloadable documents (e.g., PDFs) from a specified website URL.

## Features

- Extracts all HTML tables from a web page and saves them as CSV files.
- Finds and prints download links for documents (default: `.pdf`).
- Downloads found documents to a local directory.
- Simple CLI interface with configurable options.
- Uses `pandas`, `requests`, and `BeautifulSoup` for robust scraping.
- Type-annotated and formatted with Ruff; includes Google-style docstrings.

## Requirements

- Python 3.11+
- [UV](https://github.com/astral-sh/uv) for dependency management and virtual environments (recommended)
- [Ruff](https://docs.astral.sh/ruff/) for formatting/linting (optional, for development)
- See `requirements.txt` for dependencies.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Command-line Arguments](#command-line-arguments)
- [Logging](#logging)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Overview

A Python 3.11+ command-line tool for scraping tables and downloadable documents (e.g., PDFs) from a specified website URL.

## Installation

### Using UV (Recommended)

```bash
# Clone the repository
git clone https://github.com/anjurad/webscraping/
cd webscraping

# Create and activate a virtual environment with UV
uv venv .venv
source .venv/bin/activate

# Install dependencies (from requirements.txt or pyproject.toml)
uv pip install -r requirements.txt
```

### Alternative: pip

If UV is unavailable, you can use pip:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py <url> [--output OUTPUT_DIR] [--find-download-links] [--download-tables] [--download-documents] [--logging-level LOGGING_LEVEL]
```

## Command-line Arguments

The script accepts the following arguments:

- `url` (positional, required): The URL of the website to scrape.
- `--output` (optional, default: `output`): Directory to save scraped data.
- `--find-download-links` (flag, optional): Find and print download links for documents (default: False).
- `--download-tables` (flag, optional): Extract and save tables as CSV files (default: False).
- `--download-documents` (flag, optional): Download the found document links to the output directory (default: False).
- `--log-to-console` (flag, optional): Also log to the console in addition to the log file.

Example usage:
```bash
python src/main.py "https://example.com" --output results --download-tables --find-download-links --log-to-console
```

## Logging

Logging is configurable via the `--log-to-console` argument. By default, logs are written to `webscraping.log` in the output directory. Use `--log-to-console` to also print logs to the console.

## Testing

- Tests should be placed under `/tests` and use `pytest`.
- Mock network calls for unit tests; do not hit live websites.
- Code coverage is enforced at ≥90% (see `pyproject.toml`).

## Contributing

Contributions are welcome! Please fork the repository at [https://github.com/anjurad/webscraping/](https://github.com/anjurad/webscraping/) and submit a pull request.

- Format code with [Ruff](https://docs.astral.sh/ruff/) using `ruff format`.
- Lint and sort imports with `ruff check`.
- Keep line length ≤ 120 chars.
- Follow Google-style docstrings for public functions, classes, and modules.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
