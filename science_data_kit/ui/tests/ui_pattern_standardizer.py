"""
UI Pattern Standardizer for Science Data Kit

This module provides tools for standardizing UI patterns across the Science Data Kit application.
It uses the results of the visual design audit to generate standardized UI components and patterns.
"""

import os
import sys
import re
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the visual design auditor
from visual_design_audit import VisualDesignAuditor, run_all_audits

class UIPatternStandardizer:
    """
    Class for standardizing UI patterns across the Science Data Kit application.
    """

    def __init__(self, style_guide_path: Optional[str] = None, audit_results_path: Optional[str] = None):
        """
        Initialize the UIPatternStandardizer.

        Args:
            style_guide_path: Optional path to a style guide JSON file
            audit_results_path: Optional path to audit results CSV file
        """
        self.style_guide = {}
        self.audit_results = {}
        self.standardization_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Load style guide if provided
        if style_guide_path and os.path.exists(style_guide_path):
            with open(style_guide_path, 'r') as f:
                self.style_guide = json.load(f)

        # Load audit results if provided
        if audit_results_path and os.path.exists(audit_results_path):
            self.audit_results = pd.read_csv(audit_results_path).to_dict(orient='records')

        # Initialize results structure
        self.results = {
            "standardization_info": {
                "timestamp": self.standardization_timestamp,
                "standardizer": "AI-Human Collaboration",
                "environment": {
                    "os": os.name,
                    "python_version": sys.version
                }
            },
            "standardized_patterns": {},
            "files_modified": []
        }

    def load_style_guide(self, style_guide_path: str) -> None:
        """
        Load a style guide from a JSON file.

        Args:
            style_guide_path: Path to the style guide JSON file
        """
        if os.path.exists(style_guide_path):
            with open(style_guide_path, 'r') as f:
                self.style_guide = json.load(f)
            print(f"Loaded style guide from {style_guide_path}")
        else:
            print(f"Style guide file not found: {style_guide_path}")

    def run_audit_if_needed(self, ui_directory: str) -> None:
        """
        Run a visual design audit if no style guide is loaded.

        Args:
            ui_directory: The directory containing UI code
        """
        if not self.style_guide:
            print("No style guide loaded. Running visual design audit...")
            auditor = run_all_audits(ui_directory)

            # Generate style guide
            style_guide_path = "science_data_kit/ui/tests/results/visual_design_style_guide.json"
            self.style_guide = auditor.generate_style_guide(style_guide_path)

            # Save audit results
            audit_results_path = "science_data_kit/ui/tests/results/visual_design_audit_results.csv"
            self.audit_results = auditor.generate_audit_report(audit_results_path).to_dict(orient='records')

    def generate_color_constants(self, output_file: str = "science_data_kit/ui/components/ui_constants.py") -> None:
        """
        Generate color constants based on the style guide.

        Args:
            output_file: Path to the output Python file
        """
        if "color" not in self.style_guide:
            print("No color information in style guide. Run audit first.")
            return

        # Extract color values from style guide
        colors = {}
        for element in self.style_guide.get("color", {}):
            value = self.style_guide["color"].get(element)
            if value and isinstance(value, str):
                # Clean up the value (remove quotes, etc.)
                value = value.strip("'\"")

                # Skip if not a valid color
                if not (value.startswith("#") or value in ["red", "green", "blue", "yellow", "orange", "purple", "black", "white", "gray", "grey"] or value.startswith("rgb")):
                    continue

                # Generate a constant name
                name = f"COLOR_{value.replace('#', 'HEX_').upper()}" if value.startswith("#") else f"COLOR_{value.upper()}"
                colors[name] = value

        # Create the constants file content
        content = [
            "\"\"\"",
            "UI Constants for Science Data Kit",
            "",
            "This module provides standardized UI constants for use across the application.",
            "\"\"\"",
            "",
            "# Color Constants",
        ]

        for name, value in colors.items():
            content.append(f"{name} = \"{value}\"")

        content.append("")
        content.append("# Dictionary of all colors for programmatic access")
        content.append("COLORS = {")
        for name, value in colors.items():
            content.append(f"    \"{name}\": {name},")
        content.append("}")

        # Write the file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write("\n".join(content))

        print(f"Generated color constants in {output_file}")
        self.results["standardized_patterns"]["colors"] = list(colors.keys())
        self.results["files_modified"].append(output_file)

    def generate_typography_constants(self, output_file: str = "science_data_kit/ui/components/ui_constants.py") -> None:
        """
        Generate typography constants based on the style guide.

        Args:
            output_file: Path to the output Python file
        """
        if "typography" not in self.style_guide:
            print("No typography information in style guide. Run audit first.")
            return

        # Check if file exists
        file_exists = os.path.exists(output_file)

        # Extract typography values from style guide
        font_sizes = {}
        font_families = {}
        font_weights = {}
        text_aligns = {}

        # Handle different style guide structures
        typography_data = self.style_guide.get("typography", {})

        # Check if typography_data is a dictionary with nested dictionaries
        if isinstance(typography_data, dict):
            for element, properties in typography_data.items():
                # Skip if properties is not a dictionary
                if not isinstance(properties, dict):
                    continue

                for prop, value in properties.items():
                    if prop == "property" and value == "font-size":
                        size_value = properties.get("value", "")
                        if size_value and str(size_value).isdigit():
                            name = f"FONT_SIZE_{size_value}"
                            font_sizes[name] = int(size_value)
                    elif prop == "property" and value == "font-family":
                        family_value = properties.get("value", "")
                        if family_value:
                            # Clean up the value (remove quotes, etc.)
                            family_value = str(family_value).strip("'\"")
                            name = f"FONT_FAMILY_{family_value.upper().replace(' ', '_').replace('-', '_')}"
                            font_families[name] = family_value
                    elif prop == "property" and value == "font-weight":
                        weight_value = properties.get("value", "")
                        if weight_value:
                            # Clean up the value (remove quotes, etc.)
                            weight_value = str(weight_value).strip("'\"")
                            name = f"FONT_WEIGHT_{weight_value.upper()}"
                            font_weights[name] = weight_value
                    elif prop == "property" and value == "text-align":
                        align_value = properties.get("value", "")
                        if align_value:
                            # Clean up the value (remove quotes, etc.)
                            align_value = str(align_value).strip("'\"")
                            name = f"TEXT_ALIGN_{align_value.upper()}"
                            text_aligns[name] = align_value

        # If no typography constants were found, add some defaults
        if not font_sizes and not font_families and not font_weights and not text_aligns:
            print("No typography data found in style guide. Adding default typography constants.")
            font_sizes = {
                "FONT_SIZE_12": 12,
                "FONT_SIZE_14": 14,
                "FONT_SIZE_16": 16,
                "FONT_SIZE_18": 18,
                "FONT_SIZE_24": 24,
                "FONT_SIZE_32": 32
            }
            font_families = {
                "FONT_FAMILY_SANS_SERIF": "sans-serif",
                "FONT_FAMILY_MONOSPACE": "monospace",
                "FONT_FAMILY_SERIF": "serif"
            }
            font_weights = {
                "FONT_WEIGHT_NORMAL": "normal",
                "FONT_WEIGHT_BOLD": "bold"
            }
            text_aligns = {
                "TEXT_ALIGN_LEFT": "left",
                "TEXT_ALIGN_CENTER": "center",
                "TEXT_ALIGN_RIGHT": "right"
            }

        # Create the constants file content
        if file_exists:
            # Read existing file
            with open(output_file, 'r') as f:
                content = f.read()

            # Check if typography constants already exist
            if "# Typography Constants" in content:
                print(f"Typography constants already exist in {output_file}")
                return

            # Append to existing file
            with open(output_file, 'a') as f:
                f.write("\n\n# Typography Constants\n")

                # Font sizes
                if font_sizes:
                    for name, value in font_sizes.items():
                        f.write(f"{name} = {value}\n")

                # Font families
                if font_families:
                    f.write("\n")
                    for name, value in font_families.items():
                        f.write(f"{name} = \"{value}\"\n")

                # Font weights
                if font_weights:
                    f.write("\n")
                    for name, value in font_weights.items():
                        f.write(f"{name} = \"{value}\"\n")

                # Text alignments
                if text_aligns:
                    f.write("\n")
                    for name, value in text_aligns.items():
                        f.write(f"{name} = \"{value}\"\n")

                # Dictionaries for programmatic access
                f.write("\n# Dictionaries for programmatic access\n")

                if font_sizes:
                    f.write("FONT_SIZES = {\n")
                    for name, value in font_sizes.items():
                        f.write(f"    \"{name}\": {name},\n")
                    f.write("}\n")

                if font_families:
                    f.write("\nFONT_FAMILIES = {\n")
                    for name, value in font_families.items():
                        f.write(f"    \"{name}\": {name},\n")
                    f.write("}\n")

                if font_weights:
                    f.write("\nFONT_WEIGHTS = {\n")
                    for name, value in font_weights.items():
                        f.write(f"    \"{name}\": {name},\n")
                    f.write("}\n")

                if text_aligns:
                    f.write("\nTEXT_ALIGNS = {\n")
                    for name, value in text_aligns.items():
                        f.write(f"    \"{name}\": {name},\n")
                    f.write("}\n")
        else:
            # Create new file
            content = [
                "\"\"\"",
                "UI Constants for Science Data Kit",
                "",
                "This module provides standardized UI constants for use across the application.",
                "\"\"\"",
                "",
                "# Typography Constants",
            ]

            # Font sizes
            if font_sizes:
                for name, value in font_sizes.items():
                    content.append(f"{name} = {value}")

            # Font families
            if font_families:
                content.append("")
                for name, value in font_families.items():
                    content.append(f"{name} = \"{value}\"")

            # Font weights
            if font_weights:
                content.append("")
                for name, value in font_weights.items():
                    content.append(f"{name} = \"{value}\"")

            # Text alignments
            if text_aligns:
                content.append("")
                for name, value in text_aligns.items():
                    content.append(f"{name} = \"{value}\"")

            # Dictionaries for programmatic access
            content.append("\n# Dictionaries for programmatic access")

            if font_sizes:
                content.append("FONT_SIZES = {")
                for name, value in font_sizes.items():
                    content.append(f"    \"{name}\": {name},")
                content.append("}")

            if font_families:
                content.append("\nFONT_FAMILIES = {")
                for name, value in font_families.items():
                    content.append(f"    \"{name}\": {name},")
                content.append("}")

            if font_weights:
                content.append("\nFONT_WEIGHTS = {")
                for name, value in font_weights.items():
                    content.append(f"    \"{name}\": {name},")
                content.append("}")

            if text_aligns:
                content.append("\nTEXT_ALIGNS = {")
                for name, value in text_aligns.items():
                    content.append(f"    \"{name}\": {name},")
                content.append("}")

            # Write the file
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                f.write("\n".join(content))

        print(f"Generated typography constants in {output_file}")
        self.results["standardized_patterns"]["typography"] = {
            "font_sizes": list(font_sizes.keys()),
            "font_families": list(font_families.keys()),
            "font_weights": list(font_weights.keys()),
            "text_aligns": list(text_aligns.keys())
        }

        if output_file not in self.results["files_modified"]:
            self.results["files_modified"].append(output_file)

    def generate_spacing_constants(self, output_file: str = "science_data_kit/ui/components/ui_constants.py") -> None:
        """
        Generate spacing constants based on the style guide.

        Args:
            output_file: Path to the output Python file
        """
        if "spacing" not in self.style_guide:
            print("No spacing information in style guide. Run audit first.")
            return

        # Check if file exists
        file_exists = os.path.exists(output_file)

        # Extract spacing values from style guide
        paddings = {}
        margins = {}
        gaps = {}

        for element, properties in self.style_guide.get("spacing", {}).items():
            for prop, value in properties.items():
                if prop == "property" and value == "padding":
                    padding_value = properties.get("value", "")
                    if padding_value and padding_value.isdigit():
                        name = f"PADDING_{padding_value}"
                        paddings[name] = int(padding_value)
                elif prop == "property" and value == "margin":
                    margin_value = properties.get("value", "")
                    if margin_value and margin_value.isdigit():
                        name = f"MARGIN_{margin_value}"
                        margins[name] = int(margin_value)
                elif prop == "property" and value == "gap":
                    gap_value = properties.get("value", "")
                    if gap_value and gap_value.isdigit():
                        name = f"GAP_{gap_value}"
                        gaps[name] = int(gap_value)

        # Create the constants file content
        if file_exists:
            # Read existing file
            with open(output_file, 'r') as f:
                content = f.read()

            # Check if spacing constants already exist
            if "# Spacing Constants" in content:
                print(f"Spacing constants already exist in {output_file}")
                return

            # Append to existing file
            with open(output_file, 'a') as f:
                f.write("\n\n# Spacing Constants\n")

                # Paddings
                if paddings:
                    for name, value in paddings.items():
                        f.write(f"{name} = {value}\n")

                # Margins
                if margins:
                    f.write("\n")
                    for name, value in margins.items():
                        f.write(f"{name} = {value}\n")

                # Gaps
                if gaps:
                    f.write("\n")
                    for name, value in gaps.items():
                        f.write(f"{name} = {value}\n")

                # Dictionaries for programmatic access
                f.write("\n# Dictionaries for programmatic access\n")

                if paddings:
                    f.write("PADDINGS = {\n")
                    for name, value in paddings.items():
                        f.write(f"    \"{name}\": {name},\n")
                    f.write("}\n")

                if margins:
                    f.write("\nMARGINS = {\n")
                    for name, value in margins.items():
                        f.write(f"    \"{name}\": {name},\n")
                    f.write("}\n")

                if gaps:
                    f.write("\nGAPS = {\n")
                    for name, value in gaps.items():
                        f.write(f"    \"{name}\": {name},\n")
                    f.write("}\n")
        else:
            # Create new file
            content = [
                "\"\"\"",
                "UI Constants for Science Data Kit",
                "",
                "This module provides standardized UI constants for use across the application.",
                "\"\"\"",
                "",
                "# Spacing Constants",
            ]

            # Paddings
            if paddings:
                for name, value in paddings.items():
                    content.append(f"{name} = {value}")

            # Margins
            if margins:
                content.append("")
                for name, value in margins.items():
                    content.append(f"{name} = {value}")

            # Gaps
            if gaps:
                content.append("")
                for name, value in gaps.items():
                    content.append(f"{name} = {value}")

            # Dictionaries for programmatic access
            content.append("\n# Dictionaries for programmatic access")

            if paddings:
                content.append("PADDINGS = {")
                for name, value in paddings.items():
                    content.append(f"    \"{name}\": {name},")
                content.append("}")

            if margins:
                content.append("\nMARGINS = {")
                for name, value in margins.items():
                    content.append(f"    \"{name}\": {name},")
                content.append("}")

            if gaps:
                content.append("\nGAPS = {")
                for name, value in gaps.items():
                    content.append(f"    \"{name}\": {name},")
                content.append("}")

            # Write the file
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                f.write("\n".join(content))

        print(f"Generated spacing constants in {output_file}")
        self.results["standardized_patterns"]["spacing"] = {
            "paddings": list(paddings.keys()),
            "margins": list(margins.keys()),
            "gaps": list(gaps.keys())
        }

        if output_file not in self.results["files_modified"]:
            self.results["files_modified"].append(output_file)

    def generate_component_templates(self, output_directory: str = "science_data_kit/ui/components/templates") -> None:
        """
        Generate standardized component templates based on the style guide.

        Args:
            output_directory: Directory to store the component templates
        """
        # Create the output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)

        # Generate the __init__.py file
        init_file = os.path.join(output_directory, "__init__.py")
        with open(init_file, 'w') as f:
            f.write('"""Component templates for Science Data Kit."""\n')

        if init_file not in self.results["files_modified"]:
            self.results["files_modified"].append(init_file)

        # Generate button template
        self._generate_button_template(output_directory)

        # Generate input template
        self._generate_input_template(output_directory)

        # Generate visualization template
        self._generate_visualization_template(output_directory)

        # Generate layout template
        self._generate_layout_template(output_directory)

    def _generate_button_template(self, output_directory: str) -> None:
        """
        Generate a standardized button template.

        Args:
            output_directory: Directory to store the template
        """
        output_file = os.path.join(output_directory, "button_templates.py")

        content = [
            '"""',
            'Button Templates for Science Data Kit',
            '',
            'This module provides standardized button templates for use across the application.',
            '"""',
            '',
            'import streamlit as st',
            'from typing import Optional, Callable, Any',
            '',
            '# Import UI constants',
            'try:',
            '    from science_data_kit.ui.components.ui_constants import *',
            'except ImportError:',
            '    # Default values if constants are not available',
            '    COLOR_PRIMARY = "#4CAF50"',
            '    COLOR_SECONDARY = "#2196F3"',
            '    COLOR_DANGER = "#F44336"',
            '    COLOR_WARNING = "#FF9800"',
            '    COLOR_INFO = "#2196F3"',
            '    COLOR_SUCCESS = "#4CAF50"',
            '',
            'def primary_button(label: str, key: Optional[str] = None, on_click: Optional[Callable] = None, args: tuple = (), kwargs: dict = None, help: Optional[str] = None, disabled: bool = False) -> bool:',
            '    """',
            '    Create a primary button with standardized styling.',
            '    ',
            '    Args:',
            '        label: The text to display on the button',
            '        key: An optional key that uniquely identifies this button',
            '        on_click: An optional callback invoked when this button is clicked',
            '        args: Optional positional arguments to pass to the callback',
            '        kwargs: Optional keyword arguments to pass to the callback',
            '        help: Optional tooltip shown when the button is hovered',
            '        disabled: Optional flag to disable the button',
            '    ',
            '    Returns:',
            '        True if the button was clicked, False otherwise',
            '    """',
            '    kwargs = kwargs or {}',
            '    return st.button(',
            '        label=label,',
            '        key=key,',
            '        on_click=on_click,',
            '        args=args,',
            '        kwargs=kwargs,',
            '        help=help,',
            '        disabled=disabled,',
            '        use_container_width=False',
            '    )',
            '',
            'def secondary_button(label: str, key: Optional[str] = None, on_click: Optional[Callable] = None, args: tuple = (), kwargs: dict = None, help: Optional[str] = None, disabled: bool = False) -> bool:',
            '    """',
            '    Create a secondary button with standardized styling.',
            '    ',
            '    Args:',
            '        label: The text to display on the button',
            '        key: An optional key that uniquely identifies this button',
            '        on_click: An optional callback invoked when this button is clicked',
            '        args: Optional positional arguments to pass to the callback',
            '        kwargs: Optional keyword arguments to pass to the callback',
            '        help: Optional tooltip shown when the button is hovered',
            '        disabled: Optional flag to disable the button',
            '    ',
            '    Returns:',
            '        True if the button was clicked, False otherwise',
            '    """',
            '    kwargs = kwargs or {}',
            '    return st.button(',
            '        label=label,',
            '        key=key,',
            '        on_click=on_click,',
            '        args=args,',
            '        kwargs=kwargs,',
            '        help=help,',
            '        disabled=disabled,',
            '        use_container_width=False',
            '    )',
            '',
            'def danger_button(label: str, key: Optional[str] = None, on_click: Optional[Callable] = None, args: tuple = (), kwargs: dict = None, help: Optional[str] = None, disabled: bool = False) -> bool:',
            '    """',
            '    Create a danger button with standardized styling.',
            '    ',
            '    Args:',
            '        label: The text to display on the button',
            '        key: An optional key that uniquely identifies this button',
            '        on_click: An optional callback invoked when this button is clicked',
            '        args: Optional positional arguments to pass to the callback',
            '        kwargs: Optional keyword arguments to pass to the callback',
            '        help: Optional tooltip shown when the button is hovered',
            '        disabled: Optional flag to disable the button',
            '    ',
            '    Returns:',
            '        True if the button was clicked, False otherwise',
            '    """',
            '    kwargs = kwargs or {}',
            '    return st.button(',
            '        label=label,',
            '        key=key,',
            '        on_click=on_click,',
            '        args=args,',
            '        kwargs=kwargs,',
            '        help=help,',
            '        disabled=disabled,',
            '        use_container_width=False',
            '    )',
            '',
            'def full_width_button(label: str, key: Optional[str] = None, on_click: Optional[Callable] = None, args: tuple = (), kwargs: dict = None, help: Optional[str] = None, disabled: bool = False) -> bool:',
            '    """',
            '    Create a full-width button with standardized styling.',
            '    ',
            '    Args:',
            '        label: The text to display on the button',
            '        key: An optional key that uniquely identifies this button',
            '        on_click: An optional callback invoked when this button is clicked',
            '        args: Optional positional arguments to pass to the callback',
            '        kwargs: Optional keyword arguments to pass to the callback',
            '        help: Optional tooltip shown when the button is hovered',
            '        disabled: Optional flag to disable the button',
            '    ',
            '    Returns:',
            '        True if the button was clicked, False otherwise',
            '    """',
            '    kwargs = kwargs or {}',
            '    return st.button(',
            '        label=label,',
            '        key=key,',
            '        on_click=on_click,',
            '        args=args,',
            '        kwargs=kwargs,',
            '        help=help,',
            '        disabled=disabled,',
            '        use_container_width=True',
            '    )',
        ]

        with open(output_file, 'w') as f:
            f.write('\n'.join(content))

        print(f"Generated button template in {output_file}")
        self.results["standardized_patterns"]["button_templates"] = [
            "primary_button",
            "secondary_button",
            "danger_button",
            "full_width_button"
        ]

        if output_file not in self.results["files_modified"]:
            self.results["files_modified"].append(output_file)

    def _generate_input_template(self, output_directory: str) -> None:
        """
        Generate a standardized input template.

        Args:
            output_directory: Directory to store the template
        """
        output_file = os.path.join(output_directory, "input_templates.py")

        content = [
            '"""',
            'Input Templates for Science Data Kit',
            '',
            'This module provides standardized input templates for use across the application.',
            '"""',
            '',
            'import streamlit as st',
            'from typing import Optional, Callable, Any, List, Union, Dict',
            '',
            'def standard_text_input(label: str, value: str = "", key: Optional[str] = None, help: Optional[str] = None, placeholder: Optional[str] = None, disabled: bool = False, max_chars: Optional[int] = None) -> str:',
            '    """',
            '    Create a standardized text input.',
            '    ',
            '    Args:',
            '        label: The label to display above the input',
            '        value: The initial value',
            '        key: An optional key that uniquely identifies this input',
            '        help: Optional tooltip shown when the input is hovered',
            '        placeholder: Optional placeholder text shown when the input is empty',
            '        disabled: Optional flag to disable the input',
            '        max_chars: Optional maximum number of characters allowed',
            '    ',
            '    Returns:',
            '        The entered text',
            '    """',
            '    return st.text_input(',
            '        label=label,',
            '        value=value,',
            '        key=key,',
            '        help=help,',
            '        placeholder=placeholder,',
            '        disabled=disabled,',
            '        max_chars=max_chars,',
            '        label_visibility="visible"',
            '    )',
            '',
            'def standard_number_input(label: str, min_value: Optional[Union[int, float]] = None, max_value: Optional[Union[int, float]] = None, value: Optional[Union[int, float]] = None, step: Optional[Union[int, float]] = None, key: Optional[str] = None, help: Optional[str] = None, disabled: bool = False) -> Union[int, float]:',
            '    """',
            '    Create a standardized number input.',
            '    ',
            '    Args:',
            '        label: The label to display above the input',
            '        min_value: The minimum value allowed',
            '        max_value: The maximum value allowed',
            '        value: The initial value',
            '        step: The stepping interval',
            '        key: An optional key that uniquely identifies this input',
            '        help: Optional tooltip shown when the input is hovered',
            '        disabled: Optional flag to disable the input',
            '    ',
            '    Returns:',
            '        The entered number',
            '    """',
            '    return st.number_input(',
            '        label=label,',
            '        min_value=min_value,',
            '        max_value=max_value,',
            '        value=value if value is not None else (min_value if min_value is not None else 0),',
            '        step=step,',
            '        key=key,',
            '        help=help,',
            '        disabled=disabled,',
            '        label_visibility="visible"',
            '    )',
            '',
            'def standard_selectbox(label: str, options: List[Any], index: int = 0, key: Optional[str] = None, help: Optional[str] = None, disabled: bool = False) -> Any:',
            '    """',
            '    Create a standardized selectbox.',
            '    ',
            '    Args:',
            '        label: The label to display above the selectbox',
            '        options: The options to select from',
            '        index: The index of the selected option',
            '        key: An optional key that uniquely identifies this selectbox',
            '        help: Optional tooltip shown when the selectbox is hovered',
            '        disabled: Optional flag to disable the selectbox',
            '    ',
            '    Returns:',
            '        The selected option',
            '    """',
            '    return st.selectbox(',
            '        label=label,',
            '        options=options,',
            '        index=index,',
            '        key=key,',
            '        help=help,',
            '        disabled=disabled,',
            '        label_visibility="visible"',
            '    )',
            '',
            'def standard_file_uploader(label: str, type: Union[str, List[str]], key: Optional[str] = None, help: Optional[str] = None, accept_multiple_files: bool = False, disabled: bool = False) -> Any:',
            '    """',
            '    Create a standardized file uploader.',
            '    ',
            '    Args:',
            '        label: The label to display above the file uploader',
            '        type: The file types to accept (e.g., "csv", ["csv", "txt"])',
            '        key: An optional key that uniquely identifies this file uploader',
            '        help: Optional tooltip shown when the file uploader is hovered',
            '        accept_multiple_files: Optional flag to accept multiple files',
            '        disabled: Optional flag to disable the file uploader',
            '    ',
            '    Returns:',
            '        The uploaded file(s)',
            '    """',
            '    return st.file_uploader(',
            '        label=label,',
            '        type=type,',
            '        key=key,',
            '        help=help,',
            '        accept_multiple_files=accept_multiple_files,',
            '        disabled=disabled,',
            '        label_visibility="visible"',
            '    )',
        ]

        with open(output_file, 'w') as f:
            f.write('\n'.join(content))

        print(f"Generated input template in {output_file}")
        self.results["standardized_patterns"]["input_templates"] = [
            "standard_text_input",
            "standard_number_input",
            "standard_selectbox",
            "standard_file_uploader"
        ]

        if output_file not in self.results["files_modified"]:
            self.results["files_modified"].append(output_file)

    def _generate_visualization_template(self, output_directory: str) -> None:
        """
        Generate a standardized visualization template.

        Args:
            output_directory: Directory to store the template
        """
        output_file = os.path.join(output_directory, "visualization_templates.py")

        content = [
            '"""',
            'Visualization Templates for Science Data Kit',
            '',
            'This module provides standardized visualization templates for use across the application.',
            '"""',
            '',
            'import streamlit as st',
            'import pandas as pd',
            'import matplotlib.pyplot as plt',
            'import seaborn as sns',
            'import io',
            'import base64',
            'from typing import Optional, List, Union, Dict, Any, Tuple',
            '',
            '# Import UI constants',
            'try:',
            '    from science_data_kit.ui.components.ui_constants import *',
            'except ImportError:',
            '    # Default values if constants are not available',
            '    COLOR_PRIMARY = "#4CAF50"',
            '    COLOR_SECONDARY = "#2196F3"',
            '',
            'def standard_bar_chart(data: pd.DataFrame, x_column: str, y_column: str, title: str, x_label: Optional[str] = None, y_label: Optional[str] = None, color: Optional[str] = None, figsize: Tuple[int, int] = (8, 5), show_values: bool = False) -> str:',
            '    """',
            '    Create a standardized bar chart.',
            '    ',
            '    Args:',
            '        data: The DataFrame containing the data',
            '        x_column: The column to use for the x-axis',
            '        y_column: The column to use for the y-axis',
            '        title: The title of the chart',
            '        x_label: Optional label for the x-axis',
            '        y_label: Optional label for the y-axis',
            '        color: Optional color for the bars',
            '        figsize: Optional figure size as (width, height) in inches',
            '        show_values: Optional flag to show values on the bars',
            '    ',
            '    Returns:',
            '        Base64-encoded image data',
            '    """',
            '    # Set default values',
            '    x_label = x_label or x_column',
            '    y_label = y_label or y_column',
            '    color = color or COLOR_PRIMARY',
            '    ',
            '    # Create the figure and axis',
            '    fig, ax = plt.subplots(figsize=figsize)',
            '    ',
            '    # Create the bar chart',
            '    bars = ax.bar(data[x_column], data[y_column], color=color)',
            '    ',
            '    # Add values on top of the bars if requested',
            '    if show_values:',
            '        for bar in bars:',
            '            height = bar.get_height()',
            '            ax.text(bar.get_x() + bar.get_width() / 2, height, f"{height:.1f}",',
            '                   ha="center", va="bottom")',
            '    ',
            '    # Set title and labels',
            '    ax.set_title(title)',
            '    ax.set_xlabel(x_label)',
            '    ax.set_ylabel(y_label)',
            '    ',
            '    # Adjust layout',
            '    plt.tight_layout()',
            '    ',
            '    # Convert the figure to a base64-encoded image',
            '    buf = io.BytesIO()',
            '    plt.savefig(buf, format="png")',
            '    plt.close(fig)',
            '    buf.seek(0)',
            '    img_str = base64.b64encode(buf.read()).decode("utf-8")',
            '    ',
            '    return img_str',
            '',
            'def standard_line_chart(data: pd.DataFrame, x_column: str, y_columns: List[str], title: str, x_label: Optional[str] = None, y_label: Optional[str] = None, figsize: Tuple[int, int] = (10, 6), show_markers: bool = False, show_legend: bool = True) -> str:',
            '    """',
            '    Create a standardized line chart.',
            '    ',
            '    Args:',
            '        data: The DataFrame containing the data',
            '        x_column: The column to use for the x-axis',
            '        y_columns: The columns to use for the y-axis (multiple lines)',
            '        title: The title of the chart',
            '        x_label: Optional label for the x-axis',
            '        y_label: Optional label for the y-axis',
            '        figsize: Optional figure size as (width, height) in inches',
            '        show_markers: Optional flag to show markers on the lines',
            '        show_legend: Optional flag to show the legend',
            '    ',
            '    Returns:',
            '        Base64-encoded image data',
            '    """',
            '    # Set default values',
            '    x_label = x_label or x_column',
            '    y_label = y_label or ", ".join(y_columns)',
            '    ',
            '    # Create the figure and axis',
            '    fig, ax = plt.subplots(figsize=figsize)',
            '    ',
            '    # Create the line chart',
            '    for y_column in y_columns:',
            '        ax.plot(data[x_column], data[y_column], marker="o" if show_markers else None, label=y_column)',
            '    ',
            '    # Set title and labels',
            '    ax.set_title(title)',
            '    ax.set_xlabel(x_label)',
            '    ax.set_ylabel(y_label)',
            '    ',
            '    # Show legend if requested',
            '    if show_legend:',
            '        ax.legend()',
            '    ',
            '    # Adjust layout',
            '    plt.tight_layout()',
            '    ',
            '    # Convert the figure to a base64-encoded image',
            '    buf = io.BytesIO()',
            '    plt.savefig(buf, format="png")',
            '    plt.close(fig)',
            '    buf.seek(0)',
            '    img_str = base64.b64encode(buf.read()).decode("utf-8")',
            '    ',
            '    return img_str',
            '',
            'def standard_scatter_plot(data: pd.DataFrame, x_column: str, y_column: str, title: str, x_label: Optional[str] = None, y_label: Optional[str] = None, color_column: Optional[str] = None, size_column: Optional[str] = None, figsize: Tuple[int, int] = (8, 8), show_legend: bool = True) -> str:',
            '    """',
            '    Create a standardized scatter plot.',
            '    ',
            '    Args:',
            '        data: The DataFrame containing the data',
            '        x_column: The column to use for the x-axis',
            '        y_column: The column to use for the y-axis',
            '        title: The title of the chart',
            '        x_label: Optional label for the x-axis',
            '        y_label: Optional label for the y-axis',
            '        color_column: Optional column to use for point colors',
            '        size_column: Optional column to use for point sizes',
            '        figsize: Optional figure size as (width, height) in inches',
            '        show_legend: Optional flag to show the legend',
            '    ',
            '    Returns:',
            '        Base64-encoded image data',
            '    """',
            '    # Set default values',
            '    x_label = x_label or x_column',
            '    y_label = y_label or y_column',
            '    ',
            '    # Create the figure and axis',
            '    fig, ax = plt.subplots(figsize=figsize)',
            '    ',
            '    # Create the scatter plot',
            '    scatter_kwargs = {}',
            '    if color_column:',
            '        scatter_kwargs["c"] = data[color_column]',
            '    if size_column:',
            '        scatter_kwargs["s"] = data[size_column]',
            '    ',
            '    scatter = ax.scatter(data[x_column], data[y_column], **scatter_kwargs)',
            '    ',
            '    # Set title and labels',
            '    ax.set_title(title)',
            '    ax.set_xlabel(x_label)',
            '    ax.set_ylabel(y_label)',
            '    ',
            '    # Show legend if requested and color_column is provided',
            '    if show_legend and color_column:',
            '        if len(data[color_column].unique()) <= 10:  # Only show legend for categorical data',
            '            legend1 = ax.legend(*scatter.legend_elements(), title=color_column)',
            '            ax.add_artist(legend1)',
            '    ',
            '    # Adjust layout',
            '    plt.tight_layout()',
            '    ',
            '    # Convert the figure to a base64-encoded image',
            '    buf = io.BytesIO()',
            '    plt.savefig(buf, format="png")',
            '    plt.close(fig)',
            '    buf.seek(0)',
            '    img_str = base64.b64encode(buf.read()).decode("utf-8")',
            '    ',
            '    return img_str',
        ]

        with open(output_file, 'w') as f:
            f.write('\n'.join(content))

        print(f"Generated visualization template in {output_file}")
        self.results["standardized_patterns"]["visualization_templates"] = [
            "standard_bar_chart",
            "standard_line_chart",
            "standard_scatter_plot"
        ]

        if output_file not in self.results["files_modified"]:
            self.results["files_modified"].append(output_file)

    def _generate_layout_template(self, output_directory: str) -> None:
        """
        Generate a standardized layout template.

        Args:
            output_directory: Directory to store the template
        """
        output_file = os.path.join(output_directory, "layout_templates.py")

        content = [
            '"""',
            'Layout Templates for Science Data Kit',
            '',
            'This module provides standardized layout templates for use across the application.',
            '"""',
            '',
            'import streamlit as st',
            'from typing import Optional, List, Union, Dict, Any, Callable',
            '',
            'def page_header(title: str, subtitle: Optional[str] = None, icon: Optional[str] = None) -> None:',
            '    """',
            '    Create a standardized page header.',
            '    ',
            '    Args:',
            '        title: The title of the page',
            '        subtitle: Optional subtitle for the page',
            '        icon: Optional icon for the page (emoji or URL)',
            '    """',
            '    if icon:',
            '        st.title(f"{icon} {title}")',
            '    else:',
            '        st.title(title)',
            '    ',
            '    if subtitle:',
            '        st.markdown(f"*{subtitle}*")',
            '    ',
            '    st.markdown("---")',
            '',
            'def section_header(title: str, description: Optional[str] = None, level: int = 2) -> None:',
            '    """',
            '    Create a standardized section header.',
            '    ',
            '    Args:',
            '        title: The title of the section',
            '        description: Optional description for the section',
            '        level: The header level (2 for h2, 3 for h3, etc.)',
            '    """',
            '    if level == 2:',
            '        st.header(title)',
            '    elif level == 3:',
            '        st.subheader(title)',
            '    else:',
            '        st.markdown(f"{"#" * level} {title}")',
            '    ',
            '    if description:',
            '        st.markdown(description)',
            '',
            'def two_column_layout(left_content: Callable, right_content: Callable, left_width: int = 1, right_width: int = 1) -> None:',
            '    """',
            '    Create a standardized two-column layout.',
            '    ',
            '    Args:',
            '        left_content: Function that populates the left column',
            '        right_content: Function that populates the right column',
            '        left_width: Optional width of the left column',
            '        right_width: Optional width of the right column',
            '    """',
            '    col1, col2 = st.columns([left_width, right_width])',
            '    ',
            '    with col1:',
            '        left_content()',
            '    ',
            '    with col2:',
            '        right_content()',
            '',
            'def three_column_layout(left_content: Callable, middle_content: Callable, right_content: Callable, left_width: int = 1, middle_width: int = 1, right_width: int = 1) -> None:',
            '    """',
            '    Create a standardized three-column layout.',
            '    ',
            '    Args:',
            '        left_content: Function that populates the left column',
            '        middle_content: Function that populates the middle column',
            '        right_content: Function that populates the right column',
            '        left_width: Optional width of the left column',
            '        middle_width: Optional width of the middle column',
            '        right_width: Optional width of the right column',
            '    """',
            '    col1, col2, col3 = st.columns([left_width, middle_width, right_width])',
            '    ',
            '    with col1:',
            '        left_content()',
            '    ',
            '    with col2:',
            '        middle_content()',
            '    ',
            '    with col3:',
            '        right_content()',
            '',
            'def card(title: str, content: Callable, expanded: bool = True) -> None:',
            '    """',
            '    Create a standardized card layout using an expander.',
            '    ',
            '    Args:',
            '        title: The title of the card',
            '        content: Function that populates the card content',
            '        expanded: Whether the card should be expanded by default',
            '    """',
            '    with st.expander(title, expanded=expanded):',
            '        content()',
            '',
            'def tabs_layout(tab_contents: Dict[str, Callable]) -> None:',
            '    """',
            '    Create a standardized tabs layout.',
            '    ',
            '    Args:',
            '        tab_contents: Dictionary mapping tab names to content functions',
            '    """',
            '    tabs = st.tabs(list(tab_contents.keys()))',
            '    ',
            '    for i, (tab_name, content_func) in enumerate(tab_contents.items()):',
            '        with tabs[i]:',
            '            content_func()',
        ]

        with open(output_file, 'w') as f:
            f.write('\n'.join(content))

        print(f"Generated layout template in {output_file}")
        self.results["standardized_patterns"]["layout_templates"] = [
            "page_header",
            "section_header",
            "two_column_layout",
            "three_column_layout",
            "card",
            "tabs_layout"
        ]

        if output_file not in self.results["files_modified"]:
            self.results["files_modified"].append(output_file)

    def generate_usage_examples(self, output_file: str = "science_data_kit/ui/docs/ui_pattern_examples.md") -> None:
        """
        Generate usage examples for the standardized UI patterns.

        Args:
            output_file: Path to the output Markdown file
        """
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        content = [
            "# UI Pattern Examples",
            "",
            "This document provides examples of how to use the standardized UI patterns in the Science Data Kit application.",
            "",
            "## UI Constants",
            "",
            "The `ui_constants.py` file provides standardized constants for colors, typography, and spacing.",
            "",
            "```python",
            "from science_data_kit.ui.components.ui_constants import *",
            "",
            "# Use color constants",
            "st.markdown(f'<div style=\"color: {COLOR_PRIMARY};\">Primary Color Text</div>', unsafe_allow_html=True)",
            "",
            "# Use typography constants",
            "st.markdown(f'<div style=\"font-size: {FONT_SIZE_16}px; font-family: {FONT_FAMILY_SANS_SERIF};\">Styled Text</div>', unsafe_allow_html=True)",
            "",
            "# Use spacing constants",
            "st.markdown(f'<div style=\"padding: {PADDING_10}px; margin: {MARGIN_20}px;\">Spaced Content</div>', unsafe_allow_html=True)",
            "```",
            "",
            "## Button Templates",
            "",
            "The `button_templates.py` file provides standardized button templates.",
            "",
            "```python",
            "from science_data_kit.ui.components.templates.button_templates import *",
            "",
            "# Primary button",
            "if primary_button('Save', key='save_button', help='Save the current data'):",
            "    st.success('Data saved!')",
            "",
            "# Secondary button",
            "if secondary_button('Cancel', key='cancel_button'):",
            "    st.warning('Operation cancelled')",
            "",
            "# Danger button",
            "if danger_button('Delete', key='delete_button', help='Delete the current data'):",
            "    st.error('Data deleted!')",
            "",
            "# Full-width button",
            "if full_width_button('Submit', key='submit_button'):",
            "    st.success('Form submitted!')",
            "```",
            "",
            "## Input Templates",
            "",
            "The `input_templates.py` file provides standardized input templates.",
            "",
            "```python",
            "from science_data_kit.ui.components.templates.input_templates import *",
            "",
            "# Text input",
            "name = standard_text_input('Name', placeholder='Enter your name', key='name_input')",
            "",
            "# Number input",
            "age = standard_number_input('Age', min_value=0, max_value=120, value=30, key='age_input')",
            "",
            "# Selectbox",
            "option = standard_selectbox('Select an option', options=['Option 1', 'Option 2', 'Option 3'], key='option_select')",
            "",
            "# File uploader",
            "uploaded_file = standard_file_uploader('Upload a file', type=['csv', 'xlsx'], key='file_upload')",
            "```",
            "",
            "## Visualization Templates",
            "",
            "The `visualization_templates.py` file provides standardized visualization templates.",
            "",
            "```python",
            "from science_data_kit.ui.components.templates.visualization_templates import *",
            "import pandas as pd",
            "",
            "# Create sample data",
            "data = pd.DataFrame({",
            "    'Category': ['A', 'B', 'C', 'D', 'E'],",
            "    'Value': [10, 25, 15, 30, 20],",
            "    'Value2': [5, 15, 10, 20, 25]",
            "})",
            "",
            "# Bar chart",
            "bar_chart_img = standard_bar_chart(",
            "    data=data,",
            "    x_column='Category',",
            "    y_column='Value',",
            "    title='Sample Bar Chart',",
            "    show_values=True",
            ")",
            "st.image(f'data:image/png;base64,{bar_chart_img}')",
            "",
            "# Line chart",
            "line_chart_img = standard_line_chart(",
            "    data=data,",
            "    x_column='Category',",
            "    y_columns=['Value', 'Value2'],",
            "    title='Sample Line Chart',",
            "    show_markers=True",
            ")",
            "st.image(f'data:image/png;base64,{line_chart_img}')",
            "",
            "# Scatter plot",
            "scatter_plot_img = standard_scatter_plot(",
            "    data=data,",
            "    x_column='Value',",
            "    y_column='Value2',",
            "    title='Sample Scatter Plot'",
            ")",
            "st.image(f'data:image/png;base64,{scatter_plot_img}')",
            "```",
            "",
            "## Layout Templates",
            "",
            "The `layout_templates.py` file provides standardized layout templates.",
            "",
            "```python",
            "from science_data_kit.ui.components.templates.layout_templates import *",
            "",
            "# Page header",
            "page_header('Dashboard', subtitle='Overview of key metrics', icon='📊')",
            "",
            "# Section header",
            "section_header('Data Analysis', description='Analysis of the imported data', level=2)",
            "",
            "# Two-column layout",
            "def left_column():",
            "    st.write('Left column content')",
            "",
            "def right_column():",
            "    st.write('Right column content')",
            "",
            "two_column_layout(left_column, right_column)",
            "",
            "# Three-column layout",
            "def middle_column():",
            "    st.write('Middle column content')",
            "",
            "three_column_layout(left_column, middle_column, right_column)",
            "",
            "# Card",
            "def card_content():",
            "    st.write('Card content')",
            "",
            "card('Sample Card', card_content)",
            "",
            "# Tabs layout",
            "def tab1_content():",
            "    st.write('Tab 1 content')",
            "",
            "def tab2_content():",
            "    st.write('Tab 2 content')",
            "",
            "tabs_layout({",
            "    'Tab 1': tab1_content,",
            "    'Tab 2': tab2_content",
            "})",
            "```",
        ]

        with open(output_file, 'w') as f:
            f.write('\n'.join(content))

        print(f"Generated usage examples in {output_file}")
        self.results["files_modified"].append(output_file)

    def generate_standardization_report(self, output_file: str = "science_data_kit/ui/tests/results/ui_pattern_standardization_report.json") -> None:
        """
        Generate a report of the standardization results.

        Args:
            output_file: Path to the output JSON file
        """
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Write the report
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"Generated standardization report in {output_file}")

    def run_standardization(self, ui_directory: str) -> None:
        """
        Run the complete UI pattern standardization process.

        Args:
            ui_directory: The directory containing UI code
        """
        # Run audit if needed
        self.run_audit_if_needed(ui_directory)

        # Generate UI constants
        self.generate_color_constants()
        self.generate_typography_constants()
        self.generate_spacing_constants()

        # Generate component templates
        self.generate_component_templates()

        # Generate usage examples
        self.generate_usage_examples()

        # Generate standardization report
        self.generate_standardization_report()

        print("\n=== UI Pattern Standardization Completed ===")
        print(f"Total Files Modified: {len(self.results['files_modified'])}")
        print(f"Total Patterns Standardized: {sum(len(patterns) if isinstance(patterns, list) else 1 for patterns in self.results['standardized_patterns'].values())}")

if __name__ == "__main__":
    # Run the UI pattern standardization
    standardizer = UIPatternStandardizer()
    standardizer.run_standardization("science_data_kit/ui")
