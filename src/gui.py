"""
Web Image Scraper - Modern GUI Interface
A sleek, user-friendly interface for the image scraping application.

Part of ProjectsHUB - Advanced Development Solutions
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import webbrowser
from pathlib import Path
import os
from typing import Optional

from src.image_scraper import ImageScraper


class ModernImageScraperGUI:
    """Modern GUI for the Image Scraper application"""

    def __init__(self):
        self.root = tk.Tk()
        self.scraper: Optional[ImageScraper] = None
        self.is_scraping = False

        # Configure window
        self.root.title("Web Image Scraper - ProjectsHUB")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)

        # Configure style
        self.setup_styles()

        # Setup GUI
        self.create_widgets()

        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def setup_styles(self):
        """Configure modern styling"""
        self.style = ttk.Style()

        # Configure colors
        self.colors = {
            'primary': '#2C3E50',
            'secondary': '#3498DB',
            'success': '#27AE60',
            'warning': '#F39C12',
            'danger': '#E74C3C',
            'light': '#ECF0F1',
            'dark': '#2C3E50',
            'bg': '#FFFFFF',
            'text': '#2C3E50'
        }

        # Configure styles
        self.style.theme_use('clam')

        # Button styles
        self.style.configure('Primary.TButton',
                             background=self.colors['secondary'],
                             foreground='white',
                             padding=(10, 8))

        self.style.map('Primary.TButton',
                       background=[('active', '#2980B9')])

        self.style.configure('Success.TButton',
                             background=self.colors['success'],
                             foreground='white',
                             padding=(8, 6))

        self.style.configure('Danger.TButton',
                             background=self.colors['danger'],
                             foreground='white',
                             padding=(8, 6))

        # Frame styles
        self.style.configure('Card.TFrame',
                             background=self.colors['bg'],
                             relief='solid',
                             borderwidth=1)

    def create_widgets(self):
        """Create all GUI widgets"""
        self.create_header()
        self.create_main_content()
        self.create_status_bar()

    def create_header(self):
        """Create header section"""
        header_frame = ttk.Frame(self.root, style='Card.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(header_frame,
                                text="Web Image Scraper",
                                font=('Arial', 18, 'bold'),
                                foreground=self.colors['primary'])
        title_label.grid(row=0, column=0, padx=15, pady=15, sticky='w')

        # ProjectsHUB branding
        brand_label = ttk.Label(header_frame,
                                text="Powered by ProjectsHUB",
                                font=('Arial', 10, 'italic'),
                                foreground=self.colors['secondary'])
        brand_label.grid(row=0, column=1, padx=15, pady=15, sticky='e')

    def create_main_content(self):
        """Create main content area"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Configuration panel
        self.create_config_panel(main_frame)

        # Progress and output panel
        self.create_progress_panel(main_frame)

    def create_config_panel(self, parent):
        """Create configuration panel"""
        config_frame = ttk.LabelFrame(parent, text="Configuration", padding=15)
        config_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        config_frame.grid_columnconfigure(1, weight=1)

        # URL input
        ttk.Label(config_frame, text="Website URL:").grid(
            row=0, column=0, sticky='w', pady=(0, 10))
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(
            config_frame, textvariable=self.url_var, font=('Arial', 10))
        url_entry.grid(row=0, column=1, sticky='ew',
                       padx=(10, 0), pady=(0, 10))

        # Output directory
        ttk.Label(config_frame, text="Output Directory:").grid(
            row=1, column=0, sticky='w', pady=(0, 10))

        dir_frame = ttk.Frame(config_frame)
        dir_frame.grid(row=1, column=1, sticky='ew',
                       padx=(10, 0), pady=(0, 10))
        dir_frame.grid_columnconfigure(0, weight=1)

        self.output_dir_var = tk.StringVar(value="downloads")
        dir_entry = ttk.Entry(
            dir_frame, textvariable=self.output_dir_var, font=('Arial', 10))
        dir_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        dir_button = ttk.Button(dir_frame, text="Browse",
                                command=self.browse_directory)
        dir_button.grid(row=0, column=1)

        # Options frame
        options_frame = ttk.Frame(config_frame)
        options_frame.grid(row=2, column=0, columnspan=2,
                           sticky='ew', pady=(10, 0))
        options_frame.grid_columnconfigure(0, weight=1)
        options_frame.grid_columnconfigure(1, weight=1)

        # Left options
        left_options = ttk.Frame(options_frame)
        left_options.grid(row=0, column=0, sticky='ew', padx=(0, 10))

        self.use_selenium_var = tk.BooleanVar(value=True)
        selenium_check = ttk.Checkbutton(left_options, text="Use Dynamic Loading (Selenium)",
                                         variable=self.use_selenium_var)
        selenium_check.grid(row=0, column=0, sticky='w')

        ttk.Label(left_options, text="Max Images:").grid(
            row=1, column=0, sticky='w', pady=(10, 0))
        self.max_images_var = tk.StringVar(value="50")
        max_images_entry = ttk.Entry(
            left_options, textvariable=self.max_images_var, width=10)
        max_images_entry.grid(row=2, column=0, sticky='w', pady=(5, 0))

        # Right options
        right_options = ttk.Frame(options_frame)
        right_options.grid(row=0, column=1, sticky='ew')

        ttk.Label(right_options, text="Min File Size (KB):").grid(
            row=0, column=0, sticky='w')
        self.min_size_var = tk.StringVar(value="10")
        min_size_entry = ttk.Entry(
            right_options, textvariable=self.min_size_var, width=10)
        min_size_entry.grid(row=1, column=0, sticky='w', pady=(5, 0))

        ttk.Label(right_options, text="Threads:").grid(
            row=2, column=0, sticky='w', pady=(10, 0))
        self.threads_var = tk.StringVar(value="5")
        threads_entry = ttk.Entry(
            right_options, textvariable=self.threads_var, width=10)
        threads_entry.grid(row=3, column=0, sticky='w', pady=(5, 0))

        # Action buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))

        self.start_button = ttk.Button(button_frame, text="Start Scraping",
                                       style='Primary.TButton',
                                       command=self.start_scraping)
        self.start_button.pack(side='left', padx=(0, 10))

        self.stop_button = ttk.Button(button_frame, text="Stop",
                                      style='Danger.TButton',
                                      command=self.stop_scraping,
                                      state='disabled')
        self.stop_button.pack(side='left', padx=(0, 10))

        self.open_folder_button = ttk.Button(button_frame, text="Open Downloads",
                                             style='Success.TButton',
                                             command=self.open_downloads_folder)
        self.open_folder_button.pack(side='left')

    def create_progress_panel(self, parent):
        """Create progress and output panel"""
        progress_frame = ttk.LabelFrame(
            parent, text="Progress & Output", padding=15)
        progress_frame.grid(row=1, column=0, sticky='nsew')
        progress_frame.grid_rowconfigure(1, weight=1)
        progress_frame.grid_columnconfigure(0, weight=1)

        # Progress bar
        self.progress_var = tk.StringVar(value="Ready to start")
        progress_label = ttk.Label(
            progress_frame, textvariable=self.progress_var)
        progress_label.grid(row=0, column=0, sticky='w', pady=(0, 5))

        self.progress_bar = ttk.Progressbar(
            progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky='ew', pady=(25, 10))

        # Output text area
        self.output_text = scrolledtext.ScrolledText(progress_frame,
                                                     wrap=tk.WORD,
                                                     font=('Consolas', 9),
                                                     background='#F8F9FA',
                                                     height=15)
        self.output_text.grid(row=1, column=0, sticky='nsew', pady=(10, 0))

        # Statistics frame
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        stats_frame.grid_columnconfigure(1, weight=1)

        self.stats_var = tk.StringVar(value="No statistics available")
        stats_label = ttk.Label(
            stats_frame, textvariable=self.stats_var, font=('Arial', 9))
        stats_label.grid(row=0, column=0, sticky='w')

        refresh_stats_button = ttk.Button(stats_frame, text="Refresh Stats",
                                          command=self.update_statistics)
        refresh_stats_button.grid(row=0, column=1, sticky='e')

    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=(5, 10))

        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                 relief='sunken', anchor='w')
        status_label.pack(fill='x', padx=5, pady=2)

    def browse_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)

    def log_message(self, message: str, level: str = "INFO"):
        """Add message to output text"""
        self.output_text.insert(tk.END, f"[{level}] {message}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()

    def update_progress(self, message: str):
        """Update progress message"""
        self.progress_var.set(message)
        self.status_var.set(message)

    def start_scraping(self):
        """Start the scraping process"""
        # Validate inputs
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a website URL")
            return

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_var.set(url)

        try:
            max_images = int(self.max_images_var.get()
                             ) if self.max_images_var.get() else None
            min_size = int(self.min_size_var.get()) * \
                1024 if self.min_size_var.get() else 0
            max_workers = int(self.threads_var.get()
                              ) if self.threads_var.get() else 5
        except ValueError:
            messagebox.showerror(
                "Error", "Please enter valid numbers for numeric fields")
            return

        # Update UI state
        self.is_scraping = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_bar.start()

        # Clear output
        self.output_text.delete(1.0, tk.END)

        # Initialize scraper
        self.scraper = ImageScraper(
            output_dir=self.output_dir_var.get(),
            max_workers=max_workers
        )

        # Start scraping in thread
        thread = threading.Thread(
            target=self._scrape_thread,
            args=(url, self.use_selenium_var.get(), max_images, min_size),
            daemon=True
        )
        thread.start()

    def _scrape_thread(self, url: str, use_selenium: bool, max_images: int, min_size: int):
        """Thread function for scraping"""
        try:
            self.log_message(f"Starting scrape of: {url}")

            downloaded = self.scraper.scrape_images(
                url=url,
                use_selenium=use_selenium,
                max_images=max_images,
                min_size=min_size,
                progress_callback=self.update_progress
            )

            if downloaded:
                self.log_message(
                    f"Successfully downloaded {len(downloaded)} images", "SUCCESS")
                self.update_statistics()
            else:
                self.log_message("No images were downloaded", "WARNING")

        except Exception as e:
            self.log_message(f"Error during scraping: {str(e)}", "ERROR")

        finally:
            # Update UI state
            self.root.after(0, self._scraping_complete)

    def _scraping_complete(self):
        """Called when scraping is complete"""
        self.is_scraping = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
        self.update_progress("Scraping completed")

    def stop_scraping(self):
        """Stop the scraping process"""
        self.is_scraping = False
        self.log_message("Stopping scraping...", "WARNING")
        self._scraping_complete()

    def open_downloads_folder(self):
        """Open the downloads folder"""
        output_dir = Path(self.output_dir_var.get())
        if output_dir.exists():
            if os.name == 'nt':  # Windows
                os.startfile(output_dir)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{output_dir}"')
        else:
            messagebox.showwarning(
                "Warning", "Downloads folder does not exist yet")

    def update_statistics(self):
        """Update download statistics"""
        if self.scraper:
            stats = self.scraper.get_statistics()
            self.stats_var.set(
                f"Files: {stats['total_files']} | Size: {stats['total_size_mb']} MB")

    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main function"""
    app = ModernImageScraperGUI()
    app.run()


if __name__ == "__main__":
    main()
