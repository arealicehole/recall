"""
Dialog windows for the Recall GUI application.

This module contains the API key configuration and about dialog implementations.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.config import AppConfig


class APIKeyDialog:
    """Dialog for API key configuration."""
    
    def __init__(self, parent: ctk.CTk, config: 'AppConfig', on_save_callback=None):
        self.parent = parent
        self.config = config
        self.on_save_callback = on_save_callback
        
    def show(self) -> None:
        """Show the API key configuration dialog."""
        # Create a custom dialog window
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("API Key Configuration")
        dialog.geometry("500x200")
        dialog.transient(self.parent)  # Make it modal
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
                self._save_api_key_to_config(api_key)
                
                # Update the current config
                self.config.api_key = api_key
                
                # Call the callback if provided
                if self.on_save_callback:
                    self.on_save_callback(api_key)
                
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
    
    def _save_api_key_to_config(self, api_key: str) -> None:
        """Save API key to a config file."""
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


class AboutDialog:
    """About dialog for the application."""
    
    @staticmethod
    def show() -> None:
        """Show the about dialog."""
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


def load_api_key_from_config() -> str:
    """Load API key from config file."""
    config_dir = os.path.expanduser("~/.recall")
    config_file = os.path.join(config_dir, "config.json")
    
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            return config_data.get('api_key', '')
    except (FileNotFoundError, json.JSONDecodeError):
        return ''