"""Improved Whisper transcriber implementation with better diarization support."""

import json
import mimetypes
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List, Tuple
import urllib.request
import urllib.parse
import urllib.error

from src.core.base_transcriber import BaseTranscriber, TranscriptionMetrics


class WhisperTranscriber(BaseTranscriber):
    """Transcriber implementation using local Whisper API."""
    
    def __init__(self, config):
        super().__init__(config)
        # Get Whisper API URL from config or use default
        self.api_url = getattr(config, 'whisper_api_url', 'http://127.0.0.1:8765')
        self.api_url = self.api_url.rstrip('/')
        
        # Check API health and capabilities
        self.diarization_available = False
        self.api_status = self._check_api_health()
    
    def _check_api_health(self) -> Dict[str, Any]:
        """Check if Whisper API is available and what features it supports."""
        try:
            health_url = f"{self.api_url}/health"
            with urllib.request.urlopen(health_url, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                # Check basic health
                if not data.get('ok', False):
                    print(f"WARNING: Whisper API at {self.api_url} returned unhealthy status")
                else:
                    print(f"INFO: Whisper API connected successfully")
                    print(f"  Model: {data.get('model', 'unknown')}")
                    print(f"  Device: {data.get('device', 'unknown')}")
                
                # Check diarization capability
                diarization = data.get('diarization', {})
                if isinstance(diarization, dict):
                    self.diarization_available = (
                        diarization.get('modules_available', False) and
                        diarization.get('token_present', False) and
                        not diarization.get('error')
                    )
                    
                    if diarization.get('error'):
                        print(f"WARNING: Diarization has errors: {diarization['error'][:100]}...")
                        print("  Speaker labels may not be available")
                    elif self.diarization_available:
                        print("  Diarization: Available ✓")
                else:
                    # Old API format compatibility
                    self.diarization_available = bool(diarization)
                
                return data
                
        except Exception as e:
            print(f"WARNING: Cannot connect to Whisper API at {self.api_url}: {e}")
            print("Make sure the Whisper API service is running:")
            print("  For whisper-on-fedora (port 8767): Check https://github.com/arealicehole/whisper-on-fedora")
            print("  For default service (port 8765): systemctl --user status whisper-api.service")
            return {}
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Get appropriate MIME type for audio file."""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            return mime_type
        
        # Fallback based on extension
        ext_to_mime = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg',
            '.m4a': 'audio/mp4',
            '.ogg': 'audio/ogg',
            '.flac': 'audio/flac',
            '.aac': 'audio/aac',
            '.wma': 'audio/x-ms-wma',
            '.amr': 'audio/amr'
        }
        
        ext = file_path.suffix.lower()
        return ext_to_mime.get(ext, 'audio/wav')
    
    def _build_multipart_request(self, audio_path: Path, enable_diarization: bool = True) -> Tuple[bytes, str]:
        """Build multipart/form-data request body."""
        boundary = '----WebKitFormBoundary' + '7MA4YWxkTrZu0gW'
        body_parts = []
        
        # Read audio file
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        # Get appropriate MIME type
        mime_type = self._get_mime_type(audio_path)
        
        # Add file part
        body_parts.extend([
            f'--{boundary}'.encode(),
            f'Content-Disposition: form-data; name="file"; filename="{audio_path.name}"'.encode(),
            f'Content-Type: {mime_type}'.encode(),
            b'',
            audio_data
        ])
        
        # Add diarize parameter if requested and available
        if enable_diarization and self.diarization_available:
            body_parts.extend([
                f'--{boundary}'.encode(),
                b'Content-Disposition: form-data; name="diarize"',
                b'',
                b'true'
            ])
            print("DEBUG: Diarization enabled in request")
        
        # Add format parameter (always use JSON for structured response)
        body_parts.extend([
            f'--{boundary}'.encode(),
            b'Content-Disposition: form-data; name="format"',
            b'',
            b'json'
        ])
        
        # Add language parameter (can be made configurable later)
        body_parts.extend([
            f'--{boundary}'.encode(),
            b'Content-Disposition: form-data; name="language"',
            b'',
            b'en'
        ])
        
        # End boundary
        body_parts.append(f'--{boundary}--'.encode())
        
        # Join with CRLF
        body = b'\r\n'.join(body_parts)
        
        return body, boundary
    
    def _aggregate_speaker_segments(self, segments: List[Dict]) -> str:
        """Aggregate consecutive segments from the same speaker."""
        if not segments:
            return ""
        
        lines = []
        current_speaker = None
        current_texts = []
        
        for segment in segments:
            speaker = segment.get('speaker', 'Unknown')
            text = segment.get('text', '').strip()
            
            if not text:
                continue
            
            # Map speaker ID to human-readable label
            speaker_label = self.map_speaker_label(speaker)
            
            # If speaker changed, flush current speaker's text
            if speaker_label != current_speaker:
                if current_speaker and current_texts:
                    combined_text = ' '.join(current_texts)
                    lines.append(f"{current_speaker}: {combined_text}")
                
                current_speaker = speaker_label
                current_texts = [text]
            else:
                # Same speaker, accumulate text
                current_texts.append(text)
        
        # Don't forget the last speaker's text
        if current_speaker and current_texts:
            combined_text = ' '.join(current_texts)
            lines.append(f"{current_speaker}: {combined_text}")
        
        return '\n'.join(lines)
    
    def transcribe_file(
        self, 
        audio_path: str, 
        progress_callback: Optional[Callable[[str, float, str, Dict[str, Any]], None]] = None
    ) -> str:
        """
        Transcribe an audio file using local Whisper API.
        
        Args:
            audio_path: Path to the audio file to transcribe
            progress_callback: Optional callback for progress updates
        
        Returns:
            Transcribed text with speaker labels (if available)
        """
        try:
            # Convert to Path for reliable handling
            audio_path = Path(audio_path)
            if not audio_path.exists():
                error_msg = f"Audio file not found: {audio_path}"
                if progress_callback:
                    progress_callback(error_msg, -1, "error", {})
                raise FileNotFoundError(error_msg)
            
            file_size = audio_path.stat().st_size / (1024 * 1024)  # Size in MB
            
            print(f"DEBUG: Starting Whisper transcription for {audio_path.name}")
            print(f"  Size: {file_size:.1f} MB")
            print(f"  Diarization: {'enabled' if self.diarization_available else 'disabled'}")
            
            # Create metrics tracker
            metrics = TranscriptionMetrics(str(audio_path), file_size)
            self.metrics.append(metrics)
            
            # Progress update: preparing
            if progress_callback:
                progress_callback(
                    f"Preparing {audio_path.name} ({file_size:.1f} MB)",
                    10,
                    "preparing",
                    {"metrics": str(metrics)}
                )
            
            # Build multipart request
            body, boundary = self._build_multipart_request(
                audio_path, 
                enable_diarization=self.diarization_available
            )
            
            # Progress update: transcribing
            if progress_callback:
                progress_callback(
                    f"Transcribing {audio_path.name}...",
                    50,
                    "transcribing",
                    {"metrics": str(metrics)}
                )
            
            # Make API request
            request = urllib.request.Request(
                f"{self.api_url}/v1/transcribe",
                data=body,
                headers={
                    'Content-Type': f'multipart/form-data; boundary={boundary}'
                }
            )
            
            # Use longer timeout for large files
            timeout = max(300, int(file_size * 10))  # 10 seconds per MB, minimum 300s
            
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    response_text = response.read().decode()
                    
                    # Try to parse as JSON
                    try:
                        result = json.loads(response_text)
                    except json.JSONDecodeError:
                        # If not JSON, treat as plain text
                        result = {'text': response_text}
                        
            except urllib.error.HTTPError as e:
                error_body = e.read().decode() if e.fp else str(e)
                error_msg = f"Whisper API error: {e.code} - {error_body}"
                print(f"ERROR: {error_msg}")
                if progress_callback:
                    progress_callback(error_msg, -1, "error", {"metrics": str(metrics)})
                raise Exception(error_msg)
                
            except urllib.error.URLError as e:
                error_msg = f"Cannot connect to Whisper API at {self.api_url}: {e.reason}"
                print(f"ERROR: {error_msg}")
                print("Make sure the Whisper API service is running:")
                print("  For whisper-on-fedora (port 8767): Check https://github.com/arealicehole/whisper-on-fedora")
                print("  For default service (port 8765): systemctl --user start whisper-api.service")
                if progress_callback:
                    progress_callback(error_msg, -1, "error", {"metrics": str(metrics)})
                raise Exception(error_msg)
            
            # Complete metrics
            metrics.complete()
            
            # Process response
            full_transcript = ""
            
            # Check for segments with speaker diarization
            if 'segments' in result and result['segments']:
                print(f"DEBUG: Processing {len(result['segments'])} segments")
                
                # Check if we have actual speaker labels
                has_speakers = any(
                    seg.get('speaker') and seg.get('speaker') != 'Unknown' 
                    for seg in result['segments']
                )
                
                if has_speakers:
                    # Aggregate segments by speaker
                    full_transcript = self._aggregate_speaker_segments(result['segments'])
                    print("DEBUG: Speaker diarization applied")
                else:
                    # No speaker info, just concatenate text
                    texts = [seg.get('text', '').strip() for seg in result['segments'] if seg.get('text')]
                    full_transcript = ' '.join(texts)
                    print("DEBUG: No speaker labels found, using plain text")
                    
            elif 'text' in result:
                # Fallback to plain text
                full_transcript = result['text']
                print("DEBUG: Using plain text response")
            else:
                # Handle empty or error response
                if 'error' in result:
                    error_msg = f"Transcription error: {result['error']}"
                else:
                    error_msg = "No speech detected in audio"
                
                if progress_callback:
                    progress_callback(error_msg, -1, "error", {"metrics": str(metrics)})
                return ""
            
            # Progress update: completed
            if progress_callback:
                word_count = len(full_transcript.split())
                progress_callback(
                    f"Completed {audio_path.name} ({word_count} words)",
                    100,
                    "completed",
                    {"metrics": str(metrics)}
                )
            
            print(f"DEBUG: Transcription complete - {len(full_transcript)} characters")
            
            return full_transcript
            
        except Exception as e:
            error_msg = f"Failed to transcribe {audio_path}: {str(e)}"
            print(f"ERROR: {error_msg}")
            if progress_callback:
                progress_callback(
                    error_msg, -1, "error", 
                    {"metrics": str(metrics) if 'metrics' in locals() else ""}
                )
            return ""
    
    def map_speaker_label(self, speaker_id: str) -> str:
        """Map speaker IDs to human-readable labels."""
        # Handle "Unknown" or empty speaker
        if not speaker_id or speaker_id == 'Unknown':
            return "Speaker"
        
        # Convert SPEAKER_00, SPEAKER_01 format to Speaker A, Speaker B
        if speaker_id.startswith("SPEAKER_"):
            try:
                speaker_num = int(speaker_id.split("_")[1])
                # Convert number to letter (0 -> A, 1 -> B, etc.)
                if speaker_num < 26:
                    return f"Speaker {chr(65 + speaker_num)}"
                else:
                    # For more than 26 speakers, use numbers
                    return f"Speaker {speaker_num + 1}"
            except (IndexError, ValueError):
                pass
        
        # Return as-is if not in expected format
        return speaker_id