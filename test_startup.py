#!/usr/bin/env python3
"""
Test startup performance of Terabox GUI components
"""

import time
import tkinter as tk
from tkinter import ttk

def test_component(name, func):
    """Test a component and measure startup time"""
    print(f"Testing {name}...")
    start_time = time.time()
    try:
        result = func()
        end_time = time.time()
        print(f"✓ {name}: {end_time - start_time:.2f}s")
        return True, result
    except Exception as e:
        end_time = time.time()
        print(f"✗ {name}: {end_time - start_time:.2f}s - Error: {e}")
        return False, None

def test_config_manager():
    from core.config_manager import ConfigManager
    return ConfigManager()

def test_terabox_api():
    from core.terabox_api import TeraboxAPI
    return TeraboxAPI()

def test_download_manager():
    from core.config_manager import ConfigManager
    from core.download_manager import DownloadManager
    config = ConfigManager()
    return DownloadManager(config)

def test_validators():
    from utils.validators import URLValidator, FileValidator, InputValidator
    return URLValidator(), FileValidator(), InputValidator()

def test_file_utils():
    from utils.file_utils import FileUtils
    return FileUtils()

def test_basic_gui():
    root = tk.Tk()
    root.title("Test")
    root.geometry("400x300")
    root.withdraw()  # Don't show window
    notebook = ttk.Notebook(root)
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Test")
    root.destroy()
    return True

def main():
    print("Testing Terabox GUI startup components...")
    print("=" * 50)
    
    # Test each component
    success, config = test_component("ConfigManager", test_config_manager)
    test_component("TeraboxAPI", test_terabox_api)
    test_component("DownloadManager", test_download_manager)
    test_component("Validators", test_validators)
    test_component("FileUtils", test_file_utils)
    test_component("Basic GUI", test_basic_gui)
    
    print("=" * 50)
    print("Component testing complete.")

if __name__ == "__main__":
    main()
