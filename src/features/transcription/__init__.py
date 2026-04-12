"""Transcription service abstractions and implementations.

AssemblyAI is optional. Do not fail import of the whole transcription package
when its dependency is unavailable.
"""

from .service import TranscriptionService
from .whisper import WhisperTranscriptionService
from .vad import VADTranscriptionService
from .factory import TranscriptionServiceFactory

__all__ = [
    'TranscriptionService',
    'WhisperTranscriptionService',
    'VADTranscriptionService',
    'TranscriptionServiceFactory',
]

try:
    from .assemblyai import AssemblyAITranscriptionService
    __all__.append('AssemblyAITranscriptionService')
except ModuleNotFoundError:
    AssemblyAITranscriptionService = None