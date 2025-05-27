# Webscraping Utility

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

## Installation

### Using UV (Recommended)

```bash
# Clone the repository
git clone <repo-url>
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
python src/main.py <url> [--output OUTPUT_DIR] [--find-download-links] [--download-tables] [--download-documents]
```

### Arguments

- `<url>`: The URL of the website to scrape (required).
- `--output`: Directory to save scraped data (default: `output`).
- `--find-download-links`: Print found document download links.
- `--download-tables`: Extract and save tables as CSV files.
- `--download-documents`: Download found documents to the output directory.

### Example

```bash
python src/main.py "https://example.com/page" --download-tables --find-download-links --download-documents
```

## Logging Configuration

By default, logs are written to `output/webscraping.log` with rotation (max 2MB, 3 backups).

To also log to the console, change the following line in `src/main.py`:

```
configure_logging(log_to_console=False)
```

to

```
configure_logging(log_to_console=True)
```

This will enable logging to both the file and the console.

## Testing

- Tests should be placed under `/tests` and use `pytest`.
- Mock network calls for unit tests; do not hit live websites.
- Code coverage is enforced at ≥90% (see `pyproject.toml`).

## Development

- Format code with Ruff: `ruff format .`
- Lint and sort imports: `ruff check .`
- Keep modules < 400 LOC; split logic into packages under `/src` as needed.
- The package is PEP 561 typed (see `src/py.typed`).

## Repository Hygiene

- The `.gitignore` is configured to exclude Python cache, environment, test output, and the `output/` directory.
- All scraped content, including `scraped_content.html` and CSVs, is saved in the `output/` directory (not tracked by git).

## License

MIT License. See [LICENSE](LICENSE) for details.
