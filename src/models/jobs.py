"""Job tracking models with Pydantic validation."""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Literal
from enum import Enum
from pathlib import Path
import uuid


class JobStatus(str, Enum):
    """Valid job status values."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TranscriptionRequest(BaseModel):
    """Request model for transcription jobs."""
    audio_file_path: str
    output_format: Literal['text', 'json', 'srt', 'vtt'] = 'text'
    enable_diarization: bool = True
    language: Optional[str] = None
    
    @validator('audio_file_path')
    def validate_audio_path(cls, v: str) -> str:
        """Validate that audio file exists."""
        if not Path(v).exists():
            raise ValueError(f"Audio file not found: {v}")
        return v
    
    @validator('language')
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        """Validate language code if provided."""
        if v:
            # Basic validation for ISO 639-1 codes (2 letters)
            if len(v) != 2 or not v.isalpha():
                raise ValueError(f"Invalid language code: {v}. Use ISO 639-1 codes (e.g., 'en', 'es', 'fr')")
        return v


class TranscriptionJob(BaseModel):
    """Model for transcription job tracking."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[str] = None
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    
    @validator('status', pre=True)
    def validate_status_value(cls, v):
        """Ensure status is valid JobStatus value."""
        if isinstance(v, str):
            try:
                return JobStatus(v)
            except ValueError:
                raise ValueError(f"Invalid status value: {v}")
        return v
    
    @validator('progress')
    def validate_progress(cls, v: float) -> float:
        """Ensure progress is between 0 and 100."""
        return max(0.0, min(100.0, v))
    
    def mark_processing(self) -> None:
        """Transition to processing state."""
        if self.status != JobStatus.PENDING:
            raise ValueError(f"Cannot transition from {self.status} to PROCESSING")
        self.status = JobStatus.PROCESSING
        self.started_at = datetime.now()
        self.progress = 0.0
    
    def mark_completed(self, result: str) -> None:
        """Mark job as completed with result."""
        if self.status not in [JobStatus.PROCESSING, JobStatus.PENDING]:
            raise ValueError(f"Cannot transition from {self.status} to COMPLETED")
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        self.progress = 100.0
        self.error_message = None
    
    def mark_failed(self, error: str) -> None:
        """Mark job as failed with error message."""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error
        self.result = None
    
    def mark_cancelled(self) -> None:
        """Mark job as cancelled."""
        if self.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            raise ValueError(f"Cannot cancel job with status {self.status}")
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.now()
    
    def update_progress(self, progress: float, message: Optional[str] = None) -> None:
        """Update job progress."""
        if self.status != JobStatus.PROCESSING:
            raise ValueError(f"Cannot update progress for job with status {self.status}")
        self.progress = max(0.0, min(100.0, progress))
        if message:
            # Could store progress messages if needed
            pass
    
    @property
    def is_complete(self) -> bool:
        """Check if job is in a terminal state."""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate job duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }