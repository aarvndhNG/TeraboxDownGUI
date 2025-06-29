"""
Viewer Tab for Terabox Downloader
Handles file browsing and viewing of downloaded content
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from core.file_viewer import FileViewer
from utils.file_utils import FileUtils

class ViewerTab:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.file_viewer = FileViewer()
        self.file_utils = FileUtils()
        
        self.create_widgets()
        # Don't auto-refresh on startup to improve performance
        # self.refresh_file_list()
        
    def create_widgets(self):
        """Create and arrange the viewer tab widgets"""
        self.frame = ttk.Frame(self.parent)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # File browser section
        self.create_file_browser_section()
        
        # File viewer section
        self.create_file_viewer_section()
        
    def create_file_browser_section(self):
        """Create file browser section"""
        browser_frame = ttk.LabelFrame(self.frame, text="Downloaded Files", padding="10")
        browser_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        browser_frame.columnconfigure(0, weight=1)
        
        # Directory selection
        dir_frame = ttk.Frame(browser_frame)
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        ttk.Label(dir_frame, text="Directory:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.current_dir_var = tk.StringVar(value=self.config.get('download_directory', os.path.expanduser('~/Downloads')))
        dir_entry = ttk.Entry(dir_frame, textvariable=self.current_dir_var, width=50)
        dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        dir_entry.bind('<Return>', lambda e: self.refresh_file_list())
        
        browse_button = ttk.Button(dir_frame, text="Browse", command=self.browse_directory)
        browse_button.grid(row=0, column=2, padx=(0, 5))
        
        refresh_button = ttk.Button(dir_frame, text="Refresh", command=self.refresh_file_list)
        refresh_button.grid(row=0, column=3)
        
        # File list
        list_frame = ttk.Frame(browser_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        
        # Treeview for files
        columns = ('Name', 'Type', 'Size', 'Modified')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        self.file_tree.heading('Name', text='File Name')
        self.file_tree.heading('Type', text='Type')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Modified', text='Modified')
        
        self.file_tree.column('Name', width=300)
        self.file_tree.column('Type', width=100)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Modified', width=150)
        
        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Scrollbar for file list
        file_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        file_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_tree.config(yscrollcommand=file_scrollbar.set)
        
        # Bind double-click event
        self.file_tree.bind('<Double-1>', self.on_file_double_click)
        
        # Action buttons
        button_frame = ttk.Frame(browser_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        open_button = ttk.Button(button_frame, text="Open File", command=self.open_selected_file)
        open_button.pack(side=tk.LEFT, padx=(0, 5))
        
        open_folder_button = ttk.Button(button_frame, text="Open in Explorer", command=self.open_in_explorer)
        open_folder_button.pack(side=tk.LEFT, padx=(0, 5))
        
        delete_button = ttk.Button(button_frame, text="Delete File", command=self.delete_selected_file)
        delete_button.pack(side=tk.LEFT)
        
    def create_file_viewer_section(self):
        """Create file viewer section"""
        viewer_frame = ttk.LabelFrame(self.frame, text="File Preview", padding="10")
        viewer_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        viewer_frame.columnconfigure(0, weight=1)
        viewer_frame.rowconfigure(0, weight=1)
        
        # Create notebook for different viewer types
        self.viewer_notebook = ttk.Notebook(viewer_frame)
        self.viewer_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Text viewer tab
        self.text_frame = ttk.Frame(self.viewer_notebook)
        self.viewer_notebook.add(self.text_frame, text="Text")
        
        self.text_widget = tk.Text(self.text_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text_scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=text_scrollbar.set)
        
        # Image viewer tab
        self.image_frame = ttk.Frame(self.viewer_notebook)
        self.viewer_notebook.add(self.image_frame, text="Image")
        
        self.image_label = ttk.Label(self.image_frame, text="No image loaded")
        self.image_label.pack(expand=True)
        
        # Video/Media info tab
        self.media_frame = ttk.Frame(self.viewer_notebook)
        self.viewer_notebook.add(self.media_frame, text="Media Info")
        
        self.media_text = tk.Text(self.media_frame, wrap=tk.WORD, state=tk.DISABLED, height=10)
        self.media_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # File info section
        info_frame = ttk.Frame(viewer_frame)
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="File Info:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.file_info_var = tk.StringVar(value="No file selected")
        info_label = ttk.Label(info_frame, textvariable=self.file_info_var, foreground="gray")
        info_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
    def refresh_file_list(self):
        """Refresh the file list from current directory"""
        directory = self.current_dir_var.get()
        
        if not os.path.exists(directory):
            messagebox.showerror("Error", f"Directory does not exist: {directory}")
            return
            
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        try:
            # Get list of files
            files = []
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    file_info = {
                        'name': filename,
                        'path': filepath,
                        'type': self.file_utils.get_file_type(filename),
                        'size': self.file_utils.format_file_size(stat.st_size),
                        'modified': self.file_utils.format_timestamp(stat.st_mtime)
                    }
                    files.append(file_info)
                    
            # Sort files by name
            files.sort(key=lambda x: x['name'].lower())
            
            # Add files to tree
            for file_info in files:
                self.file_tree.insert('', 'end', values=(
                    file_info['name'],
                    file_info['type'],
                    file_info['size'],
                    file_info['modified']
                ), tags=(file_info['path'],))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read directory: {str(e)}")
            
    def browse_directory(self):
        """Browse and select directory to view"""
        directory = filedialog.askdirectory(initialdir=self.current_dir_var.get())
        if directory:
            self.current_dir_var.set(directory)
            self.refresh_file_list()
            
    def on_file_double_click(self, event):
        """Handle double-click on file"""
        self.open_selected_file()
        
    def open_selected_file(self):
        """Open the selected file in appropriate viewer"""
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to open")
            return
            
        item = selection[0]
        tags = self.file_tree.item(item)['tags']
        if tags:
            filepath = tags[0]
            self.view_file(filepath)
            
    def view_file(self, filepath):
        """View file in the appropriate viewer"""
        try:
            file_type = self.file_utils.get_file_type(os.path.basename(filepath))
            
            # Update file info
            stat = os.stat(filepath)
            info_text = f"{os.path.basename(filepath)} | {file_type} | {self.file_utils.format_file_size(stat.st_size)}"
            self.file_info_var.set(info_text)
            
            if file_type in ['Text', 'Code']:
                self.view_text_file(filepath)
                self.viewer_notebook.select(0)  # Select text tab
                
            elif file_type == 'Image':
                self.view_image_file(filepath)
                self.viewer_notebook.select(1)  # Select image tab
                
            elif file_type in ['Video', 'Audio']:
                self.view_media_info(filepath)
                self.viewer_notebook.select(2)  # Select media tab
                
            else:
                # Try to open with system default
                self.open_with_system_default(filepath)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
            
    def view_text_file(self, filepath):
        """View text file content"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, content)
            self.text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, f"Error reading file: {str(e)}")
            self.text_widget.config(state=tk.DISABLED)
            
    def view_image_file(self, filepath):
        """View image file"""
        try:
            from PIL import Image, ImageTk
            
            # Open and resize image
            image = Image.open(filepath)
            
            # Calculate size to fit in viewer
            max_width, max_height = 600, 400
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Convert to tkinter format
            photo = ImageTk.PhotoImage(image)
            
            # Display image
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # Keep a reference
            
        except ImportError:
            self.image_label.config(image="", text="PIL not available for image viewing")
        except Exception as e:
            self.image_label.config(image="", text=f"Error loading image: {str(e)}")
            
    def view_media_info(self, filepath):
        """Show media file information"""
        try:
            stat = os.stat(filepath)
            info_text = f"File: {os.path.basename(filepath)}\n"
            info_text += f"Size: {self.file_utils.format_file_size(stat.st_size)}\n"
            info_text += f"Modified: {self.file_utils.format_timestamp(stat.st_mtime)}\n"
            info_text += f"Type: {self.file_utils.get_file_type(os.path.basename(filepath))}\n\n"
            info_text += "To play this media file, click 'Open File' to use your system's default media player."
            
            self.media_text.config(state=tk.NORMAL)
            self.media_text.delete(1.0, tk.END)
            self.media_text.insert(1.0, info_text)
            self.media_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.media_text.config(state=tk.NORMAL)
            self.media_text.delete(1.0, tk.END)
            self.media_text.insert(1.0, f"Error getting media info: {str(e)}")
            self.media_text.config(state=tk.DISABLED)
            
    def open_with_system_default(self, filepath):
        """Open file with system default application"""
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', filepath])
            else:  # Linux
                subprocess.call(['xdg-open', filepath])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file with system default: {str(e)}")
            
    def open_in_explorer(self):
        """Open selected file location in file explorer"""
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file")
            return
            
        item = selection[0]
        tags = self.file_tree.item(item)['tags']
        if tags:
            filepath = tags[0]
            directory = os.path.dirname(filepath)
            self.open_with_system_default(directory)
            
    def delete_selected_file(self):
        """Delete the selected file"""
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to delete")
            return
            
        item = selection[0]
        tags = self.file_tree.item(item)['tags']
        if tags:
            filepath = tags[0]
            filename = os.path.basename(filepath)
            
            result = messagebox.askyesno(
                "Confirm Delete", 
                f"Are you sure you want to delete '{filename}'?\n\nThis action cannot be undone."
            )
            
            if result:
                try:
                    os.remove(filepath)
                    self.refresh_file_list()
                    messagebox.showinfo("Success", f"File '{filename}' has been deleted")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete file: {str(e)}")
