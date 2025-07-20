#!/usr/bin/env python3
"""
Streamlit Dependency Removal Tool

This script helps remove Streamlit dependencies from the Science Data Kit codebase by:
1. Identifying Streamlit-related dependencies in requirements files
2. Removing or commenting out these dependencies
3. Updating setup.py to remove Streamlit dependencies
4. Generating a report of changes made

Usage:
    python remove_streamlit_dependencies.py [--dry-run] [--requirements REQUIREMENTS_FILE] [--setup SETUP_FILE]

Options:
    --dry-run               Show what would be changed without making actual changes
    --requirements FILE     Path to requirements.txt file (default: requirements.txt)
    --setup FILE            Path to setup.py file (default: setup.py)
"""

import argparse
import os
import re
import sys
from typing import List, Tuple, Dict


class StreamlitDependencyRemover:
    """Helper class for removing Streamlit dependencies from the codebase."""

    def __init__(self):
        self.streamlit_packages = [
            "streamlit",
            "streamlit-aggrid",
            "streamlit-authenticator",
            "streamlit-camera-input-live",
            "streamlit-card",
            "streamlit-chat",
            "streamlit-elements",
            "streamlit-extras",
            "streamlit-folium",
            "streamlit-image-comparison",
            "streamlit-jupyter",
            "streamlit-keyup",
            "streamlit-lottie",
            "streamlit-option-menu",
            "streamlit-plotly-events",
            "streamlit-toggle-switch",
            "streamlit-tree-select",
            "streamlit-webrtc",
            "st-annotated-text",
            "st-clickable-images",
            "st-pages",
            "st-paywall",
            "st-supabase-connection",
            "st-user-connections",
        ]
        self.changes_made = {
            "requirements": [],
            "setup": []
        }

    def process_requirements_file(self, file_path: str, dry_run: bool = False) -> List[Tuple[str, str]]:
        """
        Process a requirements file to remove Streamlit dependencies.
        
        Args:
            file_path: Path to the requirements file
            dry_run: If True, don't make actual changes
            
        Returns:
            List of (original_line, new_line) tuples representing changes
        """
        if not os.path.exists(file_path):
            print(f"Requirements file not found: {file_path}")
            return []
        
        changes = []
        new_content = []
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                original_line = line.strip()
                # Skip empty lines and comments
                if not original_line or original_line.startswith('#'):
                    new_content.append(line)
                    continue
                
                # Check if line contains a Streamlit package
                package_name = original_line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                if package_name.lower() in [p.lower() for p in self.streamlit_packages]:
                    # Comment out the line
                    new_line = f"# {line}"
                    changes.append((original_line, f"# {original_line}"))
                    new_content.append(new_line)
                else:
                    new_content.append(line)
            
            if not dry_run and changes:
                with open(file_path, 'w') as f:
                    f.writelines(new_content)
                print(f"Updated requirements file: {file_path}")
            
            return changes
            
        except Exception as e:
            print(f"Error processing requirements file {file_path}: {e}")
            return []

    def process_setup_py(self, file_path: str, dry_run: bool = False) -> List[Tuple[str, str]]:
        """
        Process setup.py to remove Streamlit dependencies.
        
        Args:
            file_path: Path to setup.py
            dry_run: If True, don't make actual changes
            
        Returns:
            List of (original_line, new_line) tuples representing changes
        """
        if not os.path.exists(file_path):
            print(f"Setup file not found: {file_path}")
            return []
        
        changes = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Look for install_requires section
            install_requires_pattern = r"install_requires\s*=\s*\[(.*?)\]"
            install_requires_match = re.search(install_requires_pattern, content, re.DOTALL)
            
            if not install_requires_match:
                print(f"Could not find install_requires section in {file_path}")
                return []
            
            install_requires_section = install_requires_match.group(1)
            new_install_requires_section = install_requires_section
            
            # Process each line in the install_requires section
            for package in self.streamlit_packages:
                # Look for the package with various quoting styles and version specifiers
                package_patterns = [
                    f'[\'"]({package})[\'"]',
                    f'[\'"]({package})(==|>=|<=)[0-9.]+[\'"]',
                ]
                
                for pattern in package_patterns:
                    matches = re.finditer(pattern, new_install_requires_section, re.IGNORECASE)
                    for match in matches:
                        original_text = match.group(0)
                        # Comment out the package
                        new_text = f"# {original_text}"
                        new_install_requires_section = new_install_requires_section.replace(original_text, new_text)
                        changes.append((original_text, new_text))
            
            # Replace the install_requires section in the content
            new_content = content.replace(install_requires_section, new_install_requires_section)
            
            if not dry_run and changes:
                with open(file_path, 'w') as f:
                    f.write(new_content)
                print(f"Updated setup file: {file_path}")
            
            return changes
            
        except Exception as e:
            print(f"Error processing setup file {file_path}: {e}")
            return []

    def find_all_requirements_files(self, start_dir: str = '.') -> List[str]:
        """
        Find all requirements files in the project.
        
        Args:
            start_dir: Directory to start searching from
            
        Returns:
            List of paths to requirements files
        """
        requirements_files = []
        
        for root, _, files in os.walk(start_dir):
            for file in files:
                if file == 'requirements.txt' or file.endswith('-requirements.txt'):
                    requirements_files.append(os.path.join(root, file))
        
        return requirements_files

    def generate_report(self, changes: Dict[str, List[Tuple[str, str]]], dry_run: bool) -> str:
        """
        Generate a report of changes made.
        
        Args:
            changes: Dictionary of changes made to each file type
            dry_run: Whether this was a dry run
            
        Returns:
            Report as a string
        """
        report = []
        report.append("# Streamlit Dependency Removal Report")
        report.append("")
        
        if dry_run:
            report.append("**DRY RUN** - No changes were made")
            report.append("")
        
        total_changes = sum(len(file_changes) for file_changes in changes.values())
        
        if total_changes == 0:
            report.append("No Streamlit dependencies found.")
            return "\n".join(report)
        
        report.append(f"Found and {'would remove' if dry_run else 'removed'} {total_changes} Streamlit dependencies.")
        report.append("")
        
        # Requirements file changes
        if changes['requirements']:
            report.append("## Requirements Files")
            report.append("")
            
            for file_path, file_changes in changes['requirements']:
                report.append(f"### {file_path}")
                report.append("")
                report.append("```diff")
                for original, new in file_changes:
                    report.append(f"- {original}")
                    report.append(f"+ {new}")
                report.append("```")
                report.append("")
        
        # Setup.py changes
        if changes['setup']:
            report.append("## Setup.py")
            report.append("")
            
            for file_path, file_changes in changes['setup']:
                report.append(f"### {file_path}")
                report.append("")
                report.append("```diff")
                for original, new in file_changes:
                    report.append(f"- {original}")
                    report.append(f"+ {new}")
                report.append("```")
                report.append("")
        
        # Next steps
        report.append("## Next Steps")
        report.append("")
        report.append("1. Review the changes to ensure no required dependencies were removed")
        report.append("2. Update any import statements in your code to use Flask instead of Streamlit")
        report.append("3. Test your application to ensure it works without Streamlit")
        report.append("4. Refer to the migration guide for more details: docs/guides/streamlit_to_flask_migration_guide.md")
        
        return "\n".join(report)

    def save_report(self, report: str, output_path: str = "dependency_removal_report.md") -> str:
        """
        Save the dependency removal report to a file.
        
        Args:
            report: Report string
            output_path: Path to save the report
            
        Returns:
            Path to the saved report
        """
        try:
            with open(output_path, 'w') as f:
                f.write(report)
            return output_path
        except Exception as e:
            print(f"Error saving report: {e}")
            return ""


def main():
    parser = argparse.ArgumentParser(description="Streamlit Dependency Removal Tool")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making actual changes")
    parser.add_argument("--requirements", help="Path to requirements.txt file (default: requirements.txt)")
    parser.add_argument("--setup", help="Path to setup.py file (default: setup.py)")
    parser.add_argument("--output", default="dependency_removal_report.md", help="Output path for the report")
    
    args = parser.parse_args()
    
    remover = StreamlitDependencyRemover()
    all_changes = {
        'requirements': [],
        'setup': []
    }
    
    # Process requirements files
    if args.requirements:
        requirements_files = [args.requirements]
    else:
        requirements_files = remover.find_all_requirements_files()
    
    for req_file in requirements_files:
        print(f"Processing requirements file: {req_file}")
        changes = remover.process_requirements_file(req_file, args.dry_run)
        if changes:
            all_changes['requirements'].append((req_file, changes))
    
    # Process setup.py
    setup_file = args.setup or 'setup.py'
    if os.path.exists(setup_file):
        print(f"Processing setup file: {setup_file}")
        changes = remover.process_setup_py(setup_file, args.dry_run)
        if changes:
            all_changes['setup'].append((setup_file, changes))
    
    # Generate and save report
    print("Generating dependency removal report...")
    report = remover.generate_report(all_changes, args.dry_run)
    report_path = remover.save_report(report, args.output)
    
    if report_path:
        print(f"Dependency removal report saved to: {report_path}")
    else:
        print("Failed to save dependency removal report")


if __name__ == "__main__":
    main()