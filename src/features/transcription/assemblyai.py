"""AssemblyAI transcription service implementation."""

from typing import Optional, Callable, Dict, Any
from pathlib import Path

from .service import TranscriptionService
from ...core.assemblyai_transcriber import AssemblyAITranscriber
from ...core.errors import TranscriptionError
from ...models.jobs import TranscriptionJob, TranscriptionRequest
from ...models.config import AppConfig


class AssemblyAITranscriptionService(TranscriptionService):
    """AssemblyAI-based transcription service implementation."""

    def __init__(self, config: AppConfig):
        """Initialize AssemblyAI transcription service."""
        self.config = config
        self._transcriber = AssemblyAITranscriber(config)

    def get_backend_name(self) -> str:
        """Return the name of the transcription backend."""
        return "AssemblyAI (Cloud)"

    def is_available(self) -> bool:
        """Check if the AssemblyAI service is available."""
        return bool(self.config.assemblyai_api_key)

    def supports_diarization(self) -> bool:
        """Check if the service supports speaker diarization."""
        return True  # AssemblyAI always supports diarization

    def get_supported_formats(self) -> tuple:
        """Return tuple of supported audio file extensions."""
        return self.config.supported_formats

    def transcribe_file(
        self,
        audio_path: str,
        progress_callback: Optional[Callable[[str, float, str, Optional[Dict[str, Any]]], None]] = None
    ) -> str:
        """
        Transcribe an audio file to text using AssemblyAI.
        
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
        # Validate the audio file
        validated_path = self.validate_audio_file(audio_path)
        
        if not self.config.assemblyai_api_key:
            raise TranscriptionError("AssemblyAI API key is not configured")
        
        try:
            # Use the existing AssemblyAITranscriber implementation
            result = self._transcriber.transcribe_file(str(validated_path), progress_callback)
            return result
        except Exception as e:
            raise TranscriptionError(f"AssemblyAI transcription failed: {str(e)}") from e

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
        try:
            job.mark_processing()
            
            # Create a wrapped progress callback that updates the job
            def job_progress_callback(message: str, progress: float, status: str, extra: Optional[Dict[str, Any]] = None):
                job.update_progress(progress)
                if progress_callback:
                    progress_callback(message, progress, status, extra)
            
            result = self.transcribe_file(request.audio_file_path, job_progress_callback)
            job.mark_completed(result)
            return result
            
        except Exception as e:
            job.mark_failed(str(e))
            raise

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
        path = Path(audio_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if not self.is_supported_format(path.name):
            supported = ", ".join(self.get_supported_formats())
            raise ValueError(f"Unsupported audio format. Supported formats: {supported}")
        
        return path