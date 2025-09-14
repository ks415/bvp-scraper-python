"""
BVP Scraper Python
==================

A Python library for scraping boatrace official website data including programs, 
previews, odds, and results.

This is a Python port of the original PHP library 'bvp-scraper' by shimomo.
Original PHP library: https://github.com/shimomo/bvp-scraper

The Python port maintains the same API design and functionality as the original 
PHP implementation while leveraging Python-specific features and libraries.
"""

__version__ = "1.0.0"
__author__ = "Port to Python (Original by shimomo)"

from .scraper import Scraper
from .scraper_core import ScraperCore

__all__ = ["Scraper", "ScraperCore"]