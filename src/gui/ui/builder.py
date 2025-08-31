"""
UI builder for the Recall GUI application.

This module contains the UI construction logic for the main application window.
"""

import customtkinter as ctk
import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gui.app import TranscriberApp


class UIBuilder:
    """Builds the user interface for the transcriber application."""
    
    def __init__(self, app: 'TranscriberApp'):
        self.app = app
    
    def setup_main_layout(self) -> None:
        """Set up the main layout with left and right columns."""
        # Create main frame with two columns
        self.app.main_frame = ctk.CTkFrame(self.app)
        self.app.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left column for existing controls
        self.app.left_frame = ctk.CTkFrame(self.app.main_frame)
        self.app.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Right column for metrics
        self.app.right_frame = ctk.CTkFrame(self.app.main_frame)
        self.app.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
    
    def setup_file_controls(self) -> None:
        """Set up file selection controls."""
        # File selection buttons
        self.app.btn_frame = ctk.CTkFrame(self.app.left_frame)
        self.app.btn_frame.pack(fill=tk.X, pady=10)
        
        self.app.select_file_btn = ctk.CTkButton(
            self.app.btn_frame,
            text="Select Files",
            command=self.app.select_files
        )
        self.app.select_file_btn.pack(side=tk.LEFT, padx=5)
        
        self.app.select_dir_btn = ctk.CTkButton(
            self.app.btn_frame,
            text="Select Directory",
            command=self.app.select_directory
        )
        self.app.select_dir_btn.pack(side=tk.LEFT, padx=5)
    
    def setup_output_controls(self) -> None:
        """Set up output directory selection controls."""
        # Output directory selection
        self.app.output_frame = ctk.CTkFrame(self.app.left_frame)
        self.app.output_frame.pack(fill=tk.X, pady=5)
        
        self.app.output_label = ctk.CTkLabel(
            self.app.output_frame,
            text="Output Directory:",
            font=("Arial", 12)
        )
        self.app.output_label.pack(side=tk.LEFT, padx=5)
        
        self.app.output_path = ctk.CTkEntry(
            self.app.output_frame,
            placeholder_text="Select output directory..."
        )
        self.app.output_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.app.output_path.insert(0, self.app.config.output_dir)
        
        self.app.select_output_btn = ctk.CTkButton(
            self.app.output_frame,
            text="Browse",
            command=self.app.select_output_directory,
            width=60
        )
        self.app.select_output_btn.pack(side=tk.RIGHT, padx=5)
        
        # Same as input directory checkbox
        self.app.same_dir_var = tk.BooleanVar(value=False)
        self.app.same_dir_checkbox = ctk.CTkCheckBox(
            self.app.output_frame,
            text="Same as input",
            variable=self.app.same_dir_var,
            command=self.app.toggle_same_directory
        )
        self.app.same_dir_checkbox.pack(side=tk.RIGHT, padx=5)
    
    def setup_files_list(self) -> None:
        """Set up the files list display."""
        # Files list
        self.app.files_frame = ctk.CTkFrame(self.app.left_frame)
        self.app.files_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.app.files_label = ctk.CTkLabel(self.app.files_frame, text="Selected Files:")
        self.app.files_label.pack(anchor=tk.W)
        
        self.app.files_text = ctk.CTkTextbox(self.app.files_frame, height=150)
        self.app.files_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_status_controls(self) -> None:
        """Set up status and progress controls."""
        # Status frame
        self.app.status_frame = ctk.CTkFrame(self.app.left_frame)
        self.app.status_frame.pack(fill=tk.X, pady=5)
        
        # Status label with icon
        self.app.status_label = ctk.CTkLabel(
            self.app.status_frame,
            text="Ready",
            font=("Arial", 12, "bold")
        )
        self.app.status_label.pack(pady=5)
        
        # Progress details
        self.app.progress_details = ctk.CTkLabel(
            self.app.status_frame,
            text="",
            font=("Arial", 10)
        )
        self.app.progress_details.pack(pady=2)
        
        # Progress bar
        self.app.progress_bar = ctk.CTkProgressBar(self.app.status_frame)
        self.app.progress_bar.pack(fill=tk.X, pady=5, padx=10)
        self.app.progress_bar.set(0)
        
        # Transcribe button
        self.app.transcribe_btn = ctk.CTkButton(
            self.app.left_frame,
            text="Start Transcription",
            command=self.app.start_transcription
        )
        self.app.transcribe_btn.pack(pady=10)
    
    def setup_metrics_panel(self) -> None:
        """Set up the performance metrics panel."""
        # Elapsed time
        self.app.time_frame = ctk.CTkFrame(self.app.right_frame)
        self.app.time_frame.pack(fill=tk.X, pady=5)
        
        self.app.time_label = ctk.CTkLabel(
            self.app.time_frame,
            text="Elapsed Time:",
            font=("Arial", 12, "bold")
        )
        self.app.time_label.pack()
        
        self.app.elapsed_time = ctk.CTkLabel(
            self.app.time_frame,
            text="00:00:00",
            font=("Arial", 20)
        )
        self.app.elapsed_time.pack(pady=5)
        
        # Performance metrics
        self.app.metrics_label = ctk.CTkLabel(
            self.app.right_frame,
            text="Performance Metrics",
            font=("Arial", 12, "bold")
        )
        self.app.metrics_label.pack(pady=(10,5))
        
        self.app.metrics_text = ctk.CTkTextbox(self.app.right_frame, height=200)
        self.app.metrics_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_log_panel(self) -> None:
        """Set up the output log panel."""
        # Output log at the bottom
        self.app.log_label = ctk.CTkLabel(self.app.main_frame, text="Output Log:")
        self.app.log_label.pack(anchor=tk.W, pady=(10,0))
        
        self.app.log_text = ctk.CTkTextbox(self.app.main_frame, height=150)
        self.app.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def setup_menu(self) -> None:
        """Create the menu bar."""
        # Create menu bar
        self.app.menubar = tk.Menu(self.app)
        self.app.configure(menu=self.app.menubar)
        
        # Settings menu
        settings_menu = tk.Menu(self.app.menubar, tearoff=0)
        self.app.menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="API Key", command=self.app.show_api_key_dialog)
        
        # Help menu
        help_menu = tk.Menu(self.app.menubar, tearoff=0)
        self.app.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.app.show_about_dialog)
    
    def build_ui(self) -> None:
        """Build the complete user interface."""
        self.setup_menu()
        self.setup_main_layout()
        self.setup_file_controls()
        self.setup_output_controls()
        self.setup_files_list()
        self.setup_status_controls()
        self.setup_metrics_panel()
        self.setup_log_panel()