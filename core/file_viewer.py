"""
File Viewer for Terabox Downloader
Handles viewing of different file types
"""

import os
import subprocess
import platform
from PIL import Image, ImageTk
import tkinter as tk

class FileViewer:
    def __init__(self):
        self.supported_image_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        self.supported_text_formats = {'.txt', '.log', '.csv', '.json', '.xml', '.html', '.css', '.js', '.py', '.md'}
        self.supported_video_formats = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
        self.supported_audio_formats = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'}
        
    def can_preview(self, filepath):
        """Check if file can be previewed in the application"""
        ext = os.path.splitext(filepath)[1].lower()
        return (ext in self.supported_image_formats or 
                ext in self.supported_text_formats)
                
    def get_file_type(self, filepath):
        """Get the type of file"""
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext in self.supported_image_formats:
            return 'image'
        elif ext in self.supported_text_formats:
            return 'text'
        elif ext in self.supported_video_formats:
            return 'video'
        elif ext in self.supported_audio_formats:
            return 'audio'
        elif ext in {'.pdf'}:
            return 'document'
        elif ext in {'.zip', '.rar', '.7z', '.tar', '.gz'}:
            return 'archive'
        else:
            return 'unknown'
            
    def view_image(self, filepath, max_width=600, max_height=400):
        """View image file and return PhotoImage object"""
        try:
            # Open image with PIL
            image = Image.open(filepath)
            
            # Get original size
            original_width, original_height = image.size
            
            # Calculate scaling to fit within max dimensions
            scale_w = max_width / original_width
            scale_h = max_height / original_height
            scale = min(scale_w, scale_h, 1.0)  # Don't upscale
            
            if scale < 1.0:
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            return photo, image.size
            
        except Exception as e:
            print(f"Error viewing image: {e}")
            return None, None
            
    def read_text_file(self, filepath, max_size=1024*1024):  # 1MB limit
        """Read text file content"""
        try:
            # Check file size
            file_size = os.path.getsize(filepath)
            if file_size > max_size:
                return f"File too large to preview ({file_size:,} bytes). Maximum preview size is {max_size:,} bytes."
                
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        content = f.read()
                    return content
                except UnicodeDecodeError:
                    continue
                    
            # If all encodings fail, read as binary and decode with errors ignored
            with open(filepath, 'rb') as f:
                content = f.read()
            return content.decode('utf-8', errors='ignore')
            
        except Exception as e:
            return f"Error reading file: {str(e)}"
            
    def get_media_info(self, filepath):
        """Get media file information"""
        try:
            stat = os.stat(filepath)
            file_type = self.get_file_type(filepath)
            
            info = {
                'filename': os.path.basename(filepath),
                'size': stat.st_size,
                'size_formatted': self._format_file_size(stat.st_size),
                'modified': stat.st_mtime,
                'type': file_type,
                'extension': os.path.splitext(filepath)[1].lower()
            }
            
            # Try to get additional info for media files
            if file_type in ['video', 'audio']:
                info.update(self._get_media_details(filepath))
                
            return info
            
        except Exception as e:
            return {'error': str(e)}
            
    def _get_media_details(self, filepath):
        """Get detailed media file information"""
        # Basic implementation without external dependencies
        # In a full implementation, you might use libraries like ffprobe
        details = {}
        
        try:
            # Get basic file info
            stat = os.stat(filepath)
            details['duration'] = 'Unknown'
            details['format'] = os.path.splitext(filepath)[1][1:].upper()
            details['bitrate'] = 'Unknown'
            
            # For video files, try to get resolution from filename if available
            filename = os.path.basename(filepath).lower()
            if any(res in filename for res in ['720p', '1080p', '4k', '480p']):
                for res in ['480p', '720p', '1080p', '4k']:
                    if res in filename:
                        details['resolution'] = res
                        break
            else:
                details['resolution'] = 'Unknown'
                
        except Exception as e:
            details['error'] = str(e)
            
        return details
        
    def open_with_system_default(self, filepath):
        """Open file with system's default application"""
        try:
            system = platform.system()
            
            if system == 'Windows':
                os.startfile(filepath)
            elif system == 'Darwin':  # macOS
                subprocess.call(['open', filepath])
            else:  # Linux and others
                subprocess.call(['xdg-open', filepath])
                
            return True
            
        except Exception as e:
            print(f"Error opening file with system default: {e}")
            return False
            
    def open_file_location(self, filepath):
        """Open file location in system file manager"""
        try:
            directory = os.path.dirname(filepath)
            system = platform.system()
            
            if system == 'Windows':
                subprocess.call(['explorer', '/select,', filepath])
            elif system == 'Darwin':  # macOS
                subprocess.call(['open', '-R', filepath])
            else:  # Linux
                subprocess.call(['xdg-open', directory])
                
            return True
            
        except Exception as e:
            print(f"Error opening file location: {e}")
            return False
            
    def _format_file_size(self, size_bytes):
        """Format file size to human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
            
    def is_safe_to_preview(self, filepath, max_size=10*1024*1024):  # 10MB limit
        """Check if file is safe to preview (not too large)"""
        try:
            size = os.path.getsize(filepath)
            return size <= max_size
        except:
            return False
            
    def get_preview_text(self, filepath, lines=50):
        """Get preview text for large files"""
        try:
            preview_lines = []
            line_count = 0
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    preview_lines.append(line.rstrip())
                    line_count += 1
                    if line_count >= lines:
                        break
                        
            preview_text = '\n'.join(preview_lines)
            
            # Check if there are more lines
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                total_lines = sum(1 for _ in f)
                
            if total_lines > lines:
                preview_text += f"\n\n... (showing first {lines} lines of {total_lines} total lines)"
                
            return preview_text
            
        except Exception as e:
            return f"Error reading file preview: {str(e)}"
