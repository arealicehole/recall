import os
from pathlib import Path
import time
from typing import Callable, Union
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
        
        # Debug: Print API key status
        if config.api_key:
            print(f"DEBUG: API key configured (length: {len(config.api_key)})")
            print(f"DEBUG: API key starts with: {config.api_key[:10]}...")
        else:
            print("DEBUG: No API key configured!")
        
        # Initialize AssemblyAI client with API key (if available)
        if config.api_key:
            aai.settings.api_key = config.api_key
            
            # Create transcriber with nano model and speaker labels
            transcriber_config = aai.TranscriptionConfig(
                speaker_labels=True,
                speech_model=aai.SpeechModel.nano
            )
            self.transcriber = aai.Transcriber(config=transcriber_config)
        else:
            self.transcriber = None
            
        self.metrics = []
        
    def transcribe_file(self, audio_path: str, progress_callback: Callable[[str, float, str, dict], None] = None) -> Union[aai.Transcript, None]:
        """
        Simple audio file transcription with detailed progress updates.
        Returns the full transcript object from AssemblyAI.
        """
        if not self.transcriber:
            error_msg = "No API key configured. Please set your AssemblyAI API key in Settings > API Key."
            print(f"ERROR: {error_msg}")
            if progress_callback:
                progress_callback(error_msg, -1, "error")
            raise Exception(error_msg)
            
        try:
            # Convert to Path for reliable handling
            audio_path = Path(audio_path)
            file_size = audio_path.stat().st_size / (1024 * 1024)  # Size in MB
            
            print(f"DEBUG: Starting transcription for {audio_path.name} (size: {file_size:.1f} MB)")
            
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
            
            print(f"DEBUG: Calling AssemblyAI API for {audio_path.name}")
            
            # Use AssemblyAI to transcribe
            transcript = self.transcriber.transcribe(str(audio_path))
            
            print(f"DEBUG: API response status: {transcript.status}")
            
            if transcript.status == aai.TranscriptStatus.error:
                error_msg = f"Transcription failed: {transcript.error}"
                print(f"ERROR: {error_msg}")
                raise Exception(error_msg)
                
            # Complete metrics
            metrics.complete()
            
            if progress_callback:
                progress_callback(
                    f"Completed {audio_path.name}",
                    100,
                    "completed",
                    {"metrics": str(metrics)}
                )
            
            # Check for silent audio
            if (hasattr(transcript, 'audio_duration') and transcript.audio_duration > 0 and
                hasattr(transcript, 'confidence') and transcript.confidence == 0.0 and
                hasattr(transcript, 'words') and len(transcript.words) == 0):
                
                print("DEBUG: Audio file appears to be silent or contain no speech")
                # Return the transcript object even for silent audio, let the caller decide what to do
                return transcript

            return transcript
            
        except Exception as e:
            error_msg = f"Failed to transcribe {audio_path}: {str(e)}"
            print(f"ERROR: {error_msg}")
            if progress_callback:
                progress_callback(error_msg, -1, "error", {"metrics": str(metrics) if 'metrics' in locals() else ""})
            return None

    def format_transcript_to_string(self, transcript: aai.Transcript) -> str:
        """Formats the transcript object into a human-readable string."""
        if not transcript:
            return ""

        # Check if this is a silent audio file
        if (hasattr(transcript, 'audio_duration') and transcript.audio_duration > 0 and
            hasattr(transcript, 'confidence') and transcript.confidence == 0.0 and
            hasattr(transcript, 'words') and not transcript.words):
            
            error_msg = (
                f"Audio file appears to be silent or contain no detectable speech. "
                f"Duration: {transcript.audio_duration} seconds, but no words were transcribed. "
                f"Please check that the audio file contains audible speech."
            )
            return error_msg

        full_transcript = ""
        if hasattr(transcript, 'utterances') and transcript.utterances:
            for utterance in transcript.utterances:
                full_transcript += f"Speaker {utterance.speaker}: {utterance.text}\n"
        elif hasattr(transcript, 'text') and transcript.text:
            full_transcript = transcript.text
        else:
            return "No text found in transcript."
            
        return full_transcript
            
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