import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
from typing import List
from datetime import datetime
import time

from src.core.audio_handler import AudioHandler
from src.core.transcriber import Transcriber
from src.utils.config import Config

class TranscriberApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.config = Config()
        self.audio_handler = AudioHandler(self.config)
        self.transcriber = Transcriber(self.config)
        
        # Setup GUI
        self.title("Audio Transcriber")
        self.geometry("800x700")  # Made window larger for metrics
        self.setup_ui()
        
        # State variables
        self.processing = False
        self.current_files: List[str] = []
        self.start_time = None
    
    def setup_ui(self):
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
            text="Select File",
            command=self.select_file
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
    
    def select_output_directory(self):
        """Select output directory for transcriptions"""
        dir_path = filedialog.askdirectory(initialdir=self.config.output_dir)
        if dir_path:
            self.config.output_dir = dir_path
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, dir_path)
            
    def select_file(self):
        filetypes = [("Audio Files", " ".join(f"*{fmt}" for fmt in self.config.supported_formats))]
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            self.current_files = [file_path]
            self.update_files_list()
            self.update_status("Ready", "info")
            
            # Update output directory if checkbox is checked
            if self.same_dir_var.get():
                input_dir = os.path.dirname(file_path)
                self.output_path.delete(0, tk.END)
                self.output_path.insert(0, input_dir)
                self.config.output_dir = input_dir
    
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
        self.files_text.delete("0.0", tk.END)
        for file in self.current_files:
            self.files_text.insert(tk.END, f"{os.path.basename(file)}\n")
    
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
            # If we have files selected, use their directory
            if self.current_files:
                input_dir = os.path.dirname(self.current_files[0])
                self.output_path.delete(0, tk.END)
                self.output_path.insert(0, input_dir)
                self.config.output_dir = input_dir
            
            # Disable output directory controls
            self.output_path.configure(state=tk.DISABLED)
            self.select_output_btn.configure(state=tk.DISABLED)
        else:
            # Re-enable output directory controls
            self.output_path.configure(state=tk.NORMAL)
            self.select_output_btn.configure(state=tk.NORMAL)
    
    def start_transcription(self):
        if not self.current_files:
            messagebox.showwarning("No Files", "Please select audio files to transcribe.")
            return
            
        # Update output directory from entry field (if not using same directory)
        if not self.same_dir_var.get():
            new_output_dir = self.output_path.get()
            if new_output_dir and new_output_dir != self.config.output_dir:
                try:
                    os.makedirs(new_output_dir, exist_ok=True)
                    self.config.output_dir = new_output_dir
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create output directory: {str(e)}")
                    return
        
        if self.processing:
            return
        
        self.processing = True
        self.transcribe_btn.configure(state=tk.DISABLED)
        self.select_file_btn.configure(state=tk.DISABLED)
        self.select_dir_btn.configure(state=tk.DISABLED)
        self.select_output_btn.configure(state=tk.DISABLED)
        self.output_path.configure(state=tk.DISABLED)
        
        # Clear log and metrics
        self.log_text.delete("0.0", tk.END)
        self.metrics_text.delete("0.0", tk.END)
        
        # Start timing
        self.start_time = time.time()
        self.update_elapsed_time()
        
        # Start transcription in a separate thread
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
    
    def process_files(self):
        try:
            total_files = len(self.current_files)
            
            for i, file_path in enumerate(self.current_files, 1):
                try:
                    # Prepare audio file
                    prepared_path = self.audio_handler.prepare_audio(file_path)
                    if not prepared_path:
                        continue
                    
                    # Transcribe
                    transcription = self.transcriber.transcribe_file(
                        prepared_path,
                        lambda msg, prog, status, extra=None: self.update_progress(
                            msg,
                            (i - 1 + prog / 100) / total_files * 100,
                            status,
                            extra
                        )
                    )
                    
                    # Clean up temporary file
                    if prepared_path != file_path:
                        self.audio_handler.cleanup_temp_file(prepared_path)
                    
                    if transcription:
                        output_path = self.transcriber.save_transcription(file_path, transcription)
                        if output_path:
                            self.update_progress(
                                f"Saved transcription to: {output_path}",
                                100 * i / total_files,
                                "completed"
                            )
                except Exception as e:
                    # Log error for this file but continue with others
                    error_msg = f"Failed to process {file_path}: {str(e)}"
                    self.update_progress(error_msg, -1, "error")
                    continue
            
            self.update_progress("All transcriptions completed!", 100, "completed")
            messagebox.showinfo("Success", "All files have been transcribed!")
            
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            self.update_progress(error_msg, -1, "error")
            messagebox.showerror("Error", error_msg)
            
        finally:
            # Always clean up any remaining temporary files
            self.audio_handler.cleanup_all_temp_files()
            
            self.processing = False
            self.start_time = None
            self.transcribe_btn.configure(state=tk.NORMAL)
            self.select_file_btn.configure(state=tk.NORMAL)
            self.select_dir_btn.configure(state=tk.NORMAL)
            self.select_output_btn.configure(state=tk.NORMAL)
            self.output_path.configure(state=tk.NORMAL) 