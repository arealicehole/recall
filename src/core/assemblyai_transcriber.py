"""AssemblyAI transcriber implementation."""

import os
from pathlib import Path
from typing import Callable, Optional, Dict, Any
import assemblyai as aai
import certifi

from src.core.base_transcriber import BaseTranscriber, TranscriptionMetrics


class AssemblyAITranscriber(BaseTranscriber):
    """Transcriber implementation using AssemblyAI API."""
    
    def __init__(self, config):
        super().__init__(config)
        
        # Set SSL certificate path before initializing AssemblyAI
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        os.environ['CURL_CA_BUNDLE'] = certifi.where()
        
        # Debug: Print API key status
        if config.assemblyai_api_key:
            print(f"DEBUG: AssemblyAI API key configured (length: {len(config.assemblyai_api_key)})")
            print(f"DEBUG: API key starts with: {config.assemblyai_api_key[:10]}...")
        else:
            print("DEBUG: No AssemblyAI API key configured!")
        
        # Initialize AssemblyAI client with API key (if available)
        if config.assemblyai_api_key:
            aai.settings.api_key = config.assemblyai_api_key
            
            # Create transcriber with nano model and speaker labels
            transcriber_config = aai.TranscriptionConfig(
                speaker_labels=getattr(config, 'enable_diarization', True),
                speech_model=aai.SpeechModel.nano
            )
            self.transcriber = aai.Transcriber(config=transcriber_config)
        else:
            self.transcriber = None
    
    def transcribe_file(
        self, 
        audio_path: str, 
        progress_callback: Optional[Callable[[str, float, str, Dict[str, Any]], None]] = None
    ) -> str:
        """
        Transcribe an audio file using AssemblyAI API.
        
        Args:
            audio_path: Path to the audio file to transcribe
            progress_callback: Optional callback for progress updates
        
        Returns:
            Transcribed text with speaker labels
        """
        if not self.transcriber:
            error_msg = "No API key configured. Please set your AssemblyAI API key in Settings > API Key."
            print(f"ERROR: {error_msg}")
            if progress_callback:
                progress_callback(error_msg, -1, "error", {})
            raise Exception(error_msg)
        
        try:
            # Convert to Path for reliable handling
            audio_path = Path(audio_path)
            file_size = audio_path.stat().st_size / (1024 * 1024)  # Size in MB
            
            print(f"DEBUG: Starting AssemblyAI transcription for {audio_path.name} (size: {file_size:.1f} MB)")
            
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
            
            # Debug: Print transcript information
            print(f"DEBUG: Transcript has utterances: {hasattr(transcript, 'utterances') and transcript.utterances}")
            print(f"DEBUG: Transcript has text: {hasattr(transcript, 'text') and transcript.text}")
            
            # Additional debugging - inspect the transcript object
            print(f"DEBUG: Transcript.text value: '{transcript.text}'")
            if hasattr(transcript, 'utterances'):
                print(f"DEBUG: Transcript.utterances value: {transcript.utterances}")
            if hasattr(transcript, 'words'):
                print(f"DEBUG: Transcript.words: {len(transcript.words) if transcript.words else 0} words")
            if hasattr(transcript, 'confidence'):
                print(f"DEBUG: Transcript.confidence: {transcript.confidence}")
            if hasattr(transcript, 'audio_duration'):
                print(f"DEBUG: Transcript.audio_duration: {transcript.audio_duration} seconds")
            
            # Check if transcript has any content at all
            transcript_dict = transcript.json_response if hasattr(transcript, 'json_response') else None
            if transcript_dict:
                print(f"DEBUG: Full transcript JSON keys: {list(transcript_dict.keys())}")
            
            # Build full transcript with speaker labels
            full_transcript = ""
            
            # Check if transcript has utterances (speaker diarization)
            if hasattr(transcript, 'utterances') and transcript.utterances:
                print(f"DEBUG: Found {len(transcript.utterances)} utterances")
                for i, utterance in enumerate(transcript.utterances):
                    print(f"DEBUG: Utterance {i}: Speaker {utterance.speaker}, Text: {utterance.text[:50]}...")
                    # Use standard speaker label format
                    speaker_label = self.map_speaker_label(utterance.speaker)
                    full_transcript += f"{speaker_label}: {utterance.text}\n"
            elif hasattr(transcript, 'text') and transcript.text:
                # Fall back to basic transcript text if no speaker diarization
                print(f"DEBUG: Using basic transcript text (length: {len(transcript.text)})")
                full_transcript = transcript.text
            else:
                # Check if this is actually a silent audio file
                if (hasattr(transcript, 'audio_duration') and transcript.audio_duration > 0 and
                    hasattr(transcript, 'confidence') and transcript.confidence == 0.0 and
                    hasattr(transcript, 'words') and len(transcript.words) == 0):
                    
                    print("DEBUG: Audio file appears to be silent or contain no speech")
                    error_msg = (
                        f"Audio file '{audio_path.name}' appears to be silent or contain no detectable speech. "
                        f"Duration: {transcript.audio_duration} seconds, but no words were transcribed. "
                        f"Please check that the audio file contains audible speech."
                    )
                    if progress_callback:
                        progress_callback(error_msg, -1, "error", {"metrics": str(metrics)})
                    return ""
                else:
                    print("DEBUG: No text found in transcript response")
                    full_transcript = ""
            
            print(f"DEBUG: Final transcript length: {len(full_transcript)}")
            
            return full_transcript
            
        except Exception as e:
            error_msg = f"Failed to transcribe {audio_path}: {str(e)}"
            print(f"ERROR: {error_msg}")
            if progress_callback:
                progress_callback(error_msg, -1, "error", {"metrics": str(metrics) if 'metrics' in locals() else ""})
            return ""