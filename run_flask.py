#!/usr/bin/env python3.13
"""
Science Data Kit - Flask Web Application Runner

This script runs the Flask web application for Science Data Kit.
"""
import os
import sys
import site

# Print Python information for debugging
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")
print(f"Site packages: {site.getsitepackages()}")

def main():
    """Run the Science Data Kit Flask web application."""
    try:
        # Import the Flask app
        from science_data_kit.web import create_app

        # Create the app
        app = create_app()

        # Get port from environment variable or use default
        port = int(os.environ.get('PORT', 5001))

        # Run the app
        app.run(host='0.0.0.0', port=port, debug=True)

    except ImportError as e:
        print(f"ERROR: Could not import Flask app: {e}", file=sys.stderr)
        print("Please ensure all dependencies are installed correctly.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Error running the application: {e}", file=sys.stderr)
        print("Please check the logs for more information.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
