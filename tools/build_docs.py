#!/usr/bin/env python
import subprocess
import sys
import os

def main():
    """Build the Sphinx documentation."""
    # Determine the location of the script and adjust the path to the docs directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == 'tools' else os.getcwd()
    docs_dir = os.path.join(project_root, 'docs')

    # Change to the docs directory
    os.chdir(docs_dir)

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
