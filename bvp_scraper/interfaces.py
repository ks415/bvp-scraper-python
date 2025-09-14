"""
Base interface for all scrapers.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, Dict, Union


class ScraperContractInterface(ABC):
    """Base contract interface for all scrapers."""
    
    @abstractmethod
    def scrape(self, race_date: Union[date, datetime, str], 
               race_stadium_number: int, race_number: int) -> Dict[str, Any]:
        """
        Main scraping method that all scrapers must implement.
        
        Args:
            race_date: Race date
            race_stadium_number: Stadium number (1-24)
            race_number: Race number (1-12)
            
        Returns:
            Dictionary containing scraped data
        """
        pass