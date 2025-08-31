"""
Progress tracking for the Recall GUI application.

This module handles progress updates, metrics display, and time tracking.
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.gui.app import TranscriberApp


class ProgressTracker:
    """Tracks and displays progress, metrics, and timing information."""
    
    def __init__(self, app: 'TranscriberApp'):
        self.app = app
    
    def update_status(self, message: str, status: str) -> None:
        """Update status with color coding."""
        status_colors = {
            "info": "gray",
            "preparing": "orange",
            "uploading": "blue",
            "transcribing": "purple",
            "completed": "green",
            "error": "red"
        }
        color = status_colors.get(status, "gray")
        self.app.status_label.configure(text=message, text_color=color)
    
    def update_elapsed_time(self) -> None:
        """Update the elapsed time display."""
        if self.app.start_time and self.app.processing:
            elapsed = time.time() - self.app.start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            
            self.app.elapsed_time.configure(
                text=f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            )
            
            # Schedule next update
            self.app.after(1000, self.update_elapsed_time)
    
    def update_progress(
        self,
        message: str,
        progress: float,
        status: str,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update progress with detailed information."""
        self.update_status(status.title(), status)
        self.app.progress_details.configure(text=message)
        self.app.progress_bar.set(progress / 100)
        
        # Log the message with timestamp
        timestamp = datetime.now().strftime("%I:%M:%S %p")  # 12-hour clock with AM/PM
        log_message = f"[{timestamp}] {message}"
        
        # Add metrics if available
        if extra and "metrics" in extra:
            self.app.metrics_text.delete("0.0", "1.0")
            self.app.metrics_text.insert("1.0", extra["metrics"])
            if status == "completed":
                performance_summary = getattr(self.app.transcriber, 'get_performance_summary', lambda: "")()
                if performance_summary:
                    self.app.metrics_text.insert("end", "\n\n" + performance_summary)
        
        self.app.log_text.insert("end", log_message + "\n")
        self.app.log_text.see("end")
    
    def reset_progress(self) -> None:
        """Reset progress indicators and clear displays."""
        self.app.progress_bar.set(0)
        self.app.progress_details.configure(text="")
        self.app.elapsed_time.configure(text="00:00:00")
        self.app.log_text.delete('1.0', "end")
        self.app.metrics_text.delete('1.0', "end")