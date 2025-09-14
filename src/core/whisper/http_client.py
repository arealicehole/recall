"""HTTP client for Whisper API communication."""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple

from .models import WhisperHealthCheck, WhisperResponse


class WhisperHTTPClient:
    """Low-level HTTP client for Whisper API communication."""
    
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip('/')
    
    def check_health(self) -> Tuple[Dict[str, Any], bool]:
        """
        Check if Whisper API is available and what features it supports.
        
        Returns:
            Tuple of (health_data, success_flag)
        """
        try:
            health_url = f"{self.api_url}/health"
            with urllib.request.urlopen(health_url, timeout=5) as response:
                data = json.loads(response.read().decode())
                return data, True
                
        except Exception as e:
            print(f"WARNING: Cannot connect to Whisper API at {self.api_url}: {e}")
            print("Make sure the Whisper API service is running:")
            print("  For whisper-on-fedora (port 8771): Check https://github.com/arealicehole/whisper-on-fedora")
            print("  For default service (port 8765): systemctl --user status whisper-api.service")
            return {}, False
    
    def transcribe(self, request_body: bytes, boundary: str, timeout: int) -> WhisperResponse:
        """
        Send transcription request to Whisper API.
        
        Args:
            request_body: Multipart form data body
            boundary: Boundary string for multipart data
            timeout: Request timeout in seconds
            
        Returns:
            WhisperResponse with transcription results
            
        Raises:
            Exception: If the request fails
        """
        try:
            # Create request
            request = urllib.request.Request(
                f"{self.api_url}/v1/transcribe",
                data=request_body,
                headers={
                    'Content-Type': f'multipart/form-data; boundary={boundary}'
                }
            )
            
            # Send request
            with urllib.request.urlopen(request, timeout=timeout) as response:
                response_text = response.read().decode()
                
                # Try to parse as JSON
                try:
                    result = json.loads(response_text)
                    return WhisperResponse(**result)
                except json.JSONDecodeError:
                    # If not JSON, treat as plain text
                    return WhisperResponse(text=response_text)
                    
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else str(e)
            error_msg = f"Whisper API error: {e.code} - {error_body}"
            print(f"ERROR: {error_msg}")
            raise Exception(error_msg)
            
        except urllib.error.URLError as e:
            error_msg = f"Cannot connect to Whisper API at {self.api_url}: {e.reason}"
            print(f"ERROR: {error_msg}")
            print("Make sure the Whisper API service is running:")
            print("  For whisper-on-fedora (port 8771): Check https://github.com/arealicehole/whisper-on-fedora")
            print("  For default service (port 8765): systemctl --user start whisper-api.service")
            raise Exception(error_msg)
    
    def check_diarization_capability(self, health_data: Dict[str, Any]) -> bool:
        """
        Check if diarization is available from health check data.
        
        Args:
            health_data: Response from health check endpoint
            
        Returns:
            True if diarization is available and working
        """
        diarization = health_data.get('diarization', {})
        
        if isinstance(diarization, dict):
            available = (
                diarization.get('modules_available', False) and
                diarization.get('token_present', False) and
                not diarization.get('error')
            )
            
            if diarization.get('error'):
                print(f"WARNING: Diarization has errors: {diarization['error'][:100]}...")
                print("  Speaker labels may not be available")
            elif available:
                print("  Diarization: Available ✓")
            
            return available
        else:
            # Old API format compatibility
            return bool(diarization)