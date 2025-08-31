# Recall Application - Refactoring Plan

**Generated**: 2025-08-31  
**Priority**: High - Critical issues affecting maintainability and scalability  
**Estimated Total Time**: 8-10 hours (individual tasks <1 hour each)

## Executive Summary

The Recall codebase has significant architectural issues that violate SOLID principles and the project's stated CLAUDE.md guidelines. Most critical are oversized files (app.py at 609 lines), massive functions (setup_ui at 158 lines), missing type safety (no Pydantic models), and classes with multiple responsibilities.

**UPDATE**: A comprehensive cleanup plan has been created at `PRPs/ai_docs/cleanup_plan.md` to remove excess files and reorganize the repository structure before refactoring begins.

## 🚨 Critical Issues by Priority

### Priority 1: HIGH - File Size Violations

#### Issue 1.1: `src/gui/app.py` - 609 lines (109 over limit)

**Location**: `/home/ice/dev/recall/src/gui/app.py`

**Why it's a problem**: 
- Violates 500-line file limit from CLAUDE.md
- Single file handling UI, business logic, and state management
- Difficult to test individual components
- High cognitive load for developers

**Specific Fix**:
```python
# Current structure (BEFORE):
src/gui/app.py  # 609 lines - Everything in one file

# Proposed structure (AFTER):
src/gui/
├── __init__.py
├── app.py                    # ~100 lines - Main window only
├── ui/
│   ├── __init__.py
│   ├── builder.py           # ~150 lines - UI construction
│   └── dialogs.py           # ~120 lines - API key & about dialogs
├── managers/
│   ├── __init__.py
│   ├── file_manager.py      # ~80 lines - File selection logic
│   ├── transcription_manager.py  # ~100 lines - Processing workflow
│   └── progress_tracker.py  # ~60 lines - Metrics and progress
```

**Implementation Location**: Create new directory structure under `src/gui/`

**Time Estimate**: 45 minutes

---

#### Issue 1.2: `src/core/whisper_transcriber.py` - 366 lines

**Location**: `/home/ice/dev/recall/src/core/whisper_transcriber.py`

**Why it's a problem**:
- Mixing HTTP client logic with business logic
- Hard to unit test without mocking HTTP calls
- Violates Single Responsibility Principle

**Specific Fix**:
```python
# Split into:
src/core/whisper/
├── __init__.py
├── transcriber.py        # ~100 lines - Main transcriber class
├── http_client.py        # ~80 lines - HTTP request handling
├── request_builder.py    # ~60 lines - Multipart request construction
├── response_parser.py    # ~60 lines - Response parsing & speaker aggregation
└── models.py            # ~50 lines - Pydantic models for requests/responses
```

**Time Estimate**: 30 minutes

---

### Priority 2: HIGH - Massive Function Decomposition

#### Issue 2.1: `setup_ui()` - 158 lines

**Location**: `/home/ice/dev/recall/src/gui/app.py:43-200`

**Why it's a problem**:
- Function should be under 50 lines (CLAUDE.md guideline)
- Currently 3x over limit
- Impossible to unit test individual UI components

**Specific Fix**:
```python
# BEFORE:
def setup_ui(self):
    # 158 lines of UI setup...
    
# AFTER:
def setup_ui(self) -> None:
    """Initialize the application UI."""
    self._create_menu_bar()
    self._create_main_frame()
    self._create_file_selection_panel()
    self._create_output_panel()
    self._create_progress_panel()
    self._create_control_buttons()
    self._bind_keyboard_shortcuts()

def _create_menu_bar(self) -> None:
    """Create and configure the menu bar."""
    # 15-20 lines max
    
def _create_file_selection_panel(self) -> None:
    """Create the file selection panel with buttons and list."""
    # 15-20 lines max
    
def _create_progress_panel(self) -> None:
    """Create progress bar and metrics display."""
    # 15-20 lines max
```

**Implementation Location**: Refactor within `src/gui/app.py` initially, then move to `ui/builder.py`

**Time Estimate**: 30 minutes

---

#### Issue 2.2: `transcribe_file()` - 164 lines

**Location**: `/home/ice/dev/recall/src/core/whisper_transcriber.py:183-346`

**Why it's a problem**:
- 8x over the 20-line guideline
- Mixing preparation, execution, and parsing
- Error handling scattered throughout

**Specific Fix**:
```python
# BEFORE:
def transcribe_file(self, audio_path: str, progress_callback=None) -> str:
    # 164 lines of mixed concerns...

# AFTER:
def transcribe_file(self, audio_path: str, progress_callback=None) -> str:
    """Main transcription orchestrator."""
    audio_path = self._validate_audio_path(audio_path)
    metrics = self._initialize_metrics(audio_path)
    
    try:
        request = self._prepare_transcription_request(audio_path, metrics, progress_callback)
        response = self._execute_transcription(request, metrics, progress_callback)
        transcript = self._process_response(response, metrics, progress_callback)
        return transcript
    except Exception as e:
        return self._handle_transcription_error(e, metrics, progress_callback)

def _validate_audio_path(self, audio_path: str) -> Path:
    """Validate audio file exists and is accessible."""
    # 10 lines max
    
def _prepare_transcription_request(self, audio_path: Path, metrics, callback) -> Request:
    """Prepare the multipart request."""
    # 15 lines max
    
def _execute_transcription(self, request: Request, metrics, callback) -> Response:
    """Execute HTTP request with proper timeout."""
    # 20 lines max
    
def _process_response(self, response: Response, metrics, callback) -> str:
    """Parse response and aggregate speaker segments."""
    # 20 lines max
```

**Time Estimate**: 30 minutes

---

### Priority 3: HIGH - Missing Type Safety with Pydantic

#### Issue 3.1: Configuration without validation

**Location**: `/home/ice/dev/recall/src/utils/config.py`

**Why it's a problem**:
- No validation of environment variables
- Runtime errors from invalid configuration
- No type safety or IDE support

**Specific Fix**:
```python
# Create new file: src/models/config.py
from pydantic import BaseSettings, Field, AnyHttpUrl, DirectoryPath, validator
from typing import Literal, Optional
from pathlib import Path

class AppConfig(BaseSettings):
    """Application configuration with validation."""
    
    # Transcriber settings
    transcriber_backend: Literal['whisper', 'assemblyai'] = Field(
        default='whisper',
        description="Transcription backend to use"
    )
    
    whisper_api_url: AnyHttpUrl = Field(
        default='http://127.0.0.1:8767',
        description="Whisper API endpoint URL"
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
        if v and not v.startswith(('sk_', 'api_')):
            # AssemblyAI keys typically have a prefix
            pass  # Log warning but don't fail
        return v
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
```

**Implementation Location**: Create `src/models/config.py`

**Time Estimate**: 20 minutes

---

#### Issue 3.2: Job handling without models

**Location**: `/home/ice/dev/recall/src/core/jobs.py`

**Why it's a problem**:
- Using raw dictionaries for job data
- No validation of job status transitions
- Type errors at runtime

**Specific Fix**:
```python
# Create new file: src/models/jobs.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Literal
from enum import Enum
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
    def validate_audio_path(cls, v):
        if not Path(v).exists():
            raise ValueError(f"Audio file not found: {v}")
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
    
    @validator('status')
    def validate_status_transition(cls, v, values):
        """Ensure valid status transitions."""
        # Add logic for valid transitions
        return v
    
    def mark_processing(self) -> None:
        """Transition to processing state."""
        if self.status != JobStatus.PENDING:
            raise ValueError(f"Cannot transition from {self.status} to PROCESSING")
        self.status = JobStatus.PROCESSING
        self.started_at = datetime.now()
    
    def mark_completed(self, result: str) -> None:
        """Mark job as completed with result."""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        self.progress = 100.0
    
    def mark_failed(self, error: str) -> None:
        """Mark job as failed with error message."""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error
```

**Time Estimate**: 25 minutes

---

### Priority 4: MEDIUM - Missing Return Type Hints

**Location**: Throughout `/home/ice/dev/recall/src/gui/app.py`

**Why it's a problem**:
- No IDE support for return types
- Potential runtime errors
- Violates type safety guidelines

**Specific Fix**:
```python
# Add return type hints to all methods
def __init__(self) -> None:
    """Initialize the transcriber application."""
    super().__init__()
    
def setup_ui(self) -> None:
    """Setup the user interface."""
    
def show_error_message(self, title: str, message: str) -> None:
    """Display error message dialog."""
    
def setup_menu(self) -> None:
    """Create application menu bar."""
    
def show_api_key_dialog(self) -> None:
    """Show API key configuration dialog."""
    
def show_about_dialog(self) -> None:
    """Display about dialog."""
    
def load_api_key_from_config(self) -> str:
    """Load API key from configuration file."""
    
def save_api_key_to_config(self, api_key: str) -> None:
    """Save API key to configuration file."""
    
def select_output_directory(self) -> None:
    """Open directory selection dialog."""
    
def select_files(self) -> None:
    """Open file selection dialog."""
    
def select_directory(self) -> None:
    """Open directory selection dialog for batch processing."""
    
def update_files_list(self) -> None:
    """Update the file list display."""
    
def update_status(self, message: str, status: str) -> None:
    """Update status bar message."""
    
def update_elapsed_time(self) -> None:
    """Update elapsed time display."""
    
def update_progress(
    self, 
    message: str, 
    progress: float, 
    status: str, 
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """Update progress bar and status."""
    
def toggle_same_directory(self) -> None:
    """Toggle same directory output option."""
    
def start_transcription(self) -> None:
    """Start the transcription process."""
    
def process_files(self) -> None:
    """Process selected files for transcription."""
    
def reset_ui_state(self) -> None:
    """Reset UI to initial state."""
```

**Time Estimate**: 15 minutes

---

### Priority 5: MEDIUM - Cross-Feature Import Issues

**Current Import Structure Analysis**:

The imports follow a reasonable pattern, but could be improved:

```
webapp.py -> imports from core, utils (OK)
web/api.py -> imports from core, utils (OK)
gui/app.py -> imports from core, utils (OK)
main.py -> imports from gui (OK)
```

**Recommended Improvement**:
```python
# Create feature-specific interfaces
src/features/
├── transcription/
│   ├── __init__.py
│   ├── service.py        # TranscriptionService interface
│   ├── whisper.py        # Whisper implementation
│   └── assemblyai.py     # AssemblyAI implementation
├── audio/
│   ├── __init__.py
│   └── handler.py        # Audio processing
└── configuration/
    ├── __init__.py
    └── settings.py       # Centralized config
```

**Time Estimate**: 45 minutes

---

## Implementation Roadmap

### Phase 0: Cleanup (30 minutes)
1. **Execute cleanup plan** from `cleanup_plan.md`
2. **Remove 11 test files** from root → `tests/` directory
3. **Delete duplicate files** (whisper_transcriber_improved.py, *.bak)
4. **Organize documentation** into `docs/` structure
5. **Update .gitignore** with comprehensive patterns

### Phase 1: Foundation (2 hours)
1. **Create Pydantic models** for configuration and jobs
2. **Add return type hints** to all functions
3. **Set up new directory structure** for vertical slices

### Phase 2: Decomposition (3 hours)
1. **Break down app.py** into multiple modules
2. **Split whisper_transcriber.py** into focused components
3. **Extract massive functions** into smaller units

### Phase 3: Refactoring (2 hours)
1. **Implement dependency injection** for better testing
2. **Create service interfaces** for transcription
3. **Add validation layers** using Pydantic

### Phase 4: Testing & Documentation (1 hour)
1. **Add unit tests** for new components
2. **Update documentation** for new structure
3. **Create migration guide** for existing code

## Success Metrics

- [ ] No files exceed 500 lines
- [ ] No functions exceed 50 lines
- [ ] All functions have return type hints
- [ ] Configuration uses Pydantic validation
- [ ] API models use Pydantic
- [ ] Classes follow Single Responsibility Principle
- [ ] Vertical slice architecture implemented

## Migration Strategy

1. **Start with new features** - implement patterns in new code
2. **Gradual refactoring** - migrate existing code incrementally
3. **Maintain backward compatibility** - use adapters where needed
4. **Test continuously** - ensure no regression

## Anti-Patterns to Avoid

- ❌ Don't create circular imports when splitting files
- ❌ Don't break existing API contracts
- ❌ Don't mix refactoring with feature changes
- ❌ Don't skip type hints "temporarily"
- ❌ Don't ignore CLAUDE.md guidelines

## Conclusion

This refactoring plan addresses critical maintainability issues in the Recall codebase. Each task is designed to be completed in under 1 hour, allowing for incremental improvements without disrupting ongoing development. The priority order ensures maximum impact on code quality and developer experience.

Total estimated time: **8-10 hours** for complete refactoring.