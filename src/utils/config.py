import os
import json
from dotenv import load_dotenv
from pathlib import Path

class Config:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get API key from environment first, then from config file
        self.api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not self.api_key:
            self.api_key = self.load_api_key_from_config()
        
        # If still no API key, set to empty string (will be set via GUI)
        if not self.api_key:
            self.api_key = ""
            
        # Get output directory
        self.output_dir = os.getenv('OUTPUT_DIRECTORY', 'transcripts')

        # Export timestamps option (for FFmpeg workflow)
        self.export_timestamps = os.getenv('EXPORT_TIMESTAMPS', 'false').lower() == 'true'

        # Only create directory if it's a valid path
        try:
            # Convert to Path object to handle Windows paths properly
            output_path = Path(self.output_dir)
            if output_path.is_absolute():
                # For absolute paths, ensure parent directories exist
                output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.mkdir(parents=True, exist_ok=True)
        except (OSError, ValueError) as e:
            # If path creation fails, use default directory
            self.output_dir = 'transcripts'
            Path(self.output_dir).mkdir(exist_ok=True)
    
    def load_api_key_from_config(self) -> str:
        """Load API key from config file"""
        config_dir = os.path.expanduser("~/.recall")
        config_file = os.path.join(config_dir, "config.json")
        
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                return config_data.get('api_key', '')
        except (FileNotFoundError, json.JSONDecodeError):
            return ''
    
    @property
    def supported_formats(self):
        """Return supported audio formats as an immutable tuple"""
        return ('.amr', '.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma')

    @property
    def supported_video_formats(self):
        """Return supported video formats as an immutable tuple"""
        return ('.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv')

    def is_supported_format(self, filename):
        """Check if a file format is supported (audio or video)"""
        return any(filename.lower().endswith(fmt) for fmt in self.supported_formats + self.supported_video_formats) 