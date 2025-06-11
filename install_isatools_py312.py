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
    """Check if Python 3.12 is available."""
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 12:
        return True, sys.executable
    
    # Try to find Python 3.12+
    python312_paths = ["python3.12", "python3.13", "python312", "python313"]
    for path in python312_paths:
        if shutil.which(path):
            return True, path
    
    return False, None

def main():
    print_color(GREEN, "ISA-Tools Installation Script for Python 3.12+")
    print("This script will install isatools from source with modifications to make it compatible with Python 3.12+.")
    print()
    
    # Check if Python 3.12+ is available
    has_python312, python312_path = check_python_version()
    if not has_python312:
        print_color(RED, "Error: Python 3.12 or higher is not installed or not in PATH.")
        print("Please install Python 3.12 or higher first.")
        print("You can download it from: https://www.python.org/downloads/")
        sys.exit(1)
    
    # Define the virtual environment path
    venv_path = Path.home() / ".venvs" / "isatools_py312_env"
    
    # Check if the virtual environment already exists
    if venv_path.exists():
        print_color(YELLOW, f"The virtual environment at {venv_path} already exists.")
        response = input("Do you want to update it? (y/n) ")
        if response.lower() != 'y':
            print("Installation aborted.")
            sys.exit(0)
        print("Updating existing environment...")
    else:
        print(f"Creating a new Python 3.12+ virtual environment at {venv_path}...")
        venv_path.parent.mkdir(parents=True, exist_ok=True)
        run_command(f"{python312_path} -m venv {venv_path}")
    
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
    
    # Install isatools dependencies (excluding mzml2isa)
    print("Installing isatools dependencies...")
    run_command(f"{pip_exe} install graphene==3.4.3 graphql-core==3.2.6 wheel~=0.43.0 setuptools~=77.0.3")
    run_command(f"{pip_exe} install numpy~=2.2.4 jsonschema~=4.23.0 pandas==2.2.3 openpyxl>=3.1.5 networkx~=3.4.2")
    run_command(f"{pip_exe} install lxml~=5.3.1 requests~=2.32.3 iso8601~=2.1.0 chardet~=5.2.0 jinja2~=3.1.4")
    run_command(f"{pip_exe} install beautifulsoup4~=4.13.3 biopython~=1.85 progressbar2~=4.4.2 deepdiff~=8.4.2")
    run_command(f"{pip_exe} install PyYAML~=6.0.2 bokeh~=3.4.2 certifi==2025.1.31 flake8==7.1.0 ddt==1.7.2")
    run_command(f"{pip_exe} install behave==1.2.6 httpretty==1.1.4 sure==2.0.1 coveralls~=4.0.1 rdflib~=7.0.0")
    run_command(f"{pip_exe} install SQLAlchemy==1.4.52 python-dateutil~=2.9.0.post0 Flask~=3.1.0 flask_sqlalchemy~=3.0.2")
    
    # Install isatools from the local repository with our modifications
    print("Installing isatools from the local repository with Python 3.12+ compatibility modifications...")
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
    print("This installation does not include the mzml2isa package, which is not compatible with Python 3.12+.")
    print("Some functionality related to mzML file processing will not be available.")
    print("If you need full mzML functionality, use the Python 3.9 environment with isatools[mzml] installed.")

if __name__ == "__main__":
    main()