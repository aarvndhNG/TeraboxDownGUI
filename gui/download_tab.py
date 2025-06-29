"""
Download Tab for Terabox Downloader
Handles URL input, download management, and progress tracking
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from core.terabox_api import TeraboxAPI
from core.download_manager import DownloadManager
from utils.validators import URLValidator

class DownloadTab:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.terabox_api = TeraboxAPI()
        self.download_manager = DownloadManager(config)
        self.url_validator = URLValidator()
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create and arrange the download tab widgets"""
        self.frame = ttk.Frame(self.parent)
        self.frame.columnconfigure(0, weight=1)
        
        # URL Input Section
        self.create_url_input_section()
        
        # Download Options Section
        self.create_download_options_section()
        
        # Progress Section
        self.create_progress_section()
        
        # Download Queue Section
        self.create_queue_section()
        
    def create_url_input_section(self):
        """Create URL input section"""
        url_frame = ttk.LabelFrame(self.frame, text="Terabox URL Input", padding="10")
        url_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(1, weight=1)
        
        # Single URL input
        ttk.Label(url_frame, text="URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        add_button = ttk.Button(url_frame, text="Add to Queue", command=self.add_url_to_queue)
        add_button.grid(row=0, column=2)
        
        # Batch URL input
        ttk.Label(url_frame, text="Batch URLs:").grid(row=1, column=0, sticky=(tk.W, tk.N), padx=(0, 5), pady=(10, 0))
        
        # Text widget for multiple URLs
        self.batch_text = tk.Text(url_frame, height=4, width=60)
        self.batch_text.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(10, 0))
        
        # Scrollbar for text widget
        batch_scrollbar = ttk.Scrollbar(url_frame, orient=tk.VERTICAL, command=self.batch_text.yview)
        batch_scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S), pady=(10, 0))
        self.batch_text.config(yscrollcommand=batch_scrollbar.set)
        
        # Batch add button
        batch_button = ttk.Button(url_frame, text="Add Batch URLs", command=self.add_batch_urls)
        batch_button.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
    def create_download_options_section(self):
        """Create download options section"""
        options_frame = ttk.LabelFrame(self.frame, text="Download Options", padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # Download directory
        ttk.Label(options_frame, text="Download to:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.download_dir_var = tk.StringVar(value=self.config.get('download_directory', os.path.expanduser('~/Downloads')))
        dir_entry = ttk.Entry(options_frame, textvariable=self.download_dir_var, width=50)
        dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_button = ttk.Button(options_frame, text="Browse", command=self.browse_download_directory)
        browse_button.grid(row=0, column=2)
        
        # Download options checkboxes
        self.auto_start_var = tk.BooleanVar(value=True)
        auto_start_check = ttk.Checkbutton(options_frame, text="Auto-start downloads", variable=self.auto_start_var)
        auto_start_check.grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        self.open_after_download_var = tk.BooleanVar(value=False)
        open_check = ttk.Checkbutton(options_frame, text="Open file after download", variable=self.open_after_download_var)
        open_check.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
    def create_progress_section(self):
        """Create progress tracking section"""
        progress_frame = ttk.LabelFrame(self.frame, text="Download Progress", padding="10")
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # Current download info
        self.current_file_var = tk.StringVar(value="No active downloads")
        current_label = ttk.Label(progress_frame, textvariable=self.current_file_var)
        current_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Progress details
        details_frame = ttk.Frame(progress_frame)
        details_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        details_frame.columnconfigure(0, weight=1)
        details_frame.columnconfigure(2, weight=1)
        
        self.speed_var = tk.StringVar(value="Speed: 0 KB/s")
        speed_label = ttk.Label(details_frame, textvariable=self.speed_var)
        speed_label.grid(row=0, column=0, sticky=tk.W)
        
        self.eta_var = tk.StringVar(value="ETA: --:--")
        eta_label = ttk.Label(details_frame, textvariable=self.eta_var)
        eta_label.grid(row=0, column=1)
        
        self.size_var = tk.StringVar(value="0 MB / 0 MB")
        size_label = ttk.Label(details_frame, textvariable=self.size_var)
        size_label.grid(row=0, column=2, sticky=tk.E)
        
    def create_queue_section(self):
        """Create download queue section"""
        queue_frame = ttk.LabelFrame(self.frame, text="Download Queue", padding="10")
        queue_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        queue_frame.columnconfigure(0, weight=1)
        queue_frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(3, weight=1)
        
        # Treeview for queue
        columns = ('URL', 'Status', 'Size', 'Progress')
        self.queue_tree = ttk.Treeview(queue_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        self.queue_tree.heading('URL', text='URL')
        self.queue_tree.heading('Status', text='Status')
        self.queue_tree.heading('Size', text='Size')
        self.queue_tree.heading('Progress', text='Progress')
        
        self.queue_tree.column('URL', width=400)
        self.queue_tree.column('Status', width=100)
        self.queue_tree.column('Size', width=80)
        self.queue_tree.column('Progress', width=80)
        
        self.queue_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for treeview
        queue_scrollbar = ttk.Scrollbar(queue_frame, orient=tk.VERTICAL, command=self.queue_tree.yview)
        queue_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.queue_tree.config(yscrollcommand=queue_scrollbar.set)
        
        # Control buttons
        button_frame = ttk.Frame(queue_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        start_button = ttk.Button(button_frame, text="Start Downloads", command=self.start_downloads)
        start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        pause_button = ttk.Button(button_frame, text="Pause", command=self.pause_downloads)
        pause_button.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_button = ttk.Button(button_frame, text="Clear Completed", command=self.clear_completed)
        clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_button = ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected)
        remove_button.pack(side=tk.LEFT)
        
    def add_url_to_queue(self):
        """Add single URL to download queue"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Invalid Input", "Please enter a Terabox URL")
            return
            
        if not self.url_validator.is_valid_terabox_url(url):
            messagebox.showerror("Invalid URL", "Please enter a valid Terabox share URL")
            return
            
        # Add to queue in a separate thread
        threading.Thread(target=self._add_url_thread, args=(url,), daemon=True).start()
        self.url_var.set("")
        
    def add_batch_urls(self):
        """Add multiple URLs to download queue"""
        urls_text = self.batch_text.get("1.0", tk.END).strip()
        if not urls_text:
            messagebox.showwarning("Invalid Input", "Please enter Terabox URLs")
            return
            
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        valid_urls = []
        
        for url in urls:
            if self.url_validator.is_valid_terabox_url(url):
                valid_urls.append(url)
                
        if not valid_urls:
            messagebox.showerror("Invalid URLs", "No valid Terabox URLs found")
            return
            
        # Add URLs in a separate thread
        threading.Thread(target=self._add_batch_urls_thread, args=(valid_urls,), daemon=True).start()
        self.batch_text.delete("1.0", tk.END)
        
    def _add_url_thread(self, url):
        """Add URL to queue in background thread"""
        try:
            # Insert into queue tree
            item_id = self.queue_tree.insert('', 'end', values=(url, 'Pending', 'Unknown', '0%'))
            
            # Get file info from API
            file_info = self.terabox_api.get_file_info(url)
            if file_info:
                # Update tree with file info
                self.queue_tree.item(item_id, values=(
                    file_info.get('filename', url),
                    'Ready',
                    file_info.get('size_formatted', 'Unknown'),
                    '0%'
                ))
                
                # Add to download manager
                self.download_manager.add_download(url, file_info, item_id)
                
                # Auto-start if enabled
                if self.auto_start_var.get():
                    self.start_downloads()
            else:
                self.queue_tree.item(item_id, values=(url, 'Error', 'Unknown', 'Failed'))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add URL: {str(e)}")
            
    def _add_batch_urls_thread(self, urls):
        """Add multiple URLs to queue in background thread"""
        for url in urls:
            self._add_url_thread(url)
            
    def start_downloads(self):
        """Start all pending downloads"""
        download_dir = self.download_dir_var.get()
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create download directory: {str(e)}")
                return
                
        self.download_manager.set_download_directory(download_dir)
        self.download_manager.start_downloads(self.update_progress_callback)
        
    def pause_downloads(self):
        """Pause all active downloads"""
        self.download_manager.pause_downloads()
        
    def clear_completed(self):
        """Clear completed downloads from queue"""
        for item in self.queue_tree.get_children():
            values = self.queue_tree.item(item)['values']
            if len(values) > 1 and values[1] in ['Completed', 'Error']:
                self.queue_tree.delete(item)
                
    def remove_selected(self):
        """Remove selected item from queue"""
        selection = self.queue_tree.selection()
        if selection:
            for item in selection:
                self.queue_tree.delete(item)
                self.download_manager.remove_download(item)
                
    def browse_download_directory(self):
        """Browse and select download directory"""
        directory = filedialog.askdirectory(initialdir=self.download_dir_var.get())
        if directory:
            self.download_dir_var.set(directory)
            self.config.set('download_directory', directory)
            
    def update_progress_callback(self, item_id, progress_data):
        """Callback to update progress in GUI"""
        try:
            if item_id in [item for item in self.queue_tree.get_children()]:
                # Update progress in tree
                values = list(self.queue_tree.item(item_id)['values'])
                if len(values) >= 4:
                    values[1] = progress_data.get('status', 'Downloading')
                    values[3] = f"{progress_data.get('progress', 0):.1f}%"
                    self.queue_tree.item(item_id, values=values)
                    
                # Update current download display
                if progress_data.get('is_current', False):
                    self.current_file_var.set(progress_data.get('filename', 'Unknown'))
                    self.progress_var.set(progress_data.get('progress', 0))
                    self.speed_var.set(f"Speed: {progress_data.get('speed', '0 KB/s')}")
                    self.eta_var.set(f"ETA: {progress_data.get('eta', '--:--')}")
                    self.size_var.set(progress_data.get('size_info', '0 MB / 0 MB'))
                    
        except Exception as e:
            print(f"Progress update error: {e}")
