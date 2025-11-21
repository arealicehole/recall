import argparse
import os
import sys
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.utils.config import Config
from src.core.audio_handler import AudioHandler
from src.core.transcriber import Transcriber
from src.core.errors import APIKeyError

def main():
    """
    CLI for transcribing audio and video files.
    """
    parser = argparse.ArgumentParser(description="Transcribe audio/video files from the command line.")
    parser.add_argument("input_path", help="Path to the media file or directory to process.")
    parser.add_argument("-o", "--output_dir", default="transcripts", help="Directory to save the transcripts.")
    parser.add_argument("--same-as-input", action="store_true", help="Save the transcript in the same directory as the input file.")
    args = parser.parse_args()

    print("--- Recall CLI Transcriber ---")

    config = Config()
    if not config.api_key:
        print("Error: AssemblyAI API key not found.")
        print("Please set the ASSEMBLYAI_API_KEY environment variable or run the GUI/web setup.")
        sys.exit(1)

    audio_handler = AudioHandler(config)
    transcriber = Transcriber(config)

    # Get list of files to process
    print(f"🔍 Searching for media files in: {args.input_path}")
    media_files = audio_handler.get_audio_files(args.input_path)

    if not media_files:
        print("No supported media files found.")
        sys.exit(0)

    print(f"Found {len(media_files)} file(s) to process.")
    total_start_time = datetime.now()

    for i, file_path in enumerate(media_files):
        filename = os.path.basename(file_path)
        print(f"--- Processing file {i+1}/{len(media_files)}: {filename} ---")
        file_start_time = datetime.now()

        try:
            # 1. Prepare audio (extracts from video, converts to WAV)
            print("🔊 Preparing audio...")
            prepared_path = audio_handler.prepare_audio(file_path)
            if not prepared_path:
                print(f"Skipping {filename}: Could not prepare audio.")
                continue

            # 2. Transcribe
            print(f"✍️ Transcribing (using AssemblyAI)...")
            transcript = transcriber.transcribe_file(prepared_path)

            # 3. Save transcript
            if args.same_as_input:
                output_dir = os.path.dirname(file_path)
            else:
                output_dir = args.output_dir
            
            os.makedirs(output_dir, exist_ok=True)
            output_filename = f"{os.path.splitext(filename)[0]}_transcription.txt"
            output_filepath = os.path.join(output_dir, output_filename)

            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(transcript)
            
            file_end_time = datetime.now()
            duration = (file_end_time - file_start_time).total_seconds()
            print(f"✅ Success! Transcript saved to: {output_filepath}")
            print(f"⏱️ Time for this file: {duration:.2f} seconds")

        except APIKeyError as e:
            print(f"❌ API Key Error: {e}")
            break # Stop processing if API key is invalid
        except Exception as e:
            print(f"❌ An error occurred while processing {filename}: {e}")
        finally:
            # Clean up all temp files created during this iteration
            audio_handler.cleanup_all_temp_files()
    
    total_end_time = datetime.now()
    total_duration = (total_end_time - total_start_time).total_seconds()
    print("---")
    print(f"🎉 All files processed in {total_duration:.2f} seconds. ---")


if __name__ == "__main__":
    main()
