"""Application configuration models with Pydantic validation."""

from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import Literal, Optional
from pathlib import Path


class AppConfig(BaseSettings):
    """Application configuration with validation."""
    
    # Transcriber settings
    transcriber_backend: Literal['whisper', 'assemblyai'] = Field(
        default='whisper',
        description="Transcription backend to use"
    )
    
    whisper_api_url: str = Field(
        default='http://127.0.0.1:8771',
        description="Whisper API endpoint URL"
    )
    
    whisper_model: Literal['tiny', 'base', 'small', 'large-v3'] = Field(
        default='tiny',
        description="Whisper model size to use"
    )
    
    enable_diarization: bool = Field(
        default=True,
        description="Enable speaker diarization (speaker identification)"
    )
    
    # API Keys
    assemblyai_api_key: Optional[str] = Field(
        default=None,
        env='ASSEMBLYAI_API_KEY',
        description="AssemblyAI API key for cloud transcription"
    )
    
    # Output settings
    output_directory: Path = Field(
        default=Path('transcripts'),
        description="Default output directory for transcriptions"
    )
    
    @validator('output_directory')
    def ensure_output_dir_exists(cls, v: Path) -> Path:
        """Create output directory if it doesn't exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator('assemblyai_api_key')
    def validate_api_key_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate API key format if provided."""
        if v and not v.startswith(('sk_', 'api_', 'aai_')):
            # AssemblyAI keys can have various prefixes, just log warning
            pass  # Log warning but don't fail
        return v
    
    @validator('whisper_api_url')
    def validate_whisper_url(cls, v: str) -> str:
        """Validate Whisper API URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL format: {v}")
        return v
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
        env_prefix = ''  # No prefix for environment variables
        
    @property
    def supported_formats(self) -> tuple:
        """Return supported audio formats as an immutable tuple."""
        return ('.amr', '.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma')
    
    def is_supported_format(self, filename: str) -> bool:
        """Check if file format is supported."""
        return any(filename.lower().endswith(fmt) for fmt in self.supported_formats)
    
    @property
    def api_key(self) -> Optional[str]:
        """Backward compatibility property for assemblyai_api_key."""
        return self.assemblyai_api_key
    
    @api_key.setter
    def api_key(self, value: Optional[str]) -> None:
        """Backward compatibility setter for assemblyai_api_key."""
        self.assemblyai_api_key = value