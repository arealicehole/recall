"""Base transcriber implementation with common functionality and metrics."""

import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Optional, List, Dict, Any


class TranscriptionMetrics:
    """Tracks performance metrics for transcription operations."""
    
    def __init__(self, file_path: str, file_size_mb: float):
        self.file_path = file_path
        self.file_size_mb = file_size_mb
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
        self.mb_per_second: Optional[float] = None
        
    def complete(self):
        """Mark the transcription as completed and calculate performance metrics."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.mb_per_second = self.file_size_mb / self.duration if self.duration > 0 else 0
        
    def __str__(self):
        if not self.end_time:
            return f"Transcribing {Path(self.file_path).name} ({self.file_size_mb:.1f} MB)"
        
        return (
            f"File: {Path(self.file_path).name}\n"
            f"Size: {self.file_size_mb:.1f} MB\n"
            f"Duration: {self.duration:.1f} seconds\n"
            f"Speed: {self.mb_per_second:.2f} MB/s"
        )


class BaseTranscriber(ABC):
    """Abstract base class for transcription services."""
    
    def __init__(self, config):
        self.config = config
        self.metrics: List[TranscriptionMetrics] = []
    
    @abstractmethod
    def transcribe_file(
        self, 
        audio_path: str, 
        progress_callback: Optional[Callable[[str, float, str, Dict[str, Any]], None]] = None
    ) -> str:
        """
        Transcribe an audio file.
        
        Args:
            audio_path: Path to the audio file to transcribe
            progress_callback: Optional callback for progress updates
        
        Returns:
            Transcribed text
        """
        pass
    
    def save_transcription(self, audio_path: str, transcription: str, same_as_input: bool = False) -> str:
        """
        Save transcription to file.
        
        Args:
            audio_path: Path to the original audio file
            transcription: The transcription text to save
            same_as_input: If True, save in the same directory as the audio file
            
        Returns:
            Path to the saved transcription file
        """
        try:
            if same_as_input:
                # Save in the same directory as the audio file
                audio_dir = Path(audio_path).parent
                out_path = audio_dir / f"{Path(audio_path).stem}_transcription.txt"
            else:
                # Save in the configured output directory
                out_path = Path(self.config.output_dir) / f"{Path(audio_path).stem}_transcription.txt"
            
            out_path.write_text(transcription, encoding='utf-8')
            return str(out_path)
        except Exception as e:
            print(f"Failed to save transcription: {e}")
            return ""
    
    def get_performance_summary(self) -> str:
        """Get a summary of all transcription performance metrics."""
        if not self.metrics:
            return "No transcriptions performed yet."
            
        total_size = sum(m.file_size_mb for m in self.metrics)
        total_time = sum(m.duration for m in self.metrics if m.duration)
        avg_speed = total_size / total_time if total_time > 0 else 0
        
        return (
            f"Performance Summary:\n"
            f"Total files: {len(self.metrics)}\n"
            f"Total size: {total_size:.1f} MB\n"
            f"Total time: {total_time:.1f} seconds\n"
            f"Average speed: {avg_speed:.2f} MB/s"
        )