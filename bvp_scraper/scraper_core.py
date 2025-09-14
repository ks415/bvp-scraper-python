"""
Core scraper class that manages all specific scrapers.
"""

import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

import requests
from tenacity import retry, stop_after_attempt, wait_fixed

from .base_scraper import BaseScraper


class ScraperCore:
    """Core scraper that manages and orchestrates all specific scrapers."""
    
    def __init__(self, session: Optional[requests.Session] = None):
        """
        Initialize scraper core.
        
        Args:
            session: Optional requests session for connection reuse
        """
        self.session = session or requests.Session()
        self._scraper_instances: Dict[str, BaseScraper] = {}
        
        # Mapping of method names to scraper classes
        self._scraper_classes: Dict[str, str] = {
            'scrape_odds': 'OddsScraper',
            'scrape_win_odds': 'OddsScraper',
            'scrape_place_odds': 'OddsScraper',
            'scrape_exacta_odds': 'OddsScraper',
            'scrape_quinella_odds': 'OddsScraper',
            'scrape_quinella_place_odds': 'OddsScraper',
            'scrape_trifecta_odds': 'OddsScraper',
            'scrape_trio_odds': 'OddsScraper',
            'scrape_previews': 'PreviewScraper',
            'scrape_programs': 'ProgramScraper',
            'scrape_results': 'ResultScraper',
            'scrape_stadiums': 'StadiumScraper',
        }
        
        # Mapping of class names to module names
        self._module_mapping = {
            'OddsScraper': 'odds_scraper',
            'PreviewScraper': 'preview_scraper', 
            'ProgramScraper': 'program_scraper',
            'ResultScraper': 'result_scraper',
            'StadiumScraper': 'stadium_scraper',
        }
    
    def __getattr__(self, name: str):
        """
        Dynamic method dispatch for scraper methods.
        
        Args:
            name: Method name
            
        Returns:
            Callable method
        """
        if name in self._scraper_classes:
            return lambda *args: self._scrape_method(name, *args)
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def _scrape_method(self, method_name: str, race_date: Union[date, datetime, str],
                       race_stadium_number: Optional[int] = None, 
                       race_number: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute scraping method with proper parameter handling.
        
        Args:
            method_name: Name of the scraping method
            race_date: Race date
            race_stadium_number: Stadium number (1-24), None for all stadiums
            race_number: Race number (1-12), None for all races
            
        Returns:
            Dictionary containing scraped data
            
        Raises:
            ValueError: If parameters are invalid
        """
        parsed_date = self._parse_date(race_date)
        
        # Special handling for stadium scraping (no stadium/race number needed)
        if method_name == 'scrape_stadiums':
            scraper = self._get_scraper_instance(method_name)
            return scraper.scrape(parsed_date, 0, 0)  # Dummy parameters
        
        # Get stadium numbers to process
        stadium_numbers = self._get_race_stadium_numbers(parsed_date, race_stadium_number)
        race_numbers = self._get_race_numbers(race_number)
        
        response = {}
        scraper = self._get_scraper_instance(method_name)
        
        for stadium_num in stadium_numbers:
            response[stadium_num] = {}
            for race_num in race_numbers:
                response[stadium_num][race_num] = self._call_with_retry(
                    lambda: self._execute_scraper_method(
                        scraper, method_name, parsed_date, stadium_num, race_num
                    )
                )
        
        return response
    
    def _execute_scraper_method(self, scraper: BaseScraper, method_name: str,
                                race_date: date, stadium_number: int, 
                                race_number: int) -> Dict[str, Any]:
        """
        Execute specific scraper method.
        
        Args:
            scraper: Scraper instance
            method_name: Method name
            race_date: Parsed race date
            stadium_number: Stadium number
            race_number: Race number
            
        Returns:
            Scraped data
        """
        # Handle odds-specific methods
        odds_match = re.match(r'^scrape_([a-zA-Z_]+)_odds$', method_name)
        if odds_match:
            odds_type = odds_match.group(1)
            if hasattr(scraper, f'scrape_{odds_type}'):
                return getattr(scraper, f'scrape_{odds_type}')(
                    race_date, stadium_number, race_number
                )
        
        # Default to main scrape method
        return scraper.scrape(race_date, stadium_number, race_number)
    
    def _get_scraper_instance(self, method_name: str) -> BaseScraper:
        """
        Get or create scraper instance.
        
        Args:
            method_name: Method name to get scraper for
            
        Returns:
            Scraper instance
            
        Raises:
            ValueError: If scraper class is not found
        """
        if method_name not in self._scraper_instances:
            scraper_class_name = self._scraper_classes.get(method_name)
            if not scraper_class_name:
                raise ValueError(f"Unknown scraper method: {method_name}")
            
            # Import and instantiate scraper class
            module_name = self._module_mapping.get(scraper_class_name)
            if not module_name:
                raise ValueError(f"No module mapping for {scraper_class_name}")
                
            try:
                module = __import__(f"bvp_scraper.scrapers.{module_name}", fromlist=[scraper_class_name])
                scraper_class = getattr(module, scraper_class_name)
                self._scraper_instances[method_name] = scraper_class(self.session)
            except (ImportError, AttributeError) as e:
                raise ValueError(f"Could not load scraper class {scraper_class_name}: {e}")
        
        return self._scraper_instances[method_name]
    
    def _get_race_stadium_numbers(self, race_date: date, 
                                  race_stadium_number: Optional[int]) -> List[int]:
        """
        Get list of stadium numbers to process.
        
        Args:
            race_date: Race date
            race_stadium_number: Specific stadium number or None for all
            
        Returns:
            List of stadium numbers
            
        Raises:
            ValueError: If stadium number is invalid
        """
        if race_stadium_number is None:
            # Get all stadiums for the date
            stadium_scraper = self._get_scraper_instance('scrape_stadiums')
            stadiums_data = stadium_scraper.scrape(race_date, 0, 0)
            return list(stadiums_data.keys())
        
        # Validate single stadium number
        if not isinstance(race_stadium_number, int) or not (1 <= race_stadium_number <= 24):
            raise ValueError(f"Invalid race stadium number: {race_stadium_number}")
        
        return [race_stadium_number]
    
    def _get_race_numbers(self, race_number: Optional[int]) -> List[int]:
        """
        Get list of race numbers to process.
        
        Args:
            race_number: Specific race number or None for all races
            
        Returns:
            List of race numbers (1-12)
            
        Raises:
            ValueError: If race number is invalid
        """
        if race_number is None:
            return list(range(1, 13))  # Races 1-12
        
        if not isinstance(race_number, int) or not (1 <= race_number <= 12):
            raise ValueError(f"Invalid race number: {race_number}")
        
        return [race_number]
    
    def _parse_date(self, date_input: Union[date, datetime, str]) -> date:
        """
        Parse various date input formats to date object.
        
        Args:
            date_input: Date in various formats
            
        Returns:
            date object
        """
        if isinstance(date_input, date):
            return date_input
        elif isinstance(date_input, datetime):
            return date_input.date()
        elif isinstance(date_input, str):
            from dateutil.parser import parse
            return parse(date_input).date()
        else:
            raise ValueError(f"Invalid date format: {date_input}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
    def _call_with_retry(self, callback) -> Any:
        """
        Execute callback with retry logic.
        
        Args:
            callback: Function to execute with retry
            
        Returns:
            Callback result
        """
        return callback()