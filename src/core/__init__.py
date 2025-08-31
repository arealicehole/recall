"""
Core functionality package for the Recall application
"""

# Import transcribers for backward compatibility
from .whisper.transcriber import WhisperTranscriber
from .base_transcriber import BaseTranscriber, TranscriptionMetrics

__all__ = [
    'WhisperTranscriber',
    'BaseTranscriber', 
    'TranscriptionMetrics'
] 