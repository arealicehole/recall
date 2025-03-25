# Audio Transcriber

A Python desktop application that uses OpenAI's Whisper API to transcribe audio files. The application supports various audio formats including AMR, MP3, WAV, M4A, and more.

## Features

- Modern, user-friendly GUI interface
- Support for multiple audio formats
- Batch processing of files in a directory
- Progress tracking for transcription
- Automatic file format conversion
- Clear error handling and feedback

## Requirements

- Python 3.9 or higher
- OpenAI API key
- FFmpeg (for audio file handling)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd audio-transcriber
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
   - Windows: Download from https://ffmpeg.org/download.html and add to PATH
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg`

5. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
OUTPUT_DIRECTORY=transcriptions
```

## Usage

1. Run the application:
```bash
python src/main.py
```

2. Use the interface to:
   - Select a single audio file for transcription
   - Select a directory to transcribe all supported audio files
   - Monitor transcription progress
   - View transcription results

Transcribed text files will be saved in the configured output directory (default: `transcriptions/`).

## Supported Audio Formats

- AMR (.amr)
- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- OGG (.ogg)
- FLAC (.flac)
- AAC (.aac)
- WMA (.wma)

## Error Handling

The application includes robust error handling for:
- Invalid audio files
- API errors
- File system issues
- Conversion problems

Error messages will be displayed in the GUI and logged for debugging.

## License

MIT License 