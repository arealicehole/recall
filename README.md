# recall

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Project Status

🚀 **Active Development** - Regular updates and improvements

### Recent Updates
- ✅ Dual backend support (Whisper + AssemblyAI)
- ✅ Speaker diarization with hybrid GPU/CPU mode
- ✅ Improved error handling and recovery
- ✅ Docker support for containerized deployment

### Roadmap
- 🔄 Streaming support for large files
- 🔄 Real-time transcription
- 🔄 Multi-language support expansion
- 🔄 Cloud deployment options

A Python desktop application that uses AssemblyAI's transcription API to transcribe audio files with speaker identification. The application supports various audio formats and provides a modern GUI interface with advanced features.

## Features

### 🎯 **Core Features**
- **Modern GUI Interface**: Built with CustomTkinter for a sleek, modern appearance
- **Multiple File Selection**: Select single files, multiple files, or entire directories
- **Speaker Identification**: Automatic speaker labeling in transcriptions
- **Real-time Progress Tracking**: Live progress updates with performance metrics
- **Smart Output Management**: Save transcripts alongside source files or in custom directories
- **Performance Metrics**: Detailed timing and throughput statistics

### 🔧 **Advanced Features**
- **API Key Management**: Built-in settings menu for easy API key configuration
- **Same as Input Directory**: Intelligent handling of mixed source directories
- **Enhanced File Display**: Organized file list with full paths and counts
- **Error Recovery**: Robust error handling with per-file error reporting
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| Python | 3.9 | 3.11+ | Type hints support required |
| RAM | 4GB | 8GB+ | For processing large files |
| GPU | - | NVIDIA with CUDA | For Whisper acceleration |
| FFmpeg | Required | Latest | Audio processing |
| OS | Windows 10, macOS 10.15, Linux | Any recent version | Cross-platform |

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd recall
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Install FFmpeg:
   - **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg`

## API Key Setup

You have two options for setting up your AssemblyAI API key:

### Option 1: Using the GUI (Recommended)
1. Run the application: `python run.py`
2. Go to **Settings > API Key** in the menu bar
3. Enter your AssemblyAI API key in the secure dialog
4. Click **Save** - the key will be automatically saved for future use

### Option 2: Environment Variable
Create a `.env` file in the project root:
```env
ASSEMBLYAI_API_KEY=your_api_key_here
OUTPUT_DIRECTORY=transcriptions
```

## Usage

### Running the Application
```bash
python run.py
```

### File Selection Options
1. **Select Files**: Choose multiple audio files from anywhere on your system
2. **Select Directory**: Process all supported audio files in a directory
3. **Mixed Sources**: Files from different directories are handled intelligently

### Output Options
- **Custom Directory**: Specify where to save all transcriptions
- **Same as Input**: Save each transcript in the same directory as its source file
  - For files from the same directory: Uses that directory
  - For mixed directories: Each transcript saved with its source file

### Transcription Process
1. Select your audio files using either selection method
2. Choose output directory preference
3. Click **Start Transcription**
4. Monitor real-time progress with performance metrics
5. View detailed logs and completion status

## File Format Support

The application supports all major audio formats:

- **AMR** (.amr)
- **MP3** (.mp3) 
- **WAV** (.wav)
- **M4A** (.m4a)
- **OGG** (.ogg)
- **FLAC** (.flac)
- **AAC** (.aac)
- **WMA** (.wma)

## Transcription Features

### Speaker Identification
- Automatic speaker detection and labeling
- Output format: `Speaker A: [text]`, `Speaker B: [text]`
- Uses AssemblyAI's advanced speaker diarization

### Performance Optimization
- **Nano Model**: Fast, efficient transcription engine
- **Batch Processing**: Handle multiple files seamlessly
- **Progress Tracking**: Real-time status updates
- **Performance Metrics**: Speed and throughput monitoring

## User Interface

### Main Window
- **File Selection Buttons**: Choose files or directories
- **File List**: Organized display with counts and full paths
- **Progress Tracking**: Real-time status and progress bar
- **Performance Panel**: Live metrics and timing information
- **Output Log**: Detailed transcription log with timestamps

### Settings Menu
- **API Key Management**: Secure API key storage and configuration
- **About Dialog**: Application information and supported formats

## Error Handling

Robust error handling includes:
- **Missing API Key**: Clear guidance to Settings menu
- **Invalid Audio Files**: Per-file error reporting
- **Network Issues**: Retry logic and informative error messages
- **File System Problems**: Graceful handling of permissions/access issues
- **API Errors**: Detailed AssemblyAI error reporting

For detailed troubleshooting, see our [Troubleshooting Guide](TROUBLESHOOTING.md).

## Configuration

### Whisper-on-Fedora Integration (Local Transcription)

Recall now supports the [whisper-on-fedora](https://github.com/arealicehole/whisper-on-fedora) server for local, GPU-accelerated transcription:

#### Quick Setup
1. Install and run whisper-on-fedora server on port 8767 (default)
2. Recall will automatically connect to port 8767

#### Configuration Options
Set the Whisper API URL via environment variable or `.env` file:
```env
# For whisper-on-fedora (default)
WHISPER_API_URL=http://127.0.0.1:8767

# For original whisper server
WHISPER_API_URL=http://127.0.0.1:8765

# Select backend (whisper for local, assemblyai for cloud)
TRANSCRIBER_BACKEND=whisper
```

#### Testing Connectivity
```bash
# Test whisper-on-fedora connection
python test_whisper_8767.py
```

### Automatic Configuration
- **API Key Storage**: Saved to `~/.recall/config.json`
- **Cross-Platform**: Uses standard user config directories
- **Persistent Settings**: Automatically loads saved configuration

### Manual Configuration
You can still use environment variables if preferred:
```env
ASSEMBLYAI_API_KEY=your_api_key_here
OUTPUT_DIRECTORY=transcriptions
WHISPER_API_URL=http://127.0.0.1:8767
TRANSCRIBER_BACKEND=whisper
```

## Technical Details

### Architecture Overview

Recall uses a layered architecture with pluggable backends:

```
┌─────────────────────────────────────┐
│         GUI (CustomTkinter)         │
│         Web API (Flask)             │
├─────────────────────────────────────┤
│        Core Business Logic          │
│     (Transcriber Factory Pattern)   │
├─────────────────────────────────────┤
│     Transcription Backends          │
│  ┌──────────┐    ┌──────────────┐  │
│  │ Whisper  │    │ AssemblyAI   │  │
│  │  (Local) │    │   (Cloud)    │  │
│  └──────────┘    └──────────────┘  │
└─────────────────────────────────────┘
```

The factory pattern allows seamless switching between backends via configuration.

### Core Components
- **GUI Framework**: CustomTkinter for modern appearance
- **Transcription Engine**: AssemblyAI Nano model with speaker labels
- **Audio Processing**: PyDub with FFmpeg backend
- **Threading**: Non-blocking UI with background processing
- **Configuration**: JSON-based user settings

### Performance Benchmarks

| Backend | Device | Speed | Diarization | Cost |
|---------|--------|-------|-------------|------|
| Whisper (Local) | RTX 5060 Ti | 54x real-time | CPU (0.6x) | Free |
| Whisper (Local) | CPU only | 0.5x real-time | 0.3x | Free |
| AssemblyAI | Cloud | 2-5x real-time | Included | $0.00025/sec |

*Benchmarks on 60-second audio file*

### Performance Features
- **Concurrent Processing**: Efficient handling of multiple files
- **Memory Management**: Automatic cleanup of temporary files
- **Progress Tracking**: Real-time updates without UI blocking
- **Error Recovery**: Continue processing remaining files on individual failures

## Development

For developers looking to contribute or extend Recall:

- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
- **[ONBOARDING.md](ONBOARDING.md)** - Comprehensive developer guide
- **[TESTING.md](TESTING.md)** - Test suite documentation
- **[TRANSCRIPTION_BACKENDS.md](TRANSCRIPTION_BACKENDS.md)** - Backend implementation details

### Quick Development Setup
```bash
# Clone and setup
git clone <repo>
cd recall
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Run tests
pytest

# Start developing
python run.py
```

## Contributing

We welcome contributions! Please see our [Developer Guide](ONBOARDING.md) for details.

### Quick Contribution Guide
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Maintain 80% test coverage

## License

MIT License

## Web Application

In addition to the desktop GUI, a simple Flask-based web interface is available.
Run it locally with:

```bash
python -m src.webapp
```

### Docker

You can build and run the web app in a container:

```bash
# Build the image
docker build -t audio-transcriber .

# Run with API key as environment variable
docker run -p 5000:5000 -e ASSEMBLYAI_API_KEY=your_api_key_here audio-transcriber

# Or configure API key through the web interface after starting
docker run -p 5000:5000 audio-transcriber
```

**Note:** The container will be available at `http://localhost:5000`. If no API key is provided via environment variable, you can configure it through the web interface.

## Links

- [Documentation](docs/)
- [API Reference](docs/api-reference.md)
- [Issue Tracker](https://github.com/username/recall/issues)
- [Discussions](https://github.com/username/recall/discussions)
- [Changelog](CHANGELOG.md)
