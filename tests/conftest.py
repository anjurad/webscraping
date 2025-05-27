"""Configuration file for pytest.

This module contains shared fixtures and configuration settings for pytest.
"""

import sys
from pathlib import Path

import pytest

# Add the src directory to the path so we can import modules
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)


@pytest.fixture
def sample_html() -> str:
    """Provide a sample HTML content for testing.

    Returns:
        str: A simple HTML document for testing scraping functions
    """
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Hello World</h1>
            <p class="content">This is a test paragraph.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
                <li>Item 3</li>
            </ul>
        </body>
    </html>
    """


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test output files.

    Args:
        tmp_path: Built-in pytest fixture that provides a temporary directory

    Returns:
        Path: Path to the temporary output directory
    """
    return tmp_path / "output"
