#!/usr/bin/env python3
"""
Production launch script for Recall Web Interface
Uses Gunicorn for production deployment with proper logging
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def setup_logging():
    """Configure logging for production"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'recall-web.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def get_workers():
    """Calculate optimal number of workers based on CPU cores"""
    import multiprocessing
    cores = multiprocessing.cpu_count()
    return min(max(2, cores), 4)  # Between 2-4 workers

def main():
    """Launch the web API with Gunicorn for production"""
    logger = setup_logging()
    
    logger.info("🚀 Starting Recall Web Interface (Production Mode)")
    logger.info("📍 Server will be available at: http://localhost:5000")
    logger.info("⏹️  Press Ctrl+C to stop the server")
    logger.info("-" * 50)
    
    # Ensure required directories exist
    Path("transcripts").mkdir(exist_ok=True)
    Path("uploads").mkdir(exist_ok=True)
    Path("config").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    workers = get_workers()
    logger.info(f"🔧 Using {workers} Gunicorn workers")
    
    # Configure Gunicorn settings
    gunicorn_cmd = [
        'gunicorn',
        '--bind', '0.0.0.0:5000',
        '--workers', str(workers),
        '--worker-class', 'sync',
        '--worker-connections', '1000',
        '--timeout', '300',  # 5 minutes for long transcription jobs
        '--keep-alive', '5',
        '--max-requests', '1000',
        '--max-requests-jitter', '100',
        '--preload',
        '--log-level', 'info',
        '--access-logfile', 'logs/access.log',
        '--error-logfile', 'logs/error.log',
        '--capture-output',
        '--enable-stdio-inheritance',
        'src.web.api:app'
    ]
    
    try:
        logger.info("🔧 Starting Gunicorn server...")
        subprocess.run(gunicorn_cmd, check=True)
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user!")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error starting server: {e}")
        logger.error("💡 Make sure you've installed gunicorn: pip install gunicorn")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 