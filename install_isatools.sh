#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}ISA-Tools Installation Script${NC}"
echo "This script will install isatools and its dependencies in a Python 3.9 virtual environment."
echo

# Check if Python 3.9 is installed
if ! command -v python3.9 &> /dev/null; then
    echo -e "${RED}Error: Python 3.9 is not installed or not in PATH.${NC}"
    echo "Please install Python 3.9 first:"
    echo "https://www.python.org/downloads/"
    exit 1
fi

# Define the virtual environment path
VENV_PATH="$HOME/.venvs/isatools_env"

# Check if the virtual environment already exists
if [ -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}The isatools_env virtual environment already exists at $VENV_PATH.${NC}"
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation aborted."
        exit 0
    fi
    echo "Updating existing environment..."
else
    echo "Creating a new Python 3.9 virtual environment for isatools..."
    # Create the directory if it doesn't exist
    mkdir -p "$HOME/.venvs"
    # Create the virtual environment
    python3.9 -m venv "$VENV_PATH"
fi

echo "Activating isatools_env environment..."
source "$VENV_PATH/bin/activate"

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing isatools dependencies..."
# Install the problematic dependencies first with specific versions
pip install mzml2isa==1.1.1
pip install fastobo==0.13.0
pip install SQLAlchemy==1.4.52

echo "Installing isatools from the local repository..."
cd isa-api
pip install -e .
cd ..

echo -e "${GREEN}Installation complete!${NC}"
echo
echo "To use isatools, activate the environment with:"
echo -e "${YELLOW}source $VENV_PATH/bin/activate${NC}"
echo
echo "You can then run Python scripts that import isatools."
echo
echo -e "${YELLOW}Note:${NC} The main application can still run with Python 3.12+ using the compatibility layer,"
echo "but for full isatools functionality, use the isatools_env environment."
