"""
History Tab for Terabox Downloader
Manages download history and statistics
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from utils.file_utils import FileUtils

class HistoryTab:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.file_utils = FileUtils()
        self.history_file = os.path.join(os.path.expanduser('~'), '.terabox_downloader', 'history.json')
        
        self.create_widgets()
        self.load_history()
        
    def create_widgets(self):
        """Create and arrange the history tab widgets"""
        self.frame = ttk.Frame(self.parent)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # Statistics section
        self.create_statistics_section()
        
        # History list section
        self.create_history_section()
        
        # Control buttons section
        self.create_control_section()
        
    def create_statistics_section(self):
        """Create download statistics section"""
        stats_frame = ttk.LabelFrame(self.frame, text="Download Statistics", padding="10")
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(3, weight=1)
        
        # Total downloads
        ttk.Label(stats_frame, text="Total Downloads:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.total_downloads_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.total_downloads_var, font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W)
        
        # Successful downloads
        ttk.Label(stats_frame, text="Successful:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.successful_downloads_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.successful_downloads_var, font=("Arial", 10, "bold"), foreground="green").grid(row=0, column=3, sticky=tk.W)
        
        # Failed downloads
        ttk.Label(stats_frame, text="Failed Downloads:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.failed_downloads_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.failed_downloads_var, font=("Arial", 10, "bold"), foreground="red").grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # Total data downloaded
        ttk.Label(stats_frame, text="Total Downloaded:").grid(row=1, column=2, sticky=tk.W, padx=(20, 5), pady=(5, 0))
        self.total_data_var = tk.StringVar(value="0 MB")
        ttk.Label(stats_frame, textvariable=self.total_data_var, font=("Arial", 10, "bold")).grid(row=1, column=3, sticky=tk.W, pady=(5, 0))
        
    def create_history_section(self):
        """Create download history section"""
        history_frame = ttk.LabelFrame(self.frame, text="Download History", padding="10")
        history_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Filter frame
        filter_frame = ttk.Frame(history_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(2, weight=1)
        
        ttk.Label(filter_frame, text="Filter:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.filter_var = tk.StringVar()
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, values=["All", "Successful", "Failed"], state="readonly", width=15)
        filter_combo.grid(row=0, column=1, padx=(0, 10))
        filter_combo.set("All")
        filter_combo.bind('<<ComboboxSelected>>', self.apply_filter)
        
        # Search frame
        ttk.Label(filter_frame, text="Search:").grid(row=0, column=3, sticky=tk.W, padx=(20, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=4, padx=(0, 5))
        search_entry.bind('<KeyRelease>', self.apply_search)
        
        search_button = ttk.Button(filter_frame, text="Clear", command=self.clear_search)
        search_button.grid(row=0, column=5)
        
        # History treeview
        columns = ('Date', 'URL', 'Filename', 'Size', 'Status', 'Duration')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        self.history_tree.heading('Date', text='Date')
        self.history_tree.heading('URL', text='Original URL')
        self.history_tree.heading('Filename', text='Filename')
        self.history_tree.heading('Size', text='Size')
        self.history_tree.heading('Status', text='Status')
        self.history_tree.heading('Duration', text='Duration')
        
        self.history_tree.column('Date', width=120)
        self.history_tree.column('URL', width=300)
        self.history_tree.column('Filename', width=200)
        self.history_tree.column('Size', width=80)
        self.history_tree.column('Status', width=80)
        self.history_tree.column('Duration', width=80)
        
        self.history_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for history
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        history_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.history_tree.config(yscrollcommand=history_scrollbar.set)
        
        # Context menu
        self.create_context_menu()
        self.history_tree.bind('<Button-3>', self.show_context_menu)
        
    def create_control_section(self):
        """Create control buttons section"""
        control_frame = ttk.Frame(self.frame)
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        refresh_button = ttk.Button(control_frame, text="Refresh", command=self.load_history)
        refresh_button.pack(side=tk.LEFT, padx=(0, 5))
        
        export_button = ttk.Button(control_frame, text="Export History", command=self.export_history)
        export_button.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_button = ttk.Button(control_frame, text="Clear History", command=self.clear_history)
        clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Info label
        self.info_var = tk.StringVar(value="")
        info_label = ttk.Label(control_frame, textvariable=self.info_var, foreground="gray")
        info_label.pack(side=tk.RIGHT)
        
    def create_context_menu(self):
        """Create context menu for history items"""
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="Copy URL", command=self.copy_url)
        self.context_menu.add_command(label="Copy Filename", command=self.copy_filename)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Remove from History", command=self.remove_from_history)
        
    def load_history(self):
        """Load download history from file"""
        try:
            # Create history directory if it doesn't exist
            history_dir = os.path.dirname(self.history_file)
            if not os.path.exists(history_dir):
                os.makedirs(history_dir)
                
            # Load history data
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history_data = json.load(f)
            else:
                self.history_data = []
                
            self.refresh_history_display()
            self.update_statistics()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history: {str(e)}")
            self.history_data = []
            
    def save_history(self):
        """Save download history to file"""
        try:
            history_dir = os.path.dirname(self.history_file)
            if not os.path.exists(history_dir):
                os.makedirs(history_dir)
                
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving history: {e}")
            
    def add_to_history(self, url, filename, size, status, duration=None):
        """Add a download record to history"""
        record = {
            'date': datetime.now().isoformat(),
            'url': url,
            'filename': filename,
            'size': size,
            'status': status,
            'duration': duration or 0
        }
        
        self.history_data.append(record)
        self.save_history()
        self.refresh_history_display()
        self.update_statistics()
        
    def refresh_history_display(self):
        """Refresh the history display"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Filter and search
        filtered_data = self.apply_filters(self.history_data)
        
        # Sort by date (newest first)
        filtered_data.sort(key=lambda x: x['date'], reverse=True)
        
        # Add items to tree
        for record in filtered_data:
            try:
                date_str = datetime.fromisoformat(record['date']).strftime('%Y-%m-%d %H:%M')
            except:
                date_str = record['date']
                
            duration_str = f"{record.get('duration', 0):.1f}s" if record.get('duration') else "N/A"
            
            self.history_tree.insert('', 'end', values=(
                date_str,
                record['url'][:50] + '...' if len(record['url']) > 50 else record['url'],
                record['filename'],
                record['size'],
                record['status'],
                duration_str
            ), tags=(record['url'], record['filename']))
            
        # Update info
        total_shown = len(filtered_data)
        total_all = len(self.history_data)
        if total_shown != total_all:
            self.info_var.set(f"Showing {total_shown} of {total_all} records")
        else:
            self.info_var.set(f"Total: {total_all} records")
            
    def apply_filters(self, data):
        """Apply current filters to data"""
        filtered = data
        
        # Apply status filter
        status_filter = self.filter_var.get()
        if status_filter == "Successful":
            filtered = [r for r in filtered if r['status'] == 'Completed']
        elif status_filter == "Failed":
            filtered = [r for r in filtered if r['status'] in ['Failed', 'Error']]
            
        # Apply search filter
        search_term = self.search_var.get().lower()
        if search_term:
            filtered = [r for r in filtered if 
                       search_term in r['url'].lower() or 
                       search_term in r['filename'].lower()]
                       
        return filtered
        
    def apply_filter(self, event=None):
        """Apply status filter"""
        self.refresh_history_display()
        
    def apply_search(self, event=None):
        """Apply search filter"""
        self.refresh_history_display()
        
    def clear_search(self):
        """Clear search filter"""
        self.search_var.set("")
        self.refresh_history_display()
        
    def update_statistics(self):
        """Update statistics display"""
        total = len(self.history_data)
        successful = len([r for r in self.history_data if r['status'] == 'Completed'])
        failed = len([r for r in self.history_data if r['status'] in ['Failed', 'Error']])
        
        # Calculate total data downloaded
        total_bytes = 0
        for record in self.history_data:
            if record['status'] == 'Completed' and record.get('size'):
                try:
                    # Parse size string (e.g., "10.5 MB" -> bytes)
                    size_str = record['size'].replace(',', '')
                    if 'KB' in size_str:
                        size_bytes = float(size_str.replace(' KB', '')) * 1024
                    elif 'MB' in size_str:
                        size_bytes = float(size_str.replace(' MB', '')) * 1024 * 1024
                    elif 'GB' in size_str:
                        size_bytes = float(size_str.replace(' GB', '')) * 1024 * 1024 * 1024
                    else:
                        size_bytes = 0
                    total_bytes += size_bytes
                except:
                    pass
                    
        total_data_formatted = self.file_utils.format_file_size(total_bytes)
        
        # Update display
        self.total_downloads_var.set(str(total))
        self.successful_downloads_var.set(str(successful))
        self.failed_downloads_var.set(str(failed))
        self.total_data_var.set(total_data_formatted)
        
    def show_context_menu(self, event):
        """Show context menu for history items"""
        item = self.history_tree.identify_row(event.y)
        if item:
            self.history_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def copy_url(self):
        """Copy selected URL to clipboard"""
        selection = self.history_tree.selection()
        if selection:
            tags = self.history_tree.item(selection[0])['tags']
            if tags:
                url = tags[0]
                self.frame.clipboard_clear()
                self.frame.clipboard_append(url)
                messagebox.showinfo("Copied", "URL copied to clipboard")
                
    def copy_filename(self):
        """Copy selected filename to clipboard"""
        selection = self.history_tree.selection()
        if selection:
            tags = self.history_tree.item(selection[0])['tags']
            if len(tags) > 1:
                filename = tags[1]
                self.frame.clipboard_clear()
                self.frame.clipboard_append(filename)
                messagebox.showinfo("Copied", "Filename copied to clipboard")
                
    def remove_from_history(self):
        """Remove selected item from history"""
        selection = self.history_tree.selection()
        if selection:
            tags = self.history_tree.item(selection[0])['tags']
            if tags:
                url = tags[0]
                filename = tags[1] if len(tags) > 1 else ""
                
                # Find and remove from history data
                self.history_data = [r for r in self.history_data 
                                   if not (r['url'] == url and r['filename'] == filename)]
                
                self.save_history()
                self.refresh_history_display()
                self.update_statistics()
                
    def export_history(self):
        """Export history to CSV file"""
        try:
            from tkinter import filedialog
            import csv
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export History"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['Date', 'URL', 'Filename', 'Size', 'Status', 'Duration']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for record in self.history_data:
                        try:
                            date_str = datetime.fromisoformat(record['date']).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            date_str = record['date']
                            
                        writer.writerow({
                            'Date': date_str,
                            'URL': record['url'],
                            'Filename': record['filename'],
                            'Size': record['size'],
                            'Status': record['status'],
                            'Duration': f"{record.get('duration', 0):.1f}s"
                        })
                        
                messagebox.showinfo("Success", f"History exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export history: {str(e)}")
            
    def clear_history(self):
        """Clear all download history"""
        result = messagebox.askyesno(
            "Confirm Clear", 
            "Are you sure you want to clear all download history?\n\nThis action cannot be undone."
        )
        
        if result:
            self.history_data = []
            self.save_history()
            self.refresh_history_display()
            self.update_statistics()
            messagebox.showinfo("Success", "Download history has been cleared")
