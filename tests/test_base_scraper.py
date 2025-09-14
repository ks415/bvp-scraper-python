"""
Tests for BaseScraper class.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date, datetime

from bvp_scraper.base_scraper import BaseScraper


class TestBaseScraper:
    """Test cases for BaseScraper class."""
    
    def test_initialization(self):
        """Test BaseScraper initialization."""
        scraper = BaseScraper()
        assert scraper.base_url == "https://www.boatrace.jp"
        assert scraper.seconds == 1
        assert scraper.session is not None
    
    def test_initialization_with_custom_session(self):
        """Test initialization with custom session."""
        mock_session = Mock()
        scraper = BaseScraper(mock_session)
        assert scraper.session is mock_session
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        scraper = BaseScraper()
        
        # Test whitespace normalization
        result = scraper._clean_text("  多  重  空白  ")
        assert result == "多 重 空白"
        
        # Test full-width number conversion
        result = scraper._clean_text("１２３４５")
        assert result == "12345"
    
    def test_parse_date_with_date_object(self):
        """Test date parsing with date object."""
        scraper = BaseScraper()
        test_date = date(2024, 1, 1)
        result = scraper._parse_date(test_date)
        assert result == test_date
    
    def test_parse_date_with_datetime_object(self):
        """Test date parsing with datetime object."""
        scraper = BaseScraper()
        test_datetime = datetime(2024, 1, 1, 12, 0, 0)
        result = scraper._parse_date(test_datetime)
        assert result == test_datetime.date()
    
    def test_parse_date_with_string(self):
        """Test date parsing with string."""
        scraper = BaseScraper()
        result = scraper._parse_date("2024-01-01")
        assert result == date(2024, 1, 1)
    
    def test_parse_date_with_invalid_input(self):
        """Test date parsing with invalid input."""
        scraper = BaseScraper()
        with pytest.raises(ValueError):
            scraper._parse_date(123)
    
    @patch('time.sleep')
    @patch('requests.Session.get')
    def test_request_and_parse(self, mock_get, mock_sleep):
        """Test HTTP request and parsing."""
        # Mock successful response
        mock_response = Mock()
        mock_response.content = """
            <html><body><div>Test content</div></body></html>
        """.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        scraper = BaseScraper()
        soup = scraper.request_and_parse('https://example.com')
        
        # Verify sleep was called
        mock_sleep.assert_called_once_with(1)
        
        # Verify BeautifulSoup object
        assert soup.find('div').get_text() == 'Test content'
    
    def test_filter_xpath_for_grade_number(self, sample_html):
        """Test grade number extraction."""
        from bs4 import BeautifulSoup
        
        scraper = BaseScraper()
        
        # Test with SG class
        html = '<div class="is-SG">Content</div>'
        soup = BeautifulSoup(html, 'html.parser')
        result = scraper.filter_xpath_for_grade_number(soup, 'div')
        assert result == 1
        
        # Test with G1 class
        html = '<div class="is-G1">Content</div>'
        soup = BeautifulSoup(html, 'html.parser')
        result = scraper.filter_xpath_for_grade_number(soup, 'div')
        assert result == 2
        
        # Test with ippan class
        html = '<div class="is-ippan">Content</div>'
        soup = BeautifulSoup(html, 'html.parser')
        result = scraper.filter_xpath_for_grade_number(soup, 'div')
        assert result == 5
    
    def test_filter_xpath_for_odds(self):
        """Test odds extraction."""
        from bs4 import BeautifulSoup
        
        scraper = BaseScraper()
        
        # Test valid odds
        html = '<td>1.5</td>'
        soup = BeautifulSoup(html, 'html.parser')
        result = scraper.filter_xpath_for_odds(soup, 'td')
        assert result == 1.5
        
        # Test invalid odds
        html = '<td>N/A</td>'
        soup = BeautifulSoup(html, 'html.parser')
        result = scraper.filter_xpath_for_odds(soup, 'td')
        assert result is None
    
    def test_filter_xpath_for_odds_range(self):
        """Test odds range extraction."""
        from bs4 import BeautifulSoup
        
        scraper = BaseScraper()
        
        # Test valid range
        html = '<td>1.5-2.5</td>'
        soup = BeautifulSoup(html, 'html.parser')
        result = scraper.filter_xpath_for_odds_range(soup, 'td')
        assert result == {'lower_limit': 1.5, 'upper_limit': 2.5}
        
        # Test invalid range
        html = '<td>N/A</td>'
        soup = BeautifulSoup(html, 'html.parser')
        result = scraper.filter_xpath_for_odds_range(soup, 'td')
        assert result == {'lower_limit': None, 'upper_limit': None}
    
    def test_scrape_not_implemented(self):
        """Test that scrape method raises NotImplementedError."""
        scraper = BaseScraper()
        with pytest.raises(NotImplementedError):
            scraper.scrape(date(2024, 1, 1), 1, 1)