"""
Web Image Scraper Package
A modern, efficient web image scraping application.

Part of ProjectsHUB - Advanced Development Solutions
"""

__version__ = "2.0.0"
__author__ = "ProjectsHUB"
__description__ = "Modern web image scraper with GUI interface"

from .image_scraper import ImageScraper, ImageInfo
from .gui import ModernImageScraperGUI

__all__ = ['ImageScraper', 'ImageInfo', 'ModernImageScraperGUI']
