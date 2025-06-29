#!/usr/bin/env python3
"""
Terabox Downloader GUI Application
Main entry point for the application
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
from gui.main_window import MainWindow

def main():
    """Main application entry point"""
    try:
        # Create the main application window
        root = tk.Tk()
        app = MainWindow(root)
        
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
