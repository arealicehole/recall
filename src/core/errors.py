"""
Defines custom exceptions for the Recall application.
"""

class RecallError(Exception):
    """Base exception class for all application-specific errors."""
    pass

class APIKeyError(RecallError):
    """Raised when the AssemblyAI API key is not configured."""
    pass

class AudioHandlerError(RecallError):
    """Raised for errors related to audio file processing and handling."""
    pass

class TranscriptionError(RecallError):
    """Raised for errors during the transcription process."""
    pass

class SilentAudioError(TranscriptionError):
    """Raised specifically when an audio file is silent or contains no detectable speech."""
    pass 