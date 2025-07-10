#!/usr/bin/env python3
"""
Launch script for Recall Web Interface
"""

import os
import sys
import webbrowser
import time
import threading

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)  # Wait for server to start
    webbrowser.open('http://localhost:5000')

if __name__ == "__main__":
    print("🚀 Starting Recall Web Interface...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🌐 Opening browser automatically...")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start browser opener in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Import and run the web API
    try:
        from src.web.api import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Make sure you've installed Flask: pip install flask") 