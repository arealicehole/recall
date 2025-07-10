#!/usr/bin/env python3
"""
Debug script for Recall transcription issues
This script helps identify and troubleshoot common transcription problems.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.core.audio_handler import AudioHandler
from src.core.transcriber import Transcriber
import assemblyai as aai

def main():
    print("=" * 50)
    print("Recall Transcription Debug Script")
    print("=" * 50)
    
    # Initialize configuration
    print("\n1. Checking configuration...")
    config = Config()
    
    print(f"   API Key configured: {'Yes' if config.api_key else 'No'}")
    if config.api_key:
        print(f"   API Key length: {len(config.api_key)}")
        print(f"   API Key starts with: {config.api_key[:10]}...")
    
    print(f"   Output directory: {config.output_dir}")
    print(f"   Supported formats: {config.supported_formats}")
    
    # Test API key with AssemblyAI
    if config.api_key:
        print("\n2. Testing AssemblyAI API connection...")
        try:
            aai.settings.api_key = config.api_key
            # Try to create a transcript config to test the API key
            test_config = aai.TranscriptionConfig(
                speaker_labels=True,
                speech_model=aai.SpeechModel.nano
            )
            transcriber = aai.Transcriber(config=test_config)
            print("   ✅ AssemblyAI API key appears to be valid")
        except Exception as e:
            print(f"   ❌ AssemblyAI API key test failed: {e}")
    else:
        print("\n2. ❌ No API key configured")
        print("   Run: python setup_api_key.py")
        return
    
    # Check for test files
    print("\n3. Checking for audio files...")
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    
    if os.path.exists(uploads_dir):
        files = [f for f in os.listdir(uploads_dir) if f.endswith(('.amr', '.mp3', '.wav', '.m4a'))]
        print(f"   Found {len(files)} audio files in uploads directory")
        
        if files:
            # Test audio processing with the first file
            test_file = os.path.join(uploads_dir, files[0])
            print(f"\n4. Testing audio processing with: {files[0]}")
            
            audio_handler = AudioHandler(config)
            prepared_path = audio_handler.prepare_audio(test_file)
            
            if prepared_path:
                print(f"   ✅ Audio preparation successful")
                
                # Test transcription
                print("\n5. Testing transcription...")
                transcriber = Transcriber(config)
                
                try:
                    result = transcriber.transcribe_file(prepared_path)
                    
                    if result:
                        print(f"   ✅ Transcription successful!")
                        print(f"   Transcript length: {len(result)} characters")
                        print(f"   First 100 characters: {result[:100]}...")
                    else:
                        print("   ❌ Transcription returned empty result")
                        print("\n   💡 This usually means:")
                        print("      • Audio file is silent or contains no speech")
                        print("      • Audio is too quiet to detect speech")
                        print("      • Audio file may be corrupted")
                        print("\n   📋 Next steps:")
                        print("      • Run: python check_audio_content.py")
                        print("      • Check that audio files play sound in media player")
                        print("      • Verify recording was done with microphone on")
                        
                except Exception as e:
                    print(f"   ❌ Transcription failed: {e}")
                
                # Cleanup
                if prepared_path != test_file:
                    audio_handler.cleanup_temp_file(prepared_path)
                    
            else:
                print("   ❌ Audio preparation failed")
                print("   Make sure FFmpeg is installed for AMR file support")
        else:
            print("   No audio files found for testing")
            print("   Add some audio files to the uploads directory")
    else:
        print("   No uploads directory found")
    
    print("\n" + "=" * 50)
    print("Debug complete!")
    print("=" * 50)
    
    print("\n📚 For more help, see: TROUBLESHOOTING.md")
    print("🔧 Available tools:")
    print("   • python setup_api_key.py - Configure API key")
    print("   • python check_audio_content.py - Check audio files")
    print("   • python debug_transcription.py - Full system test")

if __name__ == "__main__":
    main() 