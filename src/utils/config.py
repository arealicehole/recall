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
        self.output_dir = os.getenv('OUTPUT_DIRECTORY', 'transcriptions')
        Path(self.output_dir).mkdir(exist_ok=True)
    
    def load_api_key_from_config(self) -> str:
        """Load API key from config file"""
        config_dir = os.path.expanduser("~/.audio_transcriber")
        config_file = os.path.join(config_dir, "config.json")
        
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                return config_data.get('api_key', '')
        except (FileNotFoundError, json.JSONDecodeError):
            return ''
    
    @property
    def supported_formats(self):
        return ['.amr', '.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma']
    
    def is_supported_format(self, filename):
        return any(filename.lower().endswith(fmt) for fmt in self.supported_formats) 