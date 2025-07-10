#!/usr/bin/env python3
"""
Run script for the Recall application.
This ensures the application is run from the correct directory
and that Python can find all the necessary packages.
"""

import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.main import main

if __name__ == "__main__":
    main() 