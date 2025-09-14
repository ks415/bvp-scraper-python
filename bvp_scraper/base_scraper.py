"""
Base scraper class providing common functionality.
"""

import re
import time
from datetime import date, datetime
from typing import Any, Dict, Optional, Union

import requests
from bs4 import BeautifulSoup

from .interfaces import ScraperContractInterface


class BaseScraper(ScraperContractInterface):
    """Base scraper class with common HTTP and parsing functionality."""

    def __init__(self, session: Optional[requests.Session] = None):
        """
        Initialize base scraper.

        Args:
            session: Optional requests session for connection reuse
        """
        self.base_url = "https://www.boatrace.jp"
        self.base_level = 0
        self.seconds = 1  # Sleep duration between requests
        self.session = session or requests.Session()

        # Configure session with headers similar to browser
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

    def request_and_parse(self, url: str) -> BeautifulSoup:
        """
        Make HTTP request and parse HTML response.

        Args:
            url: URL to request

        Returns:
            BeautifulSoup object for parsing

        Raises:
            requests.RequestException: On HTTP errors
        """
        response = self.session.get(url)
        response.raise_for_status()
        time.sleep(self.seconds)

        return BeautifulSoup(response.content, "html.parser")

    def filter_xpath_text(
        self, soup: BeautifulSoup, css_selector: str
    ) -> Optional[str]:
        """
        Extract text content using CSS selector.

        Args:
            soup: BeautifulSoup object
            css_selector: CSS selector string

        Returns:
            Extracted and cleaned text or None
        """
        element = soup.select_one(css_selector)
        if element is None:
            return None

        text = element.get_text(strip=True)
        return self._clean_text(text) if text else None

    def filter_xpath_attr(
        self, soup: BeautifulSoup, css_selector: str, attr_name: str
    ) -> Optional[str]:
        """
        Extract attribute value using CSS selector.

        Args:
            soup: BeautifulSoup object
            css_selector: CSS selector string
            attr_name: Attribute name to extract

        Returns:
            Attribute value or None
        """
        element = soup.select_one(css_selector)
        if element is None:
            return None

        return element.get(attr_name)

    def filter_xpath_for_grade_number(
        self, soup: BeautifulSoup, css_selector: str
    ) -> Optional[int]:
        """
        Extract race grade number from CSS class.

        Args:
            soup: BeautifulSoup object
            css_selector: CSS selector string

        Returns:
            Grade number (1=SG, 2=G1, 3=G2, 4=G3, 5=一般) or None
        """
        class_attr = self.filter_xpath_attr(soup, css_selector, "class")
        if not class_attr:
            return None

        class_str = " ".join(class_attr) if isinstance(class_attr, list) else class_attr

        match = re.search(r"is-([a-zA-Z0-9]+)", class_str)
        if not match:
            return None

        grade_type = match.group(1)

        if grade_type == "ippan":
            return 5
        elif grade_type.startswith("SG"):
            return 1
        elif grade_type.startswith("G1"):
            return 2
        elif grade_type.startswith("G2"):
            return 3
        elif grade_type.startswith("G3"):
            return 4

        return None

    def filter_xpath_for_odds(
        self, soup: BeautifulSoup, css_selector: str
    ) -> Optional[float]:
        """
        Extract odds value as float.

        Args:
            soup: BeautifulSoup object
            css_selector: CSS selector string

        Returns:
            Odds value as float or None
        """
        text = self.filter_xpath_text(soup, css_selector)
        if not text:
            return None

        try:
            return float(text)
        except ValueError:
            return None

    def filter_xpath_for_odds_range(
        self, soup: BeautifulSoup, css_selector: str
    ) -> Dict[str, Optional[float]]:
        """
        Extract odds range (lower-upper format).

        Args:
            soup: BeautifulSoup object
            css_selector: CSS selector string

        Returns:
            Dictionary with 'lower_limit' and 'upper_limit' keys
        """
        text = self.filter_xpath_text(soup, css_selector)
        result = {"lower_limit": None, "upper_limit": None}

        if not text:
            return result

        if "-" in text:
            parts = text.split("-")
            if len(parts) == 2:
                try:
                    result["lower_limit"] = float(parts[0].strip())
                    result["upper_limit"] = float(parts[1].strip())
                except ValueError:
                    pass

        return result

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.

        Args:
            text: Raw text string

        Returns:
            Cleaned text string
        """
        if not text:
            return ""

        # Remove extra whitespace and normalize
        text = re.sub(r"\s+", " ", text.strip())

        # Convert full-width numbers to half-width
        text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))

        return text

    def _parse_date(self, date_input: Union[date, datetime, str]) -> date:
        """
        Parse various date input formats to date object.

        Args:
            date_input: Date in various formats

        Returns:
            date object
        """
        if isinstance(date_input, datetime):
            return date_input.date()
        elif isinstance(date_input, date):
            return date_input
        elif isinstance(date_input, str):
            # Try to parse string date
            from dateutil.parser import parse

            return parse(date_input).date()
        else:
            raise ValueError(f"Invalid date format: {date_input}")

    def scrape(
        self,
        race_date: Union[date, datetime, str],
        race_stadium_number: int,
        race_number: int,
    ) -> Dict[str, Any]:
        """
        Abstract method to be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement scrape method")
