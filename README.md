# Terabox Downloader GUI

A comprehensive Python application for downloading files from Terabox cloud storage service with both desktop GUI and Google Colab support.

## Features

- **Desktop GUI Application**: Full-featured tkinter interface with tabs for downloads, file viewing, history, and settings
- **Google Colab Support**: Jupyter notebook interface for cloud-based downloading
- **Web Interface**: Browser-based interface for Colab environments
- **Batch Downloads**: Download multiple files simultaneously
- **Progress Tracking**: Real-time download progress and statistics
- **File Viewer**: Built-in preview for images, text files, and media info
- **Download History**: Track all your downloads with search and filtering
- **Configurable Settings**: Customize download behavior, API settings, and interface preferences

## Installation & Usage

### Option 1: Desktop GUI (Recommended for Local Use)

#### Prerequisites
- Python 3.6 or higher
- tkinter (usually included with Python)

#### Setup
```bash
# Clone or download the files
# Install dependencies
pip install requests pillow

# Run the application
python main.py
```

The GUI will launch with four main tabs:
- **Download**: Add Terabox URLs and manage downloads
- **File Viewer**: Browse and preview downloaded files
- **History**: View download statistics and history
- **Settings**: Configure application preferences

### Option 2: Google Colab (Cloud-Based)

#### Quick Start
1. Upload the `Terabox_Downloader_Colab.ipynb` file to Google Colab
2. Open it in Colab and run the setup cell
3. Use the provided functions to download files

#### Example Usage in Colab
```python
# Single file download
terabox_url = "https://terabox.com/s/your-share-link"
success, result = downloader.download_file(terabox_url)

# Batch download
urls = [
    "https://terabox.com/s/link1",
    "https://terabox.com/s/link2",
    "https://terabox.com/s/link3"
]
results = downloader.download_multiple(urls)
```

#### Alternative: Web Interface in Colab
```python
# Run this in a Colab cell for a web interface
!python colab_web_interface.py &

# Then use the Colab's port forwarding to access the web interface
```

### Option 3: Command Line (Colab Setup)

```python
# Import the Colab setup
from colab_setup import main
downloader = main()

# Download files
success, filepath = downloader.download_file("https://terabox.com/s/your-link")
```

## Supported Terabox Domains

- terabox.com
- 1024terabox.com
- teraboxapp.com
- nephobox.com
- dubox.com
- 4funbox.com

## Configuration

### Desktop GUI Settings
The desktop application includes comprehensive settings:

- **Download Settings**: Directory, concurrent downloads, timeouts, retry attempts
- **Interface Settings**: Theme selection, window behavior
- **API Settings**: Choose between free APIs or configure custom endpoints
- **Advanced Settings**: Debug mode, history retention, temporary directories

### Colab Configuration
In Google Colab, downloads are saved to `/content/downloads/` by default. You can specify a different path:

```python
downloader.download_file(url, download_path="/content/my_downloads")
```

## API Information

This application uses free Terabox link extraction APIs:
- **Primary**: Ashlynn's Free API (https://ashlynn.serv00.net/Ashlynnterabox.php)
- **Backup**: Support for additional APIs can be configured

**Note**: These are third-party free services and may have limitations or occasional downtime.

## File Management

### Desktop Version
- Downloads saved to configured directory (default: ~/Downloads)
- Built-in file viewer supports images, text files, and media info
- File operations: open, delete, view in explorer

### Colab Version
- Files saved to `/content/downloads/`
- Files persist only during the Colab session
- Use the download-to-computer feature to save files locally
- Automatic zip creation for batch downloads

## Troubleshooting

### Desktop GUI Issues
- **Slow startup**: Fixed in recent version by optimizing file list loading
- **Download failures**: Check internet connection and URL validity
- **GUI not showing**: Ensure tkinter is installed and display is available

### Colab Issues
- **Module import errors**: Run the setup cell first
- **Download failures**: Verify Terabox URLs are valid share links
- **Storage full**: Colab has ~78GB storage limit
- **Session timeout**: Download files to your computer before session ends

### Common Solutions
1. **Invalid URL**: Ensure you're using a Terabox share link (contains `/s/` or `surl=`)
2. **Network errors**: Check internet connection and try again
3. **API unavailable**: The free APIs may have temporary outages
4. **File not found**: Some Terabox links may have expired or been removed

## Project Structure

```
terabox-downloader/
├── main.py                          # Desktop GUI entry point
├── gui/                            # GUI components
│   ├── main_window.py              # Main application window
│   ├── download_tab.py             # Download management tab
│   ├── viewer_tab.py               # File viewer tab
│   ├── history_tab.py              # Download history tab
│   └── settings_tab.py             # Settings configuration tab
├── core/                           # Core functionality
│   ├── config_manager.py           # Configuration management
│   ├── terabox_api.py              # API communication
│   ├── download_manager.py         # Download processing
│   └── file_viewer.py              # File viewing utilities
├── utils/                          # Utility modules
│   ├── file_utils.py               # File operations
│   └── validators.py               # URL and input validation
├── colab_setup.py                  # Google Colab setup script
├── colab_web_interface.py          # Web interface for Colab
└── Terabox_Downloader_Colab.ipynb  # Jupyter notebook for Colab
```

## Contributing

This is an open-source project. Feel free to:
- Report bugs or issues
- Suggest new features
- Submit improvements
- Add support for additional APIs

## Disclaimer

This tool is for educational and personal use only. Ensure you have permission to download files and comply with Terabox's terms of service. The developers are not responsible for any misuse of this application.

## GitHub Repository

This project is now fully configured as a GitHub repository with all necessary components:

### Repository Features
- ✅ Complete modular source code architecture
- ✅ Installation scripts (`setup.py`, `requirements-github.txt`)
- ✅ Comprehensive documentation and contribution guidelines
- ✅ MIT open-source license
- ✅ Proper Git configuration with `.gitignore`
- ✅ Multiple deployment options (desktop GUI and Google Colab)
- ✅ Cross-platform compatibility (Windows, macOS, Linux)

### Ready for GitHub Deployment
All files are prepared for immediate GitHub repository creation:
- Proper project structure and organization
- License and contribution documentation
- Installation and usage instructions
- Development setup guidelines
- Issue reporting templates

### Next Steps
1. Create a new repository on GitHub
2. Upload or push these files to your repository
3. Update GitHub URLs in `setup.py` and documentation
4. Share with the community!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and personal use only. Users are responsible for complying with Terabox's terms of service and applicable laws. The developers are not responsible for any misuse of this application.
