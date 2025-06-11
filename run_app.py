#!/usr/bin/env python
"""
Science Data Kit - Main entry point
"""
import os
import sys
import subprocess

def main():
    """
    Run the Science Data Kit application using streamlit
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

if __name__ == "__main__":
    main()