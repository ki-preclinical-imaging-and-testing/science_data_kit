#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}ISA-Tools Installation Script${NC}"
echo "This script will install isatools and its dependencies in a Python 3.9 environment."
echo

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo -e "${RED}Error: conda is not installed or not in PATH.${NC}"
    echo "Please install Miniconda or Anaconda first:"
    echo "https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Check if the isatools_env environment already exists
if conda env list | grep -q "^isatools_env "; then
    echo -e "${YELLOW}The isatools_env environment already exists.${NC}"
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation aborted."
        exit 0
    fi
    echo "Updating existing environment..."
else
    echo "Creating a new Python 3.9 environment for isatools..."
    conda create -y -n isatools_env python=3.9
fi

echo "Activating isatools_env environment..."
# We need to source the conda.sh script to use conda activate in a script
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate isatools_env

echo "Installing isatools dependencies..."
# Install the problematic dependencies first with specific versions
conda install -y -c conda-forge mzml2isa=1.1.1
conda install -y -c conda-forge fastobo=0.13.0
conda install -y -c conda-forge sqlalchemy=1.4.52

echo "Installing isatools from the local repository..."
cd isa-api
pip install -e .
cd ..

echo -e "${GREEN}Installation complete!${NC}"
echo
echo "To use isatools, activate the environment with:"
echo -e "${YELLOW}conda activate isatools_env${NC}"
echo
echo "You can then run Python scripts that import isatools."
echo
echo -e "${YELLOW}Note:${NC} The main application can still run with Python 3.12+ using the compatibility layer,"
echo "but for full isatools functionality, use the isatools_env environment."