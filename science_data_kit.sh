#!/bin/bash
# Science Data Kit Launcher
echo "Science Data Kit Environment Launcher"
echo "======================================"
echo "Launching main environment (Python 3.12+)"
echo ""

# Function to properly deactivate environments
deactivate_all() {
    # Deactivate conda if active
    if [ -n "$CONDA_DEFAULT_ENV" ]; then
        echo "Deactivating conda environment: $CONDA_DEFAULT_ENV"
        conda deactivate 2>/dev/null || true
    fi

    # Deactivate virtualenv if active
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "Deactivating virtual environment: $VIRTUAL_ENV"
        deactivate 2>/dev/null || true
    fi
}

if [ -d "science-data-kit-env" ]; then
    echo "Starting main environment..."
    deactivate_all
    source science-data-kit-env/bin/activate
    echo "Main environment active ($(python --version))"
    exec bash --rcfile <(echo "PS1='(science-data-kit) \u@\h:\w\$ '")
else
    echo "No environments found. Please run the installer first."
    exit 1
fi
