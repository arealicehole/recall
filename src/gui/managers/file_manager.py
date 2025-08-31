"""
File management for the Recall GUI application.

This module handles file selection, directory operations, and file list updates.
"""

import os
import tkinter as tk
from tkinter import filedialog
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.gui.app import TranscriberApp
    from src.core.audio_handler import AudioHandler
    from src.utils.config import Config


class FileManager:
    """Manages file selection and operations for the transcriber application."""
    
    def __init__(self, app: 'TranscriberApp', audio_handler: 'AudioHandler', config: 'Config'):
        self.app = app
        self.audio_handler = audio_handler
        self.config = config
    
    def select_files(self) -> None:
        """Select multiple audio files for transcription."""
        filetypes = [("Audio Files", " ".join(f"*{fmt}" for fmt in self.config.supported_formats))]
        file_paths = filedialog.askopenfilenames(filetypes=filetypes)
        if file_paths:
            self.app.current_files = list(file_paths)
            self.update_files_list()
            self.app.update_status("Ready", "info")
            
            # Update output directory if checkbox is checked
            if self.app.same_dir_var.get():
                self._update_output_for_same_dir(file_paths)
    
    def select_directory(self) -> None:
        """Select a directory containing audio files for transcription."""
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.app.current_files = self.audio_handler.get_audio_files(dir_path)
            self.update_files_list()
            self.app.update_status("Ready", "info")
            
            # Update output directory if checkbox is checked
            if self.app.same_dir_var.get():
                self.app.output_path.delete(0, tk.END)
                self.app.output_path.insert(0, dir_path)
                self.config.output_dir = dir_path
    
    def select_output_directory(self) -> None:
        """Select output directory for transcriptions."""
        dir_path = filedialog.askdirectory(initialdir=self.config.output_dir)
        if dir_path:
            self.config.output_dir = dir_path
            self.app.output_path.delete(0, tk.END)
            self.app.output_path.insert(0, dir_path)
    
    def update_files_list(self) -> None:
        """Update the files list display with selected files."""
        self.app.files_text.delete("0.0", tk.END)
        if not self.app.current_files:
            self.app.files_text.insert(tk.END, "No files selected")
            return
            
        # Show count of selected files
        file_count = len(self.app.current_files)
        self.app.files_text.insert(tk.END, f"Selected {file_count} file{'s' if file_count != 1 else ''}:\n\n")
        
        for i, file in enumerate(self.app.current_files, 1):
            file_name = os.path.basename(file)
            file_dir = os.path.dirname(file)
            self.app.files_text.insert(tk.END, f"{i}. {file_name}\n")
            self.app.files_text.insert(tk.END, f"   {file_dir}\n\n")
    
    def toggle_same_directory(self) -> None:
        """Handle checkbox state change for same directory option."""
        if self.app.same_dir_var.get():
            # If we have files selected, show appropriate directory info
            if self.app.current_files:
                self._update_output_for_same_dir(self.app.current_files)
            
            # Disable output directory controls
            self.app.output_path.configure(state=tk.DISABLED)
            self.app.select_output_btn.configure(state=tk.DISABLED)
        else:
            # Re-enable output directory controls and restore original output directory
            self.app.output_path.configure(state=tk.NORMAL)
            self.app.select_output_btn.configure(state=tk.NORMAL)
            self.app.output_path.delete(0, tk.END)
            self.app.output_path.insert(0, self.config.output_dir)
    
    def _update_output_for_same_dir(self, file_paths: List[str]) -> None:
        """Update output path display when 'Same as input' is enabled."""
        # When "Same as input" is enabled, each file will be saved in its own directory
        # Check if all files are from the same directory for display purposes
        directories = [os.path.dirname(path) for path in file_paths]
        if len(set(directories)) == 1:
            # All files are from the same directory - show that directory
            input_dir = directories[0]
            self.app.output_path.delete(0, tk.END)
            self.app.output_path.insert(0, input_dir)
        else:
            # Files are from different directories - show a message indicating this
            self.app.output_path.delete(0, tk.END)
            self.app.output_path.insert(0, "[Multiple directories - each transcript saved with its source]")