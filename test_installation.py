#!/usr/bin/env python
"""
Test script to verify that the Science Data Kit is installed correctly.
"""
import sys
import importlib
import subprocess
import os
from pathlib import Path

def check_module(module_name):
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def check_docker():
    """Check if Docker is running and if the Neo4j container is available."""
    try:
        # Check if Docker is running
        result = subprocess.run(
            ["docker", "info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        if result.returncode != 0:
            return False, "Docker is not running"
        
        # Check if Neo4j container is running
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=neo4j-instance"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        if "neo4j-instance" not in result.stdout:
            return False, "Neo4j container is not running"
        
        return True, "Docker and Neo4j container are running"
    except Exception as e:
        return False, f"Error checking Docker: {e}"

def check_db_config():
    """Check if the db_config.yaml file exists."""
    config_path = Path("db_config.yaml")
    if not config_path.exists():
        return False, "db_config.yaml file not found"
    return True, "db_config.yaml file found"

def check_isatools():
    """Check if isatools is installed."""
    try:
        import isatools
        return True, f"isatools version {isatools.__version__} is installed"
    except ImportError:
        return False, "isatools is not installed"

def main():
    """Run all tests."""
    print("Testing Science Data Kit installation...")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 10):
        print("ERROR: Python 3.10 or higher is required")
        sys.exit(1)
    
    # Check required modules
    required_modules = [
        "streamlit",
        "pandas",
        "neo4j",
        "docker",
        "numpy",
        "networkx",
        "app"
    ]
    
    all_modules_installed = True
    for module in required_modules:
        if check_module(module):
            print(f"✅ {module} is installed")
        else:
            print(f"❌ {module} is not installed")
            all_modules_installed = False
    
    # Check Docker and Neo4j
    docker_ok, docker_message = check_docker()
    if docker_ok:
        print(f"✅ {docker_message}")
    else:
        print(f"❌ {docker_message}")
    
    # Check db_config.yaml
    config_ok, config_message = check_db_config()
    if config_ok:
        print(f"✅ {config_message}")
    else:
        print(f"❌ {config_message}")
    
    # Check isatools (optional)
    isatools_ok, isatools_message = check_isatools()
    if isatools_ok:
        print(f"✅ {isatools_message}")
    else:
        print(f"ℹ️ {isatools_message} (optional)")
    
    # Summary
    if all_modules_installed and docker_ok and config_ok:
        print("\n✅ Science Data Kit is installed correctly!")
        print("You can start the application with: science_data_kit")
    else:
        print("\n❌ Some components are missing or not configured correctly.")
        print("Please check the error messages above and fix the issues.")

if __name__ == "__main__":
    main()