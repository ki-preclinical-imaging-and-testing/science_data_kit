"""
Test for file_models.py to verify that multiple imports don't cause errors.

This test simulates the Streamlit environment by importing the Folder class
multiple times and checking if it causes a "Class already defined" error.
"""

import importlib
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def test_multiple_imports():
    """Test that multiple imports of Folder class don't cause errors."""
    # First import
    from science_data_kit.core.models.file_models import Folder, File

    # Get the original class objects
    original_folder = Folder
    original_file = File

    # Force a reload of the module
    if 'science_data_kit.core.models.file_models' in sys.modules:
        importlib.reload(sys.modules['science_data_kit.core.models.file_models'])

    # Second import after reload
    from science_data_kit.core.models.file_models import Folder, File

    # Check that we got the same class objects
    assert Folder is original_folder, "Folder class changed after reload"
    assert File is original_file, "File class changed after reload"

    print("Test passed: Multiple imports of Folder and File classes don't cause errors")

if __name__ == "__main__":
    test_multiple_imports()
