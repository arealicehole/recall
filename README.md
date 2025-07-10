# recall

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

- Python 3.9 or higher
- AssemblyAI API key (get one free at https://www.assemblyai.com/)
- FFmpeg (for audio file handling)

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

## Configuration

### Automatic Configuration
- **API Key Storage**: Saved to `~/.recall/config.json`
- **Cross-Platform**: Uses standard user config directories
- **Persistent Settings**: Automatically loads saved configuration

### Manual Configuration
You can still use environment variables if preferred:
```env
ASSEMBLYAI_API_KEY=your_api_key_here
OUTPUT_DIRECTORY=transcriptions
```

## Technical Details

### Architecture
- **GUI Framework**: CustomTkinter for modern appearance
- **Transcription Engine**: AssemblyAI Nano model with speaker labels
- **Audio Processing**: PyDub with FFmpeg backend
- **Threading**: Non-blocking UI with background processing
- **Configuration**: JSON-based user settings

### Performance
- **Concurrent Processing**: Efficient handling of multiple files
- **Memory Management**: Automatic cleanup of temporary files
- **Progress Tracking**: Real-time updates without UI blocking
- **Error Recovery**: Continue processing remaining files on individual failures

## License

MIT License 