"""VAD-enabled transcription service.

Wraps any TranscriptionService and adds Voice Activity Detection
preprocessing to eliminate Whisper hallucinations on silence/noise.
"""

import os
import tempfile
import logging
from typing import Optional, Callable, Dict, Any
from pathlib import Path

from .service import TranscriptionService
from ...core.vad import detect_speech_segments, extract_segment
from ...core.errors import TranscriptionError
from ...models.jobs import TranscriptionJob, TranscriptionRequest
from ...models.config import AppConfig

logger = logging.getLogger(__name__)


class VADTranscriptionService(TranscriptionService):
    """
    Transcription service that preprocesses audio with VAD before transcription.

    Splits audio into speech segments using ffmpeg silencedetect,
    transcribes each segment individually, and concatenates results.
    Falls back to raw transcription if VAD fails.
    """

    def __init__(self, config: AppConfig, inner_service: TranscriptionService):
        """
        Initialize VAD transcription service.

        Args:
            config: Application configuration with VAD settings
            inner_service: The underlying transcription service (e.g. Whisper)
        """
        self.config = config
        self._inner = inner_service

    def get_backend_name(self) -> str:
        """Return the name with VAD prefix."""
        return f"{self._inner.get_backend_name()} + VAD"

    def is_available(self) -> bool:
        """Check if the inner service is available."""
        return self._inner.is_available()

    def supports_diarization(self) -> bool:
        """Delegate to inner service."""
        return self._inner.supports_diarization()

    def get_supported_formats(self) -> tuple:
        """Delegate to inner service."""
        return self._inner.get_supported_formats()

    def transcribe_file(
        self,
        audio_path: str,
        progress_callback: Optional[Callable[[str, float, str, Optional[Dict[str, Any]]], None]] = None,
    ) -> str:
        """
        Transcribe an audio file with VAD preprocessing.

        Detects speech segments, extracts them, transcribes each individually,
        and concatenates results. Falls back to raw transcription on VAD failure.

        Args:
            audio_path: Path to the audio file
            progress_callback: Optional callback for progress updates

        Returns:
            Transcribed text from all speech segments

        Raises:
            TranscriptionError: If transcription fails
        """
        validated_path = self._inner.validate_audio_file(audio_path)

        # Extract VAD parameters from config
        noise_db = getattr(self.config, 'vad_noise_db', -30)
        min_silence = getattr(self.config, 'vad_min_silence', 0.5)
        chunk_size = getattr(self.config, 'vad_chunk_size', 30)

        if progress_callback:
            progress_callback(
                f"Detecting speech in {validated_path.name}...",
                5,
                "vad_detecting",
                {},
            )

        # Run VAD detection
        try:
            segments, duration = detect_speech_segments(
                str(validated_path),
                noise_db=noise_db,
                min_silence=min_silence,
                chunk_size=chunk_size,
            )
        except Exception as e:
            logger.warning("VAD detection failed, falling back to raw transcription: %s", e)
            if progress_callback:
                progress_callback(
                    "VAD failed, using raw transcription...",
                    10,
                    "vad_fallback",
                    {},
                )
            return self._inner.transcribe_file(str(validated_path), progress_callback)

        if not segments:
            logger.warning("No speech detected by VAD for %s, trying raw transcription", validated_path.name)
            if progress_callback:
                progress_callback(
                    "No speech detected by VAD, trying raw transcription...",
                    10,
                    "vad_fallback",
                    {},
                )
            return self._inner.transcribe_file(str(validated_path), progress_callback)

        speech_time = sum(e - s for s, e in segments)
        logger.info(
            "VAD found %d segments (%.0fs speech) in %.0fs file",
            len(segments), speech_time, duration,
        )

        # Extract and transcribe each segment
        tmpdir = tempfile.mkdtemp(prefix="vad_")
        texts = []

        try:
            for i, (start, end) in enumerate(segments):
                seg_path = os.path.join(tmpdir, f"seg_{i:04d}.m4a")
                extract_segment(str(validated_path), start, end, seg_path)

                seg_dur = end - start
                base_progress = 10 + (i / len(segments)) * 80

                if progress_callback:
                    progress_callback(
                        f"Transcribing segment {i + 1}/{len(segments)} "
                        f"({start:.0f}s–{end:.0f}s, {seg_dur:.0f}s)",
                        base_progress,
                        "transcribing",
                        {
                            "segment": i + 1,
                            "total_segments": len(segments),
                            "segment_start": start,
                            "segment_end": end,
                        },
                    )

                try:
                    text = self._inner.transcribe_file(seg_path, None)
                    if text:
                        texts.append(text.strip())
                except Exception as e:
                    logger.warning("Segment %d transcription failed: %s", i, e)
                finally:
                    try:
                        os.unlink(seg_path)
                    except OSError:
                        pass

            full_text = '\n'.join(texts)

            if progress_callback:
                word_count = len(full_text.split())
                progress_callback(
                    f"Completed {validated_path.name} ({word_count} words, "
                    f"{len(segments)} segments)",
                    100,
                    "completed",
                    {"segments": len(segments), "speech_time": speech_time},
                )

            return full_text

        finally:
            # Cleanup temp directory
            try:
                os.rmdir(tmpdir)
            except OSError:
                pass

    def transcribe_job(
        self,
        job: TranscriptionJob,
        request: TranscriptionRequest,
        progress_callback: Optional[Callable[[str, float, str, Optional[Dict[str, Any]]], None]] = None,
    ) -> str:
        """Transcribe with job tracking, delegating to VAD-aware transcribe_file."""
        try:
            job.mark_processing()

            def job_progress_callback(
                message: str, progress: float, status: str,
                extra: Optional[Dict[str, Any]] = None,
            ):
                job.update_progress(progress)
                if progress_callback:
                    progress_callback(message, progress, status, extra)

            result = self.transcribe_file(request.audio_file_path, job_progress_callback)
            job.mark_completed(result)
            return result

        except Exception as e:
            job.mark_failed(str(e))
            raise

    def validate_audio_file(self, audio_path: str) -> Path:
        """Delegate to inner service."""
        return self._inner.validate_audio_file(audio_path)
