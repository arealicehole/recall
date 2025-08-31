"""Main WhisperTranscriber class that orchestrates the transcription process."""

from pathlib import Path
from typing import Callable, Optional, Dict, Any

from ..base_transcriber import BaseTranscriber, TranscriptionMetrics
from .http_client import WhisperHTTPClient
from .request_builder import WhisperRequestBuilder
from .response_parser import WhisperResponseParser
from .models import TranscriptionRequest


class WhisperTranscriber(BaseTranscriber):
    """Transcriber implementation using local Whisper API."""
    
    def __init__(self, config):
        super().__init__(config)
        
        # Get Whisper API URL from config or use default
        self.api_url = getattr(config, 'whisper_api_url', 'http://127.0.0.1:8765')
        
        # Initialize components
        self.http_client = WhisperHTTPClient(self.api_url)
        self.request_builder = WhisperRequestBuilder()
        self.response_parser = WhisperResponseParser()
        
        # Check API health and capabilities
        self.diarization_available = False
        self.api_status = self._check_api_health()
    
    def _check_api_health(self) -> Dict[str, Any]:
        """Check if Whisper API is available and what features it supports."""
        health_data, success = self.http_client.check_health()
        
        if success and health_data.get('ok', False):
            print(f"INFO: Whisper API connected successfully")
            print(f"  Model: {health_data.get('model', 'unknown')}")
            print(f"  Device: {health_data.get('device', 'unknown')}")
            
            # Check diarization capability
            self.diarization_available = self.http_client.check_diarization_capability(health_data)
        else:
            print(f"WARNING: Whisper API at {self.api_url} returned unhealthy status")
        
        return health_data
    
    def transcribe_file(
        self, 
        audio_path: str, 
        progress_callback: Optional[Callable[[str, float, str, Dict[str, Any]], None]] = None
    ) -> str:
        """
        Transcribe an audio file using local Whisper API.
        
        Args:
            audio_path: Path to the audio file to transcribe
            progress_callback: Optional callback for progress updates
        
        Returns:
            Transcribed text with speaker labels (if available)
        """
        try:
            # Convert to Path for reliable handling
            audio_path = Path(audio_path)
            if not audio_path.exists():
                error_msg = f"Audio file not found: {audio_path}"
                if progress_callback:
                    progress_callback(error_msg, -1, "error", {})
                raise FileNotFoundError(error_msg)
            
            file_size = audio_path.stat().st_size / (1024 * 1024)  # Size in MB
            
            print(f"DEBUG: Starting Whisper transcription for {audio_path.name}")
            print(f"  Size: {file_size:.1f} MB")
            print(f"  Diarization: {'enabled' if self.diarization_available else 'disabled'}")
            
            # Create metrics tracker
            metrics = TranscriptionMetrics(str(audio_path), file_size)
            self.metrics.append(metrics)
            
            # Progress update: preparing
            if progress_callback:
                progress_callback(
                    f"Preparing {audio_path.name} ({file_size:.1f} MB)",
                    10,
                    "preparing",
                    {"metrics": str(metrics)}
                )
            
            # Create transcription config
            transcription_config = TranscriptionRequest(
                enable_diarization=self.diarization_available,
                language="en",
                format="json"
            )
            
            # Build multipart request
            body, boundary = self.request_builder.build_request(
                audio_path, 
                transcription_config, 
                self.diarization_available
            )
            
            # Progress update: transcribing
            if progress_callback:
                progress_callback(
                    f"Transcribing {audio_path.name}...",
                    50,
                    "transcribing",
                    {"metrics": str(metrics)}
                )
            
            # Calculate timeout based on file size
            timeout = max(300, int(file_size * 10))  # 10 seconds per MB, minimum 300s
            
            # Send transcription request
            response = self.http_client.transcribe(body, boundary, timeout)
            
            # Complete metrics
            metrics.complete()
            
            # Process response
            full_transcript = self.response_parser.process_response(response)
            
            # Check if we got any content
            if not self.response_parser.has_speech_content(response):
                error_msg = (
                    f"Audio file '{audio_path.name}' appears to be silent or contain no detectable speech. "
                    f"Please check that the audio file contains audible speech."
                )
                if progress_callback:
                    progress_callback(error_msg, -1, "error", {"metrics": str(metrics)})
                return ""
            
            # Progress update: completed
            if progress_callback:
                word_count = len(full_transcript.split())
                progress_callback(
                    f"Completed {audio_path.name} ({word_count} words)",
                    100,
                    "completed",
                    {"metrics": str(metrics)}
                )
            
            print(f"DEBUG: Transcription complete - {len(full_transcript)} characters")
            
            return full_transcript
            
        except Exception as e:
            error_msg = f"Failed to transcribe {audio_path}: {str(e)}"
            print(f"ERROR: {error_msg}")
            if progress_callback:
                progress_callback(
                    error_msg, -1, "error", 
                    {"metrics": str(metrics) if 'metrics' in locals() else ""}
                )
            return ""
    
    def map_speaker_label(self, speaker_id: str) -> str:
        """Map speaker IDs to human-readable labels."""
        return self.response_parser.map_speaker_label(speaker_id)