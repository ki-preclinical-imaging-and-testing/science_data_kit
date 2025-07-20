#!/usr/bin/env python3
"""
Streamlit Code Cleanup Tool

This script helps clean up Streamlit-specific code from the Science Data Kit codebase by:
1. Identifying Python files with Streamlit imports and usage
2. Commenting out or removing Streamlit-specific code
3. Adding TODOs for manual review where needed
4. Generating a report of changes made

Usage:
    python clean_streamlit_code.py [--dry-run] [--directory DIR] [--backup]

Options:
    --dry-run           Show what would be changed without making actual changes
    --directory DIR     Directory to scan for Python files (default: current directory)
    --backup            Create backup files before making changes
"""

import argparse
import os
import re
import shutil
import sys
from typing import List, Tuple, Dict, Set


class StreamlitCodeCleaner:
    """Helper class for cleaning up Streamlit-specific code."""

    def __init__(self):
        self.streamlit_imports = [
            r"import\s+streamlit\s+as\s+st",
            r"from\s+streamlit\s+import\s+.*",
            r"import\s+streamlit",
        ]
        
        self.streamlit_patterns = [
            # Basic UI elements
            r"st\.(title|header|subheader|text|markdown|caption|code|latex)\s*\(",
            r"st\.(button|checkbox|radio|selectbox|multiselect|slider|select_slider)\s*\(",
            r"st\.(text_input|text_area|number_input|date_input|time_input)\s*\(",
            r"st\.file_uploader\s*\(",
            r"st\.color_picker\s*\(",
            r"st\.(image|audio|video)\s*\(",
            
            # Layout
            r"st\.(sidebar|columns|expander|container|empty)\s*\(",
            r"st\.beta_(columns|container|expander)\s*\(",
            
            # Progress and status
            r"st\.(progress|spinner|balloons|snow|error|warning|info|success|exception)\s*\(",
            
            # Data display
            r"st\.(dataframe|table|json|metric|pyplot|altair_chart|vega_lite_chart|plotly_chart|bokeh_chart|pydeck_chart|graphviz_chart)\s*\(",
            
            # Session state
            r"st\.session_state",
            
            # Caching
            r"st\.cache\s*\(",
            r"st\.cache_(data|resource)\s*\(",
            
            # Forms
            r"st\.form\s*\(",
            r"st\.form_submit_button\s*\(",
            
            # Other
            r"st\.(echo|help|experimental_rerun|experimental_memo|experimental_singleton)\s*\(",
            r"st\.set_page_config\s*\(",
            r"st\.stop\s*\(",
            r"st\.write\s*\(",
        ]
        
        self.streamlit_module_patterns = [
            r"streamlit\.(title|header|subheader|text|markdown|caption|code|latex)\s*\(",
            r"streamlit\.(button|checkbox|radio|selectbox|multiselect|slider|select_slider)\s*\(",
            r"streamlit\.(text_input|text_area|number_input|date_input|time_input)\s*\(",
            r"streamlit\.file_uploader\s*\(",
            r"streamlit\.color_picker\s*\(",
            r"streamlit\.(image|audio|video)\s*\(",
            r"streamlit\.(sidebar|columns|expander|container|empty)\s*\(",
            r"streamlit\.beta_(columns|container|expander)\s*\(",
            r"streamlit\.(progress|spinner|balloons|snow|error|warning|info|success|exception)\s*\(",
            r"streamlit\.(dataframe|table|json|metric|pyplot|altair_chart|vega_lite_chart|plotly_chart|bokeh_chart|pydeck_chart|graphviz_chart)\s*\(",
            r"streamlit\.session_state",
            r"streamlit\.cache\s*\(",
            r"streamlit\.cache_(data|resource)\s*\(",
            r"streamlit\.form\s*\(",
            r"streamlit\.form_submit_button\s*\(",
            r"streamlit\.(echo|help|experimental_rerun|experimental_memo|experimental_singleton)\s*\(",
            r"streamlit\.set_page_config\s*\(",
            r"streamlit\.stop\s*\(",
            r"streamlit\.write\s*\(",
        ]
        
        # Files to exclude from processing
        self.exclude_patterns = [
            r".*test.*\.py$",  # Test files
            r".*setup\.py$",   # Setup files
            r".*conf\.py$",    # Configuration files
        ]
        
        # Directories to exclude from processing
        self.exclude_dirs = [
            ".git",
            "__pycache__",
            "venv",
            "env",
            ".venv",
            ".env",
            "node_modules",
        ]

    def should_process_file(self, file_path: str) -> bool:
        """
        Check if a file should be processed.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file should be processed, False otherwise
        """
        # Check if file matches any exclude pattern
        for pattern in self.exclude_patterns:
            if re.match(pattern, file_path):
                return False
        
        return True

    def should_process_dir(self, dir_path: str) -> bool:
        """
        Check if a directory should be processed.
        
        Args:
            dir_path: Path to the directory
            
        Returns:
            True if the directory should be processed, False otherwise
        """
        dir_name = os.path.basename(dir_path)
        return dir_name not in self.exclude_dirs

    def find_python_files(self, directory: str) -> List[str]:
        """
        Find all Python files in a directory.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of paths to Python files
        """
        python_files = []
        
        for root, dirs, files in os.walk(directory):
            # Filter directories
            dirs[:] = [d for d in dirs if self.should_process_dir(os.path.join(root, d))]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    if self.should_process_file(file_path):
                        python_files.append(file_path)
        
        return python_files

    def has_streamlit_code(self, file_path: str) -> bool:
        """
        Check if a file contains Streamlit code.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file contains Streamlit code, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Streamlit imports
            for pattern in self.streamlit_imports:
                if re.search(pattern, content):
                    return True
            
            # Check for Streamlit patterns
            for pattern in self.streamlit_patterns + self.streamlit_module_patterns:
                if re.search(pattern, content):
                    return True
            
            return False
        except Exception as e:
            print(f"Error checking file {file_path}: {e}")
            return False

    def create_backup(self, file_path: str) -> bool:
        """
        Create a backup of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if backup was created successfully, False otherwise
        """
        backup_path = f"{file_path}.bak"
        try:
            shutil.copy2(file_path, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup of {file_path}: {e}")
            return False

    def process_file(self, file_path: str, dry_run: bool = False, create_backup: bool = False) -> Tuple[bool, List[Tuple[int, str, str]]]:
        """
        Process a file to clean up Streamlit code.
        
        Args:
            file_path: Path to the file
            dry_run: If True, don't make actual changes
            create_backup: If True, create a backup before making changes
            
        Returns:
            Tuple of (success, list of (line_number, original_line, new_line) tuples)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            changes = []
            new_lines = []
            
            # Track if we're in a Streamlit-specific function or class
            in_streamlit_block = False
            streamlit_block_indent = ""
            streamlit_block_start = 0
            
            for i, line in enumerate(lines):
                original_line = line
                new_line = line
                line_number = i + 1
                
                # Check if this line starts a Streamlit-specific function or class
                if re.search(r'def\s+render_\w+\s*\(', line) and not line.strip().startswith('#'):
                    # This might be a Streamlit render function
                    in_streamlit_block = True
                    streamlit_block_indent = re.match(r'^(\s*)', line).group(1)
                    streamlit_block_start = line_number
                
                # Check if we're exiting a Streamlit block
                if in_streamlit_block and line.strip() and not line.startswith(streamlit_block_indent):
                    in_streamlit_block = False
                
                # Process imports
                for pattern in self.streamlit_imports:
                    if re.search(pattern, line) and not line.strip().startswith('#'):
                        new_line = f"# {line}  # TODO: Replace with Flask imports\n"
                        changes.append((line_number, original_line.strip(), new_line.strip()))
                        break
                
                # Process Streamlit patterns
                if not line.strip().startswith('#'):  # Skip already commented lines
                    for pattern in self.streamlit_patterns + self.streamlit_module_patterns:
                        if re.search(pattern, line):
                            new_line = f"# {line}  # TODO: Replace with Flask equivalent\n"
                            changes.append((line_number, original_line.strip(), new_line.strip()))
                            break
                
                # If we're in a Streamlit block and haven't already commented this line
                if in_streamlit_block and new_line == original_line and not line.strip().startswith('#') and line.strip():
                    new_line = f"# {line}  # TODO: Convert to Flask route/template\n"
                    changes.append((line_number, original_line.strip(), new_line.strip()))
                
                new_lines.append(new_line)
            
            # Make changes if not a dry run
            if not dry_run and changes:
                if create_backup:
                    self.create_backup(file_path)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
            
            return True, changes
        
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return False, []

    def generate_report(self, results: Dict[str, List[Tuple[int, str, str]]], dry_run: bool) -> str:
        """
        Generate a report of changes made.
        
        Args:
            results: Dictionary mapping file paths to lists of changes
            dry_run: Whether this was a dry run
            
        Returns:
            Report as a string
        """
        report = []
        report.append("# Streamlit Code Cleanup Report")
        report.append("")
        
        if dry_run:
            report.append("**DRY RUN** - No changes were made")
            report.append("")
        
        total_files = len(results)
        total_changes = sum(len(changes) for changes in results.values())
        
        if total_files == 0:
            report.append("No files with Streamlit code were found.")
            return "\n".join(report)
        
        report.append(f"Processed {total_files} files with Streamlit code.")
        report.append(f"Made {total_changes} changes.")
        report.append("")
        
        # Sort files by number of changes (most changes first)
        sorted_files = sorted(results.items(), key=lambda x: len(x[1]), reverse=True)
        
        for file_path, changes in sorted_files:
            report.append(f"## {file_path}")
            report.append(f"Changes: {len(changes)}")
            report.append("")
            
            # Group changes by type
            imports = []
            patterns = []
            blocks = []
            
            for line_number, original, new in changes:
                if "Replace with Flask imports" in new:
                    imports.append((line_number, original, new))
                elif "Replace with Flask equivalent" in new:
                    patterns.append((line_number, original, new))
                elif "Convert to Flask route/template" in new:
                    blocks.append((line_number, original, new))
            
            # Report imports
            if imports:
                report.append("### Import Changes")
                report.append("")
                for line_number, original, new in imports:
                    report.append(f"Line {line_number}:")
                    report.append("```python")
                    report.append(f"# Original")
                    report.append(original)
                    report.append(f"# New")
                    report.append(new)
                    report.append("```")
                    report.append("")
            
            # Report pattern changes
            if patterns:
                report.append("### Pattern Changes")
                report.append("")
                for line_number, original, new in patterns:
                    report.append(f"Line {line_number}:")
                    report.append("```python")
                    report.append(f"# Original")
                    report.append(original)
                    report.append(f"# New")
                    report.append(new)
                    report.append("```")
                    report.append("")
            
            # Report block changes
            if blocks:
                report.append("### Block Changes")
                report.append("")
                report.append(f"Found {len(blocks)} lines in Streamlit-specific blocks that need to be converted to Flask routes/templates.")
                report.append("")
            
            report.append("---")
            report.append("")
        
        # Next steps
        report.append("## Next Steps")
        report.append("")
        report.append("1. Review the commented code and replace with Flask equivalents")
        report.append("2. Convert Streamlit render functions to Flask routes and templates")
        report.append("3. Test the application to ensure it works correctly")
        report.append("4. Remove any remaining Streamlit code that is no longer needed")
        report.append("5. Refer to the migration guide for more details: docs/guides/streamlit_to_flask_migration_guide.md")
        
        return "\n".join(report)

    def save_report(self, report: str, output_path: str = "streamlit_cleanup_report.md") -> str:
        """
        Save the cleanup report to a file.
        
        Args:
            report: Report string
            output_path: Path to save the report
            
        Returns:
            Path to the saved report
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            return output_path
        except Exception as e:
            print(f"Error saving report: {e}")
            return ""


def main():
    parser = argparse.ArgumentParser(description="Streamlit Code Cleanup Tool")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making actual changes")
    parser.add_argument("--directory", default=".", help="Directory to scan for Python files")
    parser.add_argument("--backup", action="store_true", help="Create backup files before making changes")
    parser.add_argument("--output", default="streamlit_cleanup_report.md", help="Output path for the report")
    
    args = parser.parse_args()
    
    cleaner = StreamlitCodeCleaner()
    
    print(f"Scanning directory: {args.directory}")
    python_files = cleaner.find_python_files(args.directory)
    print(f"Found {len(python_files)} Python files")
    
    # Filter files to only those with Streamlit code
    streamlit_files = []
    for file_path in python_files:
        if cleaner.has_streamlit_code(file_path):
            streamlit_files.append(file_path)
    
    print(f"Found {len(streamlit_files)} files with Streamlit code")
    
    # Process each file
    results = {}
    for file_path in streamlit_files:
        print(f"Processing file: {file_path}")
        success, changes = cleaner.process_file(file_path, args.dry_run, args.backup)
        if success and changes:
            results[file_path] = changes
    
    # Generate and save report
    print("Generating cleanup report...")
    report = cleaner.generate_report(results, args.dry_run)
    report_path = cleaner.save_report(report, args.output)
    
    if report_path:
        print(f"Cleanup report saved to: {report_path}")
    else:
        print("Failed to save cleanup report")
    
    print(f"Processed {len(results)} files with Streamlit code")
    total_changes = sum(len(changes) for changes in results.values())
    print(f"Made {total_changes} changes")


if __name__ == "__main__":
    main()