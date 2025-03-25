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
            # Load audio file using pydub
            audio = AudioSegment.from_file(file_path)
            
            # Convert to WAV format if not already
            if not file_path.lower().endswith('.wav'):
                temp_path = os.path.join(
                    os.path.dirname(file_path),
                    f"temp_{os.path.basename(file_path)}.wav"
                )
                audio.export(temp_path, format="wav")
                self.temp_files.add(temp_path)  # Track this temp file
                return temp_path
            
            return file_path
            
        except Exception as e:
            print(f"Error preparing audio file {file_path}: {str(e)}")
            return None
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary WAV file if it exists"""
        if file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                self.temp_files.remove(file_path)
            except Exception as e:
                print(f"Error cleaning up temporary file {file_path}: {str(e)}")
    
    def cleanup_all_temp_files(self):
        """Clean up all temporary files that were created"""
        for temp_file in list(self.temp_files):  # Create a copy of the set to iterate
            self.cleanup_temp_file(temp_file) 