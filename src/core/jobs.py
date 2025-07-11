"""
Defines the data structure for a transcription job.
"""

import os
from datetime import datetime

# Add the project root to Python path to allow for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TranscriptionJob:
    """Represents a single transcription job, which can contain multiple files."""
    def __init__(self, job_id, files, output_directory=None, same_as_input=False):
        self.job_id = job_id
        self.files = files
        self.output_directory = output_directory if output_directory is not None else os.path.join(project_root, 'transcripts')
        self.same_as_input = same_as_input
        self.status = "pending"
        self.progress = 0
        self.current_file = ""
        self.results = []
        self.error = None
        self.start_time = None
        self.end_time = None
        
    def to_dict(self):
        """Serializes the job object to a dictionary."""
        return {
            'job_id': self.job_id,
            'status': self.status,
            'progress': self.progress,
            'current_file': self.current_file,
            'results': self.results,
            'error': self.error,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        } 