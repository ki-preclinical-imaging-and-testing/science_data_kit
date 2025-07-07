"""
Visual Design Audit for Science Data Kit

This module provides functions for auditing the visual design consistency across the Science Data Kit application.
It focuses on identifying inconsistencies in colors, typography, spacing, and other visual elements.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import io
import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test result constants
PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARNING = "⚠️ WARNING"
NOT_TESTED = "❓ NOT TESTED"

class VisualDesignAuditor:
    """
    Class for auditing visual design consistency across the Science Data Kit application.
    """

    def __init__(self):
        """Initialize the VisualDesignAuditor."""
        self.results = {}
        self.current_audit = None
        self.audit_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Initialize results structure
        self.results = {
            "audit_info": {
                "timestamp": self.audit_timestamp,
                "auditor": "AI-Human Collaboration",
                "environment": {
                    "os": os.name,
                    "python_version": sys.version
                }
            },
            "audits": {},
            "inconsistencies": []
        }

    def start_audit(self, audit_name: str, description: str) -> None:
        """
        Start a new visual design audit.

        Args:
            audit_name: The name of the audit
            description: A description of the audit
        """
        self.current_audit = audit_name
        self.results["audits"][audit_name] = {
            "description": description,
            "elements": [],
            "status": NOT_TESTED,
            "notes": ""
        }

        print(f"\n=== Starting Visual Design Audit: {audit_name} ===")
        print(f"Description: {description}")
        print()

    def record_element(self, element_type: str, element_id: str, properties: Dict[str, Any]) -> None:
        """
        Record a visual element for the current audit.

        Args:
            element_type: The type of element (e.g., "button", "text", "chart")
            element_id: A unique identifier for the element
            properties: A dictionary of visual properties for the element
        """
        if self.current_audit is None:
            raise ValueError("No audit has been started. Call start_audit() first.")

        element = {
            "type": element_type,
            "id": element_id,
            "properties": properties
        }

        self.results["audits"][self.current_audit]["elements"].append(element)

        print(f"Recorded {element_type}: {element_id}")
        for prop, value in properties.items():
            print(f"  {prop}: {value}")
        print()

    def record_inconsistency(self, element_type: str, property_name: str, values: List[Any], elements: List[str], severity: str = "Medium") -> None:
        """
        Record a visual design inconsistency.

        Args:
            element_type: The type of element with the inconsistency
            property_name: The name of the property with inconsistent values
            values: The different values found for the property
            elements: The elements with inconsistent values
            severity: The severity of the inconsistency (Critical, High, Medium, Low)
        """
        if self.current_audit is None:
            raise ValueError("No audit has been started. Call start_audit() first.")

        inconsistency = {
            "audit": self.current_audit,
            "element_type": element_type,
            "property": property_name,
            "values": values,
            "elements": elements,
            "severity": severity,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.results["inconsistencies"].append(inconsistency)

        print(f"⚠️ Visual Inconsistency Detected - {element_type}.{property_name}")
        print(f"Values: {values}")
        print(f"Elements: {elements}")
        print(f"Severity: {severity}")
        print()

    def analyze_consistency(self, element_type: str = None, property_name: str = None) -> None:
        """
        Analyze the consistency of visual elements in the current audit.

        Args:
            element_type: Optional filter for element type
            property_name: Optional filter for property name
        """
        if self.current_audit is None:
            raise ValueError("No audit has been started. Call start_audit() first.")

        elements = self.results["audits"][self.current_audit]["elements"]

        # Filter elements if element_type is specified
        if element_type:
            elements = [e for e in elements if e["type"] == element_type]

        # Group elements by type
        elements_by_type = defaultdict(list)
        for element in elements:
            elements_by_type[element["type"]].append(element)

        # For each element type, check consistency of each property
        for type_name, type_elements in elements_by_type.items():
            # Skip if no elements of this type
            if not type_elements:
                continue

            # Get all property names for this element type
            all_properties = set()
            for element in type_elements:
                all_properties.update(element["properties"].keys())

            # Filter properties if property_name is specified
            if property_name:
                all_properties = [p for p in all_properties if p == property_name]

            # Check consistency for each property
            for prop in all_properties:
                # Get all values for this property
                values = {}
                for element in type_elements:
                    if prop in element["properties"]:
                        value = element["properties"][prop]
                        # Convert value to string for comparison
                        value_str = str(value)
                        if value_str not in values:
                            values[value_str] = []
                        values[value_str].append(element["id"])

                # If more than one value, record inconsistency
                if len(values) > 1:
                    # Determine severity based on property and number of inconsistencies
                    severity = "Low"
                    if prop in ["color", "font-family", "font-size"]:
                        severity = "Medium"
                    if prop in ["color", "font-family"] and len(values) > 2:
                        severity = "High"

                    self.record_inconsistency(
                        type_name,
                        prop,
                        list(values.keys()),
                        [item for sublist in values.values() for item in sublist],
                        severity
                    )

    def end_audit(self, notes: str = "") -> Dict[str, Any]:
        """
        End the current audit and calculate results.

        Args:
            notes: Additional notes about the audit

        Returns:
            Dictionary containing audit results
        """
        if self.current_audit is None:
            raise ValueError("No audit has been started. Call start_audit() first.")

        audit_data = self.results["audits"][self.current_audit]

        # Count inconsistencies for this audit
        inconsistencies = [i for i in self.results["inconsistencies"] if i["audit"] == self.current_audit]

        # Determine status based on inconsistencies
        if any(i["severity"] == "Critical" for i in inconsistencies):
            audit_data["status"] = FAIL
        elif any(i["severity"] == "High" for i in inconsistencies):
            audit_data["status"] = WARNING
        elif inconsistencies:
            audit_data["status"] = WARNING
        else:
            audit_data["status"] = PASS

        audit_data["notes"] = notes

        # Print summary
        print(f"\n=== Visual Design Audit Completed: {self.current_audit} ===")
        print(f"Status: {audit_data['status']}")
        print(f"Elements Audited: {len(audit_data['elements'])}")
        print(f"Inconsistencies Found: {len(inconsistencies)}")
        if notes:
            print(f"Notes: {notes}")
        print()

        current_audit = self.current_audit
        self.current_audit = None

        return self.results["audits"][current_audit]

    def generate_audit_report(self, output_file: str = None) -> pd.DataFrame:
        """
        Generate a report of the audit results.

        Args:
            output_file: Optional file path to save the report as CSV

        Returns:
            DataFrame containing the audit results
        """
        # Create a list to hold all audit results
        all_results = []

        # Iterate through all audits
        for audit_name, audit_data in self.results["audits"].items():
            # Count inconsistencies for this audit
            inconsistencies = [i for i in self.results["inconsistencies"] if i["audit"] == audit_name]

            all_results.append({
                "Audit": audit_name,
                "Description": audit_data["description"],
                "Status": audit_data["status"],
                "Elements Audited": len(audit_data["elements"]),
                "Inconsistencies Found": len(inconsistencies),
                "Notes": audit_data["notes"]
            })

        # Create a DataFrame from the results
        df = pd.DataFrame(all_results)

        # Save to file if specified
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Audit report saved to {output_file}")

        return df

    def generate_inconsistencies_report(self, output_file: str = None) -> pd.DataFrame:
        """
        Generate a report of the visual design inconsistencies.

        Args:
            output_file: Optional file path to save the report as CSV

        Returns:
            DataFrame containing the inconsistencies
        """
        # Create a DataFrame from the inconsistencies
        df = pd.DataFrame(self.results["inconsistencies"])

        # Save to file if specified
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Inconsistencies report saved to {output_file}")

        return df

    def generate_style_guide(self, output_file: str = None) -> Dict[str, Any]:
        """
        Generate a style guide based on the most common values for each property.

        Args:
            output_file: Optional file path to save the style guide as JSON

        Returns:
            Dictionary containing the style guide
        """
        # Create a dictionary to hold the style guide
        style_guide = {}

        # Iterate through all audits and elements
        all_elements = []
        for audit_data in self.results["audits"].values():
            all_elements.extend(audit_data["elements"])

        # Group elements by type
        elements_by_type = defaultdict(list)
        for element in all_elements:
            elements_by_type[element["type"]].append(element)

        # For each element type, find the most common value for each property
        for type_name, type_elements in elements_by_type.items():
            style_guide[type_name] = {}

            # Get all property names for this element type
            all_properties = set()
            for element in type_elements:
                all_properties.update(element["properties"].keys())

            # Find the most common value for each property
            for prop in all_properties:
                # Get all values for this property
                values = defaultdict(int)
                for element in type_elements:
                    if prop in element["properties"]:
                        value = element["properties"][prop]
                        # Convert value to string for counting
                        value_str = str(value)
                        values[value_str] += 1

                # Find the most common value
                if values:
                    most_common_value = max(values.items(), key=lambda x: x[1])[0]
                    style_guide[type_name][prop] = most_common_value

        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(style_guide, f, indent=2)
            print(f"Style guide saved to {output_file}")

        return style_guide

def audit_color_consistency(auditor: VisualDesignAuditor, ui_directory: str) -> None:
    """
    Audit color consistency across the application.

    Args:
        auditor: The VisualDesignAuditor instance
        ui_directory: The directory containing UI code
    """
    auditor.start_audit(
        "Color Consistency",
        "Audit the consistency of colors used across the application"
    )

    # Define color patterns to search for
    color_patterns = [
        r'color\s*=\s*[\'"]([^\'"]+)[\'"]',  # color="value"
        r'color\s*=\s*([a-zA-Z0-9_]+)',  # color=variable
        r'background_color\s*=\s*[\'"]([^\'"]+)[\'"]',  # background_color="value"
        r'background_color\s*=\s*([a-zA-Z0-9_]+)',  # background_color=variable
        r'fill_color\s*=\s*[\'"]([^\'"]+)[\'"]',  # fill_color="value"
        r'fill_color\s*=\s*([a-zA-Z0-9_]+)',  # fill_color=variable
        r'plt\.cm\.([a-zA-Z0-9_]+)',  # plt.cm.colormap
        r'cmap\s*=\s*[\'"]([^\'"]+)[\'"]',  # cmap="value"
        r'cmap\s*=\s*([a-zA-Z0-9_]+)'  # cmap=variable
    ]

    # Walk through the UI directory and search for color definitions
    for root, dirs, files in os.walk(ui_directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                    # Search for color definitions
                    for pattern in color_patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            color_value = match.group(1)
                            element_id = f"{file}:{match.start()}"

                            # Record the color element
                            auditor.record_element(
                                "color",
                                element_id,
                                {
                                    "value": color_value,
                                    "file": file,
                                    "line": content.count('\n', 0, match.start()) + 1,
                                    "context": content[max(0, match.start() - 50):match.end() + 50]
                                }
                            )
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")

    # Analyze color consistency
    auditor.analyze_consistency("color", "value")

    # End the audit
    auditor.end_audit("Color consistency is important for a cohesive user experience")

def audit_typography_consistency(auditor: VisualDesignAuditor, ui_directory: str) -> None:
    """
    Audit typography consistency across the application.

    Args:
        auditor: The VisualDesignAuditor instance
        ui_directory: The directory containing UI code
    """
    auditor.start_audit(
        "Typography Consistency",
        "Audit the consistency of typography used across the application"
    )

    # Define typography patterns to search for
    typography_patterns = [
        r'font_size\s*=\s*(\d+)',  # font_size=value
        r'fontsize\s*=\s*(\d+)',  # fontsize=value
        r'font_family\s*=\s*[\'"]([^\'"]+)[\'"]',  # font_family="value"
        r'fontfamily\s*=\s*[\'"]([^\'"]+)[\'"]',  # fontfamily="value"
        r'font_weight\s*=\s*[\'"]([^\'"]+)[\'"]',  # font_weight="value"
        r'fontweight\s*=\s*[\'"]([^\'"]+)[\'"]',  # fontweight="value"
        r'text_align\s*=\s*[\'"]([^\'"]+)[\'"]',  # text_align="value"
        r'textalign\s*=\s*[\'"]([^\'"]+)[\'"]',  # textalign="value"
        r'st\.markdown\(\s*[\'"]<[^>]*style\s*=\s*[\'"]([^\'"]+)[\'"]',  # st.markdown with style
        r'st\.write\(\s*[\'"]<[^>]*style\s*=\s*[\'"]([^\'"]+)[\'"]'  # st.write with style
    ]

    # Walk through the UI directory and search for typography definitions
    for root, dirs, files in os.walk(ui_directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                    # Search for typography definitions
                    for pattern in typography_patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            typography_value = match.group(1)
                            element_id = f"{file}:{match.start()}"

                            # Determine the property type
                            property_type = "unknown"
                            if "font_size" in pattern or "fontsize" in pattern:
                                property_type = "font-size"
                            elif "font_family" in pattern or "fontfamily" in pattern:
                                property_type = "font-family"
                            elif "font_weight" in pattern or "fontweight" in pattern:
                                property_type = "font-weight"
                            elif "text_align" in pattern or "textalign" in pattern:
                                property_type = "text-align"
                            elif "style" in pattern:
                                # Parse CSS style string
                                style_parts = typography_value.split(';')
                                for part in style_parts:
                                    if ':' in part:
                                        prop, val = part.split(':', 1)
                                        prop = prop.strip()
                                        val = val.strip()

                                        # Record each CSS property separately
                                        if prop in ["font-size", "font-family", "font-weight", "text-align"]:
                                            auditor.record_element(
                                                "typography",
                                                f"{element_id}:{prop}",
                                                {
                                                    "property": prop,
                                                    "value": val,
                                                    "file": file,
                                                    "line": content.count('\n', 0, match.start()) + 1,
                                                    "context": content[max(0, match.start() - 50):match.end() + 50]
                                                }
                                            )
                                continue

                            # Record the typography element
                            auditor.record_element(
                                "typography",
                                element_id,
                                {
                                    "property": property_type,
                                    "value": typography_value,
                                    "file": file,
                                    "line": content.count('\n', 0, match.start()) + 1,
                                    "context": content[max(0, match.start() - 50):match.end() + 50]
                                }
                            )
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")

    # Analyze typography consistency
    auditor.analyze_consistency("typography", "property")

    # End the audit
    auditor.end_audit("Typography consistency is important for readability and visual harmony")

def audit_spacing_consistency(auditor: VisualDesignAuditor, ui_directory: str) -> None:
    """
    Audit spacing consistency across the application.

    Args:
        auditor: The VisualDesignAuditor instance
        ui_directory: The directory containing UI code
    """
    auditor.start_audit(
        "Spacing Consistency",
        "Audit the consistency of spacing used across the application"
    )

    # Define spacing patterns to search for
    spacing_patterns = [
        r'padding\s*=\s*(\d+)',  # padding=value
        r'margin\s*=\s*(\d+)',  # margin=value
        r'gap\s*=\s*(\d+)',  # gap=value
        r'st\.markdown\(\s*[\'"]<[^>]*padding\s*:\s*([^;]+)',  # padding in markdown
        r'st\.markdown\(\s*[\'"]<[^>]*margin\s*:\s*([^;]+)',  # margin in markdown
        r'st\.markdown\(\s*[\'"]<[^>]*gap\s*:\s*([^;]+)'  # gap in markdown
    ]

    # Walk through the UI directory and search for spacing definitions
    for root, dirs, files in os.walk(ui_directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                    # Search for spacing definitions
                    for pattern in spacing_patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            spacing_value = match.group(1)
                            element_id = f"{file}:{match.start()}"

                            # Determine the property type
                            property_type = "unknown"
                            if "padding" in pattern:
                                property_type = "padding"
                            elif "margin" in pattern:
                                property_type = "margin"
                            elif "gap" in pattern:
                                property_type = "gap"

                            # Record the spacing element
                            auditor.record_element(
                                "spacing",
                                element_id,
                                {
                                    "property": property_type,
                                    "value": spacing_value,
                                    "file": file,
                                    "line": content.count('\n', 0, match.start()) + 1,
                                    "context": content[max(0, match.start() - 50):match.end() + 50]
                                }
                            )
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")

    # Analyze spacing consistency
    auditor.analyze_consistency("spacing")

    # End the audit
    auditor.end_audit("Spacing consistency is important for visual rhythm and layout harmony")

def audit_component_styling_consistency(auditor: VisualDesignAuditor, ui_directory: str) -> None:
    """
    Audit component styling consistency across the application.

    Args:
        auditor: The VisualDesignAuditor instance
        ui_directory: The directory containing UI code
    """
    auditor.start_audit(
        "Component Styling Consistency",
        "Audit the consistency of styling for common components"
    )

    # Define component patterns to search for
    component_patterns = [
        (r'st\.button\(([^)]+)', "button"),
        (r'st\.selectbox\(([^)]+)', "selectbox"),
        (r'st\.multiselect\(([^)]+)', "multiselect"),
        (r'st\.slider\(([^)]+)', "slider"),
        (r'st\.text_input\(([^)]+)', "text_input"),
        (r'st\.text_area\(([^)]+)', "text_area"),
        (r'st\.checkbox\(([^)]+)', "checkbox"),
        (r'st\.radio\(([^)]+)', "radio"),
        (r'st\.date_input\(([^)]+)', "date_input"),
        (r'st\.time_input\(([^)]+)', "time_input"),
        (r'st\.file_uploader\(([^)]+)', "file_uploader"),
        (r'st\.color_picker\(([^)]+)', "color_picker"),
        (r'st\.metric\(([^)]+)', "metric"),
        (r'st\.dataframe\(([^)]+)', "dataframe"),
        (r'st\.table\(([^)]+)', "table"),
        (r'st\.json\(([^)]+)', "json"),
        (r'st\.pyplot\(([^)]+)', "pyplot"),
        (r'st\.altair_chart\(([^)]+)', "altair_chart"),
        (r'st\.vega_lite_chart\(([^)]+)', "vega_lite_chart"),
        (r'st\.plotly_chart\(([^)]+)', "plotly_chart"),
        (r'st\.bokeh_chart\(([^)]+)', "bokeh_chart"),
        (r'st\.pydeck_chart\(([^)]+)', "pydeck_chart"),
        (r'st\.graphviz_chart\(([^)]+)', "graphviz_chart"),
        (r'st\.map\(([^)]+)', "map"),
        (r'st\.image\(([^)]+)', "image"),
        (r'st\.audio\(([^)]+)', "audio"),
        (r'st\.video\(([^)]+)', "video"),
        (r'st\.markdown\(([^)]+)', "markdown"),
        (r'st\.caption\(([^)]+)', "caption"),
        (r'st\.code\(([^)]+)', "code"),
        (r'st\.latex\(([^)]+)', "latex"),
        (r'st\.title\(([^)]+)', "title"),
        (r'st\.header\(([^)]+)', "header"),
        (r'st\.subheader\(([^)]+)', "subheader"),
        (r'st\.text\(([^)]+)', "text"),
        (r'st\.write\(([^)]+)', "write"),
        (r'st\.error\(([^)]+)', "error"),
        (r'st\.warning\(([^)]+)', "warning"),
        (r'st\.info\(([^)]+)', "info"),
        (r'st\.success\(([^)]+)', "success"),
        (r'st\.exception\(([^)]+)', "exception"),
        (r'st\.sidebar\.[a-zA-Z_]+\(([^)]+)', "sidebar_component")
    ]

    # Walk through the UI directory and search for component definitions
    for root, dirs, files in os.walk(ui_directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                    # Search for component definitions
                    for pattern, component_type in component_patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            args = match.group(1)
                            element_id = f"{file}:{match.start()}"

                            # Extract styling properties from args
                            properties = {}

                            # Look for common styling parameters
                            for prop in ["key", "help", "label_visibility", "disabled", "use_container_width"]:
                                prop_match = re.search(f"{prop}\\s*=\\s*([^,)]+)", args)
                                if prop_match:
                                    properties[prop] = prop_match.group(1).strip()

                            # Record the component element if it has styling properties
                            if properties:
                                auditor.record_element(
                                    component_type,
                                    element_id,
                                    {
                                        **properties,
                                        "file": file,
                                        "line": content.count('\n', 0, match.start()) + 1,
                                        "context": content[max(0, match.start() - 50):match.end() + 50]
                                    }
                                )
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")

    # Analyze component styling consistency
    for component_type in set(ct for _, ct in component_patterns):
        auditor.analyze_consistency(component_type)

    # End the audit
    auditor.end_audit("Component styling consistency is important for a unified user interface")

def run_all_audits(ui_directory: str) -> VisualDesignAuditor:
    """
    Run all visual design audits.

    Args:
        ui_directory: The directory containing UI code

    Returns:
        The VisualDesignAuditor instance with all audit results
    """
    auditor = VisualDesignAuditor()

    # Run audits for different visual design aspects
    audit_color_consistency(auditor, ui_directory)
    audit_typography_consistency(auditor, ui_directory)
    audit_spacing_consistency(auditor, ui_directory)
    audit_component_styling_consistency(auditor, ui_directory)

    # Generate reports
    os.makedirs("science_data_kit/ui/tests/results", exist_ok=True)
    audit_df = auditor.generate_audit_report("science_data_kit/ui/tests/results/visual_design_audit_results.csv")
    inconsistencies_df = auditor.generate_inconsistencies_report("science_data_kit/ui/tests/results/visual_design_inconsistencies.csv")
    style_guide = auditor.generate_style_guide("science_data_kit/ui/tests/results/visual_design_style_guide.json")

    print("\n=== All Visual Design Audits Completed ===")
    print(f"Total Audits: {len(auditor.results['audits'])}")
    print(f"Total Inconsistencies Found: {len(auditor.results['inconsistencies'])}")

    # Print the top inconsistencies by severity
    if auditor.results['inconsistencies']:
        print("\nTop Visual Design Inconsistencies:")
        inconsistencies_by_severity = sorted(
            auditor.results['inconsistencies'],
            key=lambda x: (
                0 if x['severity'] == 'Critical' else
                1 if x['severity'] == 'High' else
                2 if x['severity'] == 'Medium' else 3
            )
        )
        for i, inconsistency in enumerate(inconsistencies_by_severity[:5], 1):
            print(f"{i}. {inconsistency['element_type']}.{inconsistency['property']}: {len(inconsistency['values'])} different values ({inconsistency['severity']})")

    return auditor

if __name__ == "__main__":
    # Run all audits on the UI directory
    auditor = run_all_audits("science_data_kit/ui")
