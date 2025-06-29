"""
Validators for Terabox Downloader
Contains validation functions for URLs, files, and other inputs
"""

import re
import os
from urllib.parse import urlparse, parse_qs
import requests

class URLValidator:
    def __init__(self):
        # Terabox domain patterns
        self.terabox_domains = [
            'terabox.com',
            'www.terabox.com',
            '1024terabox.com',
            'www.1024terabox.com',
            'teraboxapp.com',
            'www.teraboxapp.com',
            'nephobox.com',
            'www.nephobox.com',
            'dubox.com',
            'www.dubox.com',
            '4funbox.com',
            'www.4funbox.com'
        ]
        
        # Terabox URL patterns
        self.terabox_patterns = [
            r'https?://(?:www\.)?terabox\.com/s/[\w-]+',
            r'https?://(?:www\.)?terabox\.com/sharing/link\?surl=[\w-]+',
            r'https?://(?:www\.)?1024terabox\.com/s/[\w-]+',
            r'https?://(?:www\.)?teraboxapp\.com/s/[\w-]+',
            r'https?://(?:www\.)?nephobox\.com/s/[\w-]+',
            r'https?://(?:www\.)?dubox\.com/s/[\w-]+',
            r'https?://(?:www\.)?4funbox\.com/s/[\w-]+',
        ]
        
    def is_valid_url(self, url):
        """Check if URL is valid format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
            
    def is_valid_terabox_url(self, url):
        """Check if URL is a valid Terabox share URL"""
        if not self.is_valid_url(url):
            return False
            
        try:
            parsed = urlparse(url.lower())
            
            # Check domain
            if not any(domain in parsed.netloc for domain in self.terabox_domains):
                return False
                
            # Check URL pattern
            for pattern in self.terabox_patterns:
                if re.match(pattern, url, re.IGNORECASE):
                    return True
                    
            # Additional checks for common Terabox URL formats
            if '/s/' in parsed.path or 'surl=' in parsed.query:
                return True
                
            return False
            
        except Exception:
            return False
            
    def extract_terabox_id(self, url):
        """Extract Terabox share ID from URL"""
        try:
            parsed = urlparse(url)
            
            # Check for /s/ format
            if '/s/' in parsed.path:
                return parsed.path.split('/s/')[-1].split('/')[0]
                
            # Check for surl parameter
            query_params = parse_qs(parsed.query)
            if 'surl' in query_params:
                return query_params['surl'][0]
                
            return None
            
        except Exception:
            return None
            
    def normalize_terabox_url(self, url):
        """Normalize Terabox URL to standard format"""
        try:
            if not self.is_valid_terabox_url(url):
                return None
                
            share_id = self.extract_terabox_id(url)
            if share_id:
                return f"https://terabox.com/s/{share_id}"
                
            return url
            
        except Exception:
            return None
            
    def validate_multiple_urls(self, urls_text):
        """Validate multiple URLs from text input"""
        if not urls_text or not urls_text.strip():
            return [], ["No URLs provided"]
            
        lines = [line.strip() for line in urls_text.strip().split('\n')]
        valid_urls = []
        errors = []
        
        for i, line in enumerate(lines, 1):
            if not line:
                continue
                
            if self.is_valid_terabox_url(line):
                normalized = self.normalize_terabox_url(line)
                if normalized:
                    valid_urls.append(normalized)
                else:
                    errors.append(f"Line {i}: Could not normalize URL")
            else:
                errors.append(f"Line {i}: Invalid Terabox URL - {line[:50]}...")
                
        return valid_urls, errors
        
    def check_url_accessibility(self, url, timeout=10):
        """Check if URL is accessible"""
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            return response.status_code == 200
        except Exception:
            return False


class FileValidator:
    def __init__(self):
        self.max_filename_length = 255
        self.forbidden_chars = ['<', '>', ':', '"', '|', '?', '*']
        self.reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
    def is_valid_filename(self, filename):
        """Check if filename is valid for the current OS"""
        if not filename or not filename.strip():
            return False, "Filename cannot be empty"
            
        filename = filename.strip()
        
        # Check length
        if len(filename) > self.max_filename_length:
            return False, f"Filename too long (max {self.max_filename_length} characters)"
            
        # Check forbidden characters
        for char in self.forbidden_chars:
            if char in filename:
                return False, f"Filename contains forbidden character: {char}"
                
        # Check for control characters
        if any(ord(char) < 32 for char in filename):
            return False, "Filename contains control characters"
            
        # Check reserved names (Windows)
        name_without_ext = os.path.splitext(filename)[0].upper()
        if name_without_ext in self.reserved_names:
            return False, f"Filename uses reserved name: {name_without_ext}"
            
        # Check for trailing dots or spaces (Windows)
        if filename.endswith('.') or filename.endswith(' '):
            return False, "Filename cannot end with dot or space"
            
        return True, ""
        
    def sanitize_filename(self, filename):
        """Sanitize filename to make it valid"""
        if not filename:
            return "untitled"
            
        # Remove or replace forbidden characters
        for char in self.forbidden_chars:
            filename = filename.replace(char, '_')
            
        # Remove control characters
        filename = ''.join(char for char in filename if ord(char) >= 32)
        
        # Remove trailing dots and spaces
        filename = filename.rstrip('. ')
        
        # Handle reserved names
        name_part, ext = os.path.splitext(filename)
        if name_part.upper() in self.reserved_names:
            filename = f"{name_part}_file{ext}"
            
        # Truncate if too long
        if len(filename) > self.max_filename_length:
            name_part, ext = os.path.splitext(filename)
            max_name_length = self.max_filename_length - len(ext)
            filename = name_part[:max_name_length] + ext
            
        # Ensure not empty
        if not filename.strip():
            filename = "untitled"
            
        return filename
        
    def is_valid_directory_path(self, path):
        """Check if directory path is valid"""
        if not path:
            return False, "Path cannot be empty"
            
        try:
            # Check if path is absolute
            if not os.path.isabs(path):
                return False, "Path must be absolute"
                
            # Check if parent directories exist or can be created
            parent = os.path.dirname(path)
            if parent and not os.path.exists(parent):
                return False, f"Parent directory does not exist: {parent}"
                
            # Check permissions
            if os.path.exists(path):
                if not os.path.isdir(path):
                    return False, "Path exists but is not a directory"
                if not os.access(path, os.W_OK):
                    return False, "No write permission for directory"
            else:
                # Check if we can create the directory
                try:
                    os.makedirs(path, exist_ok=True)
                    os.rmdir(path)  # Clean up test directory
                except Exception as e:
                    return False, f"Cannot create directory: {str(e)}"
                    
            return True, ""
            
        except Exception as e:
            return False, f"Invalid path: {str(e)}"


class InputValidator:
    def __init__(self):
        pass
        
    def validate_positive_integer(self, value, min_val=1, max_val=None):
        """Validate positive integer input"""
        try:
            int_val = int(value)
            if int_val < min_val:
                return False, f"Value must be at least {min_val}"
            if max_val and int_val > max_val:
                return False, f"Value must be at most {max_val}"
            return True, int_val
        except (ValueError, TypeError):
            return False, "Must be a valid integer"
            
    def validate_timeout(self, value):
        """Validate timeout value"""
        valid, result = self.validate_positive_integer(value, 10, 3600)
        if not valid:
            return False, "Timeout must be between 10 and 3600 seconds"
        return True, result
        
    def validate_concurrent_downloads(self, value):
        """Validate concurrent downloads count"""
        valid, result = self.validate_positive_integer(value, 1, 10)
        if not valid:
            return False, "Concurrent downloads must be between 1 and 10"
        return True, result
        
    def validate_retry_count(self, value):
        """Validate retry count"""
        valid, result = self.validate_positive_integer(value, 0, 10)
        if not valid:
            return False, "Retry count must be between 0 and 10"
        return True, result
        
    def validate_proxy_url(self, url):
        """Validate proxy URL format"""
        if not url or not url.strip():
            return True, ""  # Empty is valid (no proxy)
            
        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                return False, "Proxy URL must include protocol (http:// or https://)"
            if not parsed.netloc:
                return False, "Proxy URL must include host"
            if parsed.scheme not in ['http', 'https', 'socks4', 'socks5']:
                return False, "Proxy protocol must be http, https, socks4, or socks5"
            return True, url
        except Exception:
            return False, "Invalid proxy URL format"
            
    def validate_api_key(self, api_key):
        """Validate API key format"""
        if not api_key or not api_key.strip():
            return True, ""  # Empty is valid for free APIs
            
        # Basic validation - not empty and reasonable length
        api_key = api_key.strip()
        if len(api_key) < 8:
            return False, "API key seems too short"
        if len(api_key) > 256:
            return False, "API key seems too long"
            
        return True, api_key
