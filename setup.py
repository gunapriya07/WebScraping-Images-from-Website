"""
Setup script for Web Image Scraper
Part of ProjectsHUB - Advanced Development Solutions
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(
    encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith('#')
        ]
else:
    requirements = [
        'requests>=2.31.0',
        'beautifulsoup4>=4.12.0',
        'lxml>=4.9.0',
        'selenium>=4.15.0',
        'webdriver-manager>=4.0.0'
    ]

setup(
    name="web-image-scraper",
    version="2.0.0",
    author="ProjectsHUB",
    author_email="info@projectshub.com",
    description="A modern, efficient web image scraper with GUI interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/projectshub/web-image-scraper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "image-processing": [
            "Pillow>=10.0.0",
            "opencv-python>=4.8.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "web-image-scraper=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.ini", "*.md", "*.txt"],
    },
    keywords="web scraping, image download, selenium, gui, automation",
    project_urls={
        "Bug Reports": "https://github.com/projectshub/web-image-scraper/issues",
        "Source": "https://github.com/projectshub/web-image-scraper",
        "Documentation": "https://github.com/projectshub/web-image-scraper/wiki",
    },
)
