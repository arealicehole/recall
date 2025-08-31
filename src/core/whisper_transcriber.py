"""
Backward compatibility module for WhisperTranscriber.

This module provides backward compatibility by importing WhisperTranscriber
from the new modular whisper package structure.
"""

# Import from new location for backward compatibility
from .whisper.transcriber import WhisperTranscriber

__all__ = ['WhisperTranscriber']