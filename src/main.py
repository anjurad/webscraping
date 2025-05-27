"""Main entry point for the webscraping utility.

This script allows users to scrape tables and documents from a specified website URL.
"""

import argparse
import logging
from io import StringIO
from logging.handlers import RotatingFileHandler
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup


class WebScrapingError(Exception):
    """Custom exception for webscraping errors."""

    pass


def configure_logging(log_dir: str, log_to_console: bool = False) -> None:
    """Configure logging to file (in the given directory) and optionally to console.

    Args:
        log_dir (str): Directory where the log file will be stored.
        log_to_console (bool): If True, also log to the console.
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    log_file = log_path / "webscraping.log"

    file_handler = RotatingFileHandler(log_file, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    handlers: list[logging.Handler] = [file_handler]
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    # Remove all existing handlers
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
    for h in handlers:
        root_logger.addHandler(h)


logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments including the URL to scrape.
    """
    parser = argparse.ArgumentParser(description="Scrape tables and documents from a website.")
    parser.add_argument(
        "url",
        type=str,
        help="The URL of the website to scrape.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Directory to save scraped data (default: output).",
    )
    parser.add_argument(
        "--find-download-links",
        action="store_true",
        default=False,
        help="Find and print download links for documents (default: False).",
    )
    parser.add_argument(
        "--download-tables",
        action="store_true",
        default=False,
        help="Extract and save tables as CSV files (default: False).",
    )
    parser.add_argument(
        "--download-documents",
        action="store_true",
        default=False,
        help="Download the found document links to the output directory (default: False).",
    )
    parser.add_argument(
        "--log-to-console",
        action="store_true",
        default=False,
        help="Also log to the console in addition to the log file.",
    )
    return parser.parse_args()


def scrape_website(url: str) -> BeautifulSoup:
    """Fetch and parse the HTML content of a website.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        BeautifulSoup: Parsed HTML content of the page.

    Raises:
        requests.RequestException: If the HTTP request fails.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error(f"Failed to fetch {url}: {exc}", exc_info=True)
        raise WebScrapingError(f"Failed to fetch {url}") from exc
    # Reason: Use 'html.parser' for built-in compatibility; can switch to 'lxml' if needed
    return BeautifulSoup(response.text, "html.parser")


def extract_tables_from_soup(soup: BeautifulSoup) -> list[pd.DataFrame]:
    """Extract all HTML tables from a BeautifulSoup object and convert them to pandas DataFrames.

    Args:
        soup (BeautifulSoup): Parsed HTML content.

    Returns:
        list[pd.DataFrame]: List of DataFrames, one for each table found.
    """
    tables = soup.find_all("table")
    dataframes: list[pd.DataFrame] = []
    for idx, table in enumerate(tables):
        try:
            html_str = str(table)
            dfs: list[pd.DataFrame] = pd.read_html(StringIO(html_str))
            if dfs and not dfs[0].empty:
                dataframes.append(dfs[0])
            else:
                logger.info(f"Table {idx + 1} is empty or could not be parsed.")
        except ValueError as exc:
            logger.warning(f"Skipping table {idx + 1}: {exc}")
            continue  # Reason: Skip tables that cannot be parsed by pandas
    return dataframes


def extract_download_links(soup: BeautifulSoup, base_url: str, extensions: list[str] | None = None) -> list[str]:
    """Extract download links for specified document types from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): Parsed HTML content.
        base_url (str): The base URL to resolve relative links.
        extensions (list[str] | None): List of file extensions to look for (e.g., ['.pdf']). Defaults to ['.pdf'].

    Returns:
        list[str]: List of absolute URLs to downloadable documents.
    """
    if extensions is None:
        extensions = [".pdf"]
    links: list[str] = []
    from bs4.element import Tag

    for a_tag in soup.find_all("a", href=True):
        if not isinstance(a_tag, Tag):
            continue
        href = a_tag.get("href")
        if not isinstance(href, str):
            continue
        if any(href.lower().endswith(ext) for ext in extensions):
            links.append(urljoin(base_url, href))
    return links


def download_documents(links: list[str], output_dir: str) -> None:
    """Download documents from the provided links to the specified output directory.

    Args:
        links (list[str]): List of document URLs to download.
        output_dir (str): Directory to save downloaded documents.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)  # Ensure output directory exists
    for url in links:
        try:
            filename = url.split("/")[-1]
            file_path = output_path / filename
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            logger.info(f"Downloaded: {filename}")
        except requests.RequestException as exc:
            logger.error(f"Failed to download {url}: {exc}", exc_info=True)
        except Exception as exc:
            logger.error(f"Unexpected error downloading {url}: {exc}", exc_info=True)


def save_tables_as_csv(tables: list[pd.DataFrame], output_dir: str) -> None:
    """Save a list of pandas DataFrames as CSV files in the specified directory.

    Args:
        tables (list[pd.DataFrame]): List of DataFrames to save.
        output_dir (str): Directory to save CSV files.
    """
    output_path = Path(output_dir)
    for idx, df in enumerate(tables):
        csv_path = output_path / f"table_{idx + 1}.csv"
        try:
            df.to_csv(csv_path, index=False)
            logger.info(f"Saved table {idx + 1} to {csv_path}")
        except Exception as exc:
            logger.error(f"Failed to save table {idx + 1} to {csv_path}: {exc}", exc_info=True)


def save_html_content(soup: BeautifulSoup, output_dir: str) -> None:
    """Save the BeautifulSoup HTML content to a file in the specified directory.

    Args:
        soup (BeautifulSoup): Parsed HTML content to save.
        output_dir (str): Directory to save the HTML file.
    """
    output_path = Path(output_dir)
    html_path = output_path / "scraped_content.html"

    prettified = soup.prettify()
    if not isinstance(prettified, str):
        prettified = str(prettified)
    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(prettified)
        logger.info(f"Saved HTML content to {html_path}")
    except Exception as exc:
        logger.error(f"Failed to save HTML content to {html_path}: {exc}", exc_info=True)


def main() -> None:
    """Main function to run the webscraping script."""
    args = parse_args()

    # Configure logging to use the output directory specified by the user and log-to-console flag
    configure_logging(args.output, log_to_console=args.log_to_console)
    logger.info("Webscraping utility is running.")
    logger.info(f"URL to scrape: {args.url}")
    logger.info(f"Output directory: {args.output}")

    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        soup = scrape_website(args.url)
    except WebScrapingError as exc:
        logger.error(f"Aborting: {exc}")
        return

    # Always save the HTML content
    save_html_content(soup, args.output)

    # Extract and save tables if requested
    if args.download_tables:
        tables = extract_tables_from_soup(soup)
        save_tables_as_csv(tables, args.output)

    # Find and print download links if requested
    download_links: list[str] = []
    if args.find_download_links or args.download_documents:
        download_links = extract_download_links(soup, args.url)
        if args.find_download_links:
            logger.info("Found download links:")
            for link in download_links:
                logger.info(link)

    # Download documents if requested
    if args.download_documents and download_links:
        download_documents(download_links, args.output)

    # Note: For production workloads, consider using async libraries (e.g., httpx, aiofiles) for I/O-bound operations.


if __name__ == "__main__":
    main()
