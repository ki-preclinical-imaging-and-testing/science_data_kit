"""
Run UI Pattern Standardization for Science Data Kit

This script runs the UI pattern standardization process to create standardized UI components and patterns.
"""

import os
import sys

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui_pattern_standardizer import UIPatternStandardizer

def main():
    """Run the UI pattern standardization process."""
    print("\n=== Running UI Pattern Standardization ===\n")

    # Create a UI pattern standardizer
    standardizer = UIPatternStandardizer()

    # Run the standardization process
    standardizer.run_standardization("science_data_kit/ui")

    print("\n=== UI Pattern Standardization Completed ===\n")
    print("The following files have been created or modified:")
    for file in standardizer.results["files_modified"]:
        print(f"- {file}")

    print("\nThe following UI patterns have been standardized:")
    for category, patterns in standardizer.results["standardized_patterns"].items():
        if isinstance(patterns, list):
            print(f"- {category}: {len(patterns)} patterns")
        elif isinstance(patterns, dict):
            total = sum(len(p) for p in patterns.values())
            print(f"- {category}: {total} patterns")

    print("\nSee the generated usage examples in science_data_kit/ui/docs/ui_pattern_examples.md")
    print("See the standardization report in science_data_kit/ui/tests/results/ui_pattern_standardization_report.json")

if __name__ == "__main__":
    main()
