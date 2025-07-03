#!/bin/bash
echo "Activating Science Data Kit main environment..."

# Deactivate any existing conda/virtual environments
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo "Deactivating conda environment: $CONDA_DEFAULT_ENV"
    conda deactivate 2>/dev/null || true
fi

if [ -n "$VIRTUAL_ENV" ]; then
    echo "Deactivating virtual environment: $VIRTUAL_ENV"
    deactivate 2>/dev/null || true
fi

# Activate our environment
if [ -f "science-data-kit-env/bin/activate" ]; then
    source science-data-kit-env/bin/activate
    echo "Main environment active ($(python --version))"
    echo "Available commands: science_data_kit, python, pip"
    echo "Type 'deactivate' to exit this environment"
else
    echo "Error: Main environment not found. Please run the installer."
    exit 1
fi
