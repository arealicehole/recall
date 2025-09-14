# Recall - Audio Transcription Application

## Purpose
Recall is a Python desktop and web application for audio transcription with speaker identification. It supports multiple backends:
- Local Whisper server (default, free, no API key required)
- AssemblyAI cloud service (requires API key)

## Tech Stack
- **GUI**: CustomTkinter for modern desktop interface
- **Web**: Flask for web interface 
- **Transcription**: Whisper (local) and AssemblyAI (cloud)
- **Config**: Pydantic BaseSettings with environment variable support
- **Architecture**: Factory pattern with dependency injection
- **Audio**: PyDub with FFmpeg backend

## Key Components
- `src/models/` - Pydantic configuration and job models
- `src/features/transcription/` - Backend factory and services
- `src/gui/` - Desktop application with CustomTkinter
- `src/webapp/` - Flask web interface
- `src/core/` - Transcription engines and utilities

## Default Configuration
- Backend: `whisper` (local, no API key needed)
- Whisper URL: `http://127.0.0.1:8767`
- AssemblyAI: Optional API key via environment variable