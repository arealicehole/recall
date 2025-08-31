"""Audio file handling and validation."""

from pathlib import Path
from typing import List, Tuple
import os
from ...models.config import AppConfig


class AudioHandler:
    """Handles audio file operations and validation."""

    def __init__(self, config: AppConfig):
        """Initialize audio handler with configuration."""
        self.config = config

    def get_supported_formats(self) -> tuple:
        """Get supported audio file formats."""
        return self.config.supported_formats

    def is_supported_format(self, filename: str) -> bool:
        """Check if file format is supported."""
        return self.config.is_supported_format(filename)

    def validate_audio_file(self, file_path: str) -> Path:
        """
        Validate that an audio file exists and is supported.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Path object for the validated file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        if not self.is_supported_format(path.name):
            supported = ", ".join(self.get_supported_formats())
            raise ValueError(f"Unsupported audio format. Supported formats: {supported}")
        
        return path

    def get_audio_files_in_directory(self, directory: str) -> List[Path]:
        """
        Get all supported audio files in a directory.
        
        Args:
            directory: Path to directory to search
            
        Returns:
            List of Path objects for supported audio files
        """
        dir_path = Path(directory)
        
        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"Invalid directory: {directory}")
        
        audio_files = []
        for file_path in dir_path.iterdir():
            if file_path.is_file() and self.is_supported_format(file_path.name):
                audio_files.append(file_path)
        
        return sorted(audio_files)

    def get_file_info(self, file_path: str) -> Tuple[str, int, str]:
        """
        Get basic information about an audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Tuple of (filename, file_size_bytes, format_extension)
        """
        path = self.validate_audio_file(file_path)
        
        file_size = path.stat().st_size
        filename = path.name
        format_ext = path.suffix.lower()
        
        return filename, file_size, format_ext

    def format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: File size in bytes
            
        Returns:
            Formatted file size string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"