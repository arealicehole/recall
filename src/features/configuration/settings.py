"""Configuration management service."""

import json
import os
from pathlib import Path
from typing import Optional
from functools import lru_cache

from ...models.config import AppConfig


class ConfigurationService:
    """Centralized configuration management service."""

    def __init__(self):
        """Initialize configuration service."""
        self._config: Optional[AppConfig] = None
        self._config_dir = Path.home() / ".recall"
        self._config_file = self._config_dir / "config.json"

    @lru_cache(maxsize=1)
    def get_config(self) -> AppConfig:
        """Get cached application configuration."""
        if self._config is None:
            self._config = AppConfig()
        return self._config

    def reload_config(self) -> AppConfig:
        """Reload configuration from environment/files."""
        self._config = None
        if hasattr(self.get_config, 'cache_clear'):
            self.get_config.cache_clear()
        return self.get_config()

    def save_api_key(self, api_key: str) -> None:
        """
        Save API key to local configuration file.
        
        Args:
            api_key: AssemblyAI API key to save
        """
        # Ensure config directory exists
        self._config_dir.mkdir(exist_ok=True)
        
        # Load existing config or create new
        config_data = {}
        if self._config_file.exists():
            try:
                with open(self._config_file, 'r') as f:
                    config_data = json.load(f)
            except (json.JSONDecodeError, OSError):
                config_data = {}
        
        # Update API key
        config_data['api_key'] = api_key
        
        # Save updated config
        with open(self._config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Update in-memory config if it exists
        if self._config is not None:
            self._config.assemblyai_api_key = api_key

    def load_api_key(self) -> str:
        """
        Load API key from configuration file.
        
        Returns:
            API key string, or empty string if not found
        """
        if not self._config_file.exists():
            return ""
        
        try:
            with open(self._config_file, 'r') as f:
                config_data = json.load(f)
                return config_data.get('api_key', '')
        except (json.JSONDecodeError, OSError):
            return ""

    def get_transcriber_backend(self) -> str:
        """Get configured transcriber backend."""
        return self.get_config().transcriber_backend

    def get_whisper_api_url(self) -> str:
        """Get Whisper API URL."""
        return self.get_config().whisper_api_url

    def get_assemblyai_api_key(self) -> Optional[str]:
        """Get AssemblyAI API key."""
        config = self.get_config()
        return config.assemblyai_api_key or self.load_api_key()

    def get_output_directory(self) -> Path:
        """Get output directory for transcripts."""
        return self.get_config().output_directory

    def is_backend_available(self, backend: str) -> bool:
        """
        Check if a transcription backend is available.
        
        Args:
            backend: Backend name ('whisper' or 'assemblyai')
            
        Returns:
            True if backend is available, False otherwise
        """
        if backend == 'whisper':
            # For Whisper, we'd need to check if the API is running
            # This is a simplified check - in practice, you'd ping the API
            return True  # Assume available for now
        elif backend == 'assemblyai':
            return bool(self.get_assemblyai_api_key())
        else:
            return False

    def get_supported_formats(self) -> tuple:
        """Get supported audio file formats."""
        return self.get_config().supported_formats

    def is_supported_format(self, filename: str) -> bool:
        """Check if file format is supported."""
        return self.get_config().is_supported_format(filename)