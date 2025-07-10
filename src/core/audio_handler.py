import os
from pydub import AudioSegment
from typing import List, Optional, Set
from pathlib import Path

class AudioHandler:
    def __init__(self, config):
        self.config = config
        self.temp_files: Set[str] = set()  # Track all temp files created
        
    def get_audio_files(self, path: str) -> List[str]:
        """Get all supported audio files from a directory or single file"""
        if os.path.isfile(path):
            return [path] if self.config.is_supported_format(path) else []
        
        audio_files = []
        for root, _, files in os.walk(path):
            for file in files:
                if self.config.is_supported_format(file):
                    audio_files.append(os.path.join(root, file))
        return audio_files
    
    def prepare_audio(self, file_path: str) -> Optional[str]:
        """Prepare audio file for transcription"""
        try:
            file_ext = Path(file_path).suffix.lower()
            file_size = os.path.getsize(file_path)
            print(f"DEBUG: Preparing audio file: {file_path} (format: {file_ext}, size: {file_size} bytes)")
            
            # Check if file is empty
            if file_size == 0:
                print(f"ERROR: Audio file is empty: {file_path}")
                return None
            
            # Load audio file using pydub
            if file_ext == '.amr':
                # AMR files need special handling
                print("DEBUG: Processing AMR file...")
                try:
                    audio = AudioSegment.from_file(file_path, format="amr")
                    print(f"DEBUG: AMR file loaded successfully - duration: {len(audio)}ms, channels: {audio.channels}, sample rate: {audio.frame_rate}")
                except Exception as e:
                    print(f"ERROR: Failed to load AMR file: {e}")
                    return None
            else:
                # Other formats
                print(f"DEBUG: Processing {file_ext} file...")
                try:
                    audio = AudioSegment.from_file(file_path)
                    print(f"DEBUG: Audio file loaded successfully - duration: {len(audio)}ms, channels: {audio.channels}, sample rate: {audio.frame_rate}")
                except Exception as e:
                    print(f"ERROR: Failed to load audio file: {e}")
                    return None
            
            # Check if audio is silent or very short
            if len(audio) == 0:
                print(f"ERROR: Audio file has zero duration: {file_path}")
                return None
            elif len(audio) < 1000:  # Less than 1 second
                print(f"WARNING: Audio file is very short ({len(audio)}ms): {file_path}")
            
            # Convert to WAV format if not already
            if not file_path.lower().endswith('.wav'):
                temp_path = os.path.join(
                    os.path.dirname(file_path),
                    f"temp_{os.path.basename(file_path)}.wav"
                )
                print(f"DEBUG: Converting to WAV format: {temp_path}")
                
                # Export with standard settings for transcription
                audio.export(
                    temp_path,
                    format="wav",
                    parameters=["-ar", "16000", "-ac", "1"]  # 16kHz mono
                )
                
                # Verify the exported file
                if os.path.exists(temp_path):
                    exported_size = os.path.getsize(temp_path)
                    print(f"DEBUG: WAV file exported successfully (size: {exported_size} bytes)")
                    if exported_size == 0:
                        print(f"ERROR: Exported WAV file is empty: {temp_path}")
                        return None
                else:
                    print(f"ERROR: Failed to create WAV file: {temp_path}")
                    return None
                
                self.temp_files.add(temp_path)  # Track this temp file
                return temp_path
            
            print(f"DEBUG: Audio file already in WAV format, using original: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"ERROR: Error preparing audio file {file_path}: {str(e)}")
            print(f"DEBUG: Make sure you have ffmpeg installed for AMR file support")
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