"""
Main Scraper class providing singleton-like interface.
"""

from typing import Any, Dict, Optional, Union
from datetime import date, datetime

import requests

from .scraper_core import ScraperCore


class Scraper:
    """Main scraper class with singleton-like behavior."""
    
    _instance: Optional['Scraper'] = None
    
    def __init__(self, scraper_core: Optional[ScraperCore] = None):
        """
        Initialize scraper.
        
        Args:
            scraper_core: Optional ScraperCore instance
        """
        self._scraper_core = scraper_core or ScraperCore()
    
    def __getattr__(self, name: str):
        """
        Delegate attribute access to scraper core.
        
        Args:
            name: Attribute name
            
        Returns:
            Attribute from scraper core
            
        Raises:
            AttributeError: If attribute doesn't exist in scraper core
        """
        try:
            return getattr(self._scraper_core, name)
        except AttributeError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    @classmethod
    def get_instance(cls, scraper_core: Optional[ScraperCore] = None) -> 'Scraper':
        """
        Get singleton instance.
        
        Args:
            scraper_core: Optional ScraperCore instance
            
        Returns:
            Scraper instance
        """
        if cls._instance is None:
            cls._instance = cls(scraper_core)
        return cls._instance
    
    @classmethod
    def create_instance(cls, scraper_core: Optional[ScraperCore] = None) -> 'Scraper':
        """
        Create new instance (overwrites singleton).
        
        Args:
            scraper_core: Optional ScraperCore instance
            
        Returns:
            New Scraper instance
        """
        cls._instance = cls(scraper_core)
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance."""
        cls._instance = None
    
    # Static method shortcuts for convenience
    @classmethod
    def scrape_programs(cls, race_date: Union[date, datetime, str],
                        race_stadium_number: Optional[int] = None,
                        race_number: Optional[int] = None) -> Dict[str, Any]:
        """Scrape race programs."""
        instance = cls.get_instance()
        return instance._scraper_core.scrape_programs(race_date, race_stadium_number, race_number)
    
    @classmethod 
    def scrape_previews(cls, race_date: Union[date, datetime, str],
                        race_stadium_number: Optional[int] = None,
                        race_number: Optional[int] = None) -> Dict[str, Any]:
        """Scrape race previews."""
        instance = cls.get_instance()
        return instance._scraper_core.scrape_previews(race_date, race_stadium_number, race_number)
    
    @classmethod
    def scrape_odds(cls, race_date: Union[date, datetime, str],
                    race_stadium_number: Optional[int] = None,
                    race_number: Optional[int] = None) -> Dict[str, Any]:
        """Scrape all odds."""
        instance = cls.get_instance()
        return instance._scraper_core.scrape_odds(race_date, race_stadium_number, race_number)
    
    @classmethod
    def scrape_results(cls, race_date: Union[date, datetime, str],
                       race_stadium_number: Optional[int] = None,
                       race_number: Optional[int] = None) -> Dict[str, Any]:
        """Scrape race results."""
        instance = cls.get_instance()
        return instance._scraper_core.scrape_results(race_date, race_stadium_number, race_number)
    
    @classmethod
    def scrape_stadiums(cls, race_date: Union[date, datetime, str]) -> Dict[str, Any]:
        """Scrape stadium information."""
        instance = cls.get_instance()
        return instance._scraper_core.scrape_stadiums(race_date)