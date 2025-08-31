"""
Transcription management for the Recall GUI application.

This module handles the transcription workflow, processing, and file operations.
"""

import os
import threading
import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING

from src.core.errors import (
    RecallError, APIKeyError, AudioHandlerError, 
    TranscriptionError, SilentAudioError
)

if TYPE_CHECKING:
    from src.gui.app import TranscriberApp
    from src.core.audio_handler import AudioHandler
    from src.core.transcriber import Transcriber


class TranscriptionManager:
    """Manages the transcription workflow and processing."""
    
    def __init__(
        self,
        app: 'TranscriberApp',
        audio_handler: 'AudioHandler',
        transcriber: 'Transcriber'
    ):
        self.app = app
        self.audio_handler = audio_handler
        self.transcriber = transcriber
    
    def start_transcription(self) -> None:
        """Validate inputs and start the transcription process in a background thread."""
        if self.app.processing:
            messagebox.showwarning("In Progress", "A transcription is already in progress.")
            return
            
        if not self.app.current_files:
            messagebox.showerror("Error", "No files selected for transcription.")
            return

        # Early API key check
        if not self.app.config.api_key:
            self.app.show_error_message(
                "API Key Error",
                "AssemblyAI API key not set. Please set it in Settings > API Key."
            )
            return
            
        self.app.processing = True
        self.app.start_time = self.app.get_current_time()
        self.app.progress_tracker.reset_progress()
        
        self.app.progress_tracker.update_status("Starting...", "processing")
        self.app.progress_tracker.update_elapsed_time()

        # Run file processing in a separate thread to keep UI responsive
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()

    def process_files(self) -> None:
        """
        The core file processing logic that runs in a background thread.
        Handles audio preparation, transcription, and progress updates.
        """
        try:
            total_files = len(self.app.current_files)
            
            for i, file_path in enumerate(self.app.current_files):
                if not self.app.processing:
                    self.app.progress_tracker.update_status("Cancelled", "cancelled")
                    break

                progress_percent = (i / total_files) * 100
                filename = os.path.basename(file_path)
                self.app.progress_tracker.update_progress(
                    f"Processing {filename}...", 
                    progress_percent, 
                    "processing"
                )
                
                try:
                    # Prepare audio file for transcription
                    prepared_path = self.audio_handler.prepare_audio(file_path)
                    
                    # Transcribe the prepared file
                    transcript = self.transcriber.transcribe_file(prepared_path)
                    
                    # Clean up the temporary file if one was created
                    if prepared_path != file_path:
                        self.audio_handler.cleanup_temp_file(prepared_path)
                    
                    if not transcript or transcript.strip() == "":
                        raise SilentAudioError("Transcription returned empty or silent result.")
                    
                    # Save the transcript
                    self._save_transcript(file_path, transcript)
                    
                    self.app.progress_tracker.update_progress(
                        f"✓ Completed {filename}", 
                        progress_percent, 
                        "processing"
                    )

                except (AudioHandlerError, TranscriptionError) as e:
                    self.app.progress_tracker.update_progress(
                        f"✗ Error on {filename}: {e}", 
                        progress_percent, 
                        "error"
                    )
                
            if self.app.processing:
                self.app.progress_tracker.update_status("Completed", "completed")
            
        except APIKeyError as e:
            self.app.show_error_message("API Key Error", str(e))
            self.app.progress_tracker.update_status("Failed", "error")
        except Exception as e:
            self.app.show_error_message("An Unexpected Error Occurred", f"An unexpected error occurred: {e}")
            self.app.progress_tracker.update_status("Failed", "error")
        finally:
            self.app.processing = False
            self.app.after(0, self._reset_ui_state)

    def _save_transcript(self, file_path: str, transcript: str) -> None:
        """Save the transcript to a file."""
        output_dir = self.app.output_path.get()
        if self.app.same_dir_var.get():
            output_dir = os.path.dirname(file_path)
        
        filename = os.path.basename(file_path)
        output_filename = f"{os.path.splitext(filename)[0]}_transcription.txt"
        output_filepath = os.path.join(output_dir, output_filename)
        
        os.makedirs(output_dir, exist_ok=True)
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(transcript)

    def _reset_ui_state(self) -> None:
        """Reset the UI controls to their default, non-processing state."""
        self.app.transcribe_btn.configure(text="Start Transcription", state=tk.NORMAL)
        self.app.select_file_btn.configure(state=tk.NORMAL)
        self.app.select_dir_btn.configure(state=tk.NORMAL)
        self.app.select_output_btn.configure(state=tk.NORMAL)
        self.app.output_path.configure(state=tk.NORMAL)
        self.app.same_dir_checkbox.configure(state=tk.NORMAL)