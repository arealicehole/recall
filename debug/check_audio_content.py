#!/usr/bin/env python3
"""
Audio Content Checker
This script analyzes audio files in the 'uploads' directory to check for common issues
like silence, low volume, or corruption before transcription.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from pydub import AudioSegment, silence
except ImportError:
    print("Error: pydub or its dependencies are not installed. Please install them.")
    print("You can install them using: pip install pydub")
    sys.exit(1)

def analyze_audio_content(file_path):
    """Analyze if audio file contains speech content"""
    print(f"\n🔍 Analyzing: {os.path.basename(file_path)}")
    print("-" * 50)
    
    try:
        # Load audio file
        if file_path.lower().endswith('.amr'):
            audio = AudioSegment.from_file(file_path, format="amr")
        else:
            audio = AudioSegment.from_file(file_path)
        
        # Basic audio info
        duration = len(audio) / 1000  # Convert to seconds
        print(f"📏 Duration: {duration:.1f} seconds")
        print(f"🔊 Sample rate: {audio.frame_rate} Hz")
        print(f"📡 Channels: {audio.channels}")
        print(f"🎚️  Volume (dBFS): {audio.dBFS:.1f}")
        
        # Check if audio is completely silent
        if audio.dBFS == float('-inf'):
            print("❌ Audio is completely silent")
            return False
        
        # Check volume level
        max_volume = audio.max_dBFS
        print(f"📢 Peak volume: {max_volume:.1f} dBFS")
        
        if max_volume < -40:
            print("⚠️  Audio is very quiet (may be difficult to transcribe)")
        elif max_volume < -20:
            print("⚠️  Audio is quiet but should be transcribable")
        else:
            print("✅ Audio volume is good")
        
        # Detect non-silent segments
        print("\n🔍 Analyzing speech content...")
        
        # Detect non-silent chunks
        # min_silence_len: minimum length of silence to be considered a pause (ms)
        # silence_thresh: silence threshold in dBFS
        nonsilent_ranges = silence.detect_nonsilent(
            audio,
            min_silence_len=500,  # 500ms of silence
            silence_thresh=audio.dBFS - 16  # 16dB below average
        )
        
        if not nonsilent_ranges:
            print("❌ No speech content detected - audio appears to be silent")
            return False
        
        # Calculate speech percentage
        total_speech_duration = sum(end - start for start, end in nonsilent_ranges)
        speech_percentage = (total_speech_duration / len(audio)) * 100
        
        print(f"🎤 Speech segments found: {len(nonsilent_ranges)}")
        print(f"⏱️  Total speech duration: {total_speech_duration / 1000:.1f} seconds")
        print(f"📊 Speech percentage: {speech_percentage:.1f}%")
        
        if speech_percentage > 10:
            print("✅ Audio contains significant speech content")
            return True
        elif speech_percentage > 2:
            print("⚠️  Audio contains some speech content (may transcribe partially)")
            return True
        else:
            print("❌ Audio contains very little speech content")
            return False
            
    except Exception as e:
        print(f"❌ Error analyzing audio: {e}")
        return False

def main():
    print("=" * 60)
    print("Audio Content Checker")
    print("=" * 60)
    
    # Check uploads directory
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print("❌ No uploads directory found")
        return
    
    # Find audio files
    audio_files = []
    for file in os.listdir(uploads_dir):
        if file.lower().endswith(('.amr', '.wav', '.mp3', '.m4a', '.ogg', '.flac')):
            audio_files.append(os.path.join(uploads_dir, file))
    
    if not audio_files:
        print("❌ No audio files found in uploads directory")
        return
    
    print(f"📁 Found {len(audio_files)} audio files")
    
    # Analyze each file
    good_files = []
    problematic_files = []
    
    for file_path in audio_files:
        has_speech = analyze_audio_content(file_path)
        if has_speech:
            good_files.append(file_path)
        else:
            problematic_files.append(file_path)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if good_files:
        print(f"✅ Files with speech content ({len(good_files)}):")
        for file in good_files:
            print(f"   • {os.path.basename(file)}")
    
    if problematic_files:
        print(f"\n❌ Files with no/little speech content ({len(problematic_files)}):")
        for file in problematic_files:
            print(f"   • {os.path.basename(file)}")
        
        print("\n💡 Tips for problematic files:")
        print("   • Check if the audio was recorded properly")
        print("   • Verify the microphone was working")
        print("   • Try increasing the volume if the audio is very quiet")
        print("   • Check if the audio contains actual speech vs. just noise")

if __name__ == "__main__":
    main() 