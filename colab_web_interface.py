#!/usr/bin/env python3
"""
Web-based Terabox Downloader for Google Colab
Creates a simple web interface that works in Colab environment
"""

import os
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import html

class TeraboxWebHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.api = TeraboxAPI()
        self.validator = URLValidator()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_index()
        elif self.path == '/status':
            self.serve_status()
        elif self.path.startswith('/download'):
            self.handle_download_request()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == '/download':
            self.handle_download_post()
        else:
            self.send_error(404, "Not Found")

    def serve_index(self):
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Terabox Downloader - Colab Edition</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .header { text-align: center; margin-bottom: 30px; }
                .form-group { margin-bottom: 20px; }
                label { display: block; margin-bottom: 5px; font-weight: bold; }
                input[type="text"], textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
                button { background: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background: #45a049; }
                .status { margin-top: 20px; padding: 10px; border-radius: 4px; }
                .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
                .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
                .progress { background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }
                .file-list { margin-top: 20px; }
                .file-item { padding: 8px; border-bottom: 1px solid #eee; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📥 Terabox Downloader</h1>
                <p>Download files from Terabox share links in Google Colab</p>
            </div>
            
            <form id="downloadForm">
                <div class="form-group">
                    <label for="url">Terabox Share URL:</label>
                    <input type="text" id="url" name="url" placeholder="https://terabox.com/s/your-share-link" required>
                </div>
                
                <div class="form-group">
                    <label for="batch_urls">Or Multiple URLs (one per line):</label>
                    <textarea id="batch_urls" name="batch_urls" rows="5" placeholder="https://terabox.com/s/link1
https://terabox.com/s/link2
https://terabox.com/s/link3"></textarea>
                </div>
                
                <button type="submit">Download</button>
            </form>
            
            <div id="status"></div>
            <div id="downloads" class="file-list"></div>
            
            <script>
                document.getElementById('downloadForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    const url = document.getElementById('url').value.trim();
                    const batchUrls = document.getElementById('batch_urls').value.trim();
                    const statusDiv = document.getElementById('status');
                    
                    if (!url && !batchUrls) {
                        statusDiv.innerHTML = '<div class="status error">Please enter at least one URL</div>';
                        return;
                    }
                    
                    statusDiv.innerHTML = '<div class="status progress">Starting download...</div>';
                    
                    const formData = new FormData();
                    if (url) formData.append('url', url);
                    if (batchUrls) formData.append('batch_urls', batchUrls);
                    
                    fetch('/download', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            statusDiv.innerHTML = '<div class="status success">' + data.message + '</div>';
                            updateDownloadsList();
                        } else {
                            statusDiv.innerHTML = '<div class="status error">' + data.error + '</div>';
                        }
                    })
                    .catch(error => {
                        statusDiv.innerHTML = '<div class="status error">Error: ' + error.message + '</div>';
                    });
                });
                
                function updateDownloadsList() {
                    fetch('/status')
                    .then(response => response.json())
                    .then(data => {
                        const downloadsDiv = document.getElementById('downloads');
                        if (data.files && data.files.length > 0) {
                            let html = '<h3>Downloaded Files:</h3>';
                            data.files.forEach(file => {
                                html += '<div class="file-item">📄 ' + file.name + ' (' + file.size + ')</div>';
                            });
                            downloadsDiv.innerHTML = html;
                        }
                    });
                }
                
                // Auto-refresh downloads list every 5 seconds
                setInterval(updateDownloadsList, 5000);
                updateDownloadsList();
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())

    def handle_download_post(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Parse form data
        params = parse_qs(post_data)
        
        try:
            urls = []
            
            # Single URL
            if 'url' in params and params['url'][0].strip():
                urls.append(params['url'][0].strip())
            
            # Batch URLs
            if 'batch_urls' in params and params['batch_urls'][0].strip():
                batch_urls = [url.strip() for url in params['batch_urls'][0].strip().split('\n') if url.strip()]
                urls.extend(batch_urls)
            
            if not urls:
                self.send_json_response({'success': False, 'error': 'No URLs provided'})
                return
            
            # Start download in background thread
            threading.Thread(target=self.download_files, args=(urls,), daemon=True).start()
            
            self.send_json_response({
                'success': True, 
                'message': f'Started downloading {len(urls)} file(s)'
            })
            
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)})

    def download_files(self, urls):
        """Download files in background"""
        download_dir = "/content/downloads"
        os.makedirs(download_dir, exist_ok=True)
        
        for url in urls:
            try:
                if not self.validator.is_valid_terabox_url(url):
                    print(f"Invalid URL: {url}")
                    continue
                
                print(f"Processing: {url}")
                file_info = self.api.get_file_info(url)
                
                if not file_info:
                    print(f"Failed to get file info for: {url}")
                    continue
                
                download_url = file_info['download_url']
                filename = file_info.get('filename', 'unknown_file')
                filepath = os.path.join(download_dir, filename)
                
                print(f"Downloading: {filename}")
                
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f"Downloaded: {filepath}")
                
            except Exception as e:
                print(f"Error downloading {url}: {e}")

    def serve_status(self):
        """Serve status and file list"""
        download_dir = "/content/downloads"
        files = []
        
        if os.path.exists(download_dir):
            for filename in os.listdir(download_dir):
                filepath = os.path.join(download_dir, filename)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    size_mb = size / (1024 * 1024)
                    files.append({
                        'name': filename,
                        'size': f"{size_mb:.2f} MB"
                    })
        
        self.send_json_response({'files': files})

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        # Suppress default logging
        pass

class TeraboxAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.primary_api_url = "https://ashlynn.serv00.net/Ashlynnterabox.php"
        
    def get_file_info(self, terabox_url):
        try:
            response = self.session.get(self.primary_api_url, 
                                      params={'url': terabox_url}, 
                                      timeout=30)
            response.raise_for_status()
            
            try:
                data = response.json()
            except:
                return None
                
            return self._parse_response(data, terabox_url)
            
        except Exception as e:
            print(f"API Error: {e}")
            return None
            
    def _parse_response(self, data, original_url):
        if not isinstance(data, dict):
            return None
            
        download_url = None
        filename = None
        
        # Extract download URL
        for field in ['download_url', 'url', 'direct_url', 'link']:
            if field in data and data[field]:
                download_url = data[field]
                break
                
        # Extract filename
        for field in ['filename', 'name', 'title']:
            if field in data and data[field]:
                filename = data[field]
                break
                
        if download_url:
            return {
                'download_url': download_url,
                'filename': filename or f"terabox_file_{int(time.time())}.bin",
                'original_url': original_url
            }
            
        return None

class URLValidator:
    def __init__(self):
        self.terabox_domains = [
            'terabox.com', 'www.terabox.com', '1024terabox.com',
            'teraboxapp.com', 'nephobox.com', 'dubox.com'
        ]
        
    def is_valid_terabox_url(self, url):
        try:
            parsed = urlparse(url.lower())
            return any(domain in parsed.netloc for domain in self.terabox_domains)
        except:
            return False

def start_web_server(port=8000):
    """Start the web server"""
    server = HTTPServer(('0.0.0.0', port), TeraboxWebHandler)
    print(f"Terabox Downloader Web Interface starting on port {port}")
    print(f"Access it at: http://localhost:{port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    start_web_server()
