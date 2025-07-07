#!/usr/bin/env python
"""
Science Data Kit - Main entry point
"""
import sys
import importlib.util

def run_app():
    """
    Run the Science Data Kit application using the UI framework.

    This is the primary application interface.

    Raises:
        ImportError: If the app module cannot be imported.
        Exception: If there is an error running the app.
    """
    try:
        # Import the app module
        from science_data_kit.ui.app import run_app

        # Run the app
        run_app()
    except ImportError as e:
        print(f"ERROR: Could not import app module: {e}", file=sys.stderr)
        print("Please ensure all dependencies are installed correctly.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Error running the application: {e}", file=sys.stderr)
        print("Please check the logs for more information.", file=sys.stderr)
        sys.exit(1)

def main():
    """
    Run the Science Data Kit application.
    """
    # Check if --legacy flag is provided
    if "--legacy" in sys.argv:
        print("The legacy app has been removed from the codebase.")
        print("The code can still be accessed from the git history if needed for reference.")
        sys.exit(1)

    # Run the app
    print("Running Science Data Kit")
    run_app()

if __name__ == "__main__":
    main()
