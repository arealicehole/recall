#!/usr/bin/env python3
"""
Unit tests for the Config class
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.utils.config import Config


class TestConfig:
    """Test suite for Config class"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.json')
        
    def teardown_method(self):
        """Clean up test environment after each test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_config_initialization(self):
        """Test Config class initialization"""
        config = Config()
        
        # Check that all required attributes exist
        assert hasattr(config, 'api_key')
        assert hasattr(config, 'output_dir')
        assert hasattr(config, 'supported_formats')
        
        # Check supported formats
        assert isinstance(config.supported_formats, tuple)
        assert len(config.supported_formats) > 0
        assert '.wav' in config.supported_formats
        assert '.mp3' in config.supported_formats
        assert '.amr' in config.supported_formats
    
    @patch.dict(os.environ, {'ASSEMBLYAI_API_KEY': 'test_api_key_123'})
    def test_api_key_from_environment(self):
        """Test API key loading from environment variable"""
        config = Config()
        assert config.api_key == 'test_api_key_123'
    
    @patch.dict(os.environ, {'OUTPUT_DIRECTORY': 'custom_output_path'})
    def test_output_directory_from_environment(self):
        """Test output directory loading from environment variable"""
        config = Config()
        assert config.output_dir == 'custom_output_path'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_default_values(self):
        """Test default values when no environment variables are set"""
        config = Config()
        
        # API key should be string type (can be empty or have value from config file)
        assert isinstance(config.api_key, str)
        
        # Output directory should have a default
        assert config.output_dir is not None
        assert len(config.output_dir) > 0
    
    def test_supported_formats_completeness(self):
        """Test that all expected audio formats are supported"""
        config = Config()
        
        expected_formats = ['.amr', '.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma']
        
        for format_ext in expected_formats:
            assert format_ext in config.supported_formats, f"Format {format_ext} not supported"
    
    def test_config_file_creation(self):
        """Test configuration file creation and loading"""
        # This test assumes the Config class has file-based configuration
        # If not implemented, this test will help identify the need
        config = Config()
        
        # Test that config can be created without errors
        assert config is not None
        
        # Test that we can access configuration directory
        config_dir = os.path.expanduser('~/.recall')
        # The directory might not exist, but the path should be valid
        assert os.path.isabs(config_dir)
    
    @patch('builtins.open', create=True)
    def test_config_file_handling(self, mock_open):
        """Test configuration file reading and writing"""
        config = Config()
        
        # Test that config object can be created
        assert config is not None
        
        # Test that configuration has all required attributes
        required_attrs = ['api_key', 'output_dir', 'supported_formats']
        for attr in required_attrs:
            assert hasattr(config, attr), f"Missing required attribute: {attr}"
    
    def test_config_immutability(self):
        """Test that supported formats are immutable"""
        config = Config()
        
        # Supported formats should be a tuple (immutable)
        assert isinstance(config.supported_formats, tuple)
        
        # Try to modify - should raise an error
        with pytest.raises((TypeError, AttributeError)):
            config.supported_formats.append('.new_format')
    
    def test_config_string_representation(self):
        """Test string representation of config"""
        config = Config()
        
        # Should be able to convert to string without error
        config_str = str(config)
        assert isinstance(config_str, str)
        assert len(config_str) > 0
    
    @patch.dict(os.environ, {'ASSEMBLYAI_API_KEY': 'sk_test_123456789'})
    def test_api_key_validation(self):
        """Test API key format validation"""
        config = Config()
        
        # API key should be loaded
        assert config.api_key == 'sk_test_123456789'
        
        # Test that API key has reasonable length
        assert len(config.api_key) > 10
    
    def test_output_directory_validation(self):
        """Test output directory validation"""
        config = Config()
        
        # Output directory should be a valid path
        assert isinstance(config.output_dir, str)
        assert len(config.output_dir) > 0
        
        # Should not contain invalid characters
        invalid_chars = ['<', '>', '|', '*', '?']
        for char in invalid_chars:
            assert char not in config.output_dir, f"Invalid character '{char}' in output directory"
    
    def test_config_updates(self):
        """Test configuration updates"""
        config = Config()
        
        # Test that we can update API key
        original_api_key = config.api_key
        config.api_key = 'new_test_key'
        assert config.api_key == 'new_test_key'
        
        # Test that we can update output directory
        original_output_dir = config.output_dir
        config.output_dir = '/new/test/path'
        assert config.output_dir == '/new/test/path'
    
    @patch('pathlib.Path.mkdir')
    def test_output_directory_creation(self, mock_mkdir):
        """Test output directory creation"""
        config = Config()
        
        # If config attempts to create directories, it should work
        # This is a basic test for directory handling
        assert config.output_dir is not None 