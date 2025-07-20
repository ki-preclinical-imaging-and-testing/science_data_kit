#!/usr/bin/env python3
"""
Streamlit to Flask Migration Helper

This script helps users migrate from the Streamlit version of the Science Data Kit
to the Flask version by:
1. Converting Streamlit configuration files to Flask format
2. Scanning for Streamlit imports and suggesting Flask alternatives
3. Checking for common Streamlit patterns and suggesting Flask equivalents
4. Providing a report of changes needed

Usage:
    python streamlit_to_flask_migration.py [--config CONFIG_PATH] [--scan-dir DIRECTORY]

Options:
    --config CONFIG_PATH    Path to the Streamlit configuration file
    --scan-dir DIRECTORY    Directory to scan for Streamlit imports and patterns
"""

import argparse
import os
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class StreamlitToFlaskMigration:
    """Helper class for migrating from Streamlit to Flask."""

    def __init__(self):
        self.streamlit_imports = [
            "import streamlit as st",
            "from streamlit",
            "import streamlit",
        ]
        self.streamlit_patterns = [
            r"st\.[a-zA-Z_]+\(",
            r"streamlit\.[a-zA-Z_]+\(",
        ]
        self.import_replacements = {
            "import streamlit as st": "from flask import Flask, render_template, request, jsonify",
            "from streamlit import": "from flask import",
            "import streamlit": "from flask import Flask",
            "from science_data_kit.ui.streamlit": "from science_data_kit.ui.flask",
        }
        self.pattern_replacements = {
            r"st\.title\((.*?)\)": r"<h1>\1</h1>",
            r"st\.header\((.*?)\)": r"<h2>\1</h2>",
            r"st\.subheader\((.*?)\)": r"<h3>\1</h3>",
            r"st\.text\((.*?)\)": r"<p>\1</p>",
            r"st\.markdown\((.*?)\)": r"{{ markdown(\1) }}",
            r"st\.sidebar\.": r"# Use Flask sidebar component: ",
            r"st\.button\((.*?)\)": r"<button type='button'>\1</button>",
            r"st\.checkbox\((.*?)\)": r"<input type='checkbox'> \1",
            r"st\.radio\((.*?), options=(.*?)\)": r"{% for option in \2 %}<input type='radio' name='\1'> {{ option }}{% endfor %}",
            r"st\.selectbox\((.*?), options=(.*?)\)": r"<select name='\1'>{% for option in \2 %}<option>{{ option }}</option>{% endfor %}</select>",
            r"st\.multiselect\((.*?), options=(.*?)\)": r"<select name='\1' multiple>{% for option in \2 %}<option>{{ option }}</option>{% endfor %}</select>",
            r"st\.slider\((.*?)\)": r"<input type='range' name='\1'>",
            r"st\.text_input\((.*?)\)": r"<input type='text' name='\1'>",
            r"st\.text_area\((.*?)\)": r"<textarea name='\1'></textarea>",
            r"st\.date_input\((.*?)\)": r"<input type='date' name='\1'>",
            r"st\.time_input\((.*?)\)": r"<input type='time' name='\1'>",
            r"st\.file_uploader\((.*?)\)": r"<input type='file' name='\1'>",
            r"st\.image\((.*?)\)": r"<img src='\1'>",
            r"st\.video\((.*?)\)": r"<video src='\1' controls></video>",
            r"st\.audio\((.*?)\)": r"<audio src='\1' controls></audio>",
            r"st\.balloons\(\)": r"# Flask doesn't have balloons, use JavaScript confetti",
            r"st\.progress\((.*?)\)": r"<div class='progress'><div class='progress-bar' style='width: \1%'></div></div>",
            r"st\.spinner\((.*?)\)": r"<div class='spinner'>\1</div>",
            r"st\.success\((.*?)\)": r"<div class='alert alert-success'>\1</div>",
            r"st\.info\((.*?)\)": r"<div class='alert alert-info'>\1</div>",
            r"st\.warning\((.*?)\)": r"<div class='alert alert-warning'>\1</div>",
            r"st\.error\((.*?)\)": r"<div class='alert alert-danger'>\1</div>",
            r"st\.exception\((.*?)\)": r"<div class='alert alert-danger'>\1</div>",
        }

    def convert_config(self, config_path: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Convert a Streamlit configuration file to Flask format.
        
        Args:
            config_path: Path to the Streamlit configuration file
            
        Returns:
            Tuple of (success, output_path, config_dict)
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if not config:
                return False, "", None
                
            # Create Flask config structure
            flask_config = {}
            
            # Convert Streamlit server settings to Flask
            if 'streamlit' in config and 'server' in config['streamlit']:
                flask_config['flask'] = {'server': {}}
                
                # Port
                if 'port' in config['streamlit']['server']:
                    flask_config['flask']['server']['port'] = config['streamlit']['server']['port']
                else:
                    flask_config['flask']['server']['port'] = 5000
                
                # Host
                flask_config['flask']['server']['host'] = "0.0.0.0"
                
                # Debug mode
                flask_config['flask']['server']['debug'] = False
            
            # Convert theme settings
            if 'streamlit' in config and 'theme' in config['streamlit']:
                if 'flask' not in flask_config:
                    flask_config['flask'] = {}
                
                flask_config['flask']['theme'] = {}
                
                # Primary color
                if 'primaryColor' in config['streamlit']['theme']:
                    flask_config['flask']['theme']['primary_color'] = config['streamlit']['theme']['primaryColor']
                
                # Background color
                if 'backgroundColor' in config['streamlit']['theme']:
                    flask_config['flask']['theme']['background_color'] = config['streamlit']['theme']['backgroundColor']
                
                # Secondary background color
                if 'secondaryBackgroundColor' in config['streamlit']['theme']:
                    flask_config['flask']['theme']['secondary_background_color'] = config['streamlit']['theme']['secondaryBackgroundColor']
                
                # Text color
                if 'textColor' in config['streamlit']['theme']:
                    flask_config['flask']['theme']['text_color'] = config['streamlit']['theme']['textColor']
                
                # Font
                if 'font' in config['streamlit']['theme']:
                    flask_config['flask']['theme']['font'] = config['streamlit']['theme']['font']
            
            # Preserve any other settings that might be useful
            for key, value in config.items():
                if key != 'streamlit':
                    flask_config[key] = value
            
            # Generate output path
            output_path = os.path.join(os.path.dirname(config_path), 'sdk_config.yaml')
            
            # Write the new config file
            with open(output_path, 'w') as f:
                yaml.dump(flask_config, f, default_flow_style=False)
            
            return True, output_path, flask_config
            
        except Exception as e:
            print(f"Error converting config: {e}")
            return False, "", None

    def scan_directory(self, directory: str) -> Dict[str, List[Tuple[str, int, str]]]:
        """
        Scan a directory for Streamlit imports and patterns.
        
        Args:
            directory: Directory to scan
            
        Returns:
            Dictionary with file paths as keys and lists of (type, line_number, line) as values
        """
        results = {}
        
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        file_results = self.scan_file(file_path)
                        if file_results:
                            results[file_path] = file_results
        except Exception as e:
            print(f"Error scanning directory: {e}")
        
        return results

    def scan_file(self, file_path: str) -> List[Tuple[str, int, str]]:
        """
        Scan a file for Streamlit imports and patterns.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            List of (type, line_number, line) tuples
        """
        results = []
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                # Check for imports
                for import_pattern in self.streamlit_imports:
                    if import_pattern in line:
                        results.append(("import", i + 1, line.strip()))
                        break
                
                # Check for patterns
                for pattern in self.streamlit_patterns:
                    if re.search(pattern, line):
                        results.append(("pattern", i + 1, line.strip()))
                        break
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")
        
        return results

    def suggest_replacements(self, scan_results: Dict[str, List[Tuple[str, int, str]]]) -> Dict[str, List[Tuple[str, int, str, str]]]:
        """
        Suggest replacements for Streamlit imports and patterns.
        
        Args:
            scan_results: Results from scan_directory
            
        Returns:
            Dictionary with file paths as keys and lists of (type, line_number, original, suggestion) as values
        """
        suggestions = {}
        
        for file_path, results in scan_results.items():
            file_suggestions = []
            
            for result_type, line_number, line in results:
                if result_type == "import":
                    # Find matching import replacement
                    for pattern, replacement in self.import_replacements.items():
                        if pattern in line:
                            suggestion = line.replace(pattern, replacement)
                            file_suggestions.append((result_type, line_number, line, suggestion))
                            break
                    else:
                        file_suggestions.append((result_type, line_number, line, "# TODO: Replace Streamlit import with Flask equivalent"))
                
                elif result_type == "pattern":
                    # Find matching pattern replacement
                    suggestion = line
                    for pattern, replacement in self.pattern_replacements.items():
                        suggestion = re.sub(pattern, replacement, suggestion)
                    
                    if suggestion != line:
                        file_suggestions.append((result_type, line_number, line, suggestion))
                    else:
                        file_suggestions.append((result_type, line_number, line, "# TODO: Replace Streamlit pattern with Flask equivalent"))
            
            if file_suggestions:
                suggestions[file_path] = file_suggestions
        
        return suggestions

    def generate_report(self, config_result: Tuple[bool, str, Optional[Dict]], suggestions: Dict[str, List[Tuple[str, int, str, str]]]) -> str:
        """
        Generate a report of the migration analysis.
        
        Args:
            config_result: Result from convert_config
            suggestions: Result from suggest_replacements
            
        Returns:
            Report as a string
        """
        report = []
        report.append("# Streamlit to Flask Migration Report")
        report.append("")
        
        # Config conversion section
        report.append("## Configuration Conversion")
        if config_result[0]:
            report.append(f"✅ Successfully converted configuration to: {config_result[1]}")
            report.append("")
            report.append("```yaml")
            report.append(yaml.dump(config_result[2], default_flow_style=False))
            report.append("```")
        else:
            report.append("❌ Failed to convert configuration")
        
        report.append("")
        
        # Code suggestions section
        report.append("## Code Migration Suggestions")
        
        if not suggestions:
            report.append("No Streamlit code found in the scanned directories.")
        else:
            total_files = len(suggestions)
            total_issues = sum(len(issues) for issues in suggestions.values())
            
            report.append(f"Found {total_issues} Streamlit references in {total_files} files.")
            report.append("")
            
            for file_path, file_suggestions in suggestions.items():
                report.append(f"### {file_path}")
                report.append("")
                
                for result_type, line_number, original, suggestion in file_suggestions:
                    report.append(f"Line {line_number} - {result_type.capitalize()}:")
                    report.append("```python")
                    report.append(f"# Original")
                    report.append(original)
                    report.append(f"# Suggested")
                    report.append(suggestion)
                    report.append("```")
                    report.append("")
        
        # Next steps section
        report.append("## Next Steps")
        report.append("")
        report.append("1. Review and apply the suggested configuration changes")
        report.append("2. Review and apply the suggested code changes")
        report.append("3. Test your application with the Flask implementation")
        report.append("4. Refer to the migration guide for more details: docs/guides/streamlit_to_flask_migration_guide.md")
        report.append("")
        report.append("For more help, please see the resources in the migration guide.")
        
        return "\n".join(report)

    def save_report(self, report: str, output_path: str = "migration_report.md") -> str:
        """
        Save the migration report to a file.
        
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
    parser = argparse.ArgumentParser(description="Streamlit to Flask Migration Helper")
    parser.add_argument("--config", help="Path to the Streamlit configuration file")
    parser.add_argument("--scan-dir", help="Directory to scan for Streamlit imports and patterns")
    parser.add_argument("--output", default="migration_report.md", help="Output path for the migration report")
    
    args = parser.parse_args()
    
    if not args.config and not args.scan_dir:
        parser.print_help()
        sys.exit(1)
    
    migration = StreamlitToFlaskMigration()
    
    # Convert config if provided
    config_result = (False, "", None)
    if args.config:
        print(f"Converting configuration file: {args.config}")
        config_result = migration.convert_config(args.config)
        if config_result[0]:
            print(f"Configuration converted successfully to: {config_result[1]}")
        else:
            print("Failed to convert configuration")
    
    # Scan directory if provided
    suggestions = {}
    if args.scan_dir:
        print(f"Scanning directory: {args.scan_dir}")
        scan_results = migration.scan_directory(args.scan_dir)
        print(f"Found Streamlit references in {len(scan_results)} files")
        
        print("Generating suggestions...")
        suggestions = migration.suggest_replacements(scan_results)
    
    # Generate and save report
    print("Generating migration report...")
    report = migration.generate_report(config_result, suggestions)
    report_path = migration.save_report(report, args.output)
    
    if report_path:
        print(f"Migration report saved to: {report_path}")
    else:
        print("Failed to save migration report")


if __name__ == "__main__":
    main()