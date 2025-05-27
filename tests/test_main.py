import tempfile
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest
from bs4 import BeautifulSoup

from src.main import (
    download_documents,
    extract_download_links,
    extract_tables_from_soup,
    main,
    save_html_content,
    save_tables_as_csv,
    scrape_website,
)

HTML_WITH_TABLE = """
<html>
  <body>
    <table>
      <tr><th>Col1</th><th>Col2</th></tr>
      <tr><td>A</td><td>1</td></tr>
      <tr><td>B</td><td>2</td></tr>
    </table>
  </body>
</html>
"""

HTML_WITH_LINKS = """
<html>
  <body>
    <a href="doc1.pdf">PDF 1</a>
    <a href="/files/doc2.pdf">PDF 2</a>
    <a href="not_a_doc.txt">Not a PDF</a>
  </body>
</html>
"""


@pytest.fixture
def mock_soup():
    """Create a mock BeautifulSoup object for testing.

    Returns:
        BeautifulSoup: A BeautifulSoup object with sample HTML content.
    """
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Hello World</h1>
            <p>This is a test page.</p>
        </body>
    </html>
    """
    return BeautifulSoup(html_content, "html.parser")


def test_scrape_website_success(monkeypatch):
    class MockResponse:
        def __init__(self, text):
            self.text = text

        def raise_for_status(self):
            pass

    monkeypatch.setattr("requests.get", lambda url, timeout: MockResponse(HTML_WITH_TABLE))
    soup = scrape_website("http://example.com")
    assert isinstance(soup, BeautifulSoup)
    assert soup.find("table") is not None


def test_scrape_website_failure(monkeypatch):
    class MockResponse:
        def raise_for_status(self):
            raise Exception("HTTP error")

    monkeypatch.setattr("requests.get", lambda url, timeout: MockResponse())
    with pytest.raises(Exception):
        scrape_website("http://badurl.com")


def test_extract_tables_from_soup():
    soup = BeautifulSoup(HTML_WITH_TABLE, "html.parser")
    dfs = extract_tables_from_soup(soup)
    assert len(dfs) == 1
    assert isinstance(dfs[0], pd.DataFrame)
    assert list(dfs[0].columns) == ["Col1", "Col2"]
    assert dfs[0].iloc[0, 0] == "A"


def test_extract_tables_from_soup_no_tables():
    soup = BeautifulSoup("<html><body>No tables here</body></html>", "html.parser")
    dfs = extract_tables_from_soup(soup)
    assert dfs == []


def test_extract_download_links_absolute_and_relative():
    soup = BeautifulSoup(HTML_WITH_LINKS, "html.parser")
    links = extract_download_links(soup, "http://example.com")
    assert "http://example.com/doc1.pdf" in links
    assert "http://example.com/files/doc2.pdf" in links
    assert all(link.endswith(".pdf") for link in links)
    assert len(links) == 2


def test_extract_download_links_custom_extension():
    soup = BeautifulSoup(HTML_WITH_LINKS, "html.parser")
    links = extract_download_links(soup, "http://example.com", extensions=[".txt"])
    assert links == ["http://example.com/not_a_doc.txt"]


def test_download_documents(tmp_path, monkeypatch):
    # Mock requests.get to return a fake file stream
    class MockResponse:
        def __init__(self):
            self.status_code = 200
            self.iter_content_called = False

        def raise_for_status(self):
            pass

        def iter_content(self, chunk_size=8192):
            self.iter_content_called = True
            yield b"testdata"

    monkeypatch.setattr("requests.get", lambda url, stream, timeout: MockResponse())
    links = ["http://example.com/doc1.pdf"]
    download_documents(links, str(tmp_path))
    files = list(tmp_path.iterdir())
    assert any(f.name == "doc1.pdf" for f in files)


def test_save_tables_as_csv(tmp_path):
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    save_tables_as_csv([df], str(tmp_path))
    files = list(tmp_path.iterdir())
    assert any(f.name.startswith("table_") and f.suffix == ".csv" for f in files)
    # Check CSV content
    csv_file = next(f for f in files if f.suffix == ".csv")
    loaded = pd.read_csv(csv_file)
    assert loaded.equals(df)


def test_save_html_content(mock_soup):
    """Test that the save_html_content function saves HTML content to a file.

    Args:
        mock_soup (BeautifulSoup): Mock BeautifulSoup object from fixture.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        save_html_content(mock_soup, temp_dir)

        # Check if the HTML file was created
        html_path = Path(temp_dir) / "scraped_content.html"
        assert html_path.exists(), "HTML file was not created"

        # Check if the content was correctly saved
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        import re

        # Accepts <title>Test Page</title> and <h1>Hello World</h1> with or without whitespace/newlines
        assert re.search(r"<title>\s*Test Page\s*</title>", content), "HTML content was not saved correctly"
        assert re.search(r"<h1>\s*Hello World\s*</h1>", content), "HTML content was not saved correctly"


@mock.patch("src.main.scrape_website")
@mock.patch("src.main.parse_args")
@mock.patch("src.main.save_html_content")
def test_main_always_saves_html_content(mock_save_html, mock_parse_args, mock_scrape_website, mock_soup):
    """Test that the main function always saves HTML content regardless of other parameters.

    Args:
        mock_save_html: Mock for save_html_content function.
        mock_parse_args: Mock for parse_args function.
        mock_scrape_website: Mock for scrape_website function.
        mock_soup (BeautifulSoup): Mock BeautifulSoup object from fixture.
    """
    # Setup mocks
    mock_args = mock.MagicMock()
    mock_args.url = "https://example.com"
    mock_args.output = "output_dir"
    mock_args.find_download_links = False
    mock_args.download_tables = False
    mock_args.download_documents = False

    mock_parse_args.return_value = mock_args
    mock_scrape_website.return_value = mock_soup

    # Call main function
    main()

    # Verify that save_html_content was called with the correct arguments
    mock_save_html.assert_called_once_with(mock_soup, mock_args.output)


@mock.patch("src.main.scrape_website")
@mock.patch("src.main.parse_args")
@mock.patch("src.main.save_html_content")
@mock.patch("src.main.extract_tables_from_soup")
@mock.patch("src.main.save_tables_as_csv")
def test_main_with_download_tables(
    mock_save_csv, mock_extract_tables, mock_save_html, mock_parse_args, mock_scrape_website, mock_soup
):
    """Test that the main function saves HTML content even when downloading tables.

    Args:
        mock_save_csv: Mock for save_tables_as_csv function.
        mock_extract_tables: Mock for extract_tables_from_soup function.
        mock_save_html: Mock for save_html_content function.
        mock_parse_args: Mock for parse_args function.
        mock_scrape_website: Mock for scrape_website function.
        mock_soup (BeautifulSoup): Mock BeautifulSoup object from fixture.
    """
    # Setup mocks
    mock_args = mock.MagicMock()
    mock_args.url = "https://example.com"
    mock_args.output = "output_dir"
    mock_args.find_download_links = False
    mock_args.download_tables = True  # Enable table downloading
    mock_args.download_documents = False

    mock_parse_args.return_value = mock_args
    mock_scrape_website.return_value = mock_soup
    mock_tables = [mock.MagicMock()]
    mock_extract_tables.return_value = mock_tables

    # Call main function
    main()

    # Verify that both save_html_content and save_tables_as_csv were called
    mock_save_html.assert_called_once_with(mock_soup, mock_args.output)
    mock_extract_tables.assert_called_once_with(mock_soup)
    mock_save_csv.assert_called_once_with(mock_tables, mock_args.output)


@pytest.mark.integration
def test_integration_save_html_content():
    """Integration test for saving HTML content to the output directory.

    This test creates a real BeautifulSoup object and saves it to a temporary directory.
    """
    html_content = "<html><body><h1>Integration Test</h1></body></html>"
    soup = BeautifulSoup(html_content, "html.parser")

    with tempfile.TemporaryDirectory() as temp_dir:
        save_html_content(soup, temp_dir)

        # Verify file was created and contains the right content
        html_path = Path(temp_dir) / "scraped_content.html"
        assert html_path.exists()

        with open(html_path, "r", encoding="utf-8") as f:
            saved_content = f.read()

        import re

        # Accepts <h1>Integration Test</h1> with or without whitespace/newlines
        assert re.search(r"<h1>\s*Integration Test\s*</h1>", saved_content)
