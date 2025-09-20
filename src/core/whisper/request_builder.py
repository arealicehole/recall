"""Request builder for Whisper API multipart form data."""

import mimetypes
from pathlib import Path
from typing import Tuple

from .models import TranscriptionRequest


class WhisperRequestBuilder:
    """Builds multipart/form-data requests for Whisper API."""
    
    def __init__(self):
        self.boundary = '----WebKitFormBoundary' + '7MA4YWxkTrZu0gW'
    
    def get_mime_type(self, file_path: Path) -> str:
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
    
    def build_request(
        self, 
        audio_path: Path, 
        config: TranscriptionRequest, 
        diarization_available: bool
    ) -> Tuple[bytes, str]:
        """
        Build multipart/form-data request body.
        
        Args:
            audio_path: Path to audio file
            config: Transcription configuration
            diarization_available: Whether diarization is available on the server
            
        Returns:
            Tuple of (request_body, boundary)
        """
        body_parts = []
        
        # Read audio file
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        # Get appropriate MIME type
        mime_type = self.get_mime_type(audio_path)
        
        # Add file part
        body_parts.extend([
            f'--{self.boundary}'.encode(),
            f'Content-Disposition: form-data; name="file"; filename="{audio_path.name}"'.encode(),
            f'Content-Type: {mime_type}'.encode(),
            b'',
            audio_data
        ])
        
        # Add diarize parameter if requested and available
        if config.enable_diarization and diarization_available:
            body_parts.extend([
                f'--{self.boundary}'.encode(),
                b'Content-Disposition: form-data; name="diarize"',
                b'',
                b'true'
            ])
            print("DEBUG: Diarization enabled in request")
        
        # Add format parameter
        body_parts.extend([
            f'--{self.boundary}'.encode(),
            b'Content-Disposition: form-data; name="format"',
            b'',
            config.format.encode()
        ])
        
        # Add language parameter
        body_parts.extend([
            f'--{self.boundary}'.encode(),
            b'Content-Disposition: form-data; name="language"',
            b'',
            config.language.encode()
        ])
        
        # Add model parameter if specified
        if hasattr(config, 'model') and config.model:
            body_parts.extend([
                f'--{self.boundary}'.encode(),
                b'Content-Disposition: form-data; name="model"',
                b'',
                config.model.encode()
            ])
            print(f"DEBUG: Model parameter added to request: {config.model}")
        
        # End boundary
        body_parts.append(f'--{self.boundary}--'.encode())
        
        # Join with CRLF
        body = b'\r\n'.join(body_parts)
        
        return body, self.boundary