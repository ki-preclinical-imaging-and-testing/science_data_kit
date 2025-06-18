#!/usr/bin/env python
"""
Science Data Kit - Main entry point
"""
import os
import sys
import subprocess
import importlib.util

def run_new_app():
    """
    Run the Science Data Kit application using the new UI framework.

    Returns:
        True if the app was run successfully, False otherwise.
    """
    try:
        # Try to import the new app module
        from science_data_kit.ui.app import run_app

        # Run the app
        run_app()
        return True
    except ImportError as e:
        print(f"Could not import new app module: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error running new app: {e}", file=sys.stderr)
        return False

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
        print(f"Error running Science Data Kit: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Science Data Kit stopped by user")
        sys.exit(0)

def main():
    """
    Run the Science Data Kit application.

    First tries to run the new app, and falls back to the legacy app if that fails.
    """
    # Check if --legacy flag is provided
    if "--legacy" in sys.argv:
        print("Running legacy app (--legacy flag provided)")
        run_legacy_app()
        return

    # Try to run the new app first
    if not run_new_app():
        print("Falling back to legacy app")
        run_legacy_app()

if __name__ == "__main__":
    main()
