import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import threading
from typing import List
from datetime import datetime
import time
import json

from src.core.audio_handler import AudioHandler
from src.core.transcriber import Transcriber
from src.utils.config import Config
from src.core.errors import RecallError, APIKeyError, AudioHandlerError, TranscriptionError, SilentAudioError

class TranscriberApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.config = Config()
        
        # Load API key from config file if not already set
        if not self.config.api_key:
            saved_api_key = self.load_api_key_from_config()
            if saved_api_key:
                self.config.api_key = saved_api_key
        
        self.audio_handler = AudioHandler(self.config)
        self.transcriber = Transcriber(self.config)
        
        # Setup GUI
        self.title("Recall")
        self.geometry("800x700")  # Made window larger for metrics
        self.setup_ui()
        
        # State variables
        self.processing = False
        self.current_files: List[str] = []
        self.start_time = None
    
    def setup_ui(self):
        # Create menu bar
        self.setup_menu()
        
        # Create main frame with two columns
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left column for existing controls
        self.left_frame = ctk.CTkFrame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # File selection buttons
        self.btn_frame = ctk.CTkFrame(self.left_frame)
        self.btn_frame.pack(fill=tk.X, pady=10)
        
        self.select_file_btn = ctk.CTkButton(
            self.btn_frame,
            text="Select Files",
            command=self.select_files
        )
        self.select_file_btn.pack(side=tk.LEFT, padx=5)
        
        self.select_dir_btn = ctk.CTkButton(
            self.btn_frame,
            text="Select Directory",
            command=self.select_directory
        )
        self.select_dir_btn.pack(side=tk.LEFT, padx=5)
        
        # Output directory selection
        self.output_frame = ctk.CTkFrame(self.left_frame)
        self.output_frame.pack(fill=tk.X, pady=5)
        
        self.output_label = ctk.CTkLabel(
            self.output_frame,
            text="Output Directory:",
            font=("Arial", 12)
        )
        self.output_label.pack(side=tk.LEFT, padx=5)
        
        self.output_path = ctk.CTkEntry(
            self.output_frame,
            placeholder_text="Select output directory..."
        )
        self.output_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.output_path.insert(0, self.config.output_dir)
        
        self.select_output_btn = ctk.CTkButton(
            self.output_frame,
            text="Browse",
            command=self.select_output_directory,
            width=60
        )
        self.select_output_btn.pack(side=tk.RIGHT, padx=5)
        
        # Same as input directory checkbox
        self.same_dir_var = tk.BooleanVar(value=False)
        self.same_dir_checkbox = ctk.CTkCheckBox(
            self.output_frame,
            text="Same as input",
            variable=self.same_dir_var,
            command=self.toggle_same_directory
        )
        self.same_dir_checkbox.pack(side=tk.RIGHT, padx=5)

        # Export timestamps checkbox (for FFmpeg workflow)
        self.export_timestamps_frame = ctk.CTkFrame(self.left_frame)
        self.export_timestamps_frame.pack(fill=tk.X, pady=5)

        self.export_timestamps_var = tk.BooleanVar(value=self.config.export_timestamps)
        self.export_timestamps_checkbox = ctk.CTkCheckBox(
            self.export_timestamps_frame,
            text="Export timestamps and captions (for video editing)",
            variable=self.export_timestamps_var
        )
        self.export_timestamps_checkbox.pack(side=tk.LEFT, padx=5)
        
        # Files list
        self.files_frame = ctk.CTkFrame(self.left_frame)
        self.files_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.files_label = ctk.CTkLabel(self.files_frame, text="Selected Files:")
        self.files_label.pack(anchor=tk.W)
        
        self.files_text = ctk.CTkTextbox(self.files_frame, height=150)
        self.files_text.pack(fill=tk.BOTH, expand=True)
        
        # Status frame
        self.status_frame = ctk.CTkFrame(self.left_frame)
        self.status_frame.pack(fill=tk.X, pady=5)
        
        # Status label with icon
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=("Arial", 12, "bold")
        )
        self.status_label.pack(pady=5)
        
        # Progress details
        self.progress_details = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=("Arial", 10)
        )
        self.progress_details.pack(pady=2)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.status_frame)
        self.progress_bar.pack(fill=tk.X, pady=5, padx=10)
        self.progress_bar.set(0)
        
        # Transcribe button
        self.transcribe_btn = ctk.CTkButton(
            self.left_frame,
            text="Start Transcription",
            command=self.start_transcription
        )
        self.transcribe_btn.pack(pady=10)
        
        # Right column for metrics
        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        # Elapsed time
        self.time_frame = ctk.CTkFrame(self.right_frame)
        self.time_frame.pack(fill=tk.X, pady=5)
        
        self.time_label = ctk.CTkLabel(
            self.time_frame,
            text="Elapsed Time:",
            font=("Arial", 12, "bold")
        )
        self.time_label.pack()
        
        self.elapsed_time = ctk.CTkLabel(
            self.time_frame,
            text="00:00:00",
            font=("Arial", 20)
        )
        self.elapsed_time.pack(pady=5)
        
        # Performance metrics
        self.metrics_label = ctk.CTkLabel(
            self.right_frame,
            text="Performance Metrics",
            font=("Arial", 12, "bold")
        )
        self.metrics_label.pack(pady=(10,5))
        
        self.metrics_text = ctk.CTkTextbox(self.right_frame, height=200)
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        
        # Output log at the bottom
        self.log_label = ctk.CTkLabel(self.main_frame, text="Output Log:")
        self.log_label.pack(anchor=tk.W, pady=(10,0))
        
        self.log_text = ctk.CTkTextbox(self.main_frame, height=150)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def show_error_message(self, title: str, message: str):
        """Safely show an error message box from any thread."""
        self.after(0, lambda: messagebox.showerror(title, message))

    def setup_menu(self):
        """Create the menu bar"""
        # Create menu bar
        self.menubar = tk.Menu(self)
        self.configure(menu=self.menubar)
        
        # Settings menu
        settings_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="API Key", command=self.show_api_key_dialog)
        
        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about_dialog)
    
    def show_api_key_dialog(self):
        """Show dialog to input and save API key"""
        # Create a custom dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title("API Key Configuration")
        dialog.geometry("500x200")
        dialog.transient(self)  # Make it modal
        dialog.grab_set()  # Make it modal
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"500x200+{x}+{y}")
        
        # Dialog content
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="AssemblyAI API Key Configuration",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Instructions
        info_label = ctk.CTkLabel(
            main_frame,
            text="Enter your AssemblyAI API key. You can get one at: https://www.assemblyai.com/",
            font=("Arial", 10),
            wraplength=450
        )
        info_label.pack(pady=(0, 10))
        
        # API Key input
        api_key_frame = ctk.CTkFrame(main_frame)
        api_key_frame.pack(fill=tk.X, pady=(0, 10))
        
        api_key_label = ctk.CTkLabel(api_key_frame, text="API Key:")
        api_key_label.pack(side=tk.LEFT, padx=(10, 5))
        
        # Get current API key if it exists
        current_api_key = getattr(self.config, 'api_key', '') or ''
        
        api_key_entry = ctk.CTkEntry(
            api_key_frame, 
            placeholder_text="Enter your AssemblyAI API key...",
            width=300,
            show="*"  # Hide the API key
        )
        api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        if current_api_key:
            api_key_entry.insert(0, current_api_key)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def save_api_key():
            api_key = api_key_entry.get().strip()
            if not api_key:
                messagebox.showerror("Error", "Please enter an API key.")
                return
            
            try:
                # Save API key to config file
                self.save_api_key_to_config(api_key)
                
                # Update the current config
                self.config.api_key = api_key
                
                # Recreate the transcriber with new API key
                self.transcriber = Transcriber(self.config)
                
                messagebox.showinfo("Success", "API key saved successfully!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save API key: {str(e)}")
        
        def cancel():
            dialog.destroy()
        
        cancel_btn = ctk.CTkButton(
            button_frame, 
            text="Cancel", 
            command=cancel,
            width=100
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 10), pady=10)
        
        save_btn = ctk.CTkButton(
            button_frame, 
            text="Save", 
            command=save_api_key,
            width=100
        )
        save_btn.pack(side=tk.RIGHT, padx=(0, 5), pady=10)
        
        # Focus on the entry field
        api_key_entry.focus()
    
    def show_about_dialog(self):
        """Show about dialog"""
        about_text = (
            "Recall\n\n"
            "A simple audio transcription application using AssemblyAI.\n\n"
            "Features:\n"
            "• Multiple file selection\n"
            "• Directory processing\n"
            "• Real-time progress tracking\n"
            "• Performance metrics\n\n"
            "Supported formats: MP3, WAV, M4A, FLAC, AAC, WMA, OGG, AMR"
        )
        messagebox.showinfo("About", about_text)
    
    def save_api_key_to_config(self, api_key: str):
        """Save API key to a config file"""
        config_dir = os.path.expanduser("~/.recall")
        os.makedirs(config_dir, exist_ok=True)
        config_file = os.path.join(config_dir, "config.json")
        
        # Load existing config or create new one
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config_data = {}
        
        # Update API key
        config_data['api_key'] = api_key
        
        # Save config
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def load_api_key_from_config(self) -> str:
        """Load API key from config file"""
        config_dir = os.path.expanduser("~/.recall")
        config_file = os.path.join(config_dir, "config.json")
        
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                return config_data.get('api_key', '')
        except (FileNotFoundError, json.JSONDecodeError):
            return ''
    
    def select_output_directory(self):
        """Select output directory for transcriptions"""
        dir_path = filedialog.askdirectory(initialdir=self.config.output_dir)
        if dir_path:
            self.config.output_dir = dir_path
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, dir_path)
            
    def select_files(self):
        """Select multiple audio or video files for transcription"""
        audio_formats = " ".join(f"*{f}" for f in self.config.supported_formats)
        video_formats = " ".join(f"*{f}" for f in self.config.supported_video_formats)
        all_formats = f"{audio_formats} {video_formats}"
        
        filetypes = [
            ("All Media Files", all_formats),
            ("Video Files", video_formats),
            ("Audio Files", audio_formats),
            ("All files", "*.*")
        ]
        
        file_paths = filedialog.askopenfilenames(filetypes=filetypes)
        if file_paths:
            self.current_files = list(file_paths)
            self.update_files_list()
            self.update_status("Ready", "info")
            
            if self.same_dir_var.get():
                directories = {os.path.dirname(path) for path in file_paths}
                if len(directories) == 1:
                    self.output_path.delete(0, tk.END)
                    self.output_path.insert(0, list(directories)[0])
                else:
                    self.output_path.delete(0, tk.END)
                    self.output_path.insert(0, "[Multiple source directories]")
    
    def select_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.current_files = self.audio_handler.get_audio_files(dir_path)
            self.update_files_list()
            self.update_status("Ready", "info")
            
            # Update output directory if checkbox is checked
            if self.same_dir_var.get():
                self.output_path.delete(0, tk.END)
                self.output_path.insert(0, dir_path)
                self.config.output_dir = dir_path
    
    def update_files_list(self):
        """Update the files list display with selected files"""
        self.files_text.delete("0.0", tk.END)
        if not self.current_files:
            self.files_text.insert(tk.END, "No files selected")
            return
            
        # Show count of selected files
        file_count = len(self.current_files)
        self.files_text.insert(tk.END, f"Selected {file_count} file{'s' if file_count != 1 else ''}:\n\n")
        
        for i, file in enumerate(self.current_files, 1):
            file_name = os.path.basename(file)
            file_dir = os.path.dirname(file)
            self.files_text.insert(tk.END, f"{i}. {file_name}\n")
            self.files_text.insert(tk.END, f"   {file_dir}\n\n")
    
    def update_status(self, message: str, status: str):
        """Update status with color coding"""
        status_colors = {
            "info": "gray",
            "preparing": "orange",
            "uploading": "blue",
            "transcribing": "purple",
            "completed": "green",
            "error": "red"
        }
        color = status_colors.get(status, "gray")
        self.status_label.configure(text=message, text_color=color)
    
    def update_elapsed_time(self):
        """Update the elapsed time display"""
        if self.start_time and self.processing:
            elapsed = time.time() - self.start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            
            self.elapsed_time.configure(
                text=f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            )
            
            # Schedule next update
            self.after(1000, self.update_elapsed_time)
    
    def update_progress(self, message: str, progress: float, status: str, extra: dict = None):
        """Update progress with detailed information"""
        self.update_status(status.title(), status)
        self.progress_details.configure(text=message)
        self.progress_bar.set(progress / 100)
        
        # Log the message with timestamp
        timestamp = datetime.now().strftime("%I:%M:%S %p")  # 12-hour clock with AM/PM
        log_message = f"[{timestamp}] {message}"
        
        # Add metrics if available
        if extra and "metrics" in extra:
            self.metrics_text.delete("0.0", tk.END)
            self.metrics_text.insert(tk.END, extra["metrics"])
            if status == "completed":
                self.metrics_text.insert(tk.END, "\n\n" + self.transcriber.get_performance_summary())
        
        self.log_text.insert(tk.END, log_message + "\n")
        self.log_text.see(tk.END)
    
    def toggle_same_directory(self):
        """Handle checkbox state change for same directory option"""
        if self.same_dir_var.get():
            # If we have files selected, show appropriate directory info
            if self.current_files:
                directories = [os.path.dirname(path) for path in self.current_files]
                if len(set(directories)) == 1:
                    # All files are from the same directory
                    input_dir = directories[0]
                    self.output_path.delete(0, tk.END)
                    self.output_path.insert(0, input_dir)
                else:
                    # Files are from different directories
                    self.output_path.delete(0, tk.END)
                    self.output_path.insert(0, "[Multiple directories - each transcript saved with its source]")
            
            # Disable output directory controls
            self.output_path.configure(state=tk.DISABLED)
            self.select_output_btn.configure(state=tk.DISABLED)
        else:
            # Re-enable output directory controls and restore original output directory
            self.output_path.configure(state=tk.NORMAL)
            self.select_output_btn.configure(state=tk.NORMAL)
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, self.config.output_dir)
    
    def start_transcription(self):
        """Validate inputs and start the transcription process in a background thread."""
        if self.processing:
            messagebox.showwarning("In Progress", "A transcription is already in progress.")
            return
            
        if not self.current_files:
            messagebox.showerror("Error", "No files selected for transcription.")
            return

        # Early API key check
        if not self.config.api_key:
            self.show_error_message(
                "API Key Error",
                "AssemblyAI API key not set. Please set it in Settings > API Key."
            )
            return
            
        self.processing = True
        self.start_time = time.time()
        self.log_text.delete('1.0', tk.END)
        self.metrics_text.delete('1.0', tk.END)
        
        self.update_status("Starting...", "processing")
        self.update_elapsed_time()

        # Run file processing in a separate thread to keep UI responsive
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()

    def process_files(self):
        """
        The core file processing logic that runs in a background thread.
        Handles audio preparation, transcription, and progress updates.
        """
        try:
            total_files = len(self.current_files)
            
            for i, file_path in enumerate(self.current_files):
                if not self.processing:
                    self.update_status("Cancelled", "cancelled")
                    break

                progress_percent = (i / total_files) * 100
                self.update_progress(f"Processing {os.path.basename(file_path)}...", progress_percent, "processing")
                
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
                    output_dir = self.output_path.get()
                    if self.same_dir_var.get():
                        output_dir = os.path.dirname(file_path)

                    filename = os.path.basename(file_path)
                    output_filename = f"{os.path.splitext(filename)[0]}_transcription.txt"
                    output_filepath = os.path.join(output_dir, output_filename)

                    os.makedirs(output_dir, exist_ok=True)
                    with open(output_filepath, 'w', encoding='utf-8') as f:
                        f.write(transcript)

                    # Export timestamps and captions if checkbox is checked
                    if self.export_timestamps_var.get() and self.transcriber.last_transcript:
                        try:
                            saved_files = self.transcriber.save_transcript_data(
                                file_path,
                                self.transcriber.last_transcript,
                                same_as_input=self.same_dir_var.get()
                            )

                            # Log which files were saved
                            if saved_files:
                                log_msg = f"  → Exported: "
                                if 'json' in saved_files:
                                    log_msg += f"JSON data, "
                                if 'srt' in saved_files:
                                    log_msg += f"SRT captions"
                                self.log_text.insert(tk.END, log_msg + "\n")
                                self.log_text.see(tk.END)
                        except Exception as e:
                            print(f"WARNING: Failed to export timestamps: {e}")

                    self.update_progress(f"✓ Completed {filename}", progress_percent, "processing", extra={'transcript_path': output_filepath})

                except (AudioHandlerError, TranscriptionError) as e:
                    self.update_progress(f"✗ Error on {os.path.basename(file_path)}: {e}", progress_percent, "error")
                
            if self.processing:
                self.update_status("Completed", "completed")
            
        except APIKeyError as e:
            self.show_error_message("API Key Error", str(e))
            self.update_status("Failed", "error")
        except Exception as e:
            self.show_error_message("An Unexpected Error Occurred", f"An unexpected error occurred: {e}")
            self.update_status("Failed", "error")
        finally:
            self.processing = False
            self.after(0, self.reset_ui_state)

    def reset_ui_state(self):
        """Resets the UI controls to their default, non-processing state."""
        self.transcribe_btn.configure(text="Start Transcription", state=tk.NORMAL)
        self.select_file_btn.configure(state=tk.NORMAL)
        self.select_dir_btn.configure(state=tk.NORMAL)
        self.select_output_btn.configure(state=tk.NORMAL)
        self.output_path.configure(state=tk.NORMAL)
        self.same_dir_checkbox.configure(state=tk.NORMAL)

if __name__ == '__main__':
    app = TranscriberApp()
    app.mainloop() 