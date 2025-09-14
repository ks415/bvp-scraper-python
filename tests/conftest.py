"""
Test configuration and fixtures.
"""

import pytest
import requests_mock
from datetime import date


@pytest.fixture
def mock_session():
    """Provide a mock requests session."""
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def test_date():
    """Provide a test date."""
    return date(2024, 1, 1)


@pytest.fixture
def sample_html():
    """Provide sample HTML for testing."""
    return """
    <html>
        <body>
            <main>
                <div>
                    <div>
                        <div>
                            <div>
                                <div>
                                    <div>
                                        <h2>Test Race</h2>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </body>
    </html>
    """