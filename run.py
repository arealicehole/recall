#!/usr/bin/env python3
"""
Master run script for the Recall application.
This script can launch the GUI, the development web server,
or the production web server based on command-line arguments.
"""

import os
import sys
import subprocess
import logging
import argparse
import webbrowser
import time
import threading
from pathlib import Path

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_gui():
    """Launches the CustomTkinter GUI."""
    print("🎨 Launching Recall GUI...")
    try:
        from src.main import main as start_gui
        start_gui()
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        print("💡 Make sure you've installed all GUI dependencies: pip install customtkinter")

def run_web_development(host='0.0.0.0', port=5000):
    """Launches the Flask development server."""
    print("🚀 Starting Recall Web Interface (Development Mode)...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print("🌐 Opening browser automatically...")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)

    def open_browser():
        """Open browser after a short delay."""
        time.sleep(2)
        webbrowser.open(f'http://localhost:{port}')

    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    try:
        from src.web.api import app
        app.run(host=host, port=port, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Make sure you've installed Flask: pip install flask")

def run_web_production(host='0.0.0.0', port=5000, workers=None):
    """Launches the web API with Gunicorn for production."""
    
    # --- Logging Setup ---
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
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting Recall Web Interface (Production Mode)")
    logger.info(f"📍 Server will be available at: http://{host}:{port}")
    logger.info("⏹️  Press Ctrl+C to stop the server")
    logger.info("-" * 50)
    
    # --- Ensure required directories exist ---
    Path("transcripts").mkdir(exist_ok=True)
    Path("uploads").mkdir(exist_ok=True)
    Path("config").mkdir(exist_ok=True)
    
    # --- Gunicorn Worker Calculation ---
    if workers is None:
        # With an in-memory job store, we must use a single worker process.
        # Gunicorn with multiple workers creates separate processes, and the
        # 'jobs' dictionary containing job statuses would not be shared.
        workers = 1
    logger.info(f"🔧 Using {workers} Gunicorn workers")
    
    # --- Gunicorn Command ---
    gunicorn_cmd = [
        'gunicorn',
        '--bind', f'{host}:{port}',
        '--workers', str(workers),
        '--worker-class', 'sync',
        '--timeout', '300',  # 5 minutes for long jobs
        '--preload',
        '--log-level', 'info',
        '--access-logfile', str(log_dir / 'access.log'),
        '--error-logfile', str(log_dir / 'error.log'),
        '--capture-output',
        'src.web.api:app'
    ]
    
    try:
        logger.info("🔧 Starting Gunicorn server...")
        subprocess.run(gunicorn_cmd, check=True)
    except KeyboardInterrupt:
        logger.info("\n👋 Server stopped by user!")
    except FileNotFoundError:
        logger.error("❌ Gunicorn not found.")
        logger.error("💡 Please install it for production mode: pip install gunicorn")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error starting server: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Run the Recall application in different modes.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "mode",
        choices=["gui", "web"],
        help="The mode to run the application in:\n"
             "  gui: Launch the desktop graphical user interface.\n"
             "  web: Launch the web server interface."
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Run the web server in production mode using Gunicorn.\n(Only valid with 'web' mode)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host for the web server. (Default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port for the web server. (Default: 5000)"
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        help="Number of Gunicorn workers. (Default: auto-detected)"
    )

    args = parser.parse_args()

    if args.mode == "gui":
        if args.prod or args.workers is not None:
            parser.error("--prod and --workers are only applicable for 'web' mode.")
        run_gui()

    elif args.mode == "web":
        if args.prod:
            run_web_production(host=args.host, port=args.port, workers=args.workers)
        else:
            if args.workers is not None:
                parser.error("--workers is only applicable for production mode (--prod).")
            run_web_development(host=args.host, port=args.port)

if __name__ == "__main__":
    main() 