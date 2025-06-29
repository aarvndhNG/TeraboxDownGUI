#!/usr/bin/env python3
"""
Google Colab setup for Terabox Downloader
Provides both GUI and command-line interfaces for Colab environment
"""

import os
import sys

def setup_colab_environment():
    """Set up the environment for Google Colab"""
    print("Setting up Terabox Downloader for Google Colab...")
    
    # Install required packages
    os.system("pip install requests pillow")
    
    # Try to set up display for GUI (may not work in all Colab environments)
    try:
        os.system("apt-get update")
        os.system("apt-get install -y xvfb")
        os.environ['DISPLAY'] = ':99'
        os.system("Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &")
        print("✓ Display server set up")
    except:
        print("⚠ Display server setup failed - GUI mode may not work")
    
    print("✓ Environment setup complete")

def create_colab_interface():
    """Create a Colab-friendly interface"""
    from core.terabox_api import TeraboxAPI
    from core.config_manager import ConfigManager
    from utils.validators import URLValidator
    import requests
    
    class ColabTeraboxDownloader:
        def __init__(self):
            self.api = TeraboxAPI()
            self.config = ConfigManager()
            self.validator = URLValidator()
            
        def download_file(self, terabox_url, download_path="/content/downloads"):
            """Download a file from Terabox URL"""
            print(f"Processing URL: {terabox_url}")
            
            # Validate URL
            if not self.validator.is_valid_terabox_url(terabox_url):
                return False, "Invalid Terabox URL"
            
            # Get file info
            print("Getting file information...")
            file_info = self.api.get_file_info(terabox_url)
            
            if not file_info:
                return False, "Could not extract download link"
            
            # Create download directory
            os.makedirs(download_path, exist_ok=True)
            
            # Download file
            download_url = file_info['download_url']
            filename = file_info.get('filename', 'downloaded_file')
            filepath = os.path.join(download_path, filename)
            
            print(f"Downloading: {filename}")
            print(f"Size: {file_info.get('size_formatted', 'Unknown')}")
            
            try:
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Show progress
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                print(f"\rProgress: {progress:.1f}%", end="", flush=True)
                
                print(f"\n✓ Download complete: {filepath}")
                return True, filepath
                
            except Exception as e:
                return False, f"Download failed: {str(e)}"
    
    return ColabTeraboxDownloader()

def main():
    """Main function for Colab usage"""
    print("Terabox Downloader for Google Colab")
    print("=" * 40)
    
    # Set up environment
    setup_colab_environment()
    
    # Create downloader instance
    downloader = create_colab_interface()
    
    print("\nUsage example:")
    print("downloader.download_file('https://terabox.com/s/your-share-link')")
    print("\nFor multiple files:")
    print("urls = ['url1', 'url2', 'url3']")
    print("for url in urls:")
    print("    success, result = downloader.download_file(url)")
    print("    print(f'Downloaded: {result}' if success else f'Failed: {result}')")
    
    return downloader

if __name__ == "__main__":
    downloader = main()
