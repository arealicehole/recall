# Troubleshooting Guide for Recall

## Common Issues and Solutions

### 1. "Transcription returned empty result" - Silent Audio Files

**Symptoms:**
- Transcription process completes successfully
- All files show "Failed - Transcription returned empty result"
- Empty zip download

**Cause:** 
Your audio files are silent or contain no detectable speech content.

**Solution:**
1. **Check your audio files first:**
   ```bash
   python check_audio_content.py
   ```
   This will analyze all your audio files and tell you if they contain speech.

2. **Common causes of silent audio:**
   - Microphone was muted during recording
   - Audio recording app didn't capture audio properly
   - Audio files are corrupted
   - Wrong audio input device was selected
   - Volume was too low during recording

3. **How to fix:**
   - Re-record your audio with proper microphone settings
   - Test your recording setup before important sessions
   - Use audio editing software to boost volume if audio is very quiet
   - Check that your audio files play sound when opened in a media player

### 2. "No API key configured"

**Symptoms:**
- Error message about missing API key
- Transcription fails immediately

**Solution:**
1. **Run the API key setup script:**
   ```bash
   python setup_api_key.py
   ```

2. **Get your API key from AssemblyAI:**
   - Go to https://www.assemblyai.com/
   - Sign up for a free account
   - Copy your API key from the dashboard

3. **Alternative setup methods:**
   - Create a `.env` file with `ASSEMBLYAI_API_KEY=your_key_here`
   - Set environment variable: `set ASSEMBLYAI_API_KEY=your_key_here`

### 3. Audio Processing Issues

**Symptoms:**
- "Failed to prepare audio file for transcription"
- AMR files not processing correctly

**Solution:**
1. **Install FFmpeg:**
   - Windows: Download from https://ffmpeg.org/download.html
   - Add FFmpeg to your system PATH
   - Restart your command prompt

2. **Check supported formats:**
   - AMR, MP3, WAV, M4A, OGG, FLAC, AAC, WMA
   - If your format isn't supported, convert it first

### 4. Very Quiet Audio

**Symptoms:**
- Audio files process but transcription is incomplete
- Some speech is missing from transcription

**Solution:**
1. **Check audio volume:**
   ```bash
   python check_audio_content.py
   ```

2. **Boost audio volume:**
   - Use audio editing software (Audacity, etc.)
   - Increase volume by 10-20dB
   - Ensure audio doesn't clip/distort

3. **Recording tips:**
   - Speak closer to the microphone
   - Use a dedicated microphone instead of built-in ones
   - Check recording levels during recording

### 5. Network/API Issues

**Symptoms:**
- Transcription fails with network errors
- API connection timeouts

**Solution:**
1. **Check internet connection**
2. **Verify API key is valid**
3. **Check AssemblyAI service status:** https://status.assemblyai.com/
4. **Try again after a few minutes**

## Debug Tools

### 1. Full System Test
```bash
python debug_transcription.py
```
This will test your entire setup and identify issues.

### 2. Audio Content Analysis
```bash
python check_audio_content.py
```
This will analyze your audio files for speech content.

### 3. API Key Setup
```bash
python setup_api_key.py
```
This will help you configure your AssemblyAI API key.

## Getting Help

If you're still having issues:

1. **Check the console output** for detailed error messages
2. **Run the debug script** to identify the problem
3. **Verify your audio files** contain actual speech
4. **Check that your API key is valid** and has credits remaining

## Tips for Better Transcription

1. **Audio Quality:**
   - Record in quiet environments
   - Use good quality microphones
   - Speak clearly and at normal pace
   - Avoid background noise

2. **File Formats:**
   - WAV files generally work best
   - MP3 is also very reliable
   - AMR files work but may need FFmpeg

3. **Recording Settings:**
   - Sample rate: 16kHz or higher
   - Bit depth: 16-bit or higher
   - Mono is fine for speech

4. **Content:**
   - Ensure audio actually contains speech
   - Check that conversations are audible
   - Verify recording wasn't accidentally muted 