import os
from pydub import AudioSegment
from typing import List, Optional, Set
from pathlib import Path

class AudioHandler:
    def __init__(self, config):
        self.config = config
        self.temp_files: Set[str] = set()  # Track all temp files created
        
    def get_audio_files(self, path: str) -> List[str]:
        """Get all supported audio and video files from a directory or single file"""
        if os.path.isfile(path):
            return [path] if self.config.is_supported_format(path) else []
        
        media_files = []
        for root, _, files in os.walk(path):
            for file in files:
                if self.config.is_supported_format(file):
                    media_files.append(os.path.join(root, file))
        return media_files
    
    def prepare_audio(self, file_path: str) -> Optional[str]:
        """Prepare audio from an audio or video file for transcription"""
        try:
            file_ext = Path(file_path).suffix.lower()
            is_video = file_ext in self.config.supported_video_formats
            file_size = os.path.getsize(file_path)
            
            print(f"DEBUG: Preparing file: {file_path} (format: {file_ext}, size: {file_size} bytes, is_video: {is_video})")
            
            if file_size == 0:
                print(f"ERROR: File is empty: {file_path}")
                return None
            
            # Load file using pydub - it handles audio and video files
            print(f"DEBUG: Loading file with pydub...")
            try:
                audio = AudioSegment.from_file(file_path)
                print(f"DEBUG: File loaded successfully - duration: {len(audio)}ms, channels: {audio.channels}, sample rate: {audio.frame_rate}")
            except Exception as e:
                print(f"ERROR: Failed to load file with pydub: {e}")
                return None
            
            if len(audio) == 0:
                print(f"ERROR: Audio stream has zero duration: {file_path}")
                return None
            elif len(audio) < 1000:
                print(f"WARNING: Audio stream is very short ({len(audio)}ms): {file_path}")

            # Always convert to a standard WAV format for transcription
            temp_path = os.path.join(
                os.path.dirname(file_path),
                f"temp_{os.path.basename(file_path)}.wav"
            )
            print(f"DEBUG: Converting to WAV format: {temp_path}")
            
            # Export with standard settings
            audio.export(
                temp_path,
                format="wav",
                parameters=["-ar", "16000", "-ac", "1"]  # 16kHz mono
            )
            
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                print(f"DEBUG: WAV file exported successfully (size: {os.path.getsize(temp_path)} bytes)")
                self.temp_files.add(temp_path)
                return temp_path
            else:
                print(f"ERROR: Failed to create or exported WAV file is empty: {temp_path}")
                return None
            
        except Exception as e:
            print(f"ERROR: Error preparing file {file_path}: {str(e)}")
            print(f"DEBUG: Make sure you have ffmpeg installed for full format support.")
            return None
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary WAV file if it exists"""
        if file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"DEBUG: Cleaned up temporary file: {file_path}")
                self.temp_files.remove(file_path)
            except Exception as e:
                print(f"ERROR: Error cleaning up temporary file {file_path}: {str(e)}")
    
    def cleanup_all_temp_files(self):
        """Clean up all temporary files that were created"""
        print(f"DEBUG: Cleaning up {len(self.temp_files)} temporary files")
        for temp_file in list(self.temp_files):  # Create a copy of the set to iterate
            self.cleanup_temp_file(temp_file) 