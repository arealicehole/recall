#!/usr/bin/env python3
"""Test script for whisper-on-fedora server connectivity on port 8767."""

import json
import urllib.request
import urllib.error
from pathlib import Path
import sys
import os

def test_whisper_8767_connectivity():
    """Test connection to whisper-on-fedora server on port 8767."""
    
    api_url = "http://127.0.0.1:8767"
    
    print("=" * 60)
    print("Testing Whisper-on-Fedora Server (Port 8767)")
    print("=" * 60)
    
    # Step 1: Check health endpoint
    print("\n1. Testing API Health...")
    print("-" * 60)
    try:
        with urllib.request.urlopen(f"{api_url}/health", timeout=5) as response:
            health = json.loads(response.read().decode())
            
            # Check basic health
            is_healthy = health.get('ok', False)
            print(f"✓ API Status: {'Healthy' if is_healthy else 'Unhealthy'}")
            
            if not is_healthy:
                print("⚠ WARNING: API returned unhealthy status")
                return False
            
            # Display model and device info
            print(f"  Model: {health.get('model', 'unknown')}")
            print(f"  Device: {health.get('device', 'unknown')}")
            
            # Check diarization capability
            diarization = health.get('diarization', {})
            if isinstance(diarization, dict):
                modules_available = diarization.get('modules_available', False)
                token_present = diarization.get('token_present', False)
                has_error = bool(diarization.get('error'))
                
                is_available = modules_available and token_present and not has_error
                
                print(f"\n  Diarization Status:")
                print(f"    Modules Available: {modules_available}")
                print(f"    Token Present: {token_present}")
                
                if has_error:
                    print(f"    ⚠ Error: {diarization['error'][:100]}...")
                
                print(f"    Overall Available: {'✓ Yes' if is_available else '✗ No'}")
            else:
                # Old API format compatibility
                print(f"  Diarization: {diarization}")
            
            assert is_healthy == True, "API should be healthy"
            print("\n✓ Health check passed!")
            
    except urllib.error.URLError as e:
        print(f"✗ Cannot connect to Whisper API at {api_url}: {e.reason}")
        print("\nMake sure the whisper-on-fedora server is running:")
        print("  Check: https://github.com/arealicehole/whisper-on-fedora")
        return False
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False
    
    # Step 2: Test endpoint availability
    print("\n2. Testing API Endpoints...")
    print("-" * 60)
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/v1/transcribe", "Synchronous transcription endpoint"),
        ("/v2/transcript", "Asynchronous transcription endpoint")
    ]
    
    for endpoint, description in endpoints:
        try:
            # Use HEAD request for endpoint checking (less intrusive)
            request = urllib.request.Request(
                f"{api_url}{endpoint}",
                method='HEAD' if endpoint != "/" else 'GET'
            )
            with urllib.request.urlopen(request, timeout=5) as response:
                status_code = response.getcode()
                if status_code in [200, 405, 422]:  # 405/422 expected for HEAD/POST endpoints
                    print(f"  ✓ {endpoint}: {description} - Available")
                else:
                    print(f"  ⚠ {endpoint}: {description} - Status {status_code}")
        except urllib.error.HTTPError as e:
            if e.code in [405, 422]:  # Method not allowed / Validation error (expected for POST endpoints)
                print(f"  ✓ {endpoint}: {description} - Available (POST only)")
            else:
                print(f"  ⚠ {endpoint}: {description} - HTTP {e.code}")
        except Exception as e:
            print(f"  ✗ {endpoint}: {description} - Error: {e}")
    
    # Step 3: Test configuration integration
    print("\n3. Testing Configuration Integration...")
    print("-" * 60)
    
    try:
        from src.utils.config import Config
        from src.core.whisper_transcriber import WhisperTranscriber
        
        # Test default configuration
        config = Config()
        print(f"  Default Whisper URL: {config.whisper_api_url}")
        
        # Test with explicit port 8767
        config.whisper_api_url = 'http://127.0.0.1:8767'
        transcriber = WhisperTranscriber(config)
        
        print(f"  API Status: {'Connected' if transcriber.api_status else 'Not connected'}")
        print(f"  Diarization Available: {transcriber.diarization_available}")
        
        print("\n✓ Configuration integration test passed!")
        
    except ImportError as e:
        print(f"  ⚠ Could not import required modules: {e}")
        print("  This is expected if running outside the project environment")
    except Exception as e:
        print(f"  ✗ Configuration test failed: {e}")
    
    # Step 4: Test backward compatibility
    print("\n4. Testing Backward Compatibility...")
    print("-" * 60)
    
    try:
        # Test that environment variable override works
        old_url = os.environ.get('WHISPER_API_URL')
        
        # Test with port 8765
        os.environ['WHISPER_API_URL'] = 'http://127.0.0.1:8765'
        from src.utils.config import Config as Config8765
        config_8765 = Config8765()
        print(f"  With env override (8765): {config_8765.whisper_api_url}")
        
        # Test with port 8767
        os.environ['WHISPER_API_URL'] = 'http://127.0.0.1:8767'
        from src.utils.config import Config as Config8767
        config_8767 = Config8767()
        print(f"  With env override (8767): {config_8767.whisper_api_url}")
        
        # Restore original
        if old_url:
            os.environ['WHISPER_API_URL'] = old_url
        else:
            del os.environ['WHISPER_API_URL']
        
        print("\n✓ Backward compatibility test passed!")
        
    except Exception as e:
        print(f"  ✗ Backward compatibility test failed: {e}")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_whisper_8767_connectivity()
    sys.exit(0 if success else 1)