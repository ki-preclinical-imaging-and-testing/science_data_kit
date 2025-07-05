#!/usr/bin/env python
"""
Run Workshop Script for Science Data Kit

This script launches the Science Data Kit application in workshop mode.
It provides a simplified UI with features relevant to workshop attendees.
"""

import os
import sys
import streamlit.web.bootstrap
from pathlib import Path

def main():
    """Run the Science Data Kit application in workshop mode."""
    # Get the path to the workshop app module
    workshop_app_path = Path(__file__).parent / "science_data_kit" / "ui" / "workshop_app.py"
    
    # Check if the workshop app module exists
    if not workshop_app_path.exists():
        print(f"Error: Workshop app module not found at {workshop_app_path}")
        return 1
    
    # Set environment variables for workshop mode
    os.environ["SDK_WORKSHOP_MODE"] = "1"
    
    # Launch the Streamlit app with the workshop app module
    sys.argv = ["streamlit", "run", str(workshop_app_path), "--server.port=8501"]
    streamlit.web.bootstrap.run()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())