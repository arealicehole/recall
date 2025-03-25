# Audio Transcription Desktop Application

## Project Overview
A Python desktop application that uses AssemblyAI's API to transcribe audio files. The application supports batch processing of multiple audio files and various audio formats, with a focus on efficiency and user experience.

## Core Requirements
1. Desktop GUI application built with Python
2. Integration with AssemblyAI API for transcription
3. Support for multiple audio formats including:
   - AMR
   - MP3
   - WAV
   - M4A
   - And other common audio formats
4. Features:
   - Select single file or directory for transcription
   - Batch processing of multiple files
   - Progress tracking with detailed metrics
   - Flexible output directory selection
   - Same-as-input directory option
   - Performance metrics and timing display
   - Automatic temporary file cleanup
   - Output transcriptions to text files
   - Clear error handling and user feedback

## Goals
- Create an intuitive, user-friendly interface
- Provide efficient batch processing capabilities
- Ensure robust error handling
- Support a wide range of audio formats
- Maintain clear documentation and code structure
- Optimize performance with AssemblyAI's nano model
- Keep system resources clean with proper cleanup

## Current Status
- Using AssemblyAI's nano model for faster processing
- Implemented comprehensive progress tracking
- Added flexible output directory management
- Enhanced error handling and recovery
- Improved temporary file management
- Added real-time performance metrics 