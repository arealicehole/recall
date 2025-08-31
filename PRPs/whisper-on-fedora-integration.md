name: "Whisper-on-Fedora Local API Integration"
description: |
  Integration with local Whisper server running on port 8767 from whisper-on-fedora repository

---

## Goal

**Feature Goal**: Enable Recall application to use the local Whisper server from the whisper-on-fedora repository running on port 8767 instead of port 8765

**Deliverable**: Updated configuration system and WhisperTranscriber to support the new port with full backward compatibility

**Success Definition**: Application successfully transcribes audio files using the Whisper server on port 8767 with speaker diarization support when available

## User Persona

**Target User**: Developer/End User running the whisper-on-fedora server locally

**Use Case**: User has the whisper-on-fedora server (https://github.com/arealicehole/whisper-on-fedora) running on port 8767 and wants to use it with Recall for local, privacy-preserving transcription

**User Journey**: 
1. User starts whisper-on-fedora server on port 8767
2. User configures Recall to use port 8767 via environment variable or .env file
3. User launches Recall application
4. User selects audio files for transcription
5. Recall connects to local Whisper server and transcribes with speaker diarization

**Pain Points Addressed**: 
- Current hardcoded port 8765 conflicts with whisper-on-fedora default port 8767
- Need for seamless integration with existing whisper-on-fedora installation

## Why

- Enables use of the optimized whisper-on-fedora server without port conflicts
- Maintains privacy by using local GPU-accelerated transcription
- Leverages existing whisper-on-fedora features including speaker diarization
- Provides flexibility for users with different Whisper server configurations

## What

Enable configuration of Whisper API port to use whisper-on-fedora server on port 8767 while maintaining full backward compatibility with existing setups.

### Success Criteria

- [ ] Application connects to Whisper server on port 8767 when configured
- [ ] Health check properly detects API status and diarization capabilities
- [ ] Transcription with speaker diarization works correctly
- [ ] Backward compatibility maintained for existing port 8765 users
- [ ] Configuration can be set via environment variable or .env file

## All Needed Context

### Context Completeness Check

_This PRP provides complete context for implementing Whisper-on-Fedora integration including API specifications, configuration patterns, and existing codebase structure._

### Documentation & References

```yaml
# MUST READ - Include these in your context window
- url: https://github.com/arealicehole/whisper-on-fedora
  why: Official repository with API specifications and endpoints
  critical: API runs on port 8767 by default, supports /v1/transcribe and /v2/transcript endpoints

- file: src/core/whisper_transcriber.py
  why: Current WhisperTranscriber implementation that needs port configuration update
  pattern: Line 20-21 shows current port configuration, health check logic at lines 27-67
  gotcha: Diarization availability detection logic must be preserved (lines 43-58)

- file: src/utils/config.py
  why: Configuration management where WHISPER_API_URL is defined
  pattern: Line 15 shows current default URL with port 8765
  gotcha: Must maintain backward compatibility for existing users

- file: src/core/transcriber.py
  why: Factory pattern for transcriber selection
  pattern: Lines 26-32 show Whisper backend initialization
  gotcha: Error messages reference systemctl commands that may need updating

- docfile: test_whisper_integration.py
  why: Shows expected API interaction patterns and health check format
  section: Health check and transcription request format
```

### Current Codebase tree (run `tree` in the root of the project) to get an overview of the codebase

```bash
recall/
├── src/
│   ├── core/
│   │   ├── whisper_transcriber.py     # WhisperTranscriber class (port 8765)
│   │   ├── transcriber.py             # Factory for backend selection
│   │   ├── base_transcriber.py        # Base class for transcribers
│   │   └── assemblyai_transcriber.py  # Alternative backend
│   ├── utils/
│   │   └── config.py                  # Config class with WHISPER_API_URL
│   └── gui/
│       └── app.py                      # GUI application
├── test_whisper_integration.py        # Integration tests
├── .env.example                        # Example environment configuration
└── requirements.txt                    # Dependencies
```

### Desired Codebase tree with files to be added and responsibility of file

```bash
recall/
├── src/
│   ├── core/
│   │   ├── whisper_transcriber.py     # MODIFIED: Support configurable port
│   │   └── ...
│   ├── utils/
│   │   └── config.py                  # MODIFIED: Default to port 8767
│   └── ...
├── .env.example                        # MODIFIED: Document WHISPER_API_URL
├── test_whisper_8767.py              # NEW: Test for port 8767 connectivity
└── ...
```

### Known Gotchas of our codebase & Library Quirks

```python
# CRITICAL: whisper-on-fedora API differences from default implementation:
# - Default port is 8767 (not 8765)
# - Supports both /v1/transcribe (sync) and /v2/transcript (async) endpoints
# - Diarization requires both modules_available=true AND token_present=true
# - Health endpoint returns nested diarization object with error field
# - Request timeout should scale with file size (10 seconds per MB minimum)
```

## Implementation Blueprint

### Data models and structure

No new data models required - existing TranscriptionMetrics and response handling sufficient.

### Implementation Tasks (ordered by dependencies)

```yaml
Task 1: MODIFY src/utils/config.py
  - UPDATE: Default WHISPER_API_URL from port 8765 to 8767
  - FOLLOW pattern: Line 15 environment variable loading
  - PRESERVE: Backward compatibility via environment variable override
  - PLACEMENT: Line 15 modification

Task 2: MODIFY src/core/whisper_transcriber.py  
  - VERIFY: Port configuration from config object works correctly
  - UPDATE: Error messages to reference both possible ports
  - FOLLOW pattern: Lines 64-66 error message format
  - PRESERVE: All existing diarization detection logic
  - PLACEMENT: Lines 63-66 for error messages

Task 3: MODIFY .env.example
  - ADD: Documentation for WHISPER_API_URL configuration
  - EXAMPLE: WHISPER_API_URL=http://127.0.0.1:8767
  - EXPLAIN: How to configure for different ports
  - PLACEMENT: After TRANSCRIBER_BACKEND line

Task 4: CREATE test_whisper_8767.py
  - IMPLEMENT: Connectivity test for port 8767
  - FOLLOW pattern: test_whisper_integration.py structure
  - TEST: Health check, diarization availability, basic transcription
  - PLACEMENT: Root directory with other test files

Task 5: UPDATE documentation
  - MODIFY: README.md to mention port configuration
  - ADD: Section about whisper-on-fedora integration
  - PLACEMENT: In configuration section
```

### Implementation Patterns & Key Details

```python
# config.py modification (Task 1)
class Config:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get Whisper API URL - now defaults to whisper-on-fedora port
        # Supports both whisper-on-fedora (8767) and original (8765) servers
        self.whisper_api_url = os.getenv('WHISPER_API_URL', 'http://127.0.0.1:8767')

# whisper_transcriber.py modification (Task 2)
def _check_api_health(self) -> Dict[str, Any]:
    except Exception as e:
        print(f"WARNING: Cannot connect to Whisper API at {self.api_url}: {e}")
        print("Make sure the Whisper API service is running:")
        print("  For whisper-on-fedora (port 8767): Check https://github.com/arealicehole/whisper-on-fedora")
        print("  For default service (port 8765): systemctl --user status whisper-api.service")
        return {}

# .env.example addition (Task 3)
# Transcriber backend selection (whisper or assemblyai)
TRANSCRIBER_BACKEND=whisper

# Whisper API URL configuration
# For whisper-on-fedora: http://127.0.0.1:8767 (default)
# For original whisper: http://127.0.0.1:8765
WHISPER_API_URL=http://127.0.0.1:8767

# test_whisper_8767.py pattern (Task 4)
def test_whisper_8767_connectivity():
    """Test connection to whisper-on-fedora server on port 8767."""
    api_url = "http://127.0.0.1:8767"
    
    # Test health endpoint
    with urllib.request.urlopen(f"{api_url}/health", timeout=5) as response:
        health = json.loads(response.read().decode())
        assert health.get('ok') == True, "API should be healthy"
        
    # Test diarization availability
    diarization = health.get('diarization', {})
    if isinstance(diarization, dict):
        is_available = (
            diarization.get('modules_available', False) and
            diarization.get('token_present', False) and
            not diarization.get('error')
        )
        print(f"Diarization available: {is_available}")
```

### Integration Points

```yaml
CONFIG:
  - file: .env
  - change: Set WHISPER_API_URL=http://127.0.0.1:8767
  - fallback: Works with 8765 if explicitly configured

ENVIRONMENT:
  - variable: WHISPER_API_URL
  - default: http://127.0.0.1:8767
  - override: User can set to any URL/port combination

TESTING:
  - manual: python test_whisper_8767.py
  - integration: Existing tests work with new port via config
```

## Validation Loop

### Level 1: Syntax & Style (Immediate Feedback)

```bash
# Check Python syntax
python -m py_compile src/utils/config.py
python -m py_compile src/core/whisper_transcriber.py
python -m py_compile test_whisper_8767.py

# Run linting if available
rg --files -g "*.py" | xargs python -m flake8 --max-line-length=100

# Expected: Zero syntax errors
```

### Level 2: Unit Tests (Component Validation)

```bash
# Test configuration loading
python -c "from src.utils.config import Config; c = Config(); print(f'Whisper URL: {c.whisper_api_url}')"

# Test with custom port via environment
WHISPER_API_URL=http://127.0.0.1:8765 python -c "from src.utils.config import Config; c = Config(); print(f'Custom URL: {c.whisper_api_url}')"

# Run connectivity test
python test_whisper_8767.py

# Expected: Configuration loads correctly, tests pass if server is running
```

### Level 3: Integration Testing (System Validation)

```bash
# Start Recall with new configuration
WHISPER_API_URL=http://127.0.0.1:8767 python run.py &
sleep 3

# Test transcription via GUI or direct API call
# Create test audio if needed
echo "import pydub; pydub.AudioSegment.silent(5000).export('test.wav', format='wav')" | python

# Test with whisper_transcriber directly
python -c "
from src.utils.config import Config
from src.core.whisper_transcriber import WhisperTranscriber
config = Config()
config.whisper_api_url = 'http://127.0.0.1:8767'
transcriber = WhisperTranscriber(config)
print('API Status:', transcriber.api_status)
print('Diarization Available:', transcriber.diarization_available)
"

# Expected: Application connects to port 8767, transcription works
```

### Level 4: Creative & Domain-Specific Validation

```bash
# Test backward compatibility
WHISPER_API_URL=http://127.0.0.1:8765 python run.py &
# Should work with old port if specified

# Test error handling when server not running
pkill -f "python.*8767"  # Stop server if running
python test_whisper_8767.py
# Should show appropriate error messages

# Test with actual audio file
curl -L https://github.com/pytorch/audio/raw/main/test/assets/steam-train-whistle-daniel_simon.wav -o test_audio.wav
python -c "
from pathlib import Path
from src.utils.config import Config
from src.core.whisper_transcriber import WhisperTranscriber
config = Config()
transcriber = WhisperTranscriber(config)
result = transcriber.transcribe_file('test_audio.wav')
print('Transcription length:', len(result))
"

# Performance check with larger file
# Expected: Transcription completes, speaker labels if diarization available
```

## Final Validation Checklist

### Technical Validation

- [ ] Configuration defaults to port 8767
- [ ] Environment variable override works for custom ports
- [ ] WhisperTranscriber connects to configured port
- [ ] Health check properly detects capabilities
- [ ] Error messages reference both possible server types

### Feature Validation

- [ ] Transcription works with port 8767 server
- [ ] Speaker diarization detected and used when available
- [ ] Backward compatibility maintained for port 8765
- [ ] GUI shows correct backend information
- [ ] Test file validates connectivity

### Code Quality Validation

- [ ] Minimal changes to existing code
- [ ] Clear documentation in .env.example
- [ ] Helpful error messages for troubleshooting
- [ ] No hardcoded ports in transcriber code
- [ ] Configuration centralized in Config class

### Documentation & Deployment

- [ ] .env.example documents WHISPER_API_URL option
- [ ] README updated with configuration instructions
- [ ] Test file provides validation tool
- [ ] Error messages guide users to solutions

---

## Anti-Patterns to Avoid

- ❌ Don't hardcode port 8767 - keep it configurable
- ❌ Don't break existing port 8765 installations
- ❌ Don't remove diarization detection logic
- ❌ Don't change API endpoint paths (/v1/transcribe)
- ❌ Don't modify transcription response parsing
- ❌ Don't alter the factory pattern in transcriber.py

## Confidence Score

**Implementation Success Likelihood: 9/10**

This PRP provides comprehensive context for updating the Recall application to work with the whisper-on-fedora server on port 8767. The changes are minimal, focused on configuration, and maintain full backward compatibility. The implementation leverages existing patterns and requires no architectural changes.