#!/usr/bin/env python
"""
Science Data Kit - Legacy App Runner

This script runs the legacy version of the Science Data Kit application.
The legacy app is maintained for reference purposes only and is not actively developed.
For the current version, use run_app.py instead.
"""
import os
import sys
import subprocess

def run_legacy_app():
    """
    Run the Science Data Kit application using the legacy app.
    """
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the app.py file
    app_path = os.path.join(script_dir, 'app', 'app.py')

    # Run the streamlit app
    cmd = ['streamlit', 'run', app_path]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Science Data Kit legacy app: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Science Data Kit legacy app stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    print("Running Science Data Kit legacy app")
    print("Note: This is the legacy version maintained for reference purposes only.")
    print("For the current version, use run_app.py instead.")
    run_legacy_app()