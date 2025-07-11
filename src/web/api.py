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

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac', 'wma', 'amr'}

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
                transcript_obj = transcriber.transcribe_file(prepared_path)
                
                # Clean up temporary file if it was created
                if prepared_path != file_path:
                    audio_handler.cleanup_temp_file(prepared_path)

                if not transcript_obj:
                    raise TranscriptionError("Transcription failed and returned no object.")

                transcript_text = transcriber.format_transcript_to_string(transcript_obj)

                if not transcript_text or "silent" in transcript_text or "no detectable speech" in transcript_text:
                    raise SilentAudioError(transcript_text or "Transcription returned empty or silent result.")
                
                # Determine output directory
                if job.same_as_input:
                    # For web uploads, "same as input" means save in uploads folder
                    output_dir = os.path.dirname(file_path)
                else:
                    output_dir = job.output_directory

                # Ensure the output directory exists
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                else: # Fallback to default if something goes wrong
                    output_dir = os.path.join(project_root, 'transcripts')
                    os.makedirs(output_dir, exist_ok=True)

                base_filename = os.path.splitext(job.current_file)[0]
                
                # Save .json transcript
                output_path_json = os.path.join(output_dir, f"{base_filename}_transcription.json")
                if hasattr(transcript_obj, 'json_response'):
                    with open(output_path_json, 'w', encoding='utf-8') as f:
                        json.dump(transcript_obj.json_response, f, indent=4)
                else:
                    # If for some reason there's no json_response, save the text as a fallback.
                    with open(output_path_json, 'w', encoding='utf-8') as f:
                        json.dump({'text': transcript_text}, f, indent=4)

                job.results.append({
                    'file': job.current_file,
                    'status': 'completed',
                    'transcript_path_json': output_path_json,
                    'transcript_preview': transcript_text[:200] + '...' if len(transcript_text) > 200 else transcript_text
                })
                
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
    job = TranscriptionJob(job_id, uploaded_files, output_directory, same_as_input)
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

@app.route('/api/transcript/<job_id>/<filename>')
def get_transcript(job_id, filename):
    """Get a specific transcript file."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404

    job = jobs[job_id]
    result = next((r for r in job.results if r['file'] == filename and r['status'] == 'completed'), None)

    if not result:
        return jsonify({'error': 'Transcript for this file not found or not completed'}), 404

    json_path = result.get('transcript_path_json')

    if json_path and os.path.exists(json_path):
        return send_file(json_path, as_attachment=True)
        
    return jsonify({'error': 'Transcript file not found on disk'}), 404

@app.route('/api/job/<job_id>/<original_filename>/processed', methods=['POST'])
def receive_processed_transcript(job_id, original_filename):
    """Endpoint to receive the processed transcript from the AI service."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404

    job = jobs[job_id]
    result = next((r for r in job.results if r['file'] == original_filename and r['status'] == 'completed'), None)

    if not result:
        return jsonify({'error': 'Original transcript for this file not found or not completed'}), 404

    processed_data = request.json
    if not processed_data:
        return jsonify({'error': 'No JSON data provided'}), 400

    json_path = result.get('transcript_path_json')
    if not json_path:
        return jsonify({'error': 'Original JSON transcript path not found'}), 404

    # Save the processed data to a new file
    output_dir = os.path.dirname(json_path)
    base_filename = os.path.splitext(original_filename)[0]
    processed_filename = f"{base_filename}_transcription.processed.json"
    processed_filepath = os.path.join(output_dir, processed_filename)

    try:
        with open(processed_filepath, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=4)
        
        # Optionally, update the job result to include the path to the processed file
        result['processed_transcript_path'] = processed_filepath
        result['status'] = 'processed'

        return jsonify({
            'status': 'success',
            'message': f'Processed transcript saved to {processed_filepath}'
        }), 200
    except Exception as e:
        logging.exception(f"Failed to save processed transcript for job {job_id}")
        return jsonify({'error': f'Failed to save processed file: {str(e)}'}), 500

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
    """Download all transcripts from a job as a zip file"""
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
                    # The transcript path is already a full, safe path
                    json_path = result.get('transcript_path_json')
                    if json_path and os.path.exists(json_path):
                        zf.write(json_path, os.path.basename(json_path))
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