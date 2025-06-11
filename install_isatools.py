#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# ANSI colors for output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

def print_color(color, message):
    """Print a message with color."""
    print(f"{color}{message}{NC}")

def run_command(command, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, check=check, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
        return result
    except subprocess.CalledProcessError as e:
        print_color(RED, f"Error executing command: {command}")
        print(e.stderr)
        if check:
            sys.exit(1)
        return e

def check_python_version():
    """Check if Python 3.9 is available."""
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor == 9:
        return True, sys.executable
    
    # Try to find Python 3.9
    python39_paths = ["python3.9", "python39"]
    for path in python39_paths:
        if shutil.which(path):
            return True, path
    
    return False, None

def main():
    print_color(GREEN, "ISA-Tools Installation Script (Python Version)")
    print("This script will install isatools and its dependencies in a Python 3.9 virtual environment.")
    print()
    
    # Check if Python 3.9 is available
    has_python39, python39_path = check_python_version()
    if not has_python39:
        print_color(RED, "Error: Python 3.9 is not installed or not in PATH.")
        print("Please install Python 3.9 first.")
        print("You can download it from: https://www.python.org/downloads/")
        sys.exit(1)
    
    # Define the virtual environment path
    venv_path = Path.home() / ".venvs" / "isatools_env"
    
    # Check if the virtual environment already exists
    if venv_path.exists():
        print_color(YELLOW, f"The virtual environment at {venv_path} already exists.")
        response = input("Do you want to update it? (y/n) ")
        if response.lower() != 'y':
            print("Installation aborted.")
            sys.exit(0)
        print("Updating existing environment...")
    else:
        print(f"Creating a new Python 3.9 virtual environment at {venv_path}...")
        venv_path.parent.mkdir(parents=True, exist_ok=True)
        run_command(f"{python39_path} -m venv {venv_path}")
    
    # Determine the path to the Python and pip executables in the virtual environment
    if platform.system() == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    # Upgrade pip
    print("Upgrading pip...")
    run_command(f"{python_exe} -m pip install --upgrade pip")
    
    # Install the problematic dependencies first with specific versions
    print("Installing isatools dependencies...")
    run_command(f"{pip_exe} install mzml2isa==1.1.1")
    run_command(f"{pip_exe} install fastobo==0.13.0")
    run_command(f"{pip_exe} install SQLAlchemy==1.4.52")
    
    # Install isatools from the local repository
    print("Installing isatools from the local repository...")
    repo_path = Path.cwd() / "isa-api"
    if not repo_path.exists():
        print_color(RED, f"Error: isa-api repository not found at {repo_path}")
        print("Please clone the repository first:")
        print("git clone https://github.com/ISA-tools/isa-api.git")
        sys.exit(1)
    
    run_command(f"{pip_exe} install -e {repo_path}")
    
    print_color(GREEN, "Installation complete!")
    print()
    print("To use isatools, activate the virtual environment:")
    if platform.system() == "Windows":
        print_color(YELLOW, f"{venv_path}\\Scripts\\activate")
    else:
        print_color(YELLOW, f"source {venv_path}/bin/activate")
    print()
    print("You can then run Python scripts that import isatools.")
    print()
    print_color(YELLOW, "Note:") 
    print("The main application can still run with Python 3.12+ using the compatibility layer,")
    print("but for full isatools functionality, use the isatools_env environment.")

if __name__ == "__main__":
    main()