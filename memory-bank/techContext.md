# Technical Context

## Core Technologies
- Python 3.9+
- AssemblyAI API (nano model)
- CustomTkinter (Modern themed Tkinter for GUI)
- pydub (Audio file handling)

## Development Setup
1. Python environment setup with required dependencies
2. AssemblyAI API key configuration
3. Virtual environment for dependency management

## Dependencies
```
assemblyai>=0.20.0
customtkinter>=5.2.0
pydub>=0.25.1
python-dotenv>=1.0.0
certifi>=2024.2.2
```

## Technical Constraints
- Requires AssemblyAI API key
- Internet connection for API calls
- Sufficient disk space for audio files
- System audio codecs for various formats

## File Structure
```
audio-transcriber/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── gui/
│   │   ├── __init__.py
│   │   └── app.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── transcriber.py
│   │   └── audio_handler.py
│   └── utils/
│       ├── __init__.py
│       └── config.py
├── memory-bank/
│   ├── projectbrief.md
│   ├── techContext.md
│   ├── systemPatterns.md
│   ├── productContext.md
│   ├── activeContext.md
│   └── progress.md
├── requirements.txt
├── .env.example
└── README.md
```

## Environment Configuration
- `.env` file with AssemblyAI API key
- Output directory configuration
- SSL certificate handling for API calls

## Performance Considerations
- Using AssemblyAI's nano model for faster processing
- Efficient temporary file management
- Automatic cleanup of temporary WAV files
- Real-time progress tracking and metrics