"""
Main Window for Terabox Downloader GUI
Contains the primary interface with tabbed layout
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from gui.download_tab import DownloadTab
from gui.viewer_tab import ViewerTab
from gui.history_tab import HistoryTab
from gui.settings_tab import SettingsTab
from core.config_manager import ConfigManager

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.config = ConfigManager()
        
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Configure the main window properties"""
        self.root.title("Terabox Downloader v1.0")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"1000x700+{x}+{y}")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        """Create and arrange the main interface widgets"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Create title label
        title_label = ttk.Label(
            main_frame, 
            text="Terabox File Downloader", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.download_tab = DownloadTab(self.notebook, self.config)
        self.viewer_tab = ViewerTab(self.notebook, self.config)
        self.history_tab = HistoryTab(self.notebook, self.config)
        self.settings_tab = SettingsTab(self.notebook, self.config)
        
        # Add tabs to notebook
        self.notebook.add(self.download_tab.frame, text="Download")
        self.notebook.add(self.viewer_tab.frame, text="File Viewer")
        self.notebook.add(self.history_tab.frame, text="History")
        self.notebook.add(self.settings_tab.frame, text="Settings")
        
        # Create status bar
        self.create_status_bar(main_frame)
        
    def create_status_bar(self, parent):
        """Create status bar at the bottom"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Version label
        version_label = ttk.Label(status_frame, text="v1.0", foreground="gray")
        version_label.grid(row=0, column=1, sticky=tk.E)
        
    def update_status(self, message):
        """Update the status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def on_closing(self):
        """Handle application closing"""
        try:
            # Cancel any ongoing downloads
            if hasattr(self.download_tab, 'download_manager'):
                self.download_tab.download_manager.cancel_all_downloads()
            
            # Save configuration
            self.config.save_config()
            
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
            self.root.destroy()
