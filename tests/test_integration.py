"""
Integration tests for the complete scraper functionality.
"""

from unittest.mock import Mock, patch

import pytest

from bvp_scraper import Scraper


class TestIntegration:
    """Integration tests for complete scraper functionality."""

    @pytest.mark.integration
    def test_scraper_initialization(self):
        """Test that scraper can be initialized and configured."""
        scraper = Scraper.get_instance()
        assert scraper is not None

        # Test that we can access scraper core
        assert hasattr(scraper, "_scraper_core")

        # Reset for clean state
        Scraper.reset_instance()

    @pytest.mark.integration
    @patch("bvp_scraper.scrapers.program_scraper.ProgramScraper.request_and_parse")
    def test_program_scraping_flow(self, mock_request):
        """Test complete program scraping flow."""
        from bs4 import BeautifulSoup

        # Mock response
        mock_html = """
        <html><body><main><div><div><div>
            <div><div><div><h2>Test Race</h2></div></div></div>
            <div><div></div><div><h3>一般戦 1800m</h3></div></div>
        </div></div></main></body></html>
        """
        mock_request.return_value = BeautifulSoup(mock_html, "html.parser")

        # Test scraping
        result = Scraper.scrape_programs("2024-01-01", 1, 1)

        # Verify structure
        assert isinstance(result, dict)
        assert 1 in result  # Stadium number
        assert 1 in result[1]  # Race number

        race_data = result[1][1]
        assert "race_date" in race_data
        assert "race_stadium_number" in race_data
        assert "race_number" in race_data

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test invalid date
        with pytest.raises(ValueError):
            Scraper.scrape_programs("invalid-date")

        # Test invalid stadium number
        with pytest.raises(ValueError):
            Scraper.scrape_programs("2024-01-01", 25, 1)  # Stadium 25 doesn't exist

        # Test invalid race number
        with pytest.raises(ValueError):
            Scraper.scrape_programs("2024-01-01", 1, 13)  # Race 13 doesn't exist

    def test_static_method_shortcuts(self):
        """Test that static methods work correctly."""
        test_date = "2024-01-01"

        with patch.object(Scraper, "get_instance") as mock_get_instance:
            mock_instance = Mock()
            mock_scraper_core = Mock()
            mock_instance._scraper_core = mock_scraper_core
            mock_get_instance.return_value = mock_instance

            # Test all static methods
            Scraper.scrape_programs(test_date, 1, 1)
            Scraper.scrape_previews(test_date, 1, 1)
            Scraper.scrape_odds(test_date, 1, 1)
            Scraper.scrape_results(test_date, 1, 1)
            Scraper.scrape_stadiums(test_date)

            # Verify all were called
            assert mock_scraper_core.scrape_programs.called
            assert mock_scraper_core.scrape_previews.called
            assert mock_scraper_core.scrape_odds.called
            assert mock_scraper_core.scrape_results.called
            assert mock_scraper_core.scrape_stadiums.called
