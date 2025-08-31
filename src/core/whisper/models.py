"""Pydantic models for Whisper API requests and responses."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class WhisperSegment(BaseModel):
    """A segment of transcribed audio with optional speaker information."""
    text: str = Field(..., description="Transcribed text for this segment")
    speaker: Optional[str] = Field(None, description="Speaker identifier (if diarization is available)")
    start: Optional[float] = Field(None, description="Start time in seconds")
    end: Optional[float] = Field(None, description="End time in seconds")


class WhisperResponse(BaseModel):
    """Response from Whisper API transcription."""
    text: Optional[str] = Field(None, description="Full transcribed text")
    segments: Optional[List[WhisperSegment]] = Field(None, description="Individual segments with timing and speaker info")
    error: Optional[str] = Field(None, description="Error message if transcription failed")


class WhisperHealthCheck(BaseModel):
    """Response from Whisper API health check."""
    ok: bool = Field(..., description="Whether the API is healthy")
    model: Optional[str] = Field(None, description="Model being used")
    device: Optional[str] = Field(None, description="Device (CPU/GPU)")
    diarization: Optional[Dict[str, Any]] = Field(None, description="Diarization capability info")


class DiarizationInfo(BaseModel):
    """Information about diarization capabilities."""
    modules_available: bool = Field(False, description="Whether diarization modules are available")
    token_present: bool = Field(False, description="Whether Hugging Face token is present")
    error: Optional[str] = Field(None, description="Error message if diarization is not working")


class TranscriptionRequest(BaseModel):
    """Configuration for transcription request."""
    enable_diarization: bool = Field(True, description="Whether to enable speaker diarization")
    language: str = Field("en", description="Language code for transcription")
    format: str = Field("json", description="Response format (json/text)")
    
    class Config:
        extra = "forbid"