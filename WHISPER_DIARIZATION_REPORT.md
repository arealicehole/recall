# Whisper Server Diarization Integration Report

## Executive Summary
The Recall transcription application requires speaker diarization (speaker identification) functionality from the Whisper server. Currently, the server reports diarization as unavailable despite having the configuration properly set up on the client side.

## Current Server Status (Port 8767)

### Health Check Response
```json
{
    "status": "healthy",
    "gpu_required": true,
    "gpu_available": true,
    "gpu_enforced": true,
    "model": "tiny",
    "device": "cuda",
    "compute_type": "float16",
    "gpu": {
        "device_name": "NVIDIA GeForce RTX 5060 Ti",
        "device_capability": [12, 0],
        "memory_allocated": "0.01GB",
        "memory_reserved": "0.02GB",
        "memory_total": "15.48GB"
    },
    "diarization": {
        "modules_available": false,
        "pipeline_loaded": false,
        "token_present": true,
        "device": null,
        "error": "module 'torchaudio' has no attribute 'AudioMetaData'"
    },
    "processing_mode": {
        "whisper": "GPU",
        "diarization": "N/A"
    },
    "timestamp": "2025-08-31T10:12:17.497421"
}
```

## Issues Identified

### 1. Missing Diarization Modules
- **Status**: `modules_available: false`
- **Error**: `"module 'torchaudio' has no attribute 'AudioMetaData'"`
- **Impact**: Diarization cannot be enabled despite client requests

### 2. Pipeline Not Loaded
- **Status**: `pipeline_loaded: false`
- **Cause**: Missing required Python packages for speaker diarization

## Client-Side Configuration

### Request Format
The Recall application sends transcription requests with the following structure:

```python
class TranscriptionRequest(BaseModel):
    enable_diarization: bool = Field(True, description="Whether to enable speaker diarization")
    language: str = Field("en", description="Language code for transcription")
    format: str = Field("json", description="Response format (json/text)")
    model: str = Field("tiny", description="Whisper model to use")
```

### Default Settings
- **enable_diarization**: `True` (always requested by default)
- **model**: Configurable (tiny, base, small, medium, large, large-v2, large-v3)
- **format**: JSON (expecting structured response with speaker labels)

## Required Server Updates

### 1. Install Required Dependencies
```bash
# Core diarization package
pip install pyannote.audio

# Dependencies for audio processing
pip install torchaudio --upgrade
pip install pyannote.core
pip install pyannote.database
pip install pyannote.metrics
pip install pyannote.pipeline

# Optional but recommended
pip install speechbrain
```

### 2. Fix TorchAudio Compatibility
The error `"module 'torchaudio' has no attribute 'AudioMetaData'"` suggests a version compatibility issue. Recommended fix:

```bash
# Ensure compatible versions
pip install torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
```

### 3. Hugging Face Token Configuration
The server reports `token_present: true`, but ensure it has proper access:

```python
# In your server configuration
from pyannote.audio import Pipeline

# Initialize with token
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="YOUR_HF_TOKEN"
)
```

## Expected Response Format

When diarization is enabled and working, the client expects responses in this format:

### With Speaker Diarization
```json
{
    "text": "Full transcript text...",
    "segments": [
        {
            "start": 0.0,
            "end": 2.5,
            "text": "Hello, how are you?",
            "speaker": "SPEAKER_00"
        },
        {
            "start": 2.5,
            "end": 5.0,
            "text": "I'm doing well, thank you.",
            "speaker": "SPEAKER_01"
        }
    ],
    "speakers": {
        "SPEAKER_00": {"segments": 5, "duration": 45.2},
        "SPEAKER_01": {"segments": 4, "duration": 38.7}
    }
}
```

### Without Diarization (Current Fallback)
```json
{
    "text": "Full transcript without speaker labels...",
    "segments": [
        {
            "start": 0.0,
            "end": 5.0,
            "text": "Hello, how are you? I'm doing well, thank you."
        }
    ]
}
```

## Performance Considerations

### GPU Utilization
- Current: Whisper on GPU, Diarization N/A
- Target: Both Whisper and Diarization on GPU
- The RTX 5060 Ti with 15.48GB memory has sufficient capacity for both

### Processing Pipeline
Recommended approach for optimal performance:

1. **Parallel Processing**: Run Whisper transcription and VAD (Voice Activity Detection) in parallel
2. **Speaker Embedding**: Extract speaker embeddings only for speech segments
3. **Clustering**: Use optimized clustering for speaker identification
4. **Merge Results**: Combine transcription with speaker labels

## Testing Endpoints

### Current Test Request
```bash
curl -X POST http://127.0.0.1:8767/transcribe \
  -F "audio=@test_audio.mp3" \
  -F "enable_diarization=true" \
  -F "model=tiny" \
  -F "format=json"
```

### Expected Successful Response
```json
{
    "status": "success",
    "diarization_enabled": true,
    "speakers_found": 2,
    "segments": [...],
    "processing_time": {
        "whisper": 2.3,
        "diarization": 1.8,
        "total": 4.1
    }
}
```

## Integration Priority

### Critical Features
1. **Speaker Label Format**: Use consistent format (SPEAKER_00, SPEAKER_01, etc.)
2. **Segment Timestamps**: Provide accurate start/end times for each speaker segment
3. **Fallback Behavior**: When diarization fails, still return transcription without speaker labels

### Nice-to-Have Features
1. **Speaker Count Detection**: Automatic detection of number of speakers
2. **Speaker Confidence Scores**: Confidence level for speaker identification
3. **Overlapping Speech Detection**: Handle multiple simultaneous speakers
4. **Speaker Gender Detection**: Optional gender classification

## Client Application Context

### Use Cases
1. **Meeting Transcriptions**: Multiple participants need identification
2. **Interview Recordings**: Distinguish interviewer from interviewee  
3. **Podcast Episodes**: Identify host(s) and guest(s)
4. **Phone Conversations**: Two-party speaker separation

### Current Workaround
When diarization is unavailable, the application:
- Continues with plain transcription
- Notifies user that speaker identification is unavailable
- Logs the limitation for debugging

## Recommendations

### Immediate Actions
1. Install missing pyannote.audio dependencies
2. Fix torchaudio compatibility issue
3. Verify Hugging Face token has proper model access

### Testing Protocol
1. Start with 2-speaker audio files
2. Test with various audio qualities (8kHz to 48kHz)
3. Verify speaker consistency across long recordings
4. Test fallback behavior when diarization fails

### Future Enhancements
1. Support for configurable number of speakers
2. Real-time diarization for streaming audio
3. Speaker profile persistence across sessions
4. Custom speaker labels (replace SPEAKER_00 with actual names)

## Contact Information

For questions or clarifications about this integration:
- **Application**: Recall Transcription System
- **Current Integration**: whisper-on-fedora server on port 8767
- **Diarization Requirement**: Default ON, toggle available in UI
- **Models Supported**: tiny, base, small, medium, large, large-v2, large-v3

## Appendix: Sample Test Audio

For testing diarization, use audio files with:
- Clear speaker changes
- Minimal overlapping speech
- Good audio quality (minimal background noise)
- At least 2 distinct speakers
- Duration of 30 seconds to 5 minutes

The Recall application has been tested with:
- IC Recorder MP3 files (44.1kHz, stereo)
- Meeting recordings (various formats)
- Phone call recordings (8kHz, mono)

---

**Document Generated**: August 31, 2025  
**Purpose**: Enable speaker diarization support in Whisper server for Recall application  
**Priority**: High - Core feature requirement for user workflows