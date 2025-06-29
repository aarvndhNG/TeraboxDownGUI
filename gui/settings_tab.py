"""
Settings Tab for Terabox Downloader
Manages application configuration and preferences
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class SettingsTab:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        
        self.create_widgets()
        self.load_settings()
        
    def create_widgets(self):
        """Create and arrange the settings tab widgets"""
        self.frame = ttk.Frame(self.parent)
        self.frame.columnconfigure(0, weight=1)
        
        # Create scrollable frame
        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.frame.rowconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(0, weight=1)
        
        # Create setting sections
        self.create_download_settings()
        self.create_interface_settings()
        self.create_api_settings()
        self.create_advanced_settings()
        self.create_action_buttons()
        
    def create_download_settings(self):
        """Create download-related settings"""
        download_frame = ttk.LabelFrame(self.scrollable_frame, text="Download Settings", padding="10")
        download_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        download_frame.columnconfigure(1, weight=1)
        
        # Default download directory
        ttk.Label(download_frame, text="Default Download Directory:").grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 5), pady=(0, 5))
        
        self.download_dir_var = tk.StringVar()
        dir_frame = ttk.Frame(download_frame)
        dir_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        dir_frame.columnconfigure(0, weight=1)
        
        dir_entry = ttk.Entry(dir_frame, textvariable=self.download_dir_var, width=50)
        dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_button = ttk.Button(dir_frame, text="Browse", command=self.browse_download_directory)
        browse_button.grid(row=0, column=1)
        
        # Maximum concurrent downloads
        ttk.Label(download_frame, text="Max Concurrent Downloads:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        
        self.max_downloads_var = tk.IntVar()
        max_downloads_spin = ttk.Spinbox(download_frame, from_=1, to=5, textvariable=self.max_downloads_var, width=10)
        max_downloads_spin.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # Download timeout
        ttk.Label(download_frame, text="Download Timeout (seconds):").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        
        self.timeout_var = tk.IntVar()
        timeout_spin = ttk.Spinbox(download_frame, from_=30, to=300, increment=30, textvariable=self.timeout_var, width=10)
        timeout_spin.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
        # Retry attempts
        ttk.Label(download_frame, text="Retry Attempts:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        
        self.retry_var = tk.IntVar()
        retry_spin = ttk.Spinbox(download_frame, from_=0, to=5, textvariable=self.retry_var, width=10)
        retry_spin.grid(row=3, column=1, sticky=tk.W, pady=(5, 0))
        
        # Auto options
        self.auto_start_var = tk.BooleanVar()
        auto_start_check = ttk.Checkbutton(download_frame, text="Auto-start downloads when added", variable=self.auto_start_var)
        auto_start_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        self.open_after_download_var = tk.BooleanVar()
        open_check = ttk.Checkbutton(download_frame, text="Open file location after successful download", variable=self.open_after_download_var)
        open_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        self.notify_completion_var = tk.BooleanVar()
        notify_check = ttk.Checkbutton(download_frame, text="Show notification on download completion", variable=self.notify_completion_var)
        notify_check.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
    def create_interface_settings(self):
        """Create interface-related settings"""
        interface_frame = ttk.LabelFrame(self.scrollable_frame, text="Interface Settings", padding="10")
        interface_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        interface_frame.columnconfigure(1, weight=1)
        
        # Theme selection
        ttk.Label(interface_frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=(0, 5))
        
        self.theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(interface_frame, textvariable=self.theme_var, 
                                  values=["System Default", "Light", "Dark"], 
                                  state="readonly", width=20)
        theme_combo.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        # Window settings
        self.remember_window_var = tk.BooleanVar()
        remember_check = ttk.Checkbutton(interface_frame, text="Remember window size and position", variable=self.remember_window_var)
        remember_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        self.minimize_to_tray_var = tk.BooleanVar()
        tray_check = ttk.Checkbutton(interface_frame, text="Minimize to system tray", variable=self.minimize_to_tray_var)
        tray_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        self.start_minimized_var = tk.BooleanVar()
        start_min_check = ttk.Checkbutton(interface_frame, text="Start minimized", variable=self.start_minimized_var)
        start_min_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
    def create_api_settings(self):
        """Create API-related settings"""
        api_frame = ttk.LabelFrame(self.scrollable_frame, text="API Settings", padding="10")
        api_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        api_frame.columnconfigure(1, weight=1)
        
        # API selection
        ttk.Label(api_frame, text="Primary API:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=(0, 5))
        
        self.api_choice_var = tk.StringVar()
        api_combo = ttk.Combobox(api_frame, textvariable=self.api_choice_var,
                                values=["Ashlynn Free API", "Custom API"], 
                                state="readonly", width=25)
        api_combo.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        api_combo.bind('<<ComboboxSelected>>', self.on_api_selection_change)
        
        # Custom API URL
        ttk.Label(api_frame, text="Custom API URL:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        
        self.custom_api_var = tk.StringVar()
        self.custom_api_entry = ttk.Entry(api_frame, textvariable=self.custom_api_var, width=60)
        self.custom_api_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # API Key
        ttk.Label(api_frame, text="API Key (if required):").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, show="*", width=60)
        self.api_key_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Test API button
        test_button = ttk.Button(api_frame, text="Test API Connection", command=self.test_api_connection)
        test_button.grid(row=3, column=1, sticky=tk.W, pady=(10, 0))
        
        # Use proxy
        self.use_proxy_var = tk.BooleanVar()
        proxy_check = ttk.Checkbutton(api_frame, text="Use proxy for API requests", variable=self.use_proxy_var)
        proxy_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        proxy_check.bind('<Button-1>', self.toggle_proxy_settings)
        
        # Proxy settings frame
        self.proxy_frame = ttk.Frame(api_frame)
        self.proxy_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        self.proxy_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.proxy_frame, text="Proxy URL:").grid(row=0, column=0, sticky=tk.W, padx=(20, 5))
        
        self.proxy_url_var = tk.StringVar()
        proxy_entry = ttk.Entry(self.proxy_frame, textvariable=self.proxy_url_var, width=40)
        proxy_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
    def create_advanced_settings(self):
        """Create advanced settings"""
        advanced_frame = ttk.LabelFrame(self.scrollable_frame, text="Advanced Settings", padding="10")
        advanced_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        advanced_frame.columnconfigure(1, weight=1)
        
        # Debug mode
        self.debug_mode_var = tk.BooleanVar()
        debug_check = ttk.Checkbutton(advanced_frame, text="Enable debug logging", variable=self.debug_mode_var)
        debug_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Auto-update
        self.auto_update_var = tk.BooleanVar()
        update_check = ttk.Checkbutton(advanced_frame, text="Check for updates on startup", variable=self.auto_update_var)
        update_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Keep history
        ttk.Label(advanced_frame, text="Keep download history for:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        
        self.history_days_var = tk.IntVar()
        history_combo = ttk.Combobox(advanced_frame, textvariable=self.history_days_var,
                                   values=[30, 60, 90, 180, 365, 0], 
                                   state="readonly", width=15)
        history_combo.grid(row=2, column=1, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(advanced_frame, text="(0 = keep forever)").grid(row=3, column=1, sticky=tk.W, pady=(0, 5))
        
        # Temp directory
        ttk.Label(advanced_frame, text="Temporary Directory:").grid(row=4, column=0, sticky=(tk.W, tk.N), padx=(0, 5), pady=(10, 0))
        
        temp_frame = ttk.Frame(advanced_frame)
        temp_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        temp_frame.columnconfigure(0, weight=1)
        
        self.temp_dir_var = tk.StringVar()
        temp_entry = ttk.Entry(temp_frame, textvariable=self.temp_dir_var, width=40)
        temp_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        temp_browse_button = ttk.Button(temp_frame, text="Browse", command=self.browse_temp_directory)
        temp_browse_button.grid(row=0, column=1)
        
    def create_action_buttons(self):
        """Create action buttons"""
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(20, 0))
        
        save_button = ttk.Button(button_frame, text="Save Settings", command=self.save_settings)
        save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        reset_button = ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_to_defaults)
        reset_button.pack(side=tk.LEFT, padx=(0, 5))
        
        export_button = ttk.Button(button_frame, text="Export Settings", command=self.export_settings)
        export_button.pack(side=tk.LEFT, padx=(0, 5))
        
        import_button = ttk.Button(button_frame, text="Import Settings", command=self.import_settings)
        import_button.pack(side=tk.LEFT)
        
        # Status label
        self.status_var = tk.StringVar()
        status_label = ttk.Label(button_frame, textvariable=self.status_var, foreground="green")
        status_label.pack(side=tk.RIGHT)
        
    def load_settings(self):
        """Load settings from configuration"""
        # Download settings
        self.download_dir_var.set(self.config.get('download_directory', os.path.expanduser('~/Downloads')))
        self.max_downloads_var.set(self.config.get('max_concurrent_downloads', 2))
        self.timeout_var.set(self.config.get('download_timeout', 120))
        self.retry_var.set(self.config.get('retry_attempts', 2))
        self.auto_start_var.set(self.config.get('auto_start_downloads', True))
        self.open_after_download_var.set(self.config.get('open_after_download', False))
        self.notify_completion_var.set(self.config.get('notify_completion', True))
        
        # Interface settings
        self.theme_var.set(self.config.get('theme', 'System Default'))
        self.remember_window_var.set(self.config.get('remember_window', True))
        self.minimize_to_tray_var.set(self.config.get('minimize_to_tray', False))
        self.start_minimized_var.set(self.config.get('start_minimized', False))
        
        # API settings
        self.api_choice_var.set(self.config.get('api_choice', 'Ashlynn Free API'))
        self.custom_api_var.set(self.config.get('custom_api_url', ''))
        self.api_key_var.set(self.config.get('api_key', ''))
        self.use_proxy_var.set(self.config.get('use_proxy', False))
        self.proxy_url_var.set(self.config.get('proxy_url', ''))
        
        # Advanced settings
        self.debug_mode_var.set(self.config.get('debug_mode', False))
        self.auto_update_var.set(self.config.get('auto_update', True))
        self.history_days_var.set(self.config.get('history_days', 90))
        self.temp_dir_var.set(self.config.get('temp_directory', os.path.join(os.path.expanduser('~'), '.terabox_downloader', 'temp')))
        
        # Update UI state
        self.on_api_selection_change()
        self.toggle_proxy_settings()
        
    def save_settings(self):
        """Save current settings to configuration"""
        try:
            # Download settings
            self.config.set('download_directory', self.download_dir_var.get())
            self.config.set('max_concurrent_downloads', self.max_downloads_var.get())
            self.config.set('download_timeout', self.timeout_var.get())
            self.config.set('retry_attempts', self.retry_var.get())
            self.config.set('auto_start_downloads', self.auto_start_var.get())
            self.config.set('open_after_download', self.open_after_download_var.get())
            self.config.set('notify_completion', self.notify_completion_var.get())
            
            # Interface settings
            self.config.set('theme', self.theme_var.get())
            self.config.set('remember_window', self.remember_window_var.get())
            self.config.set('minimize_to_tray', self.minimize_to_tray_var.get())
            self.config.set('start_minimized', self.start_minimized_var.get())
            
            # API settings
            self.config.set('api_choice', self.api_choice_var.get())
            self.config.set('custom_api_url', self.custom_api_var.get())
            self.config.set('api_key', self.api_key_var.get())
            self.config.set('use_proxy', self.use_proxy_var.get())
            self.config.set('proxy_url', self.proxy_url_var.get())
            
            # Advanced settings
            self.config.set('debug_mode', self.debug_mode_var.get())
            self.config.set('auto_update', self.auto_update_var.get())
            self.config.set('history_days', self.history_days_var.get())
            self.config.set('temp_directory', self.temp_dir_var.get())
            
            # Save configuration
            self.config.save_config()
            
            self.status_var.set("Settings saved successfully!")
            self.frame.after(3000, lambda: self.status_var.set(""))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        result = messagebox.askyesno(
            "Confirm Reset", 
            "Are you sure you want to reset all settings to defaults?\n\nThis will overwrite your current configuration."
        )
        
        if result:
            self.config.reset_to_defaults()
            self.load_settings()
            self.status_var.set("Settings reset to defaults")
            self.frame.after(3000, lambda: self.status_var.set(""))
            
    def browse_download_directory(self):
        """Browse and select download directory"""
        directory = filedialog.askdirectory(initialdir=self.download_dir_var.get())
        if directory:
            self.download_dir_var.set(directory)
            
    def browse_temp_directory(self):
        """Browse and select temporary directory"""
        directory = filedialog.askdirectory(initialdir=self.temp_dir_var.get())
        if directory:
            self.temp_dir_var.set(directory)
            
    def on_api_selection_change(self, event=None):
        """Handle API selection change"""
        api_choice = self.api_choice_var.get()
        if api_choice == "Custom API":
            self.custom_api_entry.config(state="normal")
            self.api_key_entry.config(state="normal")
        else:
            self.custom_api_entry.config(state="disabled")
            self.api_key_entry.config(state="disabled")
            
    def toggle_proxy_settings(self, event=None):
        """Toggle proxy settings visibility"""
        if self.use_proxy_var.get():
            for widget in self.proxy_frame.winfo_children():
                widget.config(state="normal")
        else:
            for widget in self.proxy_frame.winfo_children():
                if isinstance(widget, ttk.Entry):
                    widget.config(state="disabled")
                    
    def test_api_connection(self):
        """Test API connection"""
        try:
            from core.terabox_api import TeraboxAPI
            
            api = TeraboxAPI()
            # Test with a dummy URL
            test_url = "https://terabox.com/s/test"
            
            # This would be implemented in the actual API class
            result = api.test_connection(
                api_choice=self.api_choice_var.get(),
                custom_url=self.custom_api_var.get(),
                api_key=self.api_key_var.get()
            )
            
            if result:
                messagebox.showinfo("Success", "API connection test successful!")
            else:
                messagebox.showerror("Error", "API connection test failed!")
                
        except Exception as e:
            messagebox.showerror("Error", f"API test failed: {str(e)}")
            
    def export_settings(self):
        """Export settings to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Settings"
            )
            
            if filename:
                self.config.export_config(filename)
                messagebox.showinfo("Success", f"Settings exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export settings: {str(e)}")
            
    def import_settings(self):
        """Import settings from file"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Import Settings"
            )
            
            if filename:
                self.config.import_config(filename)
                self.load_settings()
                messagebox.showinfo("Success", "Settings imported successfully!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import settings: {str(e)}")
