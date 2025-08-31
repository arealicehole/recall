"""Whisper transcription package with modular architecture."""

from .transcriber import WhisperTranscriber
from .models import WhisperResponse, WhisperSegment, WhisperHealthCheck, TranscriptionRequest
from .http_client import WhisperHTTPClient
from .request_builder import WhisperRequestBuilder
from .response_parser import WhisperResponseParser

# Maintain backward compatibility
__all__ = [
    'WhisperTranscriber',
    'WhisperResponse', 
    'WhisperSegment',
    'WhisperHealthCheck',
    'TranscriptionRequest',
    'WhisperHTTPClient',
    'WhisperRequestBuilder',
    'WhisperResponseParser'
]