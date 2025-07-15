"""
Test script to verify that the updated queries using elementId() work correctly
and don't produce deprecation warnings.

This is a simplified version that doesn't require an actual Neo4j connection.
It just verifies that the queries are correctly formed with elementId() instead of id().
"""

import os
import sys
import re
from pathlib import Path

# Function to check if a file contains any instances of id() in Cypher queries
def check_file_for_id_function(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Look for patterns like id(n), id(a), id(r), etc. in Cypher queries
    # This regex looks for id( followed by a single character and )
    matches = re.findall(r'id\([a-zA-Z]\)', content)

    if matches:
        print(f"Found {len(matches)} instances of id() function in {file_path}:")
        for match in matches:
            print(f"  - {match}")
        return False
    else:
        print(f"No instances of id() function found in {file_path}")
        return True

def test_files_for_id_function():
    """
    Test the relevant files to ensure they use elementId() instead of id().

    This function checks the key files that were modified to replace id() with elementId().
    """
    print("Testing files for id() function usage...")

    # Define the files to check
    files_to_check = [
        "science_data_kit/core/db/db_manager.py",
        "science_data_kit/core/db/relationship_manager.py",
        "science_data_kit/core/db/query_templates.py"
    ]

    # Check each file
    all_passed = True
    for file_path in files_to_check:
        print(f"\nChecking {file_path}...")
        if not check_file_for_id_function(file_path):
            all_passed = False

    if all_passed:
        print("\nAll files passed the check! No instances of id() function found.")
        return True
    else:
        print("\nSome files still contain instances of id() function.")
        return False

if __name__ == "__main__":
    test_files_for_id_function()
