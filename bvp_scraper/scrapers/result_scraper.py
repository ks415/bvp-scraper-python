"""
Result scraper for race results and payouts.
"""

from datetime import date, datetime
from typing import Any, Dict, Union

from ..base_scraper import BaseScraper


class ResultScraper(BaseScraper):
    """Scraper for race results and payout information."""

    def scrape(
        self,
        race_date: Union[date, datetime, str],
        race_stadium_number: int,
        race_number: int,
    ) -> Dict[str, Any]:
        """
        Scrape race results and payouts.

        Args:
            race_date: Race date
            race_stadium_number: Stadium number (1-24)
            race_number: Race number (1-12)

        Returns:
            Dictionary containing race results
        """
        parsed_date = self._parse_date(race_date)

        url = (
            f"{self.base_url}/owpc/pc/race/raceresult"
            f"?hd={parsed_date.strftime('%Y%m%d')}"
            f"&jcd={race_stadium_number:02d}"
            f"&rno={race_number}"
        )

        soup = self.request_and_parse(url)

        # Determine base level
        self.base_level = 0
        level_element = soup.select_one(
            "body main div div div div:nth-child(2) div:nth-child(3) ul li"
        )
        if level_element:
            self.base_level = 1

        response = {
            "race_date": parsed_date.strftime("%Y-%m-%d"),
            "race_stadium_number": race_stadium_number,
            "race_number": race_number,
        }

        # Scrape race results
        result_data = self._scrape_race_result(soup)
        response.update(result_data)

        # Scrape payouts
        payout_data = self._scrape_payouts(soup)
        response.update(payout_data)

        # Scrape race info (決まり手, etc.)
        race_info_data = self._scrape_race_info(soup)
        response.update(race_info_data)

        return response

    def _scrape_race_result(self, soup) -> Dict[str, Any]:
        """Scrape race finishing order and times."""

        results = {}

        # Look for the result table with class 'is-w495'
        result_table = None
        tables = soup.find_all("table", class_="is-w495")

        # Find the table with race results (has header row with '着', '枠', 'ボートレーサー', 'レースタイム')
        for table in tables:
            rows = table.find_all("tr")
            if rows and len(rows) > 1:
                header_cells = rows[0].find_all(["th", "td"])
                header_text = [cell.get_text(strip=True) for cell in header_cells]
                if (
                    "着" in header_text
                    and "ボートレーサー" in header_text
                    and "レースタイム" in header_text
                ):
                    result_table = table
                    break

        if result_table:
            rows = result_table.find_all("tr")[1:]  # Skip header row

            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 4:
                    # Extract data from cells
                    position_text = cells[0].get_text(strip=True)
                    boat_number_text = cells[1].get_text(strip=True)
                    racer_name_text = cells[2].get_text(strip=True)
                    race_time_text = cells[3].get_text(strip=True)

                    # Convert position to integer
                    try:
                        # Handle Japanese numerals
                        position_map = {
                            "１": 1,
                            "２": 2,
                            "３": 3,
                            "４": 4,
                            "５": 5,
                            "６": 6,
                        }
                        position = position_map.get(position_text, int(position_text))
                    except (ValueError, KeyError):
                        continue

                    # Extract boat number
                    boat_number = None
                    try:
                        boat_number = int(boat_number_text)
                    except ValueError:
                        pass

                    # Clean racer name (remove extra whitespace)
                    racer_name = None
                    if racer_name_text:
                        # Extract racer number and name from format like "3771折下\u3000\u3000寛法"
                        import re

                        match = re.match(
                            r"(\d+)([ぁ-んァ-ン一-龯\u3000\s]+)", racer_name_text
                        )
                        if match:
                            name_part = match.group(2)
                            # Clean up the name part (remove extra spaces/unicode spaces)
                            racer_name = re.sub(r"[\u3000\s]+", " ", name_part).strip()

                    # Clean race time
                    race_time = None
                    if race_time_text and race_time_text != "[empty]":
                        race_time = race_time_text

                    results[position] = {
                        "position": position,
                        "boat_number": boat_number,
                        "racer_name": racer_name,
                        "race_time": race_time,
                    }

        return {"results": results}

    def _scrape_payouts(self, soup) -> Dict[str, Any]:
        """Scrape payout information for all bet types."""

        payouts = {
            "win_payouts": {},
            "place_payouts": {},
            "exacta_payouts": {},
            "quinella_payouts": {},
            "quinella_place_payouts": {},
            "trifecta_payouts": {},
            "trio_payouts": {},
        }

        # Look for the payout table with class 'is-w495'
        payout_table = None
        tables = soup.find_all("table", class_="is-w495")

        # Find the table with payout results (has header row with '勝式', '組番', '払戻金', '人気')
        for table in tables:
            rows = table.find_all("tr")
            if rows and len(rows) > 1:
                header_cells = rows[0].find_all(["th", "td"])
                header_text = [cell.get_text(strip=True) for cell in header_cells]
                if "勝式" in header_text and "払戻金" in header_text:
                    payout_table = table
                    break

        if payout_table:
            rows = payout_table.find_all("tr")[1:]  # Skip header row

            current_bet_type = None

            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 3:
                    bet_type_text = cells[0].get_text(strip=True)
                    combination_text = cells[1].get_text(strip=True)
                    payout_text = cells[2].get_text(strip=True)
                    popularity_text = (
                        cells[3].get_text(strip=True) if len(cells) > 3 else ""
                    )

                    # Update current bet type if not empty
                    if bet_type_text and bet_type_text != "[empty]":
                        current_bet_type = bet_type_text

                    # Skip empty rows
                    if (
                        combination_text == "[empty]"
                        or not combination_text
                        or payout_text == "[empty]"
                        or not payout_text
                    ):
                        continue

                    # Extract payout amount
                    payout_amount = None
                    if payout_text.startswith("¥"):
                        try:
                            # Remove ¥ and commas, convert to integer
                            amount_str = payout_text[1:].replace(",", "")
                            payout_amount = int(amount_str)
                        except ValueError:
                            pass

                    # Extract popularity
                    popularity = None
                    if popularity_text and popularity_text != "[empty]":
                        try:
                            popularity = int(popularity_text)
                        except ValueError:
                            pass

                    # Map to appropriate payout category
                    if current_bet_type and combination_text and payout_amount:
                        payout_data = {
                            "combination": combination_text,
                            "payout": payout_amount,
                            "popularity": popularity,
                        }

                        if current_bet_type == "3連単":
                            payouts["trifecta_payouts"][combination_text] = payout_data
                        elif current_bet_type == "3連複":
                            payouts["trio_payouts"][combination_text] = payout_data
                        elif current_bet_type == "2連単":
                            payouts["exacta_payouts"][combination_text] = payout_data
                        elif current_bet_type == "2連複":
                            payouts["quinella_payouts"][combination_text] = payout_data
                        elif current_bet_type == "拡連複":
                            payouts["quinella_place_payouts"][combination_text] = (
                                payout_data
                            )
                        elif current_bet_type == "単勝":
                            payouts["win_payouts"][combination_text] = payout_data
                        elif current_bet_type == "複勝":
                            payouts["place_payouts"][combination_text] = payout_data

        return payouts

    def _scrape_race_info(self, soup) -> Dict[str, Any]:
        """Scrape additional race information like 決まり手 (winning technique)."""

        race_info = {}

        # Look for 決まり手 (winning technique) table
        kimari_te = None

        # Find table with 決まり手
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) >= 2:
                # Check if first row contains '決まり手'
                first_row_text = rows[0].get_text(strip=True)
                if "決まり手" in first_row_text:
                    # Get the value from the second row
                    if len(rows) > 1:
                        second_row_cells = rows[1].find_all(["td", "th"])
                        if second_row_cells:
                            kimari_te_text = second_row_cells[0].get_text(strip=True)
                            if kimari_te_text and kimari_te_text != "[empty]":
                                kimari_te = kimari_te_text
                    break

        if kimari_te:
            race_info["winning_technique"] = kimari_te

        # Look for スタート情報 (start information) if available
        start_info = {}

        # Find table with start information (contains timing data)
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) >= 2:
                first_row_text = rows[0].get_text(strip=True)
                if "スタート情報" in first_row_text:
                    # Extract start timing for each boat
                    for i, row in enumerate(rows[1:], 1):  # Skip header row
                        if i <= 6:  # Max 6 boats
                            cells = row.find_all(["td", "th"])
                            if cells:
                                timing_text = cells[0].get_text(strip=True)
                                # Extract timing and any special info
                                if timing_text and timing_text != "[empty]":
                                    # Parse timing (e.g., "1.23" or "3.18 抜き")
                                    timing_parts = timing_text.split()
                                    timing = (
                                        timing_parts[0] if timing_parts else timing_text
                                    )
                                    special_info = (
                                        " ".join(timing_parts[1:])
                                        if len(timing_parts) > 1
                                        else None
                                    )

                                    start_info[i] = {
                                        "timing": timing,
                                        "special_info": special_info,
                                    }
                    break

        if start_info:
            race_info["start_info"] = start_info

        return race_info
