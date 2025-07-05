"""
Installation verification script for Science Data Kit.

This script checks that all required components are properly installed and configured.
It verifies core dependencies, database connections, API functionality, UI components,
and sample data access.

Usage:
    python -m science_data_kit.verify

Returns:
    0 if all checks pass, non-zero otherwise
"""

import importlib
import os
import sys
import time
from typing import Dict, List, Tuple, Any, Optional

# Define colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_status(message: str, status: str, color: str) -> None:
    """Print a formatted status message."""
    print(f"{message:<60} [{color}{status}{RESET}]")

def check_python_version() -> bool:
    """Check if Python version is 3.8 or higher."""
    major, minor, *_ = sys.version_info
    if major < 3 or (major == 3 and minor < 8):
        print_status("Python version (3.8+ required)", 
                    f"{major}.{minor} (FAIL)", RED)
        return False
    print_status("Python version (3.8+ required)", 
                f"{major}.{minor} (PASS)", GREEN)
    return True

def check_dependencies() -> bool:
    """Check if all required dependencies are installed."""
    required_packages = [
        "numpy", "pandas", "streamlit", "neo4j", "plotly", 
        "scikit-learn", "matplotlib", "requests"
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            importlib.import_module(package)
            print_status(f"Required package: {package}", "PASS", GREEN)
        except ImportError:
            print_status(f"Required package: {package}", "FAIL", RED)
            all_installed = False
    
    return all_installed

def check_optional_dependencies() -> None:
    """Check if optional dependencies are installed."""
    optional_packages = [
        "torch", "tensorflow", "seaborn", "bokeh", "altair", 
        "statsmodels", "scipy", "jupyter"
    ]
    
    for package in optional_packages:
        try:
            importlib.import_module(package)
            print_status(f"Optional package: {package}", "PASS", GREEN)
        except ImportError:
            print_status(f"Optional package: {package}", "NOT FOUND", YELLOW)

def check_database_connection() -> bool:
    """Check if the Neo4j database connection is working."""
    try:
        from science_data_kit.core.database import get_database_connection
        
        # Try to get a database connection
        connection = get_database_connection()
        
        # Run a simple query to verify connection
        result = connection.run_query("RETURN 1 as test")
        if result and result[0]["test"] == 1:
            print_status("Neo4j database connection", "PASS", GREEN)
            return True
        else:
            print_status("Neo4j database connection", "FAIL", RED)
            return False
    except Exception as e:
        print_status("Neo4j database connection", "FAIL", RED)
        print(f"  Error: {str(e)}")
        return False

def check_api_functionality() -> bool:
    """Check if the API functionality is working."""
    try:
        from science_data_kit.core.api import test_api_connection
        
        # Test API connection
        if test_api_connection():
            print_status("API functionality", "PASS", GREEN)
            return True
        else:
            print_status("API functionality", "FAIL", RED)
            return False
    except Exception as e:
        print_status("API functionality", "FAIL", RED)
        print(f"  Error: {str(e)}")
        return False

def check_ui_components() -> bool:
    """Check if UI components are working."""
    try:
        import streamlit as st
        from science_data_kit.ui.components import test_ui_components
        
        # Test UI components
        if test_ui_components():
            print_status("UI components", "PASS", GREEN)
            return True
        else:
            print_status("UI components", "FAIL", RED)
            return False
    except Exception as e:
        print_status("UI components", "FAIL", RED)
        print(f"  Error: {str(e)}")
        return False

def check_sample_data() -> bool:
    """Check if sample data is accessible."""
    try:
        from science_data_kit.data.samples import check_sample_data_access
        
        # Check sample data access
        if check_sample_data_access():
            print_status("Sample data access", "PASS", GREEN)
            return True
        else:
            print_status("Sample data access", "FAIL", RED)
            return False
    except Exception as e:
        print_status("Sample data access", "FAIL", RED)
        print(f"  Error: {str(e)}")
        return False

def check_configuration() -> bool:
    """Check if configuration is properly set up."""
    try:
        from science_data_kit.core.config import get_config
        
        # Get configuration
        config = get_config()
        if config:
            print_status("Configuration", "PASS", GREEN)
            return True
        else:
            print_status("Configuration", "FAIL", RED)
            return False
    except Exception as e:
        print_status("Configuration", "FAIL", RED)
        print(f"  Error: {str(e)}")
        return False

def run_all_checks() -> bool:
    """Run all verification checks."""
    print(f"\n{BOLD}Science Data Kit Installation Verification{RESET}\n")
    print("Running verification checks...\n")
    
    # Core checks
    python_check = check_python_version()
    dependencies_check = check_dependencies()
    
    print("\nOptional Dependencies:")
    check_optional_dependencies()
    
    print("\nFunctionality Checks:")
    config_check = check_configuration()
    db_check = check_database_connection()
    api_check = check_api_functionality()
    ui_check = check_ui_components()
    data_check = check_sample_data()
    
    # Summary
    print("\nVerification Summary:")
    all_checks_passed = all([
        python_check, dependencies_check, config_check,
        db_check, api_check, ui_check, data_check
    ])
    
    if all_checks_passed:
        print(f"\n{GREEN}{BOLD}All checks passed! Your Science Data Kit installation is ready to use.{RESET}")
    else:
        print(f"\n{YELLOW}{BOLD}Some checks failed. Please review the issues above.{RESET}")
        print("For troubleshooting help, see the INSTALL.md file or visit our documentation.")
    
    return all_checks_passed

def main() -> int:
    """Main function to run the verification script."""
    try:
        all_passed = run_all_checks()
        return 0 if all_passed else 1
    except Exception as e:
        print(f"\n{RED}Error running verification: {str(e)}{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())