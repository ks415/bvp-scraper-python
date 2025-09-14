"""
Tests for ProgramScraper class.
"""

from datetime import date
from unittest.mock import patch

from bvp_scraper.scrapers.program_scraper import ProgramScraper


class TestProgramScraper:
    """Test cases for ProgramScraper class."""

    def test_initialization(self):
        """Test ProgramScraper initialization."""
        scraper = ProgramScraper()
        assert isinstance(scraper, ProgramScraper)
        assert scraper.base_url == "https://www.boatrace.jp"

    def test_parse_subtitle_distance(self):
        """Test subtitle and distance parsing."""
        scraper = ProgramScraper()

        # Test with distance
        subtitle, distance = scraper._parse_subtitle_distance("一般戦 1800m")
        assert subtitle == "一般戦"
        assert distance == 1800

        # Test without distance
        subtitle, distance = scraper._parse_subtitle_distance("一般戦")
        assert subtitle == "一般戦"
        assert distance is None

        # Test with None
        subtitle, distance = scraper._parse_subtitle_distance(None)
        assert subtitle is None
        assert distance is None

    def test_parse_int(self):
        """Test integer parsing."""
        scraper = ProgramScraper()

        assert scraper._parse_int("123") == 123
        assert scraper._parse_int("1号艇") == 1
        assert scraper._parse_int("abc") is None
        assert scraper._parse_int(None) is None

    def test_parse_float(self):
        """Test float parsing."""
        scraper = ProgramScraper()

        assert scraper._parse_float("123.45") == 123.45
        assert scraper._parse_float("123.45kg") == 123.45
        assert scraper._parse_float("abc") is None
        assert scraper._parse_float(None) is None

    def test_parse_number_class(self):
        """Test racer number and class parsing."""
        scraper = ProgramScraper()

        number, class_str = scraper._parse_number_class("1234 A1")
        assert number == 1234
        assert class_str == "A1"

        number, class_str = scraper._parse_number_class("5678 B2")
        assert number == 5678
        assert class_str == "B2"

        number, class_str = scraper._parse_number_class(None)
        assert number is None
        assert class_str is None

    def test_parse_top123_percent(self):
        """Test top 1-2-3 percentage parsing."""
        scraper = ProgramScraper()

        # Test with three percentages
        top1, top2, top3 = scraper._parse_top123_percent("15.5% 25.3% 35.1%")
        assert top1 == 15.5
        assert top2 == 25.3
        assert top3 == 35.1

        # Test with two percentages
        top1, top2, top3 = scraper._parse_top123_percent("15.5% 25.3%")
        assert top1 == 15.5
        assert top2 == 25.3
        assert top3 is None

        # Test with None
        top1, top2, top3 = scraper._parse_top123_percent(None)
        assert top1 is None
        assert top2 is None
        assert top3 is None

    @patch.object(ProgramScraper, "request_and_parse")
    def test_scrape_basic(self, mock_request):
        """Test basic scraping functionality."""
        from bs4 import BeautifulSoup

        # Mock HTML response
        mock_html = """
        <html>
            <body>
                <main>
                    <div><div><div>
                        <div>
                            <div><div>
                                <h2>テストレース</h2>
                            </div></div>
                        </div>
                        <div>
                            <div></div>
                            <div>
                                <table>
                                    <tbody>
                                        <tr>
                                            <td>デッドライン</td>
                                            <td>12:00</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                            <div>
                                <h3>一般戦 1800m</h3>
                            </div>
                        </div>
                    </div></div>
                </main>
            </body>
        </html>
        """

        mock_request.return_value = BeautifulSoup(mock_html, "html.parser")

        scraper = ProgramScraper()
        result = scraper.scrape(date(2024, 1, 1), 1, 1)

        # Verify basic structure
        assert "race_date" in result
        assert "race_stadium_number" in result
        assert "race_number" in result
        assert result["race_date"] == "2024-01-01"
        assert result["race_stadium_number"] == 1
        assert result["race_number"] == 1

    def test_clean_racer_name(self):
        """Test racer name cleaning."""
        scraper = ProgramScraper()

        assert scraper._clean_racer_name("  田中太郎  ") == "田中太郎"
        assert scraper._clean_racer_name(None) is None
        assert scraper._clean_racer_name("") is None
