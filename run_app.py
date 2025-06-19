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

    This is now the primary application interface. The legacy app is 
    maintained for reference only and can be run using run_legacy_app.py
    or by providing the --legacy flag to this script.

    Raises:
        ImportError: If the new app module cannot be imported.
        Exception: If there is an error running the app.
    """
    try:
        # Import the new app module
        from science_data_kit.ui.app import run_app

        # Run the app
        run_app()
    except ImportError as e:
        print(f"ERROR: Could not import new app module: {e}", file=sys.stderr)
        print("Please ensure all dependencies are installed correctly.", file=sys.stderr)
        print("You can run the legacy app with: python run_legacy_app.py", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Error running the application: {e}", file=sys.stderr)
        print("Please check the logs for more information.", file=sys.stderr)
        print("You can run the legacy app with: python run_legacy_app.py", file=sys.stderr)
        sys.exit(1)

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

    Uses the new UI framework by default. The legacy app is kept for reference
    and can be run using the --legacy flag.
    """
    # Check if --legacy flag is provided
    if "--legacy" in sys.argv:
        print("Running legacy app (--legacy flag provided)")
        print("Note: The legacy app is maintained for reference purposes only.")
        run_legacy_app()
        return

    # Run the new app
    print("Running Science Data Kit with the new UI framework")
    run_new_app()

if __name__ == "__main__":
    main()
