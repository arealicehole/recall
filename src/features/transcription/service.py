"""Abstract transcription service interface."""

from abc import ABC, abstractmethod
from typing import Optional, Callable, Dict, Any
from pathlib import Path

from ...models.jobs import TranscriptionJob, TranscriptionRequest


class TranscriptionService(ABC):
    """Abstract base class for transcription services."""

    @abstractmethod
    def get_backend_name(self) -> str:
        """Return the name of the transcription backend."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the transcription service is available."""
        pass

    @abstractmethod
    def supports_diarization(self) -> bool:
        """Check if the service supports speaker diarization."""
        pass

    @abstractmethod
    def get_supported_formats(self) -> tuple:
        """Return tuple of supported audio file extensions."""
        pass

    @abstractmethod
    def transcribe_file(
        self,
        audio_path: str,
        progress_callback: Optional[Callable[[str, float, str, Optional[Dict[str, Any]]], None]] = None
    ) -> str:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_path: Path to the audio file
            progress_callback: Optional callback for progress updates
            
        Returns:
            Transcribed text with speaker labels if supported
            
        Raises:
            TranscriptionError: If transcription fails
            FileNotFoundError: If audio file doesn't exist
            ValueError: If file format is not supported
        """
        pass

    @abstractmethod
    def transcribe_job(
        self,
        job: TranscriptionJob,
        request: TranscriptionRequest,
        progress_callback: Optional[Callable[[str, float, str, Optional[Dict[str, Any]]], None]] = None
    ) -> str:
        """
        Transcribe an audio file using a job model.
        
        Args:
            job: TranscriptionJob instance for tracking
            request: TranscriptionRequest with parameters
            progress_callback: Optional callback for progress updates
            
        Returns:
            Transcribed text with speaker labels if supported
            
        Raises:
            TranscriptionError: If transcription fails
        """
        pass

    @abstractmethod
    def validate_audio_file(self, audio_path: str) -> Path:
        """
        Validate that an audio file exists and is in a supported format.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Path object for the validated file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        pass

    def is_supported_format(self, filename: str) -> bool:
        """Check if file format is supported."""
        return any(filename.lower().endswith(fmt) for fmt in self.get_supported_formats())