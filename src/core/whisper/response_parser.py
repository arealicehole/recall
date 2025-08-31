"""Response parser for Whisper API responses with speaker aggregation."""

from typing import List, Dict, Any

from .models import WhisperResponse, WhisperSegment


class WhisperResponseParser:
    """Parses and processes Whisper API responses."""
    
    def __init__(self):
        pass
    
    def map_speaker_label(self, speaker_id: str) -> str:
        """
        Map speaker IDs to human-readable labels.
        
        Args:
            speaker_id: Raw speaker ID from API response
            
        Returns:
            Human-readable speaker label
        """
        # Handle "Unknown" or empty speaker
        if not speaker_id or speaker_id == 'Unknown':
            return "Speaker"
        
        # Convert SPEAKER_00, SPEAKER_01 format to Speaker A, Speaker B
        if speaker_id.startswith("SPEAKER_"):
            try:
                speaker_num = int(speaker_id.split("_")[1])
                # Convert number to letter (0 -> A, 1 -> B, etc.)
                if speaker_num < 26:
                    return f"Speaker {chr(65 + speaker_num)}"
                else:
                    # For more than 26 speakers, use numbers
                    return f"Speaker {speaker_num + 1}"
            except (IndexError, ValueError):
                pass
        
        # Return as-is if not in expected format
        return speaker_id
    
    def aggregate_speaker_segments(self, segments: List[WhisperSegment]) -> str:
        """
        Aggregate consecutive segments from the same speaker.
        
        Args:
            segments: List of transcribed segments with speaker info
            
        Returns:
            Formatted transcript with speaker labels
        """
        if not segments:
            return ""
        
        lines = []
        current_speaker = None
        current_texts = []
        
        for segment in segments:
            speaker = segment.speaker or 'Unknown'
            text = segment.text.strip()
            
            if not text:
                continue
            
            # Map speaker ID to human-readable label
            speaker_label = self.map_speaker_label(speaker)
            
            # If speaker changed, flush current speaker's text
            if speaker_label != current_speaker:
                if current_speaker and current_texts:
                    combined_text = ' '.join(current_texts)
                    lines.append(f"{current_speaker}: {combined_text}")
                
                current_speaker = speaker_label
                current_texts = [text]
            else:
                # Same speaker, accumulate text
                current_texts.append(text)
        
        # Don't forget the last speaker's text
        if current_speaker and current_texts:
            combined_text = ' '.join(current_texts)
            lines.append(f"{current_speaker}: {combined_text}")
        
        return '\n'.join(lines)
    
    def process_response(self, response: WhisperResponse) -> str:
        """
        Process Whisper API response and return formatted transcript.
        
        Args:
            response: Parsed response from Whisper API
            
        Returns:
            Formatted transcript text
        """
        # Handle error responses
        if response.error:
            print(f"ERROR: Transcription error: {response.error}")
            return ""
        
        # Check for segments with speaker diarization
        if response.segments:
            print(f"DEBUG: Processing {len(response.segments)} segments")
            
            # Check if we have actual speaker labels
            has_speakers = any(
                seg.speaker and seg.speaker != 'Unknown' 
                for seg in response.segments
            )
            
            if has_speakers:
                # Aggregate segments by speaker
                full_transcript = self.aggregate_speaker_segments(response.segments)
                print("DEBUG: Speaker diarization applied")
                return full_transcript
            else:
                # No speaker info, just concatenate text
                texts = [seg.text.strip() for seg in response.segments if seg.text]
                full_transcript = ' '.join(texts)
                print("DEBUG: No speaker labels found, using plain text")
                return full_transcript
                
        elif response.text:
            # Fallback to plain text
            print("DEBUG: Using plain text response")
            return response.text
        else:
            # Handle empty response
            print("DEBUG: No speech detected in audio")
            return ""
    
    def has_speech_content(self, response: WhisperResponse) -> bool:
        """
        Check if the response contains any speech content.
        
        Args:
            response: Parsed response from Whisper API
            
        Returns:
            True if speech was detected and transcribed
        """
        if response.error:
            return False
        
        if response.segments:
            return any(seg.text and seg.text.strip() for seg in response.segments)
        
        return bool(response.text and response.text.strip())