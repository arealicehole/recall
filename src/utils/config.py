import os
from dotenv import load_dotenv
from pathlib import Path

class Config:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get API key
        self.api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not self.api_key:
            raise ValueError("No ASSEMBLYAI_API_KEY found in environment")
            
        # Get output directory
        self.output_dir = os.getenv('OUTPUT_DIRECTORY', 'transcriptions')
        Path(self.output_dir).mkdir(exist_ok=True)
    
    @property
    def supported_formats(self):
        return ['.amr', '.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma']
    
    def is_supported_format(self, filename):
        return any(filename.lower().endswith(fmt) for fmt in self.supported_formats) 