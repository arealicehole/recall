#!/usr/bin/env python3
"""
Web API version of Recall
Better suited for containerization
"""

import sys
import os
import io
import zipfile
# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from flask import Flask, request, jsonify, render_template, send_file
import threading
import time
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
import json
import logging

from src.core.audio_handler import AudioHandler
from src.core.transcriber import Transcriber
from src.core.jobs import TranscriptionJob
from src.core.errors import RecallError, APIKeyError, AudioHandlerError, TranscriptionError, SilentAudioError
from src.utils.config import Config

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(project_root, 'uploads')

# Initialize components
config = Config()
audio_handler = AudioHandler(config)
transcriber = Transcriber(config)

# In-memory job tracking
jobs = {}

# Dynamically build allowed extensions from config
ALLOWED_EXTENSIONS = {fmt.strip('.') for fmt in (config.supported_formats + config.supported_video_formats)}

@app.errorhandler(RecallError)
def handle_recall_error(error):
    """Handle custom application errors and return a JSON response."""
    response = jsonify({'error': str(error)})
    response.status_code = 400
    if isinstance(error, APIKeyError):
        response.status_code = 401
    return response

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_transcription_job(job_id):
    """Process transcription job in background"""
    job = jobs[job_id]
    job.status = "processing"
    job.start_time = datetime.now()
    
    try:
        total_files = len(job.files)
        
        for i, file_path in enumerate(job.files):
            job.current_file = os.path.basename(file_path)
            job.progress = (i / total_files) * 100
            
            try:
                # Prepare audio file (convert AMR/other formats to WAV if needed)
                prepared_path = audio_handler.prepare_audio(file_path)
                if not prepared_path:
                    raise AudioHandlerError("Failed to prepare audio file for transcription")
                
                # Transcribe the prepared file
                transcript = transcriber.transcribe_file(prepared_path)
                
                # Clean up temporary file if it was created
                if prepared_path != file_path:
                    audio_handler.cleanup_temp_file(prepared_path)
                
                if not transcript or transcript.strip() == "":
                    # Check if the audio file might be silent
                    if os.path.exists(prepared_path if prepared_path else file_path):
                        # Try to get audio duration for better error message
                        try:
                            from pydub import AudioSegment
                            audio = AudioSegment.from_file(prepared_path if prepared_path else file_path)
                            duration = len(audio) / 1000  # Convert to seconds
                            
                            if duration > 0:
                                raise SilentAudioError(f"Audio file appears to be silent or contain no detectable speech (duration: {duration:.1f}s).")
                            else:
                                raise TranscriptionError("Audio file has zero duration or is corrupted")
                        except Exception as audio_error:
                            # If we can't analyze the audio, just use the original error
                            if "silent" in str(audio_error) or "speech" in str(audio_error):
                                raise audio_error
                            else:
                                raise TranscriptionError("Transcription returned empty result - audio may be silent or corrupted")
                    else:
                        raise TranscriptionError("Transcription returned empty result - file not found post-processing.")
                
                # Save transcript using job's output settings
                if job.same_as_input:
                    # For web uploads, "same as input" means save in uploads folder with the uploaded files
                    upload_dir = os.path.dirname(file_path)
                    output_path = os.path.join(upload_dir, f"{os.path.splitext(job.current_file)[0]}_transcription.txt")
                else:
                    # Save in the specified output directory
                    output_path = os.path.join(job.output_directory, f"{os.path.splitext(job.current_file)[0]}_transcription.txt")
                
                # Ensure the output directory exists
                output_dir = os.path.dirname(output_path)
                if output_dir:  # Only create if there's a directory to create
                    os.makedirs(output_dir, exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(transcript)

                # Export timestamps and captions if requested
                result_data = {
                    'file': job.current_file,
                    'status': 'completed',
                    'transcript_path': output_path,
                    'transcript': transcript[:500] + '...' if len(transcript) > 500 else transcript
                }

                if job.export_timestamps and transcriber.last_transcript:
                    try:
                        saved_files = transcriber.save_transcript_data(
                            file_path,
                            transcriber.last_transcript,
                            same_as_input=job.same_as_input
                        )

                        # Add paths to result data
                        if 'json' in saved_files:
                            result_data['json_path'] = saved_files['json']
                        if 'srt' in saved_files:
                            result_data['srt_path'] = saved_files['srt']
                    except Exception as e:
                        logging.warning(f"Failed to export timestamps for {job.current_file}: {e}")

                job.results.append(result_data)
                
            except Exception as e:
                logging.exception(f"Failed to process file {job.current_file} for job {job_id}")

                # Clean up any temp files on error
                if 'prepared_path' in locals() and prepared_path != file_path:
                    audio_handler.cleanup_temp_file(prepared_path)
                    
                job.results.append({
                    'file': job.current_file,
                    'status': 'error',
                    'error': str(e)
                })
        
        job.status = "completed"
        job.progress = 100
        job.end_time = datetime.now()
        
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        job.end_time = datetime.now()
    
    finally:
        # Clean up all temporary files
        audio_handler.cleanup_all_temp_files()

@app.route('/')
def index():
    """Main page with upload form"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """Check API status"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'api_key_configured': bool(config.api_key)
    })

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Upload audio files for transcription"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No files selected'}), 400
    
    # Check API key
    if not config.api_key:
        raise APIKeyError("AssemblyAI API key not configured. Please set it via the /api/config endpoint.")
    
    # Get output directory and same_as_input setting from form data
    output_directory = request.form.get('output_directory', 'transcripts').strip()
    same_as_input = request.form.get('same_as_input', 'false').lower() == 'true'
    export_timestamps = request.form.get('export_timestamps', 'false').lower() == 'true'
    
    # Validate and create output directory if needed
    if not same_as_input:
        # Use absolute path or relative to project root
        if not os.path.isabs(output_directory):
            output_directory = os.path.join(project_root, output_directory)
        try:
            os.makedirs(output_directory, exist_ok=True)
        except Exception as e:
            raise RecallError(f"Invalid output directory: {str(e)}")
    else:
        # For same_as_input, we'll save in the uploads directory (determined later)
        output_directory = None
    
    # Create job
    job_id = str(uuid.uuid4())
    uploaded_files = []
    
    # Save uploaded files
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
            file.save(file_path)
            uploaded_files.append(file_path)
    
    if not uploaded_files:
        raise RecallError("No valid audio files uploaded")
    
    # Create and start job with output settings
    job = TranscriptionJob(job_id, uploaded_files, output_directory, same_as_input, export_timestamps)
    jobs[job_id] = job
    
    # Start processing in background
    thread = threading.Thread(target=process_transcription_job, args=(job_id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'files_count': len(uploaded_files),
        'status': 'started'
    })

@app.route('/api/job/<job_id>')
@app.route('/api/jobs/<job_id>')
def get_job_status(job_id):
    """Get job status and results"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(jobs[job_id].to_dict())

@app.route('/api/jobs')
def list_jobs():
    """List all jobs"""
    return jsonify([job.to_dict() for job in jobs.values()])

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or set API configuration"""
    if request.method == 'GET':
        return jsonify({
            'api_key_configured': bool(config.api_key),
            'output_directory': config.output_dir
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        if 'api_key' in data:
            config.api_key = data['api_key']
            # Save to config file
            config_path = os.path.expanduser('~/.recall/config.json')
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump({'api_key': config.api_key}, f)
        
        return jsonify({'success': True})

@app.route('/api/download/<job_id>')
def download_results(job_id):
    """Download all transcripts for a job as a zip file"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    if job.status != 'completed':
        return jsonify({'error': 'Job not finished'}), 400

    # Create a zip file in memory
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for result in job.results:
            if result['status'] == 'completed':
                try:
                    # Add transcript file
                    if os.path.exists(result['transcript_path']):
                        zf.write(result['transcript_path'], os.path.basename(result['transcript_path']))

                    # Add JSON data file if it exists
                    if 'json_path' in result and os.path.exists(result['json_path']):
                        zf.write(result['json_path'], os.path.basename(result['json_path']))

                    # Add SRT caption file if it exists
                    if 'srt_path' in result and os.path.exists(result['srt_path']):
                        zf.write(result['srt_path'], os.path.basename(result['srt_path']))

                except Exception as e:
                    print(f"Error adding file to zip: {e}")

    memory_file.seek(0)
    
    return send_file(memory_file, download_name=f'recall_transcripts_{job_id}.zip', as_attachment=True)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    # Ensure upload and transcript directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(project_root, 'transcripts'), exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000) 