"""
Program scraper for race programs and boat/racer information.
"""

import re
from datetime import date, datetime
from typing import Any, Dict, Optional, Union

from ..base_scraper import BaseScraper


class ProgramScraper(BaseScraper):
    """Scraper for race programs and participant information."""

    def scrape(
        self,
        race_date: Union[date, datetime, str],
        race_stadium_number: int,
        race_number: int,
    ) -> Dict[str, Any]:
        """
        Scrape race program data.

        Args:
            race_date: Race date
            race_stadium_number: Stadium number (1-24)
            race_number: Race number (1-12)

        Returns:
            Dictionary containing race program data
        """
        parsed_date = self._parse_date(race_date)

        # Build scraper URL
        url = (
            f"{self.base_url}/owpc/pc/race/racelist"
            f"?hd={parsed_date.strftime('%Y%m%d')}"
            f"&jcd={race_stadium_number:02d}"
            f"&rno={race_number}"
        )

        soup = self.request_and_parse(url)

        # Determine base level from page structure
        self.base_level = 0
        level_element = soup.select_one(
            "body main div div div div:nth-child(2) div:nth-child(3) ul li"
        )
        if level_element:
            self.base_level = 1

        # Extract race information
        race_data = self._scrape_race_info(
            soup, parsed_date, race_stadium_number, race_number
        )

        # Extract boat and racer information
        boats_data = self._scrape_boats(soup)

        response = {**race_data, **boats_data}
        return response

    def _scrape_race_info(
        self, soup, race_date: date, race_stadium_number: int, race_number: int
    ) -> Dict[str, Any]:
        """Extract basic race information."""

        # CSS selectors for race information
        race_grade_selector = (
            "body main div div div div:nth-child(1) div div:nth-child(2)"
        )
        race_title_selector = (
            "body main div div div div:nth-child(1) div div:nth-child(2) h2"
        )
        race_subtitle_distance_selector = f"body main div div div div:nth-child(2) div:nth-child({self.base_level + 3}) h3"
        race_deadline_selector = f"body main div div div div:nth-child(2) div:nth-child(2) table tbody tr:nth-child(1) td:nth-child({race_number + 1})"

        # Extract data
        race_grade_number = self.filter_xpath_for_grade_number(
            soup, race_grade_selector
        )
        race_title = self.filter_xpath_text(soup, race_title_selector)
        race_subtitle_distance = self.filter_xpath_text(
            soup, race_subtitle_distance_selector
        )
        race_deadline = self.filter_xpath_text(soup, race_deadline_selector)

        # Parse race closed time
        race_closed_at = None
        if race_deadline:
            try:
                from datetime import datetime

                deadline_time = datetime.strptime(race_deadline, "%H:%M").time()
                race_closed_at = datetime.combine(race_date, deadline_time).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            except ValueError:
                pass

        # Parse subtitle and distance
        race_subtitle, race_distance = self._parse_subtitle_distance(
            race_subtitle_distance
        )

        return {
            "race_date": race_date.strftime("%Y-%m-%d"),
            "race_stadium_number": race_stadium_number,
            "race_number": race_number,
            "race_closed_at": race_closed_at,
            "race_grade_number": race_grade_number,
            "race_title": race_title,
            "race_subtitle": race_subtitle,
            "race_distance": race_distance,
        }

    def _scrape_boats(self, soup) -> Dict[str, Any]:
        """Extract boat and racer information."""
        boats = {}

        # CSS selector templates for boat/racer data
        base_selector = f"body main div div div div:nth-child(2) div:nth-child({self.base_level + 5}) table"

        for boat_number in range(1, 7):  # Boats 1-6
            tbody_selector = f"{base_selector} tbody:nth-child({boat_number})"

            # Extract boat data
            boat_data = self._extract_boat_data(soup, tbody_selector, boat_number)
            if boat_data:
                boats[boat_number] = boat_data

        return {"boats": boats}

    def _extract_boat_data(
        self, soup, tbody_selector: str, default_boat_number: int
    ) -> Optional[Dict[str, Any]]:
        """Extract data for a single boat."""

        # Get the tbody element directly instead of using complex CSS selectors
        base_selector = f"body main div div div div:nth-child(2) div:nth-child({self.base_level + 5}) table"
        table = soup.select_one(base_selector)

        if not table:
            return None

        tbodies = table.find_all("tbody")
        if default_boat_number > len(tbodies):
            return None

        tbody = tbodies[default_boat_number - 1]  # 0-indexed
        rows = tbody.find_all("tr")

        if not rows:
            return None

        first_row = rows[0]
        cells = first_row.find_all("td")

        if len(cells) < 8:  # Minimum expected cells
            return None

        # Extract raw data directly from cells
        raw_data = {
            "boat_number": cells[0].get_text().strip() if len(cells) > 0 else None,
            "racer_info_cell": cells[2]
            if len(cells) > 2
            else None,  # Full racer info cell
            "racer_flying_late_start_timing": cells[3].get_text().strip()
            if len(cells) > 3
            else None,
            "racer_national_top123_percent": cells[4].get_text().strip()
            if len(cells) > 4
            else None,
            "racer_local_top123_percent": cells[5].get_text().strip()
            if len(cells) > 5
            else None,
            "racer_assigned_motor_number_top23_percent": cells[6].get_text().strip()
            if len(cells) > 6
            else None,
            "racer_assigned_boat_number_top23_percent": cells[7].get_text().strip()
            if len(cells) > 7
            else None,
        }

        # Extract detailed racer information from the racer info cell
        racer_name = None
        racer_number = None
        racer_class_number = None
        racer_branch_birthplace_age_weight = None

        if raw_data["racer_info_cell"]:
            divs = raw_data["racer_info_cell"].find_all("div")
            if len(divs) >= 3:
                # div[0]: レーサー番号とクラス
                number_class_text = divs[0].get_text().strip()
                if "/" in number_class_text:
                    parts = number_class_text.split("/")
                    racer_number = parts[0].strip()
                    racer_class_number = parts[1].strip()

                # div[1]: レーサー名
                racer_name = divs[1].get_text().strip()

                # div[2]: 支部/出身地、年齢、体重
                racer_branch_birthplace_age_weight = divs[2].get_text().strip()

        # Update raw_data with extracted information
        raw_data.update(
            {
                "racer_name": racer_name,
                "racer_number_class": f"{racer_number} {racer_class_number}"
                if racer_number and racer_class_number
                else None,
                "racer_branch_birthplace_age_weight": racer_branch_birthplace_age_weight,
            }
        )

        # Parse boat number
        boat_number = self._parse_int(raw_data["boat_number"]) or default_boat_number

        # Parse racer name
        racer_name = self._clean_racer_name(raw_data["racer_name"])

        # Parse number and class
        racer_number, racer_class_number = self._parse_number_class(
            raw_data["racer_number_class"]
        )

        # Parse branch, birthplace, age, weight
        (racer_branch_number, racer_birthplace_number, racer_age, racer_weight) = (
            self._parse_branch_birthplace_age_weight(
                raw_data["racer_branch_birthplace_age_weight"]
            )
        )

        # Parse flying, late, start timing
        (racer_flying_count, racer_late_count, racer_average_start_timing) = (
            self._parse_flying_late_start_timing(
                raw_data["racer_flying_late_start_timing"]
            )
        )

        # Parse national percentages
        (
            racer_national_top_1_percent,
            racer_national_top_2_percent,
            racer_national_top_3_percent,
        ) = self._parse_top123_percent(raw_data["racer_national_top123_percent"])

        # Parse local percentages
        (
            racer_local_top_1_percent,
            racer_local_top_2_percent,
            racer_local_top_3_percent,
        ) = self._parse_top123_percent(raw_data["racer_local_top123_percent"])

        # Parse motor data
        (
            racer_assigned_motor_number,
            racer_assigned_motor_top_2_percent,
            racer_assigned_motor_top_3_percent,
        ) = self._parse_assigned_motor_number_top23_percent(
            raw_data["racer_assigned_motor_number_top23_percent"]
        )

        # Parse boat data
        (
            racer_assigned_boat_number,
            racer_assigned_boat_top_2_percent,
            racer_assigned_boat_top_3_percent,
        ) = self._parse_assigned_boat_number_top23_percent(
            raw_data["racer_assigned_boat_number_top23_percent"]
        )

        return {
            "racer_boat_number": boat_number,
            "racer_name": racer_name,
            "racer_number": racer_number,
            "racer_class_number": racer_class_number,
            "racer_branch_number": racer_branch_number,
            "racer_birthplace_number": racer_birthplace_number,
            "racer_age": racer_age,
            "racer_weight": racer_weight,
            "racer_flying_count": racer_flying_count,
            "racer_late_count": racer_late_count,
            "racer_average_start_timing": racer_average_start_timing,
            "racer_national_top_1_percent": racer_national_top_1_percent,
            "racer_national_top_2_percent": racer_national_top_2_percent,
            "racer_national_top_3_percent": racer_national_top_3_percent,
            "racer_local_top_1_percent": racer_local_top_1_percent,
            "racer_local_top_2_percent": racer_local_top_2_percent,
            "racer_local_top_3_percent": racer_local_top_3_percent,
            "racer_assigned_motor_number": racer_assigned_motor_number,
            "racer_assigned_motor_top_2_percent": racer_assigned_motor_top_2_percent,
            "racer_assigned_motor_top_3_percent": racer_assigned_motor_top_3_percent,
            "racer_assigned_boat_number": racer_assigned_boat_number,
            "racer_assigned_boat_top_2_percent": racer_assigned_boat_top_2_percent,
            "racer_assigned_boat_top_3_percent": racer_assigned_boat_top_3_percent,
        }

    # Helper parsing methods
    def _parse_subtitle_distance(
        self, subtitle_distance: Optional[str]
    ) -> tuple[Optional[str], Optional[int]]:
        """Parse race subtitle and distance."""
        if not subtitle_distance:
            return None, None

        # Look for distance pattern (number + 'm')
        distance_match = re.search(r"(\d+)m", subtitle_distance)
        distance = int(distance_match.group(1)) if distance_match else None

        # Subtitle is everything except the distance part
        subtitle = re.sub(r"\s*\d+m\s*", "", subtitle_distance).strip()
        subtitle = subtitle if subtitle else None

        return subtitle, distance

    def _parse_int(self, value: Optional[str]) -> Optional[int]:
        """Parse integer value safely."""
        if not value:
            return None
        try:
            return int(re.sub(r"[^\d]", "", value))
        except (ValueError, TypeError):
            return None

    def _parse_float(self, value: Optional[str]) -> Optional[float]:
        """Parse float value safely."""
        if not value:
            return None
        try:
            return float(re.sub(r"[^\d.]", "", value))
        except (ValueError, TypeError):
            return None

    def _clean_racer_name(self, name: Optional[str]) -> Optional[str]:
        """Clean racer name."""
        return name.strip() if name else None

    def _parse_number_class(
        self, text: Optional[str]
    ) -> tuple[Optional[int], Optional[str]]:
        """Parse racer number and class."""
        if not text:
            return None, None

        # Extract number (usually at start)
        number_match = re.search(r"(\d+)", text)
        number = int(number_match.group(1)) if number_match else None

        # Extract class (A1, A2, B1, B2)
        class_match = re.search(r"([AB][12])", text)
        class_str = class_match.group(1) if class_match else None

        return number, class_str

    def _parse_branch_birthplace_age_weight(
        self, text: Optional[str]
    ) -> tuple[Optional[int], Optional[int], Optional[int], Optional[float]]:
        """Parse branch, birthplace, age, and weight from personal info text."""
        if not text:
            return None, None, None, None

        # Clean the text
        text = re.sub(r"\s+", " ", text.strip())

        # Extract branch and birthplace
        racer_branch_number = None
        racer_birthplace_number = None

        # Extract age
        racer_age = None
        age_match = re.search(r"(\d+)歳", text)
        if age_match:
            racer_age = int(age_match.group(1))

        # Extract weight
        racer_weight = None
        weight_match = re.search(r"(\d+\.?\d*)kg", text)
        if weight_match:
            racer_weight = float(weight_match.group(1))

        # TODO: Implement branch and birthplace number mapping if needed
        # For now, we'll return the text as-is for branch_birthplace
        # In a full implementation, you'd map prefecture names to numbers

        return racer_branch_number, racer_birthplace_number, racer_age, racer_weight

    def _parse_flying_late_start_timing(
        self, text: Optional[str]
    ) -> tuple[Optional[int], Optional[int], Optional[float]]:
        """Parse flying count, late count, and average start timing."""
        if not text:
            return None, None, None

        # Clean the text and split by lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        racer_flying_count = None
        racer_late_count = None
        racer_average_start_timing = None

        # Parse each line
        for line in lines:
            if line.startswith("F"):
                # Flying count
                flying_match = re.search(r"F(\d+)", line)
                if flying_match:
                    racer_flying_count = int(flying_match.group(1))
            elif line.startswith("L"):
                # Late count
                late_match = re.search(r"L(\d+)", line)
                if late_match:
                    racer_late_count = int(late_match.group(1))
            else:
                # Try to parse as start timing (decimal number)
                try:
                    timing = float(line)
                    racer_average_start_timing = timing
                except ValueError:
                    continue

        return racer_flying_count, racer_late_count, racer_average_start_timing

    def _parse_top123_percent(
        self, text: Optional[str]
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """Parse top 1, 2, 3 percentages."""
        if not text:
            return None, None, None

        # Clean the text and split by lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        percentages = []

        # Extract all decimal numbers from the lines
        for line in lines:
            try:
                percentage = float(line)
                percentages.append(percentage)
            except ValueError:
                continue

        # Ensure we have exactly 3 values, pad with None if needed
        while len(percentages) < 3:
            percentages.append(None)

        return tuple(percentages[:3])

    def _parse_assigned_motor_number_top23_percent(
        self, text: Optional[str]
    ) -> tuple[Optional[int], Optional[float], Optional[float]]:
        """Parse motor number and top 2, 3 percentages."""
        if not text:
            return None, None, None

        # Clean the text and split by lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        motor_number = None
        percentages = []

        for line in lines:
            # First line should be the motor number
            if motor_number is None:
                try:
                    motor_number = int(line)
                    continue
                except ValueError:
                    pass

            # Other lines should be percentages
            try:
                percentage = float(line)
                percentages.append(percentage)
            except ValueError:
                continue

        # Ensure we have exactly 2 percentages, pad with None if needed
        while len(percentages) < 2:
            percentages.append(None)

        top_2_percent = percentages[0] if len(percentages) > 0 else None
        top_3_percent = percentages[1] if len(percentages) > 1 else None

        return motor_number, top_2_percent, top_3_percent

    def _parse_assigned_boat_number_top23_percent(
        self, text: Optional[str]
    ) -> tuple[Optional[int], Optional[float], Optional[float]]:
        """Parse boat number and top 2, 3 percentages."""
        if not text:
            return None, None, None

        # Clean the text and split by lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        boat_number = None
        percentages = []

        for line in lines:
            # First line should be the boat number
            if boat_number is None:
                try:
                    boat_number = int(line)
                    continue
                except ValueError:
                    pass

            # Other lines should be percentages
            try:
                percentage = float(line)
                percentages.append(percentage)
            except ValueError:
                continue

        # Ensure we have exactly 2 percentages, pad with None if needed
        while len(percentages) < 2:
            percentages.append(None)

        top_2_percent = percentages[0] if len(percentages) > 0 else None
        top_3_percent = percentages[1] if len(percentages) > 1 else None

        return boat_number, top_2_percent, top_3_percent
