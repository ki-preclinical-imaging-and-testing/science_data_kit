#!/usr/bin/env python
import subprocess
import sys

def main():
    """Run mypy on the specified files or directories."""
    # Run mypy on the parallel_processing.py file
    result = subprocess.run(
        ["mypy", "science_data_kit/core/utils/parallel_processing.py"],
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