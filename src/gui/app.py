import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import time
from typing import List

from src.core.audio_handler import AudioHandler
from src.core.transcriber import Transcriber
from src.utils.config import Config
from src.gui.ui.builder import UIBuilder
from src.gui.ui.dialogs import APIKeyDialog, AboutDialog, load_api_key_from_config
from src.gui.managers.file_manager import FileManager
from src.gui.managers.transcription_manager import TranscriptionManager
from src.gui.managers.progress_tracker import ProgressTracker

class TranscriberApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        
        # Initialize components
        self.config = Config()
        
        # Load API key from config file if not already set
        if not self.config.api_key:
            saved_api_key = load_api_key_from_config()
            if saved_api_key:
                self.config.api_key = saved_api_key
        
        self.audio_handler = AudioHandler(self.config)
        self.transcriber = Transcriber(self.config)
        
        # Initialize managers
        self.ui_builder = UIBuilder(self)
        self.file_manager = FileManager(self, self.audio_handler, self.config)
        self.transcription_manager = TranscriptionManager(self, self.audio_handler, self.transcriber)
        self.progress_tracker = ProgressTracker(self)
        
        # Setup GUI
        self.title("Recall")
        self.geometry("800x700")  # Made window larger for metrics
        self.setup_ui()
        
        # State variables
        self.processing = False
        self.current_files: List[str] = []
        self.start_time = None
    
    def setup_ui(self) -> None:
        """Set up the user interface using the UI builder."""
        self.ui_builder.build_ui()
    
    def show_error_message(self, title: str, message: str) -> None:
        """Safely show an error message box from any thread."""
        self.after(0, lambda: messagebox.showerror(title, message))
    
    def get_current_time(self) -> float:
        """Get the current time for tracking purposes."""
        return time.time()
    
    def show_api_key_dialog(self) -> None:
        """Show dialog to input and save API key."""
        def on_save_callback(api_key: str):
            # Recreate the transcriber with new API key
            self.transcriber = Transcriber(self.config)
            # Update the transcription manager
            self.transcription_manager.transcriber = self.transcriber
        
        dialog = APIKeyDialog(self, self.config, on_save_callback)
        dialog.show()
    
    def show_about_dialog(self) -> None:
        """Show about dialog."""
        AboutDialog.show()
    
    
    def select_output_directory(self) -> None:
        """Select output directory for transcriptions."""
        self.file_manager.select_output_directory()
            
    def select_files(self) -> None:
        """Select multiple audio files for transcription."""
        self.file_manager.select_files()
    
    def select_directory(self) -> None:
        """Select a directory containing audio files."""
        self.file_manager.select_directory()
    
    def update_files_list(self) -> None:
        """Update the files list display with selected files."""
        self.file_manager.update_files_list()
    
    def update_status(self, message: str, status: str) -> None:
        """Update status with color coding."""
        self.progress_tracker.update_status(message, status)
    
    def update_elapsed_time(self) -> None:
        """Update the elapsed time display."""
        self.progress_tracker.update_elapsed_time()
    
    def update_progress(self, message: str, progress: float, status: str, extra=None) -> None:
        """Update progress with detailed information."""
        self.progress_tracker.update_progress(message, progress, status, extra)
    
    def toggle_same_directory(self) -> None:
        """Handle checkbox state change for same directory option."""
        self.file_manager.toggle_same_directory()
    
    def start_transcription(self) -> None:
        """Validate inputs and start the transcription process in a background thread."""
        self.transcription_manager.start_transcription()

if __name__ == '__main__':
    app = TranscriberApp()
    app.mainloop() 