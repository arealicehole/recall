"""Voice Activity Detection module using ffmpeg silencedetect.

Splits audio into speech segments before transcription to prevent
Whisper hallucinations on silence and noise.
"""

from .detector import detect_speech_segments, extract_segment

__all__ = ['detect_speech_segments', 'extract_segment']
