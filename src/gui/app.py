import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import time
from typing import List

from src.core.audio_handler import AudioHandler
from src.models.config import AppConfig
from src.gui.ui.builder import UIBuilder
from src.gui.ui.dialogs import APIKeyDialog, AboutDialog, load_api_key_from_config
from src.gui.managers.file_manager import FileManager
from src.gui.managers.transcription_manager import TranscriptionManager
from src.gui.managers.progress_tracker import ProgressTracker

class TranscriberApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        
        # Initialize with new service container system
        from src.services import ServiceContainer
        self.services = ServiceContainer()
        self.config = self.services.get_config()
        
        # Legacy compatibility - load API key from old config if needed
        if not self.config.assemblyai_api_key:
            saved_api_key = load_api_key_from_config()
            if saved_api_key:
                self.config.assemblyai_api_key = saved_api_key
        
        self.audio_handler = AudioHandler(self.config)
        
        # Use new transcription factory
        self.transcription_factory = self.services.get_transcription_factory()
        
        # Initialize managers
        self.ui_builder = UIBuilder(self)
        self.file_manager = FileManager(self, self.audio_handler, self.config)
        self.transcription_manager = TranscriptionManager(self, self.audio_handler, self.transcription_factory)
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
            # Update the configuration
            self.config.assemblyai_api_key = api_key
            # Update backend status display
            self.update_backend_status()
        
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

    
    def on_backend_changed(self, backend: str) -> None:
        """Handle backend selection change."""
        # Update the configuration
        self.config.transcriber_backend = backend
        
        # Show/hide model selection based on backend
        if backend == "whisper":
            self.model_frame.pack(fill=tk.X, pady=5, after=self.backend_frame)
        else:
            self.model_frame.pack_forget()
        
        # Update the UI status based on backend availability
        self.update_backend_status()
    
    def update_backend_status(self) -> None:
        """Update the backend status display."""
        current_backend = self.config.transcriber_backend
        
        if current_backend == "whisper":
            self.backend_status.configure(
                text="✓ Local Whisper (Free)",
                text_color="green"
            )
            # Hide API key warning
            self.api_key_warning.pack_forget()
            
        elif current_backend == "assemblyai":
            if self.config.assemblyai_api_key:
                self.backend_status.configure(
                    text="✓ AssemblyAI (Cloud)",
                    text_color="green"
                )
                self.api_key_warning.pack_forget()
            else:
                self.backend_status.configure(
                    text="✗ AssemblyAI (No API Key)",
                    text_color="red"
                )
                # Show API key warning
                self.api_key_warning.pack(side=tk.LEFT, padx=10)

    
    def on_model_changed(self, model: str) -> None:
        """Handle Whisper model selection change."""
        # Update the configuration
        self.config.whisper_model = model
        print(f"DEBUG: GUI model changed to: {model}")
        
        # Update the model info display
        model_sizes = {
            "tiny": "39M params, fastest, lowest accuracy",
            "base": "74M params, fast, good accuracy",
            "small": "244M params, balanced",
            "medium": "769M params, slower, better accuracy",
            "large": "1.5B params, slow, best accuracy",
            "large-v2": "1.5B params, improved large",
            "large-v3": "1.5B params, latest version"
        }
        self.model_info.configure(text=model_sizes.get(model, "Unknown model"))

    
    def on_diarization_changed(self) -> None:
        """Handle diarization toggle change."""
        # Update the configuration
        self.config.enable_diarization = self.diarization_var.get()
        
        # Log the change
        status = "enabled" if self.config.enable_diarization else "disabled"
        print(f"Speaker identification {status}")

if __name__ == '__main__':
    app = TranscriberApp()
    app.mainloop() 