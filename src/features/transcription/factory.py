"""Transcription service factory for dependency injection."""

from typing import Dict, Type, Optional
from functools import lru_cache

from .service import TranscriptionService
from .whisper import WhisperTranscriptionService
from .assemblyai import AssemblyAITranscriptionService
from ...models.config import AppConfig
from ...features.configuration.settings import ConfigurationService


class TranscriptionServiceFactory:
    """Factory for creating transcription service instances."""

    # Registry of available transcription services
    _services: Dict[str, Type[TranscriptionService]] = {
        'whisper': WhisperTranscriptionService,
        'assemblyai': AssemblyAITranscriptionService,
    }

    def __init__(self, config_service: ConfigurationService):
        """Initialize factory with configuration service."""
        self.config_service = config_service

    @classmethod
    def register_service(cls, name: str, service_class: Type[TranscriptionService]) -> None:
        """
        Register a new transcription service.
        
        Args:
            name: Unique identifier for the service
            service_class: Service implementation class
        """
        cls._services[name] = service_class

    @classmethod
    def get_available_backends(cls) -> list:
        """Get list of available backend names."""
        return list(cls._services.keys())

    def create_service(self, backend: Optional[str] = None) -> TranscriptionService:
        """
        Create transcription service instance.
        
        Args:
            backend: Backend name ('whisper', 'assemblyai'). 
                    If None, uses configured default.
            
        Returns:
            TranscriptionService instance
            
        Raises:
            ValueError: If backend is not supported
            RuntimeError: If no suitable backend is available
        """
        if backend is None:
            backend = self.config_service.get_transcriber_backend()
        
        if backend not in self._services:
            available = ", ".join(self.get_available_backends())
            raise ValueError(f"Unsupported backend '{backend}'. Available: {available}")
        
        config = self.config_service.get_config()
        service_class = self._services[backend]
        
        return service_class(config)

    @lru_cache(maxsize=2)
    def get_service(self, backend: Optional[str] = None) -> TranscriptionService:
        """
        Get cached transcription service instance.
        
        Args:
            backend: Backend name. If None, uses configured default.
            
        Returns:
            Cached TranscriptionService instance
        """
        return self.create_service(backend)

    def get_available_service(self) -> TranscriptionService:
        """
        Get the first available transcription service.
        
        Returns:
            TranscriptionService instance for an available backend
            
        Raises:
            RuntimeError: If no backends are available
        """
        config = self.config_service.get_config()
        
        # Try configured backend first
        preferred_backend = config.transcriber_backend
        if self.config_service.is_backend_available(preferred_backend):
            return self.create_service(preferred_backend)
        
        # Try other available backends
        for backend in self.get_available_backends():
            if self.config_service.is_backend_available(backend):
                return self.create_service(backend)
        
        raise RuntimeError("No transcription backends are available. Please configure API keys or start local services.")

    def clear_cache(self) -> None:
        """Clear cached service instances."""
        if hasattr(self.get_service, 'cache_clear'):
            self.get_service.cache_clear()