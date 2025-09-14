"""
Scrapers package for different types of boatrace data.
"""

from .odds_scraper import OddsScraper
from .preview_scraper import PreviewScraper
from .program_scraper import ProgramScraper
from .result_scraper import ResultScraper
from .stadium_scraper import StadiumScraper

__all__ = [
    "OddsScraper",
    "PreviewScraper",
    "ProgramScraper",
    "ResultScraper",
    "StadiumScraper",
]
