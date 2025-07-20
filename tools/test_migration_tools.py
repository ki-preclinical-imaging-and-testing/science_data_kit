#!/usr/bin/env python3
"""
Test Script for Streamlit to Flask Migration Tools

This script tests the functionality of the Streamlit to Flask migration tools:
1. streamlit_to_flask_migration.py - Helps users migrate from Streamlit to Flask
2. remove_streamlit_dependencies.py - Removes Streamlit dependencies from requirements files
3. clean_streamlit_code.py - Cleans up Streamlit-specific code from Python files

Usage:
    python test_migration_tools.py [--test-dir TEST_DIR]

Options:
    --test-dir TEST_DIR    Directory to create test files in (default: ./test_migration)
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def create_test_files(test_dir):
    """
    Create test files for migration tools to process.
    
    Args:
        test_dir: Directory to create test files in
    """
    # Create test directory if it doesn't exist
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a requirements.txt file with Streamlit dependencies
    requirements_content = """
# Core dependencies
numpy==1.21.0
pandas==1.3.0
matplotlib==3.4.2

# Streamlit dependencies
streamlit==1.10.0
streamlit-aggrid==0.2.3
st-annotated-text==2.0.0

# Other dependencies
requests==2.26.0
pyyaml==6.0
"""
    
    with open(os.path.join(test_dir, "requirements.txt"), "w") as f:
        f.write(requirements_content)
    
    # Create a setup.py file with Streamlit dependencies
    setup_py_content = """
from setuptools import setup, find_packages

setup(
    name="science_data_kit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.2",
        "streamlit>=1.10.0",
        "streamlit-aggrid>=0.2.3",
        "st-annotated-text>=2.0.0",
        "requests>=2.26.0",
        "pyyaml>=6.0",
    ],
)
"""
    
    with open(os.path.join(test_dir, "setup.py"), "w") as f:
        f.write(setup_py_content)
    
    # Create a Streamlit configuration file
    streamlit_config_content = """
streamlit:
  server:
    port: 8501
    enableCORS: false
  theme:
    primaryColor: "#F63366"
    backgroundColor: "#FFFFFF"
    secondaryBackgroundColor: "#F0F2F6"
    textColor: "#262730"
    font: "sans serif"
"""
    
    with open(os.path.join(test_dir, "streamlit_config.yaml"), "w") as f:
        f.write(streamlit_config_content)
    
    # Create a Python file with Streamlit code
    streamlit_app_content = """
import streamlit as st
import pandas as pd
import numpy as np

def render_main_page():
    st.title("Science Data Kit")
    st.header("Welcome to the Science Data Kit")
    
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", ["Home", "Explore", "Connect", "About"])
    
    if page == "Home":
        render_home_page()
    elif page == "Explore":
        render_explore_page()
    elif page == "Connect":
        render_connect_page()
    elif page == "About":
        render_about_page()

def render_home_page():
    st.subheader("Home Page")
    st.write("This is the home page of the Science Data Kit.")
    
    # Create some sample data
    data = pd.DataFrame({
        'x': np.random.randn(100),
        'y': np.random.randn(100),
    })
    
    # Display a chart
    st.subheader("Sample Chart")
    st.scatter_chart(data)
    
    # Display a table
    st.subheader("Sample Table")
    st.dataframe(data)
    
    # Add a button
    if st.button("Click me"):
        st.success("Button clicked!")

def render_explore_page():
    st.subheader("Explore Page")
    st.write("This is the explore page of the Science Data Kit.")
    
    # Add a file uploader
    uploaded_file = st.file_uploader("Upload a file", type=["csv", "txt", "xlsx"])
    
    if uploaded_file is not None:
        st.success(f"File {uploaded_file.name} uploaded successfully!")
        
        # Display file contents
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
            st.dataframe(data)
        elif uploaded_file.name.endswith(".txt"):
            st.text(uploaded_file.read().decode())

def render_connect_page():
    st.subheader("Connect Page")
    st.write("This is the connect page of the Science Data Kit.")
    
    # Add a form
    with st.form("connection_form"):
        connection_type = st.selectbox("Connection Type", ["Database", "API", "File System"])
        connection_name = st.text_input("Connection Name")
        connection_url = st.text_input("Connection URL")
        
        submit_button = st.form_submit_button("Connect")
        
        if submit_button:
            st.success(f"Connected to {connection_name} ({connection_type})!")

def render_about_page():
    st.subheader("About Page")
    st.write("This is the about page of the Science Data Kit.")
    
    st.markdown('''
    ## Science Data Kit
    
    The Science Data Kit is a tool for scientific data analysis and visualization.
    
    ### Features
    
    - Data exploration
    - Data visualization
    - Data connection
    - Data analysis
    
    ### Contact
    
    For more information, contact us at info@example.com.
    ''')

if __name__ == "__main__":
    render_main_page()
"""
    
    with open(os.path.join(test_dir, "app.py"), "w") as f:
        f.write(streamlit_app_content)
    
    # Create a Python file with Streamlit imports but no usage
    streamlit_imports_content = """
import streamlit as st
import pandas as pd
import numpy as np

# This file only imports streamlit but doesn't use it
"""
    
    with open(os.path.join(test_dir, "imports_only.py"), "w") as f:
        f.write(streamlit_imports_content)
    
    print(f"Created test files in {test_dir}")


def test_streamlit_to_flask_migration(test_dir):
    """
    Test the streamlit_to_flask_migration.py script.
    
    Args:
        test_dir: Directory containing test files
    """
    print("\n=== Testing streamlit_to_flask_migration.py ===")
    
    # Test configuration conversion
    config_path = os.path.join(test_dir, "streamlit_config.yaml")
    output_path = os.path.join(test_dir, "migration_report.md")
    
    cmd = [
        sys.executable,
        "tools/streamlit_to_flask_migration.py",
        "--config", config_path,
        "--output", output_path
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ streamlit_to_flask_migration.py executed successfully")
        print(f"Output saved to {output_path}")
    else:
        print("❌ streamlit_to_flask_migration.py failed")
        print(f"Error: {result.stderr}")
    
    # Test code scanning
    cmd = [
        sys.executable,
        "tools/streamlit_to_flask_migration.py",
        "--scan-dir", test_dir,
        "--output", output_path
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ streamlit_to_flask_migration.py (scan) executed successfully")
        print(f"Output saved to {output_path}")
    else:
        print("❌ streamlit_to_flask_migration.py (scan) failed")
        print(f"Error: {result.stderr}")


def test_remove_streamlit_dependencies(test_dir):
    """
    Test the remove_streamlit_dependencies.py script.
    
    Args:
        test_dir: Directory containing test files
    """
    print("\n=== Testing remove_streamlit_dependencies.py ===")
    
    # Test with dry run
    requirements_path = os.path.join(test_dir, "requirements.txt")
    setup_path = os.path.join(test_dir, "setup.py")
    output_path = os.path.join(test_dir, "dependency_removal_report.md")
    
    cmd = [
        sys.executable,
        "tools/remove_streamlit_dependencies.py",
        "--dry-run",
        "--requirements", requirements_path,
        "--setup", setup_path,
        "--output", output_path
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ remove_streamlit_dependencies.py (dry run) executed successfully")
        print(f"Output saved to {output_path}")
    else:
        print("❌ remove_streamlit_dependencies.py (dry run) failed")
        print(f"Error: {result.stderr}")
    
    # Test actual run
    cmd = [
        sys.executable,
        "tools/remove_streamlit_dependencies.py",
        "--requirements", requirements_path,
        "--setup", setup_path,
        "--output", output_path
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ remove_streamlit_dependencies.py executed successfully")
        print(f"Output saved to {output_path}")
    else:
        print("❌ remove_streamlit_dependencies.py failed")
        print(f"Error: {result.stderr}")


def test_clean_streamlit_code(test_dir):
    """
    Test the clean_streamlit_code.py script.
    
    Args:
        test_dir: Directory containing test files
    """
    print("\n=== Testing clean_streamlit_code.py ===")
    
    # Test with dry run
    output_path = os.path.join(test_dir, "streamlit_cleanup_report.md")
    
    cmd = [
        sys.executable,
        "tools/clean_streamlit_code.py",
        "--dry-run",
        "--directory", test_dir,
        "--output", output_path
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ clean_streamlit_code.py (dry run) executed successfully")
        print(f"Output saved to {output_path}")
    else:
        print("❌ clean_streamlit_code.py (dry run) failed")
        print(f"Error: {result.stderr}")
    
    # Test actual run with backup
    cmd = [
        sys.executable,
        "tools/clean_streamlit_code.py",
        "--directory", test_dir,
        "--backup",
        "--output", output_path
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ clean_streamlit_code.py executed successfully")
        print(f"Output saved to {output_path}")
    else:
        print("❌ clean_streamlit_code.py failed")
        print(f"Error: {result.stderr}")


def main():
    parser = argparse.ArgumentParser(description="Test Script for Streamlit to Flask Migration Tools")
    parser.add_argument("--test-dir", default="./test_migration", help="Directory to create test files in")
    
    args = parser.parse_args()
    
    # Create test files
    create_test_files(args.test_dir)
    
    # Test each tool
    test_streamlit_to_flask_migration(args.test_dir)
    test_remove_streamlit_dependencies(args.test_dir)
    test_clean_streamlit_code(args.test_dir)
    
    print("\n=== All tests completed ===")
    print(f"Test files are in {args.test_dir}")
    print("You can examine the output files to verify the tools' functionality.")


if __name__ == "__main__":
    main()