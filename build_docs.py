#!/usr/bin/env python
import subprocess
import sys
import os

def main():
    """Build the Sphinx documentation."""
    # Change to the docs directory
    os.chdir('docs')
    
    # Run sphinx-build to generate the documentation
    result = subprocess.run(
        ["make", "html"],
        capture_output=True,
        text=True,
    )
    
    # Print the output
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    # Return the exit code
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())