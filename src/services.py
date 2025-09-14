"""Main application services container."""

from typing import Optional
from functools import lru_cache

from .features.configuration.settings import ConfigurationService
from .features.transcription.factory import TranscriptionServiceFactory
from .features.transcription.service import TranscriptionService
from .features.audio.handler import AudioHandler
from .models.config import AppConfig


class ServiceContainer:
    """Main service container for dependency injection."""

    def __init__(self):
        """Initialize service container."""
        self._config_service: Optional[ConfigurationService] = None
        self._transcription_factory: Optional[TranscriptionServiceFactory] = None
        self._audio_handler: Optional[AudioHandler] = None

    @lru_cache(maxsize=1)
    def get_config_service(self) -> ConfigurationService:
        """Get configuration service instance."""
        if self._config_service is None:
            self._config_service = ConfigurationService()
        return self._config_service

    def get_config(self) -> 'AppConfig':
        """Get application configuration."""
        return self.get_config_service().get_config()

    @lru_cache(maxsize=1)
    def get_transcription_factory(self) -> TranscriptionServiceFactory:
        """Get transcription service factory."""
        if self._transcription_factory is None:
            self._transcription_factory = TranscriptionServiceFactory(self.get_config_service())
        return self._transcription_factory

    @lru_cache(maxsize=1)
    def get_audio_handler(self) -> AudioHandler:
        """Get audio handler instance."""
        if self._audio_handler is None:
            config = self.get_config_service().get_config()
            self._audio_handler = AudioHandler(config)
        return self._audio_handler

    def get_transcription_service(self, backend: Optional[str] = None) -> TranscriptionService:
        """
        Get transcription service instance.
        
        Args:
            backend: Specific backend to use, or None for default
            
        Returns:
            TranscriptionService instance
        """
        return self.get_transcription_factory().get_service(backend)

    def get_available_transcription_service(self) -> TranscriptionService:
        """
        Get an available transcription service.
        
        Returns:
            TranscriptionService instance for an available backend
        """
        return self.get_transcription_factory().get_available_service()

    def reload_config(self) -> None:
        """Reload configuration and clear service caches."""
        # Clear all cached services
        if hasattr(self.get_config_service, 'cache_clear'):
            self.get_config_service.cache_clear()
        if hasattr(self.get_transcription_factory, 'cache_clear'):
            self.get_transcription_factory.cache_clear()
        if hasattr(self.get_audio_handler, 'cache_clear'):
            self.get_audio_handler.cache_clear()
        
        # Clear internal references
        self._config_service = None
        self._transcription_factory = None
        self._audio_handler = None
        
        # Reload config
        config_service = self.get_config_service()
        config_service.reload_config()


# Global service container instance
_service_container: Optional[ServiceContainer] = None


def get_service_container() -> ServiceContainer:
    """Get global service container instance."""
    global _service_container
    if _service_container is None:
        _service_container = ServiceContainer()
    return _service_container


def get_config_service() -> ConfigurationService:
    """Shortcut to get configuration service."""
    return get_service_container().get_config_service()


def get_transcription_service(backend: Optional[str] = None) -> TranscriptionService:
    """Shortcut to get transcription service."""
    return get_service_container().get_transcription_service(backend)


def get_audio_handler() -> AudioHandler:
    """Shortcut to get audio handler."""
    return get_service_container().get_audio_handler()


def reload_services() -> None:
    """Reload all services (useful for config changes)."""
    get_service_container().reload_config()