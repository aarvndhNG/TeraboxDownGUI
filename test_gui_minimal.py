#!/usr/bin/env python3
"""
Minimal GUI test to identify startup bottleneck
"""

import time
import tkinter as tk
from tkinter import ttk

def test_step(name, func):
    start = time.time()
    try:
        result = func()
        print(f"✓ {name}: {time.time() - start:.2f}s")
        return result
    except Exception as e:
        print(f"✗ {name}: {time.time() - start:.2f}s - {e}")
        return None

def main():
    print("Testing GUI startup steps...")
    
    # Step 1: Basic tkinter
    root = test_step("Creating root window", lambda: tk.Tk())
    if not root:
        return
    
    # Step 2: Configure window
    test_step("Setting up window", lambda: (
        root.title("Terabox Downloader v1.0"),
        root.geometry("1000x700"),
        root.minsize(800, 600)
    ))
    
    # Step 3: Create config
    config = test_step("Loading config", lambda: __import__('core.config_manager', fromlist=['ConfigManager']).ConfigManager())
    
    # Step 4: Create main frame
    main_frame = test_step("Creating main frame", lambda: ttk.Frame(root, padding="10"))
    if main_frame:
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Step 5: Create notebook
    notebook = test_step("Creating notebook", lambda: ttk.Notebook(main_frame))
    if notebook:
        notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Step 6: Test each tab creation
    test_step("Creating download tab", lambda: __import__('gui.download_tab', fromlist=['DownloadTab']).DownloadTab(notebook, config))
    test_step("Creating viewer tab", lambda: __import__('gui.viewer_tab', fromlist=['ViewerTab']).ViewerTab(notebook, config))
    test_step("Creating history tab", lambda: __import__('gui.history_tab', fromlist=['HistoryTab']).HistoryTab(notebook, config))
    test_step("Creating settings tab", lambda: __import__('gui.settings_tab', fromlist=['SettingsTab']).SettingsTab(notebook, config))
    
    print("Test complete - destroying window")
    root.destroy()

if __name__ == "__main__":
    main()
