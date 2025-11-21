import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.audio_handler import AudioHandler
from src.utils.config import Config

class TestVideoHandler:
    """Test suite for video handling in AudioHandler"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.audio_handler = AudioHandler(self.config)
        
        # Create a dummy video file
        self.video_file_path = os.path.join(self.temp_dir, 'test_video.mp4')
        with open(self.video_file_path, 'wb') as f:
            f.write(b'dummy video content')

    def teardown_method(self):
        """Clean up test environment after each test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        self.audio_handler.cleanup_all_temp_files()

    def test_get_video_files(self):
        """Test that get_audio_files finds supported video files."""
        files = self.audio_handler.get_audio_files(self.temp_dir)
        assert self.video_file_path in files

    @patch('pydub.AudioSegment.from_file')
    def test_video_file_preparation(self, mock_from_file):
        """Test that prepare_audio correctly processes a video file."""
        # Arrange: Mock pydub's from_file to return a mock AudioSegment
        mock_audio_segment = MagicMock()
        mock_audio_segment.duration_seconds = 10  # Mock duration
        mock_audio_segment.channels = 2
        mock_audio_segment.frame_rate = 44100
        mock_audio_segment.__len__.return_value = 10000 # 10 seconds in ms
        mock_from_file.return_value = mock_audio_segment

        # Act: Call the method under test
        result_path = self.audio_handler.prepare_audio(self.video_file_path)

        # Assert: Check that the mocks were called as expected
        mock_from_file.assert_called_once_with(self.video_file_path)
        
        # Check that the audio was exported to a WAV file
        expected_temp_path = os.path.join(
            self.temp_dir,
            f"temp_{os.path.basename(self.video_file_path)}.wav"
        )
        mock_audio_segment.export.assert_called_once_with(
            expected_temp_path,
            format="wav",
            parameters=["-ar", "16000", "-ac", "1"]
        )
        
        # Assert that the result is the path to the temp file
        assert result_path == expected_temp_path
        
        # Assert that the temp file is tracked for cleanup
        assert expected_temp_path in self.audio_handler.temp_files
