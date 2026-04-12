#!/usr/bin/env python3
"""
Unit tests for VAD integration.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.models.config import AppConfig
from src.features.transcription.vad import VADTranscriptionService
from src.features.transcription.service import TranscriptionService


class MockTranscriptionService(TranscriptionService):
    """Mock inner service for testing VAD wrapper."""

    def __init__(self, config):
        self.config = config
        self.transcribed_files = []

    def get_backend_name(self):
        return "Mock"

    def is_available(self):
        return True

    def supports_diarization(self):
        return False

    def get_supported_formats(self):
        return ('.wav', '.mp3', '.m4a')

    def transcribe_file(self, audio_path, progress_callback=None):
        self.transcribed_files.append(audio_path)
        return "mock transcription result"

    def transcribe_job(self, job, request, progress_callback=None):
        return self.transcribe_file(request.audio_file_path, progress_callback)

    def validate_audio_file(self, audio_path):
        from pathlib import Path
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        return path


class TestVADConfig:
    """Test VAD configuration fields in AppConfig."""

    def test_vad_defaults(self):
        """Test VAD config defaults."""
        config = AppConfig()
        assert config.vad_enabled is True
        assert config.vad_noise_db == -30
        assert config.vad_min_silence == 0.5
        assert config.vad_chunk_size == 30

    @patch.dict(os.environ, {
        'VAD_ENABLED': 'false',
        'VAD_NOISE_DB': '-25',
        'VAD_MIN_SILENCE': '1.0',
        'VAD_CHUNK_SIZE': '60',
    })
    def test_vad_from_environment(self):
        """Test VAD config from environment variables."""
        config = AppConfig()
        assert config.vad_enabled is False
        assert config.vad_noise_db == -25
        assert config.vad_min_silence == 1.0
        assert config.vad_chunk_size == 60


class TestVADTranscriptionService:
    """Test VAD transcription service wrapper."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = AppConfig()
        self.mock_service = MockTranscriptionService(self.config)
        self.vad_service = VADTranscriptionService(self.config, self.mock_service)

    def teardown_method(self):
        """Clean up."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_backend_name(self):
        """Test backend name includes VAD."""
        assert "VAD" in self.vad_service.get_backend_name()
        assert "Mock" in self.vad_service.get_backend_name()

    def test_delegates_availability(self):
        """Test availability delegates to inner service."""
        assert self.vad_service.is_available() is True

    def test_delegates_formats(self):
        """Test format support delegates to inner service."""
        formats = self.vad_service.get_supported_formats()
        assert '.wav' in formats
        assert '.mp3' in formats

    @patch('src.features.transcription.vad.detect_speech_segments')
    def test_falls_back_on_vad_failure(self, mock_vad):
        """Test fallback to raw transcription when VAD fails."""
        mock_vad.side_effect = Exception("ffmpeg not found")

        test_file = os.path.join(self.temp_dir, 'test.wav')
        with open(test_file, 'wb') as f:
            f.write(b'fake audio data')

        result = self.vad_service.transcribe_file(test_file)
        assert result == "mock transcription result"
        assert test_file in self.mock_service.transcribed_files

    @patch('src.features.transcription.vad.detect_speech_segments')
    def test_falls_back_on_no_speech(self, mock_vad):
        """Test fallback when VAD detects no speech."""
        mock_vad.return_value = ([], 10.0)

        test_file = os.path.join(self.temp_dir, 'test.wav')
        with open(test_file, 'wb') as f:
            f.write(b'fake audio data')

        result = self.vad_service.transcribe_file(test_file)
        assert result == "mock transcription result"

    @patch('src.features.transcription.vad.extract_segment')
    @patch('src.features.transcription.vad.detect_speech_segments')
    def test_transcribes_segments(self, mock_vad, mock_extract):
        """Test that VAD segments are transcribed individually."""
        mock_vad.return_value = ([(0.0, 10.0), (12.0, 20.0)], 25.0)

        def fake_extract(path, start, end, output):
            with open(output, 'wb') as f:
                f.write(b'fake segment')
            return output

        mock_extract.side_effect = fake_extract

        test_file = os.path.join(self.temp_dir, 'test.wav')
        with open(test_file, 'wb') as f:
            f.write(b'fake audio data')

        result = self.vad_service.transcribe_file(test_file)
        # Should have called inner service for each segment
        assert len(self.mock_service.transcribed_files) == 2
        assert result == "mock transcription result\nmock transcription result"


class TestVADDetector:
    """Test VAD detector module."""

    @patch('subprocess.run')
    def test_detect_speech_segments(self, mock_run):
        """Test speech segment detection from ffmpeg output."""
        from src.core.vad import detect_speech_segments

        mock_result = MagicMock()
        mock_result.stderr = """
Duration: 00:01:30.00, start: 0.000000, bitrate: 128 kb/s
[silencedetect @ 0x1234] silence_start: 5.0
[silencedetect @ 0x1234] silence_end: 7.5 | silence_duration: 2.5
[silencedetect @ 0x1234] silence_start: 45.0
[silencedetect @ 0x1234] silence_end: 50.0 | silence_duration: 5.0
"""
        mock_run.return_value = mock_result

        # Create a dummy file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(b'fake')
            tmp_path = f.name

        try:
            segments, duration = detect_speech_segments(tmp_path)
            assert duration == 90.0
            assert len(segments) > 0
            # First speech: 0-5s, second: 7.5-45s, third: 50-90s
            # After merging and chunking, should have multiple segments
            assert segments[0][0] == 0.0
            assert segments[0][1] == 5.0
        finally:
            os.unlink(tmp_path)

    @patch('subprocess.run')
    def test_detect_speech_segments_avoids_tiny_tail_chunks(self, mock_run):
        """Chunking should not emit tiny leftover segments that cause hallucinations."""
        from src.core.vad import detect_speech_segments

        mock_result = MagicMock()
        mock_result.stderr = """
Duration: 00:00:30.10, start: 0.000000, bitrate: 128 kb/s
"""
        mock_run.return_value = mock_result

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(b'fake')
            tmp_path = f.name

        try:
            segments, duration = detect_speech_segments(tmp_path, chunk_size=30, min_segment=0.3)
            assert duration == 30.1
            assert segments == [(0.0, 30.1)]
        finally:
            os.unlink(tmp_path)

    def test_file_not_found(self):
        """Test FileNotFoundError for missing file."""
        from src.core.vad import detect_speech_segments

        with pytest.raises(FileNotFoundError):
            detect_speech_segments('/nonexistent/file.wav')
