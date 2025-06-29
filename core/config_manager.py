"""
Configuration Manager for Terabox Downloader
Handles application settings and configuration persistence
"""

import json
import os
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser('~'), '.terabox_downloader')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self.config_data = {}
        
        # Default configuration
        self.default_config = {
            # Download settings
            'download_directory': os.path.join(os.path.expanduser('~'), 'Downloads'),
            'max_concurrent_downloads': 2,
            'download_timeout': 120,
            'retry_attempts': 2,
            'auto_start_downloads': True,
            'open_after_download': False,
            'notify_completion': True,
            
            # Interface settings
            'theme': 'System Default',
            'remember_window': True,
            'minimize_to_tray': False,
            'start_minimized': False,
            'window_width': 1000,
            'window_height': 700,
            'window_x': None,
            'window_y': None,
            
            # API settings
            'api_choice': 'Ashlynn Free API',
            'custom_api_url': '',
            'api_key': '',
            'use_proxy': False,
            'proxy_url': '',
            
            # Advanced settings
            'debug_mode': False,
            'auto_update': True,
            'history_days': 90,
            'temp_directory': os.path.join(os.path.expanduser('~'), '.terabox_downloader', 'temp'),
            
            # Internal settings
            'first_run': True,
            'last_update_check': None,
            'total_downloads': 0,
            'total_data_downloaded': 0
        }
        
        self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        try:
            # Create config directory if it doesn't exist
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
                
            # Load existing config or create default
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                    
                # Merge with defaults to handle new settings
                self._merge_with_defaults()
            else:
                # First run - use defaults
                self.config_data = self.default_config.copy()
                self.save_config()
                
        except Exception as e:
            print(f"Error loading config: {e}")
            # Fall back to defaults
            self.config_data = self.default_config.copy()
            
    def save_config(self):
        """Save configuration to file"""
        try:
            # Ensure config directory exists
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
                
            # Write config file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config_data.get(key, default)
        
    def set(self, key, value):
        """Set configuration value"""
        self.config_data[key] = value
        
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.config_data = self.default_config.copy()
        self.save_config()
        
    def _merge_with_defaults(self):
        """Merge current config with defaults to add new settings"""
        for key, value in self.default_config.items():
            if key not in self.config_data:
                self.config_data[key] = value
                
    def export_config(self, filepath):
        """Export configuration to specified file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Failed to export config: {str(e)}")
            
    def import_config(self, filepath):
        """Import configuration from specified file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
                
            # Validate imported config
            if not isinstance(imported_config, dict):
                raise Exception("Invalid config file format")
                
            # Merge with current config
            self.config_data.update(imported_config)
            
            # Ensure all required keys exist
            self._merge_with_defaults()
            
            # Save the merged config
            self.save_config()
            
        except Exception as e:
            raise Exception(f"Failed to import config: {str(e)}")
            
    def get_download_directory(self):
        """Get download directory, create if doesn't exist"""
        download_dir = self.get('download_directory')
        try:
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
        except Exception as e:
            print(f"Error creating download directory: {e}")
            # Fall back to user's Downloads folder
            download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            self.set('download_directory', download_dir)
            
        return download_dir
        
    def get_temp_directory(self):
        """Get temp directory, create if doesn't exist"""
        temp_dir = self.get('temp_directory')
        try:
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
        except Exception as e:
            print(f"Error creating temp directory: {e}")
            # Fall back to system temp
            import tempfile
            temp_dir = tempfile.gettempdir()
            
        return temp_dir
        
    def increment_download_count(self):
        """Increment total download counter"""
        current = self.get('total_downloads', 0)
        self.set('total_downloads', current + 1)
        
    def add_downloaded_data(self, bytes_count):
        """Add to total downloaded data counter"""
        current = self.get('total_data_downloaded', 0)
        self.set('total_data_downloaded', current + bytes_count)
        
    def get_api_config(self):
        """Get API configuration"""
        return {
            'api_choice': self.get('api_choice', 'Ashlynn Free API'),
            'custom_api_url': self.get('custom_api_url', ''),
            'api_key': self.get('api_key', ''),
            'use_proxy': self.get('use_proxy', False),
            'proxy_url': self.get('proxy_url', '')
        }
        
    def get_window_geometry(self):
        """Get saved window geometry"""
        if self.get('remember_window', True):
            return {
                'width': self.get('window_width', 1000),
                'height': self.get('window_height', 700),
                'x': self.get('window_x'),
                'y': self.get('window_y')
            }
        return None
        
    def save_window_geometry(self, width, height, x, y):
        """Save window geometry"""
        if self.get('remember_window', True):
            self.set('window_width', width)
            self.set('window_height', height)
            self.set('window_x', x)
            self.set('window_y', y)
            
    def is_first_run(self):
        """Check if this is the first run"""
        return self.get('first_run', True)
        
    def mark_first_run_complete(self):
        """Mark first run as complete"""
        self.set('first_run', False)
        self.save_config()
        
    def cleanup_old_settings(self):
        """Remove deprecated or invalid settings"""
        # List of keys to remove if they exist
        deprecated_keys = []
        
        for key in deprecated_keys:
            if key in self.config_data:
                del self.config_data[key]
                
        # Validate current settings
        self._validate_settings()
        
    def _validate_settings(self):
        """Validate and fix invalid settings"""
        # Validate numeric settings
        numeric_settings = {
            'max_concurrent_downloads': (1, 10),
            'download_timeout': (30, 600),
            'retry_attempts': (0, 10),
            'history_days': (0, 9999),
            'window_width': (600, 3000),
            'window_height': (400, 2000)
        }
        
        for key, (min_val, max_val) in numeric_settings.items():
            current_val = self.get(key)
            if current_val is not None:
                try:
                    val = int(current_val)
                    if val < min_val or val > max_val:
                        self.set(key, self.default_config[key])
                except (ValueError, TypeError):
                    self.set(key, self.default_config[key])
                    
        # Validate directory paths
        directory_settings = ['download_directory', 'temp_directory']
        for key in directory_settings:
            path = self.get(key)
            if path and not isinstance(path, str):
                self.set(key, self.default_config[key])
                
        # Validate choice settings
        choice_settings = {
            'theme': ['System Default', 'Light', 'Dark'],
            'api_choice': ['Ashlynn Free API', 'Custom API']
        }
        
        for key, valid_choices in choice_settings.items():
            current_choice = self.get(key)
            if current_choice not in valid_choices:
                self.set(key, self.default_config[key])
