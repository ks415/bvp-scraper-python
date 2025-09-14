"""
Tests for the main Scraper class.
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch

from bvp_scraper import Scraper
from bvp_scraper.scraper_core import ScraperCore


class TestScraper:
    """Test cases for Scraper class."""
    
    def test_singleton_behavior(self):
        """Test that get_instance returns same instance."""
        scraper1 = Scraper.get_instance()
        scraper2 = Scraper.get_instance()
        assert scraper1 is scraper2
    
    def test_create_instance_overwrites_singleton(self):
        """Test that create_instance creates new instance."""
        scraper1 = Scraper.get_instance()
        scraper2 = Scraper.create_instance()
        assert scraper1 is not scraper2
    
    def test_reset_instance(self):
        """Test that reset_instance clears singleton."""
        Scraper.get_instance()
        Scraper.reset_instance()
        assert Scraper._instance is None
    
    def test_attribute_delegation(self):
        """Test that attributes are delegated to scraper core."""
        from bvp_scraper.scraper_core import ScraperCore
        
        # Use real ScraperCore to test delegation and AttributeError
        scraper_core = ScraperCore()
        scraper = Scraper(scraper_core)
        
        # Access non-existent attribute should raise AttributeError
        with pytest.raises(AttributeError):
            scraper.non_existent_method()
    
    def test_static_methods(self):
        """Test static method shortcuts."""
        test_date = date(2024, 1, 1)
        
        with patch.object(Scraper, 'get_instance') as mock_get_instance:
            mock_instance = Mock()
            mock_scraper_core = Mock()
            mock_instance._scraper_core = mock_scraper_core
            mock_get_instance.return_value = mock_instance
            
            # Test static method calls
            Scraper.scrape_programs(test_date, 1, 1)
            mock_scraper_core.scrape_programs.assert_called_once_with(test_date, 1, 1)
            
            Scraper.scrape_odds(test_date, 1, 1)
            mock_scraper_core.scrape_odds.assert_called_once_with(test_date, 1, 1)
    
    def test_initialization_with_custom_core(self):
        """Test initialization with custom scraper core."""
        mock_core = Mock(spec=ScraperCore)
        scraper = Scraper(mock_core)
        assert scraper._scraper_core is mock_core
    
    def test_initialization_with_default_core(self):
        """Test initialization with default scraper core."""
        scraper = Scraper()
        assert isinstance(scraper._scraper_core, ScraperCore)