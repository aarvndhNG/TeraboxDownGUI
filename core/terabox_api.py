"""
Terabox API Handler
Handles communication with Terabox API endpoints for link extraction
"""

import requests
import json
import re
from urllib.parse import urlparse, parse_qs
import time

class TeraboxAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Primary API endpoint (Ashlynn's free API)
        self.primary_api_url = "https://ashlynn.serv00.net/Ashlynnterabox.php"
        
        # Backup API endpoints
        self.backup_apis = [
            # Add more backup APIs here if available
        ]
        
    def get_file_info(self, terabox_url):
        """
        Extract file information from Terabox URL
        Returns dict with filename, size, download_url, etc.
        """
        try:
            # First try primary API
            result = self._try_api(self.primary_api_url, terabox_url)
            if result:
                return result
                
            # Try backup APIs
            for backup_url in self.backup_apis:
                result = self._try_api(backup_url, terabox_url)
                if result:
                    return result
                    
            return None
            
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
            
    def _try_api(self, api_url, terabox_url):
        """Try a specific API endpoint"""
        try:
            # Prepare request parameters
            params = {'url': terabox_url}
            
            # Make API request
            response = self.session.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse response
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
            else:
                # Try to parse as JSON anyway
                try:
                    data = json.loads(response.text)
                except:
                    # If not JSON, try to extract info from HTML/text response
                    return self._parse_html_response(response.text, terabox_url)
                    
            # Extract file information from JSON response
            return self._parse_json_response(data, terabox_url)
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except Exception as e:
            print(f"Error parsing API response: {e}")
            return None
            
    def _parse_json_response(self, data, original_url):
        """Parse JSON response from API"""
        try:
            # Common response formats
            if isinstance(data, dict):
                # Check for direct download link
                download_url = None
                filename = None
                file_size = None
                
                # Try different common field names
                possible_url_fields = ['download_url', 'url', 'direct_url', 'link', 'dlink']
                for field in possible_url_fields:
                    if field in data and data[field]:
                        download_url = data[field]
                        break
                        
                # Try different filename fields
                possible_name_fields = ['filename', 'name', 'title', 'server_filename']
                for field in possible_name_fields:
                    if field in data and data[field]:
                        filename = data[field]
                        break
                        
                # Try different size fields
                possible_size_fields = ['size', 'file_size', 'filesize']
                for field in possible_size_fields:
                    if field in data and data[field]:
                        file_size = data[field]
                        break
                        
                if download_url:
                    return {
                        'download_url': download_url,
                        'filename': filename or self._extract_filename_from_url(download_url),
                        'size': file_size,
                        'size_formatted': self._format_file_size(file_size) if file_size else 'Unknown',
                        'original_url': original_url,
                        'api_source': 'json_api'
                    }
                    
            elif isinstance(data, list) and len(data) > 0:
                # Handle array response
                return self._parse_json_response(data[0], original_url)
                
        except Exception as e:
            print(f"Error parsing JSON response: {e}")
            
        return None
        
    def _parse_html_response(self, html_content, original_url):
        """Parse HTML response to extract download links"""
        try:
            # Look for direct download links in HTML
            # This is a fallback for APIs that return HTML instead of JSON
            
            # Common patterns for download links
            download_patterns = [
                r'href="([^"]*terabox[^"]*)"',
                r'href="([^"]*\.(?:mp4|avi|mkv|pdf|zip|rar|doc|docx|jpg|png|gif)[^"]*)"',
                r'"download_url":"([^"]*)"',
                r'"url":"([^"]*)"'
            ]
            
            for pattern in download_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    download_url = matches[0]
                    if self._is_valid_download_url(download_url):
                        return {
                            'download_url': download_url,
                            'filename': self._extract_filename_from_url(download_url),
                            'size': None,
                            'size_formatted': 'Unknown',
                            'original_url': original_url,
                            'api_source': 'html_parser'
                        }
            
        except Exception as e:
            print(f"Error parsing HTML response: {e}")
            
        return None
        
    def _is_valid_download_url(self, url):
        """Check if URL is a valid download URL"""
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in ['http', 'https'] and
                parsed.netloc and
                not url.startswith('javascript:') and
                not url.startswith('#')
            )
        except:
            return False
            
    def _extract_filename_from_url(self, url):
        """Extract filename from URL"""
        try:
            parsed = urlparse(url)
            path = parsed.path
            
            # Get filename from path
            if '/' in path:
                filename = path.split('/')[-1]
            else:
                filename = path
                
            # Clean up filename
            if filename and '.' in filename:
                return filename
            else:
                # Generate a default filename
                return f"terabox_file_{int(time.time())}.bin"
                
        except:
            return f"terabox_file_{int(time.time())}.bin"
            
    def _format_file_size(self, size):
        """Format file size to human readable format"""
        try:
            if isinstance(size, str):
                # Try to extract number from string
                import re
                numbers = re.findall(r'\d+\.?\d*', size)
                if numbers:
                    size = float(numbers[0])
                    # Guess unit from string
                    if 'GB' in size.upper():
                        size *= 1024 * 1024 * 1024
                    elif 'MB' in size.upper():
                        size *= 1024 * 1024
                    elif 'KB' in size.upper():
                        size *= 1024
                else:
                    return size
                    
            if isinstance(size, (int, float)):
                if size >= 1024 * 1024 * 1024:
                    return f"{size / (1024 * 1024 * 1024):.2f} GB"
                elif size >= 1024 * 1024:
                    return f"{size / (1024 * 1024):.2f} MB"
                elif size >= 1024:
                    return f"{size / 1024:.2f} KB"
                else:
                    return f"{size} B"
                    
        except:
            pass
            
        return str(size) if size else 'Unknown'
        
    def test_connection(self, api_choice='Ashlynn Free API', custom_url='', api_key=''):
        """Test API connection"""
        try:
            if api_choice == "Custom API" and custom_url:
                test_url = custom_url
            else:
                test_url = self.primary_api_url
                
            # Make a simple request to test connectivity
            response = self.session.get(test_url, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"API test failed: {e}")
            return False
            
    def get_multiple_file_info(self, urls):
        """Get file info for multiple URLs"""
        results = []
        for url in urls:
            result = self.get_file_info(url)
            results.append(result)
            # Add small delay to avoid rate limiting
            time.sleep(0.5)
        return results
