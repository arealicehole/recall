# Suggested Development Commands

## Running the Application
```bash
python run.py              # Start GUI application  
python -m src.webapp        # Start web interface
```

## Development
```bash
python -m venv venv
source venv/bin/activate    # Linux/Mac
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

## Testing  
```bash
pytest                     # Run test suite
python test_backends.py    # Test transcription backends
python test_whisper_8767.py # Test local Whisper connection
```

## Code Quality
```bash
ruff check .               # Linting
ruff format .              # Formatting  
mypy src/                  # Type checking
```

## Configuration
- Environment variables: `.env` file
- API keys: `~/.recall/config.json` 
- Backend selection: `TRANSCRIBER_BACKEND=whisper|assemblyai`