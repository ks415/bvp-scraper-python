"""
Stadium scraper for venue information and race schedules.
"""

from datetime import date, datetime
from typing import Any, Dict, Union

from ..base_scraper import BaseScraper


class StadiumScraper(BaseScraper):
    """Scraper for stadium information and race schedules."""

    def scrape(
        self,
        race_date: Union[date, datetime, str],
        race_stadium_number: int = 0,
        race_number: int = 0,
    ) -> Dict[str, Any]:
        """
        Scrape stadium information for a specific date.

        Args:
            race_date: Race date
            race_stadium_number: Not used for stadium scraping
            race_number: Not used for stadium scraping

        Returns:
            Dictionary containing stadium information
        """
        parsed_date = self._parse_date(race_date)

        url = (
            f"{self.base_url}/owpc/pc/race/index"
            f"?hd={parsed_date.strftime('%Y%m%d')}"
        )

        soup = self.request_and_parse(url)

        stadiums = {}

        # Extract stadium information
        stadium_elements = soup.select("body main div div div div:nth-child(2) div div")

        for element in stadium_elements:
            stadium_data = self._extract_stadium_data(element)
            if stadium_data:
                stadium_number = stadium_data["stadium_number"]
                stadiums[stadium_number] = stadium_data

        return stadiums

    def _extract_stadium_data(self, element) -> Dict[str, Any]:
        """Extract data for a single stadium."""

        # Extract stadium number from link or data attributes
        stadium_link = element.select_one("a")
        if not stadium_link:
            return None

        href = stadium_link.get("href", "")

        # Extract stadium number from URL pattern
        import re

        stadium_match = re.search(r"jcd=(\d+)", href)
        if not stadium_match:
            return None

        stadium_number = int(stadium_match.group(1))

        # Extract stadium name
        stadium_name = self.filter_xpath_text(element, "h3")

        # Extract grade information
        grade_element = element.select_one(".grade")
        grade = grade_element.get_text(strip=True) if grade_element else None

        return {
            "stadium_number": stadium_number,
            "stadium_name": stadium_name,
            "grade": grade,
        }
