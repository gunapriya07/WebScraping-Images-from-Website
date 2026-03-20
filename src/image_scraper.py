"""
Web Image Scraper - Core Module
A modern, efficient web image scraper with advanced features.

Part of ProjectsHUB - Advanced Development Solutions
"""

import os
import requests
import logging
import time
from urllib.parse import urljoin, urlparse
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


@dataclass
class ImageInfo:
    """Data class for image information"""
    url: str
    filename: str
    size: Optional[int] = None
    format: Optional[str] = None


class ImageScraper:
    """Modern web image scraper with advanced features"""

    def __init__(self, output_dir: str = "downloads", max_workers: int = 5, timeout: int = 30):
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = self._setup_logger()

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

        # Supported image formats
        self.image_extensions = {'.jpg', '.jpeg',
                                 '.png', '.gif', '.bmp', '.webp', '.svg'}

        # Request headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('ImageScraper')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _setup_webdriver(self, headless: bool = True) -> webdriver.Chrome:
        """Setup Chrome webdriver with optimal configuration"""
        try:
            chrome_options = Options()

            if headless:
                chrome_options.add_argument('--headless')

            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(self.timeout)

            return driver

        except Exception as e:
            self.logger.error(f"Failed to setup webdriver: {e}")
            raise

    def _get_page_content(self, url: str, use_selenium: bool = True, wait_time: int = 3) -> str:
        """Get page content using either Selenium or requests"""
        try:
            if use_selenium:
                driver = self._setup_webdriver()
                try:
                    self.logger.info(f"Loading page with Selenium: {url}")
                    driver.get(url)

                    # Wait for page to load
                    WebDriverWait(driver, self.timeout).until(
                        EC.presence_of_element_located((By.TAG_NAME, "img"))
                    )

                    # Additional wait for dynamic content
                    time.sleep(wait_time)

                    # Scroll to load lazy-loaded images
                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)

                    content = driver.page_source
                    return content

                finally:
                    driver.quit()
            else:
                self.logger.info(f"Loading page with requests: {url}")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text

        except Exception as e:
            self.logger.error(f"Failed to get page content: {e}")
            raise

    def _extract_image_urls(self, html_content: str, base_url: str) -> List[str]:
        """Extract all image URLs from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        image_urls = set()

        # Find all img tags
        img_tags = soup.find_all('img')

        for img in img_tags:
            src = img.get('src') or img.get(
                'data-src') or img.get('data-lazy-src')

            if src:
                # Convert relative URLs to absolute
                full_url = urljoin(base_url, src)

                # Check if it's a valid image URL
                if self._is_valid_image_url(full_url):
                    image_urls.add(full_url)

        # Also check for background images in style attributes
        for element in soup.find_all(attrs={'style': True}):
            style = element['style']
            if 'background-image' in style:
                # Extract URL from background-image: url(...)
                import re
                urls = re.findall(r'url\([\'"]?([^\'"]+)[\'"]?\)', style)
                for url in urls:
                    full_url = urljoin(base_url, url)
                    if self._is_valid_image_url(full_url):
                        image_urls.add(full_url)

        self.logger.info(f"Found {len(image_urls)} unique image URLs")
        return list(image_urls)

    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL is a valid image URL"""
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()

            # Check file extension
            for ext in self.image_extensions:
                if path.endswith(ext):
                    return True

            # Check for common image patterns in URL
            image_patterns = ['image', 'img', 'photo', 'picture', 'thumb']
            return any(pattern in url.lower() for pattern in image_patterns)

        except Exception:
            return False

    def _get_image_info(self, url: str) -> Optional[ImageInfo]:
        """Get information about an image"""
        try:
            response = self.session.head(url, timeout=10)

            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')

                if 'image' in content_type:
                    # Generate filename
                    parsed_url = urlparse(url)
                    filename = os.path.basename(parsed_url.path)

                    if not filename or '.' not in filename:
                        # Generate filename from URL hash
                        hash_obj = hashlib.md5(url.encode())
                        ext = self._get_extension_from_content_type(
                            content_type)
                        filename = f"{hash_obj.hexdigest()[:8]}{ext}"

                    size = response.headers.get('content-length')
                    size = int(size) if size else None

                    return ImageInfo(
                        url=url,
                        filename=filename,
                        size=size,
                        format=content_type
                    )

        except Exception as e:
            self.logger.debug(f"Failed to get image info for {url}: {e}")

        return None

    def _get_extension_from_content_type(self, content_type: str) -> str:
        """Get file extension from content type"""
        extensions = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/bmp': '.bmp',
            'image/webp': '.webp',
            'image/svg+xml': '.svg'
        }
        return extensions.get(content_type, '.jpg')

    def _download_image(self, image_info: ImageInfo) -> Tuple[bool, str]:
        """Download a single image"""
        try:
            response = self.session.get(
                image_info.url, timeout=self.timeout, stream=True)
            response.raise_for_status()

            # Ensure unique filename
            filepath = self.output_dir / image_info.filename
            counter = 1
            while filepath.exists():
                name, ext = os.path.splitext(image_info.filename)
                filepath = self.output_dir / f"{name}_{counter}{ext}"
                counter += 1

            # Download image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.logger.info(f"Downloaded: {filepath.name}")
            return True, str(filepath)

        except Exception as e:
            self.logger.error(f"Failed to download {image_info.url}: {e}")
            return False, str(e)

    def scrape_images(self, url: str, use_selenium: bool = True, max_images: Optional[int] = None,
                      min_size: int = 1024, progress_callback=None) -> List[str]:
        """
        Scrape images from a website

        Args:
            url: Website URL to scrape
            use_selenium: Whether to use Selenium for dynamic content
            max_images: Maximum number of images to download
            min_size: Minimum file size in bytes
            progress_callback: Callback function for progress updates

        Returns:
            List of downloaded file paths
        """
        try:
            self.logger.info(f"Starting image scraping from: {url}")

            # Get page content
            html_content = self._get_page_content(url, use_selenium)

            # Extract image URLs
            image_urls = self._extract_image_urls(html_content, url)

            if not image_urls:
                self.logger.warning("No images found on the page")
                return []

            # Limit number of images if specified
            if max_images:
                image_urls = image_urls[:max_images]

            # Get image information
            self.logger.info("Analyzing images...")
            valid_images = []

            for i, img_url in enumerate(image_urls):
                if progress_callback:
                    progress_callback(
                        f"Analyzing image {i+1}/{len(image_urls)}")

                img_info = self._get_image_info(img_url)
                if img_info and (not min_size or not img_info.size or img_info.size >= min_size):
                    valid_images.append(img_info)

            if not valid_images:
                self.logger.warning("No valid images found")
                return []

            self.logger.info(f"Downloading {len(valid_images)} images...")

            # Download images using thread pool
            downloaded_files = []

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_image = {
                    executor.submit(self._download_image, img_info): img_info
                    for img_info in valid_images
                }

                for i, future in enumerate(as_completed(future_to_image)):
                    if progress_callback:
                        progress_callback(
                            f"Downloading {i+1}/{len(valid_images)}")

                    success, result = future.result()
                    if success:
                        downloaded_files.append(result)

            self.logger.info(
                f"Successfully downloaded {len(downloaded_files)} images")
            return downloaded_files

        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            raise

    def get_statistics(self) -> dict:
        """Get download statistics"""
        if not self.output_dir.exists():
            return {"total_files": 0, "total_size": 0}

        files = list(self.output_dir.glob("*"))
        image_files = [f for f in files if f.suffix.lower()
                       in self.image_extensions]

        total_size = sum(f.stat().st_size for f in image_files if f.is_file())

        return {
            "total_files": len(image_files),
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
