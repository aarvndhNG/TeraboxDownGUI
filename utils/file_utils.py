"""
File utilities for Terabox Downloader
Contains helper functions for file operations and formatting
"""

import os
import time
import mimetypes
import hashlib
from datetime import datetime
from pathlib import Path

class FileUtils:
    def __init__(self):
        # File type mappings
        self.image_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
            '.webp', '.svg', '.ico', '.psd', '.raw', '.heic', '.heif'
        }
        
        self.video_extensions = {
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
            '.m4v', '.3gp', '.ts', '.mts', '.vob', '.ogv', '.rm', '.rmvb'
        }
        
        self.audio_extensions = {
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
            '.opus', '.aiff', '.au', '.ra', '.amr', '.ac3'
        }
        
        self.document_extensions = {
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.odt', '.ods', '.odp', '.rtf', '.pages', '.numbers', '.key'
        }
        
        self.archive_extensions = {
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',
            '.tar.gz', '.tar.bz2', '.tar.xz', '.dmg', '.iso'
        }
        
        self.code_extensions = {
            '.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h',
            '.php', '.rb', '.go', '.rs', '.kt', '.swift', '.ts', '.jsx',
            '.tsx', '.vue', '.scss', '.sass', '.less', '.sql', '.sh'
        }
        
        self.text_extensions = {
            '.txt', '.log', '.md', '.rst', '.json', '.xml', '.yaml',
            '.yml', '.csv', '.ini', '.cfg', '.conf', '.env'
        }
        
    def get_file_type(self, filename):
        """Get the general type of file based on extension"""
        if not filename:
            return 'Unknown'
            
        ext = os.path.splitext(filename.lower())[1]
        
        if ext in self.image_extensions:
            return 'Image'
        elif ext in self.video_extensions:
            return 'Video'
        elif ext in self.audio_extensions:
            return 'Audio'
        elif ext in self.document_extensions:
            return 'Document'
        elif ext in self.archive_extensions:
            return 'Archive'
        elif ext in self.code_extensions:
            return 'Code'
        elif ext in self.text_extensions:
            return 'Text'
        else:
            return 'Other'
            
    def get_mime_type(self, filename):
        """Get MIME type of file"""
        try:
            mime_type, _ = mimetypes.guess_type(filename)
            return mime_type or 'application/octet-stream'
        except:
            return 'application/octet-stream'
            
    def format_file_size(self, size_bytes):
        """Format file size to human-readable format"""
        if size_bytes == 0:
            return "0 B"
            
        try:
            size_bytes = int(size_bytes)
        except (ValueError, TypeError):
            return "Unknown"
            
        # Define size units
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
            
        # Format with appropriate decimal places
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        elif size >= 100:
            return f"{size:.0f} {units[unit_index]}"
        elif size >= 10:
            return f"{size:.1f} {units[unit_index]}"
        else:
            return f"{size:.2f} {units[unit_index]}"
            
    def format_timestamp(self, timestamp):
        """Format timestamp to readable date/time"""
        try:
            if isinstance(timestamp, str):
                # Try to parse string timestamp
                try:
                    timestamp = float(timestamp)
                except ValueError:
                    return timestamp
                    
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, OSError, TypeError):
            return 'Unknown'
            
    def format_duration(self, seconds):
        """Format duration in seconds to readable format"""
        try:
            seconds = int(float(seconds))
            
            if seconds < 60:
                return f"{seconds}s"
            elif seconds < 3600:
                minutes = seconds // 60
                secs = seconds % 60
                return f"{minutes}m {secs}s"
            else:
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                return f"{hours}h {minutes}m"
        except (ValueError, TypeError):
            return "Unknown"
            
    def get_file_info(self, filepath):
        """Get comprehensive file information"""
        try:
            if not os.path.exists(filepath):
                return None
                
            stat = os.stat(filepath)
            
            return {
                'name': os.path.basename(filepath),
                'path': filepath,
                'size': stat.st_size,
                'size_formatted': self.format_file_size(stat.st_size),
                'modified': stat.st_mtime,
                'modified_formatted': self.format_timestamp(stat.st_mtime),
                'created': stat.st_ctime,
                'created_formatted': self.format_timestamp(stat.st_ctime),
                'type': self.get_file_type(filepath),
                'mime_type': self.get_mime_type(filepath),
                'extension': os.path.splitext(filepath)[1].lower(),
                'is_file': os.path.isfile(filepath),
                'is_dir': os.path.isdir(filepath),
                'readable': os.access(filepath, os.R_OK),
                'writable': os.access(filepath, os.W_OK),
                'executable': os.access(filepath, os.X_OK)
            }
        except Exception as e:
            return {'error': str(e)}
            
    def create_unique_filename(self, directory, filename):
        """Create a unique filename to avoid conflicts"""
        base_path = os.path.join(directory, filename)
        
        if not os.path.exists(base_path):
            return filename
            
        name, ext = os.path.splitext(filename)
        counter = 1
        
        while True:
            new_filename = f"{name} ({counter}){ext}"
            new_path = os.path.join(directory, new_filename)
            
            if not os.path.exists(new_path):
                return new_filename
                
            counter += 1
            
            # Safety limit
            if counter > 9999:
                # Use timestamp as fallback
                timestamp = int(time.time())
                return f"{name}_{timestamp}{ext}"
                
    def safe_delete(self, filepath):
        """Safely delete a file with error handling"""
        try:
            if os.path.exists(filepath):
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    return True, f"File deleted: {os.path.basename(filepath)}"
                else:
                    return False, "Path is not a file"
            else:
                return False, "File does not exist"
        except PermissionError:
            return False, "Permission denied"
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def get_directory_size(self, directory):
        """Get total size of directory and all subdirectories"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue
        except Exception:
            pass
        return total_size
        
    def clean_filename(self, filename):
        """Clean filename by removing invalid characters"""
        if not filename:
            return "untitled"
            
        # Remove or replace problematic characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
            
        # Remove control characters
        filename = ''.join(char for char in filename if ord(char) >= 32)
        
        # Remove multiple spaces and leading/trailing whitespace
        filename = ' '.join(filename.split())
        
        # Remove leading/trailing dots (Windows issue)
        filename = filename.strip('.')
        
        # Ensure not empty
        if not filename:
            filename = "untitled"
            
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
            
        return filename
        
    def calculate_file_hash(self, filepath, algorithm='md5', chunk_size=8192):
        """Calculate hash of file"""
        try:
            hash_obj = hashlib.new(algorithm)
            
            with open(filepath, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hash_obj.update(chunk)
                    
            return hash_obj.hexdigest()
        except Exception as e:
            return None
            
    def is_text_file(self, filepath, sample_size=1024):
        """Check if file is likely a text file"""
        try:
            with open(filepath, 'rb') as f:
                sample = f.read(sample_size)
                
            # Check for null bytes (binary indicator)
            if b'\x00' in sample:
                return False
                
            # Try to decode as text
            try:
                sample.decode('utf-8')
                return True
            except UnicodeDecodeError:
                try:
                    sample.decode('latin-1')
                    return True
                except UnicodeDecodeError:
                    return False
                    
        except Exception:
            return False
            
    def get_available_space(self, path):
        """Get available disk space for given path"""
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(path),
                    ctypes.pointer(free_bytes),
                    None,
                    None
                )
                return free_bytes.value
            else:  # Unix-like
                statvfs = os.statvfs(path)
                return statvfs.f_frsize * statvfs.f_available
        except Exception:
            return None
            
    def ensure_directory_exists(self, directory):
        """Ensure directory exists, create if necessary"""
        try:
            os.makedirs(directory, exist_ok=True)
            return True, ""
        except PermissionError:
            return False, "Permission denied"
        except Exception as e:
            return False, str(e)
            
    def move_to_trash(self, filepath):
        """Move file to system trash/recycle bin"""
        try:
            # Try to use system-specific trash
            if os.name == 'nt':  # Windows
                import ctypes
                from ctypes import wintypes
                
                # Use Windows API to move to recycle bin
                result = ctypes.windll.shell32.SHFileOperationW(None)
                return result == 0
            else:
                # For Unix-like systems, try to use 'trash' command
                import subprocess
                try:
                    subprocess.run(['trash', filepath], check=True)
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # Fallback to regular delete
                    os.remove(filepath)
                    return True
        except Exception:
            return False
            
    def get_temp_filepath(self, filename, temp_dir=None):
        """Get a temporary file path"""
        if temp_dir is None:
            import tempfile
            temp_dir = tempfile.gettempdir()
            
        # Create unique temp filename
        base, ext = os.path.splitext(filename)
        timestamp = int(time.time())
        temp_filename = f"{base}_{timestamp}{ext}"
        
        return os.path.join(temp_dir, temp_filename)
