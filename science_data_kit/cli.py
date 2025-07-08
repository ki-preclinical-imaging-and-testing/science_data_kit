#!/usr/bin/env python
"""
Science Data Kit CLI - Command Line Interface for Science Data Kit

This script provides the command-line interface for the Science Data Kit.
It ensures the environment is properly activated and runs the Streamlit app.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def is_environment_activated():
    """Check if the Science Data Kit environment is activated."""
    virtual_env = os.environ.get('VIRTUAL_ENV', '')
    return 'science-data-kit-env' in virtual_env or 'science_data_kit' in virtual_env

def find_project_root():
    """Find the project root directory."""
    # Try to find the project root by looking for key files
    current_dir = Path.cwd()
    
    # Check if we're already in the project root
    if (current_dir / 'science_data_kit.sh').exists():
        return current_dir
    
    # Check if we're in a subdirectory of the project
    for parent in current_dir.parents:
        if (parent / 'science_data_kit.sh').exists():
            return parent
    
    # If we can't find the project root, use the current directory
    return current_dir

def activate_environment():
    """Activate the Science Data Kit environment."""
    project_root = find_project_root()
    launcher_script = project_root / 'science_data_kit.sh'
    
    if not launcher_script.exists():
        print("ERROR: Could not find science_data_kit.sh launcher script.", file=sys.stderr)
        print("Please run this command from the Science Data Kit project directory.", file=sys.stderr)
        sys.exit(1)
    
    print("Activating Science Data Kit environment...")
    
    # Run the launcher script in a new shell
    # This will replace the current process with the new shell
    os.execv('/bin/bash', ['/bin/bash', str(launcher_script)])

def run_streamlit_app():
    """Run the Science Data Kit Streamlit application."""
    # Find the streamlit executable
    streamlit_path = shutil.which('streamlit')
    if not streamlit_path:
        print("ERROR: Could not find streamlit executable.", file=sys.stderr)
        print("Please ensure streamlit is installed in the current environment.", file=sys.stderr)
        sys.exit(1)
    
    # Find the app path
    project_root = find_project_root()
    app_path = project_root / 'science_data_kit' / 'ui' / 'app.py'
    
    if not app_path.exists():
        print(f"ERROR: Could not find app at {app_path}", file=sys.stderr)
        print("Please ensure the Science Data Kit is properly installed.", file=sys.stderr)
        sys.exit(1)
    
    print("Running Science Data Kit application...")
    
    # Run the streamlit app
    # This will replace the current process with the streamlit process
    os.execv(streamlit_path, [streamlit_path, 'run', str(app_path)] + sys.argv[1:])

def main():
    """Main entry point for the Science Data Kit CLI."""
    # Check if the environment is activated
    if not is_environment_activated():
        # If not, activate it
        activate_environment()
    
    # Run the Streamlit app
    run_streamlit_app()

if __name__ == "__main__":
    main()