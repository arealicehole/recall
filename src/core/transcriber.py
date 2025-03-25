import os
from pathlib import Path
import time
from typing import Callable
from datetime import datetime
import assemblyai as aai
import certifi

class TranscriptionMetrics:
    def __init__(self, file_path: str, file_size_mb: float):
        self.file_path = file_path
        self.file_size_mb = file_size_mb
        self.start_time = time.time()
        self.end_time = None
        self.duration = None
        self.mb_per_second = None
        
    def complete(self):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.mb_per_second = self.file_size_mb / self.duration if self.duration > 0 else 0
        
    def __str__(self):
        if not self.end_time:
            return f"Transcribing {Path(self.file_path).name} ({self.file_size_mb:.1f} MB)"
        
        return (
            f"File: {Path(self.file_path).name}\n"
            f"Size: {self.file_size_mb:.1f} MB\n"
            f"Duration: {self.duration:.1f} seconds\n"
            f"Speed: {self.mb_per_second:.2f} MB/s"
        )

class Transcriber:
    def __init__(self, config):
        self.config = config
        
        # Set SSL certificate path before initializing AssemblyAI
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        os.environ['CURL_CA_BUNDLE'] = certifi.where()
        
        # Initialize AssemblyAI client with API key
        aai.settings.api_key = config.api_key
        
        # Create transcriber with nano model and speaker labels
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            speech_model=aai.SpeechModel.nano
        )
        self.transcriber = aai.Transcriber(config=config)
        self.metrics = []
        
    def transcribe_file(self, audio_path: str, progress_callback: Callable[[str, float, str, dict], None] = None) -> str:
        """Simple audio file transcription with detailed progress updates"""
        try:
            # Convert to Path for reliable handling
            audio_path = Path(audio_path)
            file_size = audio_path.stat().st_size / (1024 * 1024)  # Size in MB
            
            # Create metrics tracker
            metrics = TranscriptionMetrics(str(audio_path), file_size)
            self.metrics.append(metrics)
            
            # Basic progress update
            if progress_callback:
                progress_callback(
                    f"Processing {audio_path.name} ({file_size:.1f} MB)",
                    0,
                    "preparing",
                    {"metrics": str(metrics)}
                )
            
            # Start transcription
            if progress_callback:
                progress_callback(
                    f"Transcribing {audio_path.name}",
                    50,
                    "transcribing",
                    {"metrics": str(metrics)}
                )
                
            # Use AssemblyAI to transcribe
            transcript = self.transcriber.transcribe(str(audio_path))
            
            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(f"Transcription failed: {transcript.error}")
                
            # Complete metrics
            metrics.complete()
            
            if progress_callback:
                progress_callback(
                    f"Completed {audio_path.name}",
                    100,
                    "completed",
                    {"metrics": str(metrics)}
                )
            
            # Build full transcript with speaker labels
            full_transcript = ""
            for utterance in transcript.utterances:
                full_transcript += f"Speaker {utterance.speaker}: {utterance.text}\n"
            
            return full_transcript
            
        except Exception as e:
            error_msg = f"Failed to transcribe {audio_path}: {str(e)}"
            print(error_msg)
            if progress_callback:
                progress_callback(error_msg, -1, "error", {"metrics": str(metrics) if 'metrics' in locals() else ""})
            return ""
    
    def save_transcription(self, audio_path: str, transcription: str) -> str:
        """Save transcription to file"""
        try:
            out_path = Path(self.config.output_dir) / f"{Path(audio_path).stem}_transcription.txt"
            out_path.write_text(transcription, encoding='utf-8')
            return str(out_path)
        except Exception as e:
            print(f"Failed to save transcription: {e}")
            return ""
            
    def get_performance_summary(self) -> str:
        """Get a summary of all transcription performance metrics"""
        if not self.metrics:
            return "No transcriptions performed yet."
            
        total_size = sum(m.file_size_mb for m in self.metrics)
        total_time = sum(m.duration for m in self.metrics if m.duration)
        avg_speed = total_size / total_time if total_time > 0 else 0
        
        return (
            f"Performance Summary:\n"
            f"Total files: {len(self.metrics)}\n"
            f"Total size: {total_size:.1f} MB\n"
            f"Total time: {total_time:.1f} seconds\n"
            f"Average speed: {avg_speed:.2f} MB/s"
        ) 