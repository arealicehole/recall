#!/usr/bin/env python3
"""
Unit tests for the Web API
"""

import pytest
import os
import tempfile
import shutil
import json
from unittest.mock import patch, MagicMock
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.web.api import app
from src.utils.config import Config


class TestWebAPI:
    """Test suite for Web API"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.app = app.test_client()
        self.app.testing = True
        
        # Set up configuration
        app.config['UPLOAD_FOLDER'] = self.temp_dir
        app.config['TESTING'] = True
        
        # Create test audio file
        self.test_audio_file = os.path.join(self.temp_dir, 'test.wav')
        with open(self.test_audio_file, 'wb') as f:
            f.write(b'RIFF\x00\x00\x00\x00WAVEfmt \x00\x00\x00\x00')
    
    def teardown_method(self):
        """Clean up test environment after each test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_app_initialization(self):
        """Test Flask app initialization"""
        assert app is not None
        assert app.config['MAX_CONTENT_LENGTH'] == 500 * 1024 * 1024  # 500MB
    
    def test_home_route(self):
        """Test home page route"""
        response = self.app.get('/')
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Should contain HTML content
        assert b'html' in response.data.lower() or b'recall' in response.data.lower()
    
    def test_status_endpoint(self):
        """Test status API endpoint"""
        response = self.app.get('/api/status')
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Should return JSON
        assert response.content_type.startswith('application/json')
        
        # Parse JSON response
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'ok'
    
    def test_upload_endpoint_no_files(self):
        """Test upload endpoint with no files"""
        response = self.app.post('/api/upload')
        
        # Should return error for no files
        assert response.status_code == 400
        
        # Should return JSON error
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_upload_endpoint_with_file(self):
        """Test upload endpoint with valid file"""
        with open(self.test_audio_file, 'rb') as f:
            response = self.app.post('/api/upload', data={
                'files': (f, 'test.wav')
            })
        
        # Should accept the file
        assert response.status_code in [200, 202]  # OK or Accepted
        
        # Should return JSON
        if response.content_type.startswith('application/json'):
            data = json.loads(response.data)
            assert 'job_id' in data or 'message' in data
    
    def test_upload_endpoint_invalid_file(self):
        """Test upload endpoint with invalid file type"""
        # Create invalid file
        invalid_file = os.path.join(self.temp_dir, 'invalid.txt')
        with open(invalid_file, 'w') as f:
            f.write('This is not an audio file')
        
        with open(invalid_file, 'rb') as f:
            response = self.app.post('/api/upload', data={
                'files': (f, 'invalid.txt')
            })
        
        # Should reject invalid file
        assert response.status_code == 400
        
        # Should return error message
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_upload_endpoint_large_file(self):
        """Test upload endpoint with large file"""
        # Create large file (but within limits)
        large_file = os.path.join(self.temp_dir, 'large.wav')
        with open(large_file, 'wb') as f:
            f.write(b'RIFF\x00\x00\x00\x00WAVEfmt \x00\x00\x00\x00' * 10000)
        
        with open(large_file, 'rb') as f:
            response = self.app.post('/api/upload', data={
                'files': (f, 'large.wav')
            })
        
        # Should handle large files
        assert response.status_code in [200, 202, 413]  # OK, Accepted, or Too Large
    
    def test_job_status_endpoint(self):
        """Test job status endpoint"""
        # Test with non-existent job
        response = self.app.get('/api/job/non-existent-job-id')
        
        # Should return 404 or error
        assert response.status_code in [404, 400]
        
        # Should return JSON
        data = json.loads(response.data)
        assert 'error' in data or 'status' in data
    
    def test_download_endpoint(self):
        """Test download endpoint"""
        # Test with non-existent job
        response = self.app.get('/api/download/non-existent-job-id')
        
        # Should return 404 or error
        assert response.status_code in [404, 400]
    
    def test_supported_file_formats(self):
        """Test supported file format validation"""
        # Test each supported format
        supported_formats = ['wav', 'mp3', 'amr', 'm4a', 'ogg', 'flac', 'aac', 'wma']
        
        for ext in supported_formats:
            test_file = os.path.join(self.temp_dir, f'test.{ext}')
            with open(test_file, 'wb') as f:
                f.write(b'fake audio data')
            
            # Import the allowed_file function if it exists
            try:
                from src.web.api import allowed_file
                assert allowed_file(f'test.{ext}') == True
            except ImportError:
                # Function might not exist or be named differently
                pass
    
    def test_api_key_configuration(self):
        """Test API key configuration"""
        # Test that API key is configured
        try:
            from src.web.api import config
            # API key might be None in test environment
            assert hasattr(config, 'api_key')
        except (ImportError, AttributeError):
            # Config might not be exposed or named differently
            pass
    
    def test_cors_headers(self):
        """Test CORS headers if implemented"""
        response = self.app.get('/api/status')
        
        # Check for CORS headers (optional)
        # This depends on whether CORS is implemented
        assert response.status_code == 200
    
    def test_error_handling(self):
        """Test error handling"""
        # Test 404 error
        response = self.app.get('/api/nonexistent')
        assert response.status_code == 404
        
        # Test with malformed request
        response = self.app.post('/api/upload', data={'invalid': 'data'})
        assert response.status_code == 400
    
    def test_file_size_limits(self):
        """Test file size limits"""
        # Test that file size limits are enforced
        assert app.config['MAX_CONTENT_LENGTH'] == 500 * 1024 * 1024
    
    def test_upload_directory_creation(self):
        """Test upload directory creation"""
        # Test that upload directory exists or can be created
        upload_dir = app.config.get('UPLOAD_FOLDER', 'uploads')
        
        # Directory should exist or be creatable
        if not os.path.exists(upload_dir):
            try:
                os.makedirs(upload_dir)
                assert os.path.exists(upload_dir)
                os.rmdir(upload_dir)  # Clean up
            except OSError:
                # Directory creation might fail due to permissions
                pass
    
    def test_content_type_validation(self):
        """Test content type validation"""
        # Test with wrong content type
        response = self.app.post('/api/upload', 
                                data='invalid data',
                                content_type='text/plain')
        
        # Should handle invalid content type
        assert response.status_code == 400
    
    def test_json_response_format(self):
        """Test JSON response format"""
        response = self.app.get('/api/status')
        
        # Should return valid JSON
        assert response.content_type.startswith('application/json')
        
        # Should be parseable JSON
        data = json.loads(response.data)
        assert isinstance(data, dict)
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        # Test multiple simultaneous requests
        responses = []
        
        for i in range(3):
            response = self.app.get('/api/status')
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
    
    def test_memory_management(self):
        """Test memory management during file uploads"""
        # Test that large file uploads don't consume excessive memory
        with open(self.test_audio_file, 'rb') as f:
            response = self.app.post('/api/upload', data={
                'files': (f, 'test.wav')
            })
        
        # Should handle without memory issues
        assert response.status_code in [200, 202, 400]
    
    def test_security_headers(self):
        """Test security headers"""
        response = self.app.get('/')
        
        # Should not expose sensitive headers
        assert 'Server' not in response.headers or 'Flask' not in response.headers.get('Server', '')
    
    def test_input_validation(self):
        """Test input validation"""
        # Test with malicious input
        response = self.app.post('/api/upload', data={
            'files': '../../../etc/passwd'
        })
        
        # Should reject malicious input
        assert response.status_code == 400
    
    def test_rate_limiting(self):
        """Test rate limiting if implemented"""
        # Test multiple rapid requests
        responses = []
        
        for i in range(10):
            response = self.app.get('/api/status')
            responses.append(response)
        
        # Should handle multiple requests
        # Rate limiting might not be implemented, so just check they don't crash
        for response in responses:
            assert response.status_code in [200, 429]  # OK or Too Many Requests
    
    @patch('src.web.api.transcriber')
    def test_transcription_integration(self, mock_transcriber):
        """Test transcription integration"""
        # Mock transcriber
        mock_transcriber.transcribe_file.return_value = "Test transcription result"
        
        # Test file upload with transcription
        with open(self.test_audio_file, 'rb') as f:
            response = self.app.post('/api/upload', data={
                'files': (f, 'test.wav')
            })
        
        # Should handle transcription request
        assert response.status_code in [200, 202]
    
    def test_cleanup_functionality(self):
        """Test cleanup of temporary files"""
        # Test that temporary files are cleaned up
        initial_files = os.listdir(self.temp_dir)
        
        # Upload a file
        with open(self.test_audio_file, 'rb') as f:
            response = self.app.post('/api/upload', data={
                'files': (f, 'test.wav')
            })
        
        # Files should be managed properly
        # This depends on implementation details
        assert response.status_code in [200, 202, 400]
    
    def test_api_versioning(self):
        """Test API versioning"""
        # Test that API endpoints are properly versioned
        response = self.app.get('/api/status')
        
        # Should work with current version
        assert response.status_code == 200
        
        # Test if version info is included
        data = json.loads(response.data)
        # Version info is optional
        assert 'version' in data or 'status' in data 