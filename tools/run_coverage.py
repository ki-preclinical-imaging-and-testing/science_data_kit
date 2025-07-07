"""
Script to run tests with coverage reporting for the Science Data Kit.

This script runs pytest with coverage reporting, generating both terminal,
HTML, and XML reports. The HTML report provides a visual representation of
coverage that can be viewed in a browser, while the XML report can be used
for integration with CI tools.

Usage:
    python run_coverage.py

The script will:
1. Run all tests with coverage analysis
2. Generate a terminal report showing missing lines
3. Generate an HTML report in the 'coverage_html' directory
4. Generate an XML report as 'coverage.xml'

The coverage configuration is based on the settings in pyproject.toml.
"""

import os
import subprocess
import sys


def run_coverage():
    """Run tests with coverage and generate reports."""
    print("Running tests with coverage...")
    
    # Create directory for HTML reports if it doesn't exist
    os.makedirs("coverage_html", exist_ok=True)
    
    # Run pytest with coverage options
    cmd = [
        "pytest",
        "--cov=science_data_kit",
        "--cov-report=term-missing",
        "--cov-report=html:coverage_html",
        "--cov-report=xml:coverage.xml"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print("Errors:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
    
    # Check if coverage reports were generated
    if os.path.exists("coverage_html/index.html"):
        print("\nHTML coverage report generated in 'coverage_html/index.html'")
    else:
        print("\nWarning: HTML coverage report was not generated", file=sys.stderr)
    
    if os.path.exists("coverage.xml"):
        print("XML coverage report generated as 'coverage.xml'")
    else:
        print("Warning: XML coverage report was not generated", file=sys.stderr)
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_coverage())