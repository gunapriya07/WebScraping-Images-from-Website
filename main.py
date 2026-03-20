#!/usr/bin/env python3
"""
Web Image Scraper - Main Application Entry Point
A modern, efficient web image scraper with GUI interface.

Usage:
    python main.py              # Launch GUI
    python main.py --cli        # Use command line interface
    python main.py --help       # Show help information
"""

from src.image_scraper import ImageScraper
from src.gui import ModernImageScraperGUI
import sys
import argparse
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))


def create_cli_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description='Web Image Scraper - Download images from websites',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Launch GUI
  python main.py --cli -u https://example.com      # CLI scraping
  python main.py --cli -u https://example.com -m 20 -o images/  # Custom settings
  
        """
    )

    parser.add_argument('--cli', action='store_true',
                        help='Use command line interface instead of GUI')

    parser.add_argument('-u', '--url', type=str,
                        help='Website URL to scrape images from')

    parser.add_argument('-o', '--output', type=str, default='downloads',
                        help='Output directory for downloaded images (default: downloads)')

    parser.add_argument('-m', '--max-images', type=int, default=50,
                        help='Maximum number of images to download (default: 50, 0 = no limit)')

    parser.add_argument('-s', '--min-size', type=int, default=10,
                        help='Minimum file size in KB (default: 10)')

    parser.add_argument('-t', '--threads', type=int, default=5,
                        help='Number of download threads (default: 5)')

    parser.add_argument('--no-selenium', action='store_true',
                        help='Disable Selenium (faster but may miss dynamic content)')

    parser.add_argument('--timeout', type=int, default=30,
                        help='Request timeout in seconds (default: 30)')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose logging')

    return parser


def run_cli(args):
    """Run command line interface"""
    if not args.url:
        print("Error: URL is required for CLI mode")
        print("Use --help for more information")
        return 1

    try:
        print(f"Web Image Scraper - CLI Mode")
        print(f"Powered by ProjectsHUB")
        print("-" * 50)
        print(f"Target URL: {args.url}")
        print(f"Output Directory: {args.output}")
        print(
            f"Max Images: {args.max_images if args.max_images > 0 else 'No limit'}")
        print(f"Min Size: {args.min_size} KB")
        print(f"Threads: {args.threads}")
        print(f"Use Selenium: {'No' if args.no_selenium else 'Yes'}")
        print("-" * 50)

        # Initialize scraper
        scraper = ImageScraper(
            output_dir=args.output,
            max_workers=args.threads,
            timeout=args.timeout
        )

        # Progress callback for CLI
        def progress_callback(message):
            print(f"Progress: {message}")

        # Start scraping
        downloaded = scraper.scrape_images(
            url=args.url,
            use_selenium=not args.no_selenium,
            max_images=args.max_images if args.max_images > 0 else None,
            min_size=args.min_size * 1024,
            progress_callback=progress_callback
        )

        # Display results
        if downloaded:
            print(f"\nSuccess! Downloaded {len(downloaded)} images")
            stats = scraper.get_statistics()
            print(f"Total files: {stats['total_files']}")
            print(f"Total size: {stats['total_size_mb']} MB")
            print(f"Output directory: {Path(args.output).absolute()}")
        else:
            print("\nNo images were downloaded")

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"\nError: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def run_gui():
    """Run GUI interface"""
    try:
        app = ModernImageScraperGUI()
        app.run()
        return 0
    except Exception as e:
        print(f"Error starting GUI: {str(e)}")
        return 1


def main():
    """Main application entry point"""
    parser = create_cli_parser()
    args = parser.parse_args()

    if args.cli:
        return run_cli(args)
    else:
        return run_gui()


if __name__ == "__main__":
    sys.exit(main())
