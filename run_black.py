#!/usr/bin/env python
import subprocess
import sys

def main():
    """Run black on the specified files or directories."""
    # Run black on the science_data_kit directory
    result = subprocess.run(
        ["black", "--check", "science_data_kit"],
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