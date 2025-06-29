"""
Download Manager for Terabox Downloader
Handles file downloads with progress tracking and queue management
"""

import requests
import threading
import time
import os
from queue import Queue
from urllib.parse import urlparse
from core.terabox_api import TeraboxAPI

class DownloadManager:
    def __init__(self, config):
        self.config = config
        self.api = TeraboxAPI()
        
        self.download_queue = Queue()
        self.active_downloads = {}
        self.completed_downloads = []
        self.failed_downloads = []
        
        self.is_running = False
        self.is_paused = False
        self.max_concurrent = config.get('max_concurrent_downloads', 2)
        self.download_threads = []
        
        self.progress_callback = None
        self.download_directory = config.get('download_directory', os.path.expanduser('~/Downloads'))
        
    def add_download(self, url, file_info, item_id):
        """Add a download to the queue"""
        download_item = {
            'url': url,
            'file_info': file_info,
            'item_id': item_id,
            'status': 'pending',
            'progress': 0,
            'speed': 0,
            'eta': 0,
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'start_time': None,
            'thread': None
        }
        
        self.download_queue.put(download_item)
        
    def remove_download(self, item_id):
        """Remove a download from queue or cancel if active"""
        # Check active downloads
        if item_id in self.active_downloads:
            download = self.active_downloads[item_id]
            download['cancelled'] = True
            if download.get('thread'):
                # Thread will check cancelled flag and stop
                pass
            del self.active_downloads[item_id]
            
    def set_download_directory(self, directory):
        """Set the download directory"""
        self.download_directory = directory
        
    def start_downloads(self, progress_callback=None):
        """Start processing the download queue"""
        self.progress_callback = progress_callback
        self.is_running = True
        self.is_paused = False
        
        # Start worker threads
        for i in range(self.max_concurrent):
            thread = threading.Thread(target=self._download_worker, daemon=True)
            thread.start()
            self.download_threads.append(thread)
            
    def pause_downloads(self):
        """Pause all downloads"""
        self.is_paused = True
        
    def resume_downloads(self):
        """Resume paused downloads"""
        self.is_paused = False
        
    def cancel_all_downloads(self):
        """Cancel all downloads and stop manager"""
        self.is_running = False
        self.is_paused = False
        
        # Mark all active downloads as cancelled
        for download in self.active_downloads.values():
            download['cancelled'] = True
            
    def _download_worker(self):
        """Worker thread for processing downloads"""
        while self.is_running:
            try:
                # Wait for downloads to be available
                if self.download_queue.empty() or self.is_paused:
                    time.sleep(1)
                    continue
                    
                # Get next download
                download_item = self.download_queue.get(timeout=1)
                if not download_item:
                    continue
                    
                # Start download
                self._process_download(download_item)
                
            except Exception as e:
                print(f"Download worker error: {e}")
                time.sleep(1)
                
    def _process_download(self, download_item):
        """Process a single download"""
        item_id = download_item['item_id']
        
        try:
            # Add to active downloads
            download_item['thread'] = threading.current_thread()
            download_item['cancelled'] = False
            self.active_downloads[item_id] = download_item
            
            # Get file info if not already available
            file_info = download_item['file_info']
            if not file_info or not file_info.get('download_url'):
                self._update_progress(item_id, {'status': 'Getting download link...'})
                file_info = self.api.get_file_info(download_item['url'])
                if not file_info:
                    raise Exception("Failed to get download link")
                download_item['file_info'] = file_info
                
            # Prepare download
            download_url = file_info['download_url']
            filename = file_info.get('filename', 'unknown_file')
            filepath = os.path.join(self.download_directory, filename)
            
            # Handle filename conflicts
            filepath = self._get_unique_filepath(filepath)
            
            # Start download
            self._download_file(download_item, download_url, filepath)
            
        except Exception as e:
            # Handle download failure
            self._update_progress(item_id, {
                'status': 'Failed',
                'error': str(e)
            })
            self.failed_downloads.append(download_item)
            
        finally:
            # Remove from active downloads
            if item_id in self.active_downloads:
                del self.active_downloads[item_id]
                
    def _download_file(self, download_item, url, filepath):
        """Download file with progress tracking"""
        item_id = download_item['item_id']
        
        try:
            # Create session with headers
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            })
            
            # Start download with streaming
            response = session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size
            total_size = int(response.headers.get('content-length', 0))
            download_item['total_bytes'] = total_size
            
            # Update initial progress
            self._update_progress(item_id, {
                'status': 'Downloading',
                'total_bytes': total_size,
                'is_current': True
            })
            
            # Download file in chunks
            downloaded = 0
            start_time = time.time()
            download_item['start_time'] = start_time
            
            # Ensure download directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    # Check if cancelled
                    if download_item.get('cancelled'):
                        raise Exception("Download cancelled")
                        
                    # Check if paused
                    while self.is_paused and not download_item.get('cancelled'):
                        time.sleep(0.1)
                        
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress every few chunks
                        if downloaded % (8192 * 10) == 0 or downloaded == total_size:
                            current_time = time.time()
                            elapsed = current_time - start_time
                            
                            if elapsed > 0:
                                speed = downloaded / elapsed
                                eta = (total_size - downloaded) / speed if speed > 0 else 0
                                
                                progress = (downloaded / total_size * 100) if total_size > 0 else 0
                                
                                self._update_progress(item_id, {
                                    'status': 'Downloading',
                                    'progress': progress,
                                    'downloaded_bytes': downloaded,
                                    'total_bytes': total_size,
                                    'speed': self._format_speed(speed),
                                    'eta': self._format_time(eta),
                                    'size_info': f"{self._format_bytes(downloaded)} / {self._format_bytes(total_size)}",
                                    'is_current': True
                                })
                                
            # Download completed
            self._update_progress(item_id, {
                'status': 'Completed',
                'progress': 100,
                'is_current': False
            })
            
            self.completed_downloads.append(download_item)
            
            # Add to history
            if hasattr(self, 'history_callback'):
                duration = time.time() - start_time
                self.history_callback(
                    download_item['url'],
                    os.path.basename(filepath),
                    self._format_bytes(total_size),
                    'Completed',
                    duration
                )
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            # Clean up partial file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            raise e
            
    def _get_unique_filepath(self, filepath):
        """Get unique filepath to avoid overwrites"""
        if not os.path.exists(filepath):
            return filepath
            
        base, ext = os.path.splitext(filepath)
        counter = 1
        
        while True:
            new_filepath = f"{base} ({counter}){ext}"
            if not os.path.exists(new_filepath):
                return new_filepath
            counter += 1
            
    def _update_progress(self, item_id, progress_data):
        """Update progress and call callback"""
        if self.progress_callback:
            try:
                self.progress_callback(item_id, progress_data)
            except Exception as e:
                print(f"Progress callback error: {e}")
                
    def _format_speed(self, bytes_per_second):
        """Format download speed"""
        if bytes_per_second < 1024:
            return f"{bytes_per_second:.1f} B/s"
        elif bytes_per_second < 1024 * 1024:
            return f"{bytes_per_second / 1024:.1f} KB/s"
        else:
            return f"{bytes_per_second / (1024 * 1024):.1f} MB/s"
            
    def _format_bytes(self, bytes_count):
        """Format byte count to human readable"""
        if bytes_count < 1024:
            return f"{bytes_count} B"
        elif bytes_count < 1024 * 1024:
            return f"{bytes_count / 1024:.1f} KB"
        elif bytes_count < 1024 * 1024 * 1024:
            return f"{bytes_count / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_count / (1024 * 1024 * 1024):.1f} GB"
            
    def _format_time(self, seconds):
        """Format time in seconds to readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
            
    def get_queue_status(self):
        """Get current queue status"""
        return {
            'queued': self.download_queue.qsize(),
            'active': len(self.active_downloads),
            'completed': len(self.completed_downloads),
            'failed': len(self.failed_downloads),
            'is_running': self.is_running,
            'is_paused': self.is_paused
        }
