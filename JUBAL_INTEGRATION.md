# Recall Service API Documentation for Jubal Integration

This document provides the API contract for integrating Recall's audio transcription service with the Jubal orchestrator framework.

## Service Overview

**Service Name:** Recall Audio Transcription Service  
**Default Port:** 5000  
**Protocol:** HTTP REST API  
**Response Format:** JSON  
**Processing Model:** Asynchronous job-based processing  

## Docker Deployment

### Dual Backend Deployment (Recommended)
```bash
# Build the container
docker build -t recall-service .

# Run with BOTH backends available for runtime switching
docker run -d \
  --name recall-service \
  -p 5000:5000 \
  -v recall-uploads:/app/uploads \
  -v recall-transcripts:/app/transcripts \
  -e TRANSCRIBER_BACKEND=assemblyai \
  -e ASSEMBLYAI_API_KEY=your_api_key_here \
  -e WHISPER_API_URL=http://host.docker.internal:8771 \
  --restart unless-stopped \
  recall-service
```

### Single Backend Deployment
```bash
# AssemblyAI only
docker run -d --name recall-service -p 5000:5000 \
  -e ASSEMBLYAI_API_KEY=your_api_key_here \
  -e TRANSCRIBER_BACKEND=assemblyai \
  recall-service

# Whisper only  
docker run -d --name recall-service -p 5000:5000 \
  -e TRANSCRIBER_BACKEND=whisper \
  -e WHISPER_API_URL=http://whisper-server:8771 \
  recall-service
```

## API Endpoints

### 1. Health Check Endpoint

**Endpoint:** `GET /api/status`  
**Purpose:** Check service health and backend availability  

**Response Format:**
```json
{
  "status": "ok",
  "timestamp": "2025-09-15T19:30:00.000Z",
  "backend": {
    "current": "assemblyai",
    "name": "AssemblyAI Cloud",
    "available": true
  },
  "api_key_configured": true,
  "whisper_url": "http://127.0.0.1:8771"
}
```

**Response Fields:**
- `status`: Always "ok" if service is running
- `backend.current`: Current backend selection ("assemblyai" or "whisper")
- `backend.available`: Boolean indicating if backend is ready for processing
- `api_key_configured`: Boolean indicating if AssemblyAI API key is set

### 2. Audio Transcription Endpoint

**Endpoint:** `POST /api/upload`  
**Purpose:** Submit audio files for transcription  
**Content-Type:** `multipart/form-data`  

**Request Parameters:**
- `files`: One or more audio files (required)
- `output_directory`: Directory for transcript output (optional, default: "transcripts")
- `same_as_input`: Boolean, save transcripts with audio files (optional, default: false)

**Supported Audio Formats:**
- MP3, WAV, M4A, OGG, FLAC, AAC, WMA, AMR

**Response Format:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "files_count": 2,
  "status": "started"
}
```

**Response Fields:**
- `job_id`: Unique identifier for tracking the transcription job
- `files_count`: Number of files accepted for processing
- `status`: Always "started" for successful submissions

### 3. Job Status Endpoint

**Endpoint:** `GET /api/job/{job_id}`  
**Purpose:** Check transcription job progress and retrieve results  

**Response Format (In Progress):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45.0,
  "current_file": "audio_file_2.mp3",
  "start_time": "2025-09-15T19:30:00.000Z",
  "files_count": 2,
  "results": [
    {
      "file": "audio_file_1.mp3",
      "status": "completed",
      "transcript_path": "/app/transcripts/audio_file_1_transcription.txt",
      "transcript": "Speaker A: Hello, this is a test transcription..."
    }
  ]
}
```

**Response Format (Completed):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100.0,
  "start_time": "2025-09-15T19:30:00.000Z",
  "end_time": "2025-09-15T19:32:30.000Z",
  "files_count": 2,
  "results": [
    {
      "file": "audio_file_1.mp3",
      "status": "completed",
      "transcript_path": "/app/transcripts/audio_file_1_transcription.txt",
      "transcript": "Speaker A: Hello, this is a test transcription with speaker diarization. Speaker B: Yes, this service supports multiple speakers."
    },
    {
      "file": "audio_file_2.mp3",
      "status": "completed",
      "transcript_path": "/app/transcripts/audio_file_2_transcription.txt",
      "transcript": "Speaker A: This is the second audio file transcription..."
    }
  ]
}
```

**Job Status Values:**
- `"processing"`: Job is actively being processed
- `"completed"`: All files processed successfully
- `"failed"`: Job failed due to system error
- Individual files can have `"completed"` or `"error"` status

## Error Handling

### HTTP Status Codes
- `200`: Success
- `400`: Bad request (invalid file format, missing files, etc.)
- `401`: Unauthorized (missing or invalid API key for AssemblyAI backend)
- `404`: Job not found
- `500`: Internal server error

### Error Response Format
```json
{
  "error": "AssemblyAI API key not configured. Please set it via the /api/config endpoint or switch to Local Whisper."
}
```

### Common Error Scenarios
1. **No API Key (AssemblyAI backend):** HTTP 401 with API key configuration error
2. **Backend Unavailable:** HTTP 400 with backend availability error
3. **Invalid File Format:** HTTP 400 with file format error
4. **Job Not Found:** HTTP 404 with job not found error
5. **Silent Audio:** Individual file marked as error with "silent audio" message

## Configuration Endpoints

### Backend Configuration
**Endpoint:** `GET /api/backend`  
**Purpose:** Get available transcription backends and current configuration

**Response:**
```json
{
  "current_backend": "assemblyai",
  "whisper_model": "tiny",
  "enable_diarization": true,
  "available_backends": [
    {
      "id": "assemblyai",
      "name": "AssemblyAI Cloud",
      "available": true,
      "supports_diarization": true
    },
    {
      "id": "whisper",
      "name": "Local Whisper",
      "available": false,
      "error": "Whisper server not accessible at http://127.0.0.1:8771"
    }
  ]
}
```

### API Key Configuration
**Endpoint:** `POST /api/config`  
**Content-Type:** `application/json`

**Request:**
```json
{
  "api_key": "your_assemblyai_api_key_here"
}
```

**Response:**
```json
{
  "success": true
}
```

## Integration Workflow for Jubal Adapter

### Recommended Processing Flow

1. **Health Check**
   ```
   GET /api/status
   → Verify backend availability before processing
   ```

2. **Submit Audio**
   ```
   POST /api/upload
   → Submit audio file(s) for transcription
   → Receive job_id for tracking
   ```

3. **Poll for Completion**
   ```
   GET /api/job/{job_id}
   → Poll every 5-10 seconds
   → Check status until "completed" or "failed"
   ```

4. **Extract Results**
   ```
   Parse job response → Extract transcript text from results array
   ```

### Sample Integration Code Pattern

```python
import httpx
import asyncio

async def transcribe_audio(recall_url: str, audio_data: bytes, filename: str):
    async with httpx.AsyncClient() as client:
        # 1. Health check
        health = await client.get(f"{recall_url}/api/status")
        if not health.json()["backend"]["available"]:
            raise Exception("Recall backend not available")
        
        # 2. Submit job
        files = {"files": (filename, audio_data, "audio/mpeg")}
        job_response = await client.post(f"{recall_url}/api/upload", files=files)
        job_id = job_response.json()["job_id"]
        
        # 3. Poll for completion
        while True:
            status_response = await client.get(f"{recall_url}/api/job/{job_id}")
            job_data = status_response.json()
            
            if job_data["status"] == "completed":
                # Extract transcripts from results
                transcripts = []
                for result in job_data["results"]:
                    if result["status"] == "completed":
                        transcripts.append(result["transcript"])
                return transcripts
            elif job_data["status"] == "failed":
                raise Exception(f"Transcription failed: {job_data.get('error')}")
            
            await asyncio.sleep(5)  # Poll every 5 seconds
```

## Backend Management and Runtime Switching

### Dual Backend Configuration

Recall supports **both backends simultaneously** for maximum flexibility. Configure both at startup:

```bash
# Container with both backends available
docker run -d \
  -e TRANSCRIBER_BACKEND=assemblyai \
  -e ASSEMBLYAI_API_KEY=your_key_here \
  -e WHISPER_API_URL=http://whisper-server:8771 \
  recall-service
```

### Dynamic Backend Switching

**Check Available Backends:**
```bash
GET /api/backend
{
  "current_backend": "assemblyai",
  "available_backends": [
    {
      "id": "whisper",
      "name": "Whisper (Local)", 
      "available": true,
      "supports_diarization": false
    },
    {
      "id": "assemblyai",
      "name": "AssemblyAI (Cloud)",
      "available": true, 
      "supports_diarization": true
    }
  ]
}
```

**Switch to Whisper Backend:**
```bash
POST /api/backend
Content-Type: application/json

{
  "backend": "whisper"
}
```

**Switch to AssemblyAI Backend:**
```bash
POST /api/backend
Content-Type: application/json

{
  "backend": "assemblyai"
}
```

**Change Whisper Model and Settings:**
```bash
POST /api/backend
Content-Type: application/json

{
  "backend": "whisper",
  "model": "small",
  "enable_diarization": true
}
```

### Backend Selection Strategy for Jubal

**Recommended approach for Jubal adapter:**

1. **Check backend availability** on startup
2. **Choose optimal backend** per request based on:
   - File size (Whisper for large files if GPU available)
   - Speed requirements (AssemblyAI for faster cloud processing)
   - Diarization needs (AssemblyAI has better speaker separation)
   - Cost considerations (Whisper is free, AssemblyAI is paid)

3. **Handle failover** automatically:
   ```python
   # Pseudocode for Jubal adapter
   async def transcribe_with_fallback(audio_file):
       # Try preferred backend
       if whisper_available and file_size > 100MB:
           try:
               return await transcribe_with_whisper(audio_file)
           except Exception:
               return await transcribe_with_assemblyai(audio_file)
       else:
           return await transcribe_with_assemblyai(audio_file)
   ```

### Backend Availability Logic

- **Whisper**: Available if server responds at configured URL
- **AssemblyAI**: Available if API key is configured and valid
- **Auto-selection**: Service uses best available backend if current backend fails

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TRANSCRIBER_BACKEND` | `whisper` | Backend to use: "assemblyai" or "whisper" |
| `ASSEMBLYAI_API_KEY` | None | AssemblyAI API key (required for cloud backend) |
| `WHISPER_API_URL` | `http://127.0.0.1:8771` | Whisper server URL (for local backend) |
| `WHISPER_MODEL` | `tiny` | Whisper model size |
| `ENABLE_DIARIZATION` | `true` | Enable speaker identification |
| `OUTPUT_DIRECTORY` | `transcripts` | Default output directory |

## Service Features

### Transcription Capabilities
- **Speaker Diarization**: Automatic speaker identification and labeling
- **Multiple Formats**: Support for all major audio formats
- **Dual Backend Support**: Cloud (AssemblyAI) AND/OR Local (Whisper) processing
- **Runtime Backend Switching**: Change backends via API without restart
- **Intelligent Failover**: Automatic fallback if primary backend unavailable
- **Async Processing**: Non-blocking job-based workflow
- **Error Recovery**: Per-file error handling with detailed messages

### Performance Characteristics
- **AssemblyAI Backend**: 2-5x real-time processing speed
- **Local Whisper Backend**: 0.5x to 54x speed (depending on hardware)
- **File Size Limit**: 500MB per request
- **Concurrent Jobs**: Unlimited (resource dependent)

### Output Format
- **Text Format**: Plain text with speaker labels
- **Speaker Format**: `Speaker A: [text]`, `Speaker B: [text]`
- **File Naming**: `{original_name}_transcription.txt`
- **Encoding**: UTF-8 text files

## Testing the Integration

### Quick Test Commands
```bash
# Health check
curl http://localhost:5000/api/status

# Upload test file
curl -X POST -F "files=@test_audio.wav" http://localhost:5000/api/upload

# Check job status (use job_id from upload response)
curl http://localhost:5000/api/job/550e8400-e29b-41d4-a716-446655440000
```

## Support and Troubleshooting

### Common Issues
1. **Backend not available**: Check API key configuration or Whisper server connectivity
2. **Job stuck in processing**: Check logs for file format or content issues
3. **Empty transcripts**: Audio may be silent or corrupted
4. **Connection errors**: Verify service is running and accessible on port 5000

### Log Locations
- **Docker logs**: `docker logs recall-service`
- **Service logs**: Check container stdout for detailed processing information

This documentation provides everything needed for the Jubal team to successfully integrate with the Recall audio transcription service.