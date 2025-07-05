#!/usr/bin/env python
"""
Science Data Kit (SDK) Installation Verification Script

This script verifies that the Science Data Kit is installed correctly and all
required dependencies are available. It checks for:
1. Core package imports
2. Optional package imports
3. Database connectivity (if configured)
4. File system access
5. Environment configuration

Usage:
    python verify.py [--verbose] [--check-db] [--check-optional]

Options:
    --verbose       Show detailed output for each check
    --check-db      Check database connectivity (requires configured database)
    --check-optional Check optional dependencies
"""

import argparse
import importlib
import os
import sys
import traceback
from typing import Dict, List, Tuple, Optional

# Define colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_status(message: str, status: str, color: str) -> None:
    """Print a status message with color."""
    print(f"{message:<60} [{color}{status}{RESET}]")

def check_import(module_name: str, verbose: bool = False) -> bool:
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        if verbose:
            print_status(f"Checking import: {module_name}", "OK", GREEN)
        return True
    except ImportError as e:
        if verbose:
            print_status(f"Checking import: {module_name}", "FAILED", RED)
            print(f"  Error: {str(e)}")
        return False
    except Exception as e:
        if verbose:
            print_status(f"Checking import: {module_name}", "ERROR", RED)
            print(f"  Unexpected error: {str(e)}")
        return False

def check_core_imports(verbose: bool = False) -> Tuple[int, int]:
    """Check all core package imports."""
    core_modules = [
        "science_data_kit",
        "science_data_kit.core",
        "science_data_kit.core.database",
        "science_data_kit.data_integration",
        "science_data_kit.analysis",
        "science_data_kit.visualization",
        "science_data_kit.export",
    ]
    
    success_count = 0
    total_count = len(core_modules)
    
    print(f"\n{BOLD}Checking core package imports:{RESET}")
    for module in core_modules:
        if check_import(module, verbose):
            success_count += 1
    
    return success_count, total_count

def check_optional_imports(verbose: bool = False) -> Dict[str, Tuple[int, int]]:
    """Check optional package imports by category."""
    optional_modules = {
        "msgraph": [
            "msgraph",
            "azure.identity",
        ],
        "dropbox": [
            "dropbox",
        ],
        "google": [
            "googleapiclient",
            "google.auth",
            "google_auth_oauthlib",
        ],
        "jupyter": [
            "IPython",
            "jupyter",
        ],
        "visualization": [
            "matplotlib",
            "PIL",
        ],
        "development": [
            "mypy",
            "black",
            "pytest",
            "sphinx",
        ]
    }
    
    results = {}
    
    print(f"\n{BOLD}Checking optional package imports:{RESET}")
    for category, modules in optional_modules.items():
        print(f"\n{category.capitalize()} modules:")
        success_count = 0
        total_count = len(modules)
        
        for module in modules:
            if check_import(module, verbose):
                success_count += 1
        
        results[category] = (success_count, total_count)
    
    return results

def check_database_connectivity(verbose: bool = False) -> bool:
    """Check database connectivity if configured."""
    print(f"\n{BOLD}Checking database connectivity:{RESET}")
    
    try:
        from science_data_kit.core.database import DatabaseManager
        
        # Try to load configuration from file
        config_file = "db_config.yaml"
        if os.path.exists(config_file):
            import yaml
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            if verbose:
                print(f"Found database configuration file: {config_file}")
            
            # Create database manager
            db_manager = DatabaseManager()
            
            # Try to connect to Neo4j if configured
            if 'neo4j' in config:
                uri = config['neo4j'].get('uri', 'bolt://localhost:7687')
                username = config['neo4j'].get('username', 'neo4j')
                password = config['neo4j'].get('password', '')
                
                if verbose:
                    print(f"Attempting to connect to Neo4j at {uri}")
                
                try:
                    db_manager.connect_to_neo4j(uri=uri, username=username, password=password)
                    connected = db_manager.test_connection()
                    if connected:
                        print_status("Neo4j database connection", "OK", GREEN)
                        return True
                    else:
                        print_status("Neo4j database connection", "FAILED", RED)
                        return False
                except Exception as e:
                    print_status("Neo4j database connection", "ERROR", RED)
                    if verbose:
                        print(f"  Error: {str(e)}")
                    return False
            else:
                print_status("Neo4j database configuration", "NOT FOUND", YELLOW)
                return False
        else:
            print_status(f"Database configuration file ({config_file})", "NOT FOUND", YELLOW)
            print("  Create a db_config.yaml file to enable database connectivity checks.")
            return False
    except ImportError:
        print_status("Database manager module", "NOT FOUND", RED)
        return False
    except Exception as e:
        print_status("Database connectivity check", "ERROR", RED)
        if verbose:
            print(f"  Error: {str(e)}")
            traceback.print_exc()
        return False

def check_file_system_access(verbose: bool = False) -> bool:
    """Check file system access for reading and writing."""
    print(f"\n{BOLD}Checking file system access:{RESET}")
    
    # Check if we can create a temporary file
    import tempfile
    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=True) as temp:
            temp.write("Science Data Kit verification test")
            temp.flush()
            
            # Read back the content
            temp.seek(0)
            content = temp.read()
            
            if content == "Science Data Kit verification test":
                print_status("File system write and read access", "OK", GREEN)
                return True
            else:
                print_status("File system write and read access", "FAILED", RED)
                if verbose:
                    print("  Content verification failed")
                return False
    except Exception as e:
        print_status("File system write and read access", "ERROR", RED)
        if verbose:
            print(f"  Error: {str(e)}")
        return False

def check_environment(verbose: bool = False) -> bool:
    """Check environment configuration."""
    print(f"\n{BOLD}Checking environment configuration:{RESET}")
    
    # Check Python version
    python_version = sys.version.split()[0]
    if verbose:
        print(f"Python version: {python_version}")
    
    major, minor, patch = map(int, python_version.split('.'))
    if major == 3 and minor >= 12:
        print_status("Python version (3.12+)", "OK", GREEN)
        python_version_ok = True
    else:
        print_status(f"Python version ({python_version})", "WARNING", YELLOW)
        print("  Science Data Kit is designed for Python 3.12+")
        python_version_ok = False
    
    # Check for virtual environment
    in_virtualenv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_virtualenv:
        print_status("Virtual environment", "DETECTED", GREEN)
        if verbose:
            print(f"  Virtual environment path: {sys.prefix}")
    else:
        print_status("Virtual environment", "NOT DETECTED", YELLOW)
        print("  It's recommended to install Science Data Kit in a virtual environment")
    
    return python_version_ok and in_virtualenv

def main():
    parser = argparse.ArgumentParser(description="Verify Science Data Kit installation")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--check-db", action="store_true", help="Check database connectivity")
    parser.add_argument("--check-optional", action="store_true", help="Check optional dependencies")
    args = parser.parse_args()
    
    print(f"{BOLD}Science Data Kit (SDK) Installation Verification{RESET}")
    print("=" * 60)
    
    # Check core imports
    core_success, core_total = check_core_imports(args.verbose)
    
    # Check optional imports if requested
    optional_results = {}
    if args.check_optional:
        optional_results = check_optional_imports(args.verbose)
    
    # Check database connectivity if requested
    db_success = False
    if args.check_db:
        db_success = check_database_connectivity(args.verbose)
    
    # Check file system access
    fs_success = check_file_system_access(args.verbose)
    
    # Check environment
    env_success = check_environment(args.verbose)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"{BOLD}Verification Summary:{RESET}")
    print(f"Core package imports: {core_success}/{core_total} successful")
    
    if args.check_optional:
        print("\nOptional package imports:")
        for category, (success, total) in optional_results.items():
            print(f"  {category.capitalize()}: {success}/{total} successful")
    
    if args.check_db:
        print(f"\nDatabase connectivity: {'Successful' if db_success else 'Failed'}")
    
    print(f"\nFile system access: {'Successful' if fs_success else 'Failed'}")
    print(f"Environment configuration: {'Optimal' if env_success else 'Suboptimal'}")
    
    # Overall status
    print("\n" + "=" * 60)
    if core_success == core_total and fs_success:
        print(f"{GREEN}{BOLD}Verification Status: PASSED{RESET}")
        print("Science Data Kit is installed correctly and ready to use.")
        if not env_success:
            print(f"{YELLOW}Note: Environment configuration is not optimal.{RESET}")
        if args.check_db and not db_success:
            print(f"{YELLOW}Note: Database connectivity check failed.{RESET}")
        return 0
    else:
        print(f"{RED}{BOLD}Verification Status: FAILED{RESET}")
        print("Science Data Kit installation has issues that need to be addressed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())