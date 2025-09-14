"""
Scrapers package for different types of boatrace data.
"""

from .program_scraper import ProgramScraper
from .odds_scraper import OddsScraper
from .preview_scraper import PreviewScraper
from .result_scraper import ResultScraper
from .stadium_scraper import StadiumScraper

__all__ = [
    "ProgramScraper",
    "OddsScraper", 
    "PreviewScraper",
    "ResultScraper",
    "StadiumScraper"
]