#!/bin/bash
echo "Activating Science Data Kit isatools environment..."

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
if [ -f "science-data-kit-isatools-env/bin/activate" ]; then
    source science-data-kit-isatools-env/bin/activate
    echo "isatools environment active ($(python --version))"
    echo "Available commands: isatools, python, pip"
    echo "Note: This environment is for isatools only. Use activate_main.sh for Science Data Kit."
    echo "Type 'deactivate' to exit this environment"
else
    echo "Error: isatools environment not found. Please run the installer."
    exit 1
fi
