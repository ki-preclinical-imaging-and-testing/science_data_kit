"""
Accessibility Audit for Science Data Kit

This module provides tools for auditing accessibility compliance with WCAG 2.1 standards.
It includes tests for keyboard navigation, screen reader compatibility, color contrast,
and other accessibility requirements.
"""

import streamlit as st
import pandas as pd
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
import re
import json
import logging
from enum import Enum

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test result constants
PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARNING = "⚠️ WARNING"
NOT_TESTED = "❓ NOT TESTED"
MANUAL_CHECK = "🔍 MANUAL CHECK REQUIRED"


class WCAGLevel(Enum):
    """WCAG conformance levels."""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class WCAGCategory(Enum):
    """WCAG guideline categories."""
    PERCEIVABLE = "Perceivable"
    OPERABLE = "Operable"
    UNDERSTANDABLE = "Understandable"
    ROBUST = "Robust"


class AccessibilityAuditor:
    """
    Class for auditing accessibility compliance with WCAG 2.1 standards.
    """

    def __init__(self):
        """Initialize the AccessibilityAuditor."""
        self.results = {}
        self.current_component = None
        self.current_category = None
        self.test_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Initialize results structure
        self.results = {
            "test_info": {
                "timestamp": self.test_timestamp,
                "tester": "AI-Human Collaboration",
                "wcag_version": "2.1",
                "target_conformance_level": WCAGLevel.AA.value
            },
            "component_results": {}
        }
        
        # Initialize WCAG criteria
        self.wcag_criteria = self._initialize_wcag_criteria()
        
    def _initialize_wcag_criteria(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize WCAG 2.1 criteria.
        
        Returns:
            Dictionary of WCAG criteria
        """
        criteria = {}
        
        # Perceivable
        criteria["1.1.1"] = {
            "name": "Non-text Content",
            "description": "All non-text content has a text alternative",
            "level": WCAGLevel.A,
            "category": WCAGCategory.PERCEIVABLE
        }
        
        criteria["1.3.1"] = {
            "name": "Info and Relationships",
            "description": "Information, structure, and relationships can be programmatically determined",
            "level": WCAGLevel.A,
            "category": WCAGCategory.PERCEIVABLE
        }
        
        criteria["1.4.1"] = {
            "name": "Use of Color",
            "description": "Color is not used as the only visual means of conveying information",
            "level": WCAGLevel.A,
            "category": WCAGCategory.PERCEIVABLE
        }
        
        criteria["1.4.3"] = {
            "name": "Contrast (Minimum)",
            "description": "Text has a contrast ratio of at least 4.5:1",
            "level": WCAGLevel.AA,
            "category": WCAGCategory.PERCEIVABLE
        }
        
        criteria["1.4.4"] = {
            "name": "Resize Text",
            "description": "Text can be resized up to 200% without loss of content or functionality",
            "level": WCAGLevel.AA,
            "category": WCAGCategory.PERCEIVABLE
        }
        
        criteria["1.4.10"] = {
            "name": "Reflow",
            "description": "Content can be presented without scrolling in two dimensions",
            "level": WCAGLevel.AA,
            "category": WCAGCategory.PERCEIVABLE
        }
        
        criteria["1.4.11"] = {
            "name": "Non-Text Contrast",
            "description": "UI components and graphical objects have a contrast ratio of at least 3:1",
            "level": WCAGLevel.AA,
            "category": WCAGCategory.PERCEIVABLE
        }
        
        # Operable
        criteria["2.1.1"] = {
            "name": "Keyboard",
            "description": "All functionality is available from a keyboard",
            "level": WCAGLevel.A,
            "category": WCAGCategory.OPERABLE
        }
        
        criteria["2.1.2"] = {
            "name": "No Keyboard Trap",
            "description": "Keyboard focus can be moved away from a component using only a keyboard",
            "level": WCAGLevel.A,
            "category": WCAGCategory.OPERABLE
        }
        
        criteria["2.4.3"] = {
            "name": "Focus Order",
            "description": "Focus order preserves meaning and operability",
            "level": WCAGLevel.A,
            "category": WCAGCategory.OPERABLE
        }
        
        criteria["2.4.7"] = {
            "name": "Focus Visible",
            "description": "Keyboard focus indicator is visible",
            "level": WCAGLevel.AA,
            "category": WCAGCategory.OPERABLE
        }
        
        criteria["2.5.3"] = {
            "name": "Label in Name",
            "description": "The name of a UI component contains the text that is presented visually",
            "level": WCAGLevel.A,
            "category": WCAGCategory.OPERABLE
        }
        
        # Understandable
        criteria["3.1.1"] = {
            "name": "Language of Page",
            "description": "The default human language of the page can be programmatically determined",
            "level": WCAGLevel.A,
            "category": WCAGCategory.UNDERSTANDABLE
        }
        
        criteria["3.2.1"] = {
            "name": "On Focus",
            "description": "When a component receives focus, it does not initiate a change of context",
            "level": WCAGLevel.A,
            "category": WCAGCategory.UNDERSTANDABLE
        }
        
        criteria["3.2.2"] = {
            "name": "On Input",
            "description": "Changing the setting of a UI component does not automatically cause a change of context",
            "level": WCAGLevel.A,
            "category": WCAGCategory.UNDERSTANDABLE
        }
        
        criteria["3.3.1"] = {
            "name": "Error Identification",
            "description": "Input errors are identified and described to the user",
            "level": WCAGLevel.A,
            "category": WCAGCategory.UNDERSTANDABLE
        }
        
        criteria["3.3.2"] = {
            "name": "Labels or Instructions",
            "description": "Labels or instructions are provided for user input",
            "level": WCAGLevel.A,
            "category": WCAGCategory.UNDERSTANDABLE
        }
        
        # Robust
        criteria["4.1.1"] = {
            "name": "Parsing",
            "description": "Elements have complete start and end tags, are nested according to specifications, and do not contain duplicate attributes",
            "level": WCAGLevel.A,
            "category": WCAGCategory.ROBUST
        }
        
        criteria["4.1.2"] = {
            "name": "Name, Role, Value",
            "description": "For all UI components, the name, role, and value can be programmatically determined",
            "level": WCAGLevel.A,
            "category": WCAGCategory.ROBUST
        }
        
        return criteria
        
    def start_component_audit(self, component_name: str) -> None:
        """
        Start auditing a new component.
        
        Args:
            component_name: The name of the component being audited
        """
        self.current_component = component_name
        self.results["component_results"][component_name] = {
            "perceivable": {},
            "operable": {},
            "understandable": {},
            "robust": {},
            "issues": [],
            "overall_status": NOT_TESTED
        }
        
        print(f"\n=== Auditing {component_name} Component ===\n")
        
    def test_perceivable(self, criterion_id: str, result: Optional[bool], notes: str = "") -> None:
        """
        Record a perceivable test result.
        
        Args:
            criterion_id: The WCAG criterion ID (e.g., "1.1.1")
            result: True if the test passed, False if it failed, None if manual check required
            notes: Additional notes about the test
        """
        self.current_category = "perceivable"
        self._record_test_result(criterion_id, result, notes)
        
    def test_operable(self, criterion_id: str, result: Optional[bool], notes: str = "") -> None:
        """
        Record an operable test result.
        
        Args:
            criterion_id: The WCAG criterion ID (e.g., "2.1.1")
            result: True if the test passed, False if it failed, None if manual check required
            notes: Additional notes about the test
        """
        self.current_category = "operable"
        self._record_test_result(criterion_id, result, notes)
        
    def test_understandable(self, criterion_id: str, result: Optional[bool], notes: str = "") -> None:
        """
        Record an understandable test result.
        
        Args:
            criterion_id: The WCAG criterion ID (e.g., "3.1.1")
            result: True if the test passed, False if it failed, None if manual check required
            notes: Additional notes about the test
        """
        self.current_category = "understandable"
        self._record_test_result(criterion_id, result, notes)
        
    def test_robust(self, criterion_id: str, result: Optional[bool], notes: str = "") -> None:
        """
        Record a robust test result.
        
        Args:
            criterion_id: The WCAG criterion ID (e.g., "4.1.1")
            result: True if the test passed, False if it failed, None if manual check required
            notes: Additional notes about the test
        """
        self.current_category = "robust"
        self._record_test_result(criterion_id, result, notes)
        
    def _record_test_result(self, criterion_id: str, result: Optional[bool], notes: str = "") -> None:
        """
        Record a test result.
        
        Args:
            criterion_id: The WCAG criterion ID (e.g., "1.1.1")
            result: True if the test passed, False if it failed, None if manual check required
            notes: Additional notes about the test
        """
        if self.current_component is None:
            raise ValueError("No component audit has been started. Call start_component_audit() first.")
            
        if self.current_category is None:
            raise ValueError("No test category has been selected.")
            
        if criterion_id not in self.wcag_criteria:
            raise ValueError(f"Unknown WCAG criterion ID: {criterion_id}")
            
        criterion = self.wcag_criteria[criterion_id]
        
        if result is True:
            status = PASS
        elif result is False:
            status = FAIL
        else:
            status = MANUAL_CHECK
            
        self.results["component_results"][self.current_component][self.current_category][criterion_id] = {
            "name": criterion["name"],
            "description": criterion["description"],
            "level": criterion["level"].value,
            "status": status,
            "notes": notes
        }
        
        # Print the result
        print(f"{status} - {criterion['category'].value} {criterion_id} {criterion['name']}")
        if notes:
            print(f"     Notes: {notes}")
            
        # If the test failed, add it to the issues list
        if result is False:
            self.results["component_results"][self.current_component]["issues"].append({
                "criterion_id": criterion_id,
                "category": criterion["category"].value,
                "name": criterion["name"],
                "level": criterion["level"].value,
                "notes": notes,
                "severity": "High" if criterion["level"] == WCAGLevel.A else "Medium"
            })
            
    def record_issue(self, criterion_id: str, description: str, severity: str = "Medium") -> None:
        """
        Record an accessibility issue.
        
        Args:
            criterion_id: The WCAG criterion ID (e.g., "1.1.1")
            description: A description of the issue
            severity: The severity of the issue (Critical, High, Medium, Low)
        """
        if self.current_component is None:
            raise ValueError("No component audit has been started. Call start_component_audit() first.")
            
        if criterion_id not in self.wcag_criteria:
            raise ValueError(f"Unknown WCAG criterion ID: {criterion_id}")
            
        criterion = self.wcag_criteria[criterion_id]
        
        self.results["component_results"][self.current_component]["issues"].append({
            "criterion_id": criterion_id,
            "category": criterion["category"].value,
            "name": criterion["name"],
            "level": criterion["level"].value,
            "notes": description,
            "severity": severity
        })
        
        # Print the issue
        print(f"⚠️ Issue Recorded - {criterion['category'].value} {criterion_id} {criterion['name']}")
        print(f"     Description: {description}")
        print(f"     Severity: {severity}")
        
    def end_component_audit(self) -> None:
        """End the current component audit and calculate overall status."""
        if self.current_component is None:
            raise ValueError("No component audit has been started. Call start_component_audit() first.")
            
        # Calculate overall status based on issues
        issues = self.results["component_results"][self.current_component]["issues"]
        
        if any(issue["level"] == WCAGLevel.A.value and issue["severity"] in ["Critical", "High"] for issue in issues):
            overall_status = FAIL
        elif any(issue["level"] == WCAGLevel.AA.value and issue["severity"] in ["Critical", "High"] for issue in issues):
            overall_status = WARNING
        elif issues:
            overall_status = WARNING
        else:
            overall_status = PASS
            
        self.results["component_results"][self.current_component]["overall_status"] = overall_status
        
        # Print summary
        print(f"\n=== {self.current_component} Component Audit Summary ===")
        print(f"Overall Status: {overall_status}")
        print(f"Issues Found: {len(issues)}")
        
        self.current_component = None
        self.current_category = None
        
    def generate_report(self, output_file: str = None) -> pd.DataFrame:
        """
        Generate a report of the audit results.
        
        Args:
            output_file: Optional file path to save the report as CSV
            
        Returns:
            DataFrame containing the audit results
        """
        # Create a list to hold all test results
        all_results = []
        
        # Iterate through all components and tests
        for component_name, component_data in self.results["component_results"].items():
            for category in ["perceivable", "operable", "understandable", "robust"]:
                for criterion_id, test_data in component_data[category].items():
                    all_results.append({
                        "Component": component_name,
                        "Category": category.capitalize(),
                        "Criterion ID": criterion_id,
                        "Criterion Name": test_data["name"],
                        "Description": test_data["description"],
                        "Level": test_data["level"],
                        "Status": test_data["status"],
                        "Notes": test_data["notes"]
                    })
        
        # Create a DataFrame from the results
        df = pd.DataFrame(all_results)
        
        # Save to file if specified
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Report saved to {output_file}")
            
        return df
        
    def generate_issues_report(self, output_file: str = None) -> pd.DataFrame:
        """
        Generate a report of the issues found.
        
        Args:
            output_file: Optional file path to save the report as CSV
            
        Returns:
            DataFrame containing the issues
        """
        # Create a list to hold all issues
        all_issues = []
        
        # Iterate through all components and issues
        for component_name, component_data in self.results["component_results"].items():
            for issue in component_data["issues"]:
                all_issues.append({
                    "Component": component_name,
                    "Criterion ID": issue["criterion_id"],
                    "Category": issue["category"],
                    "Criterion Name": issue["name"],
                    "Level": issue["level"],
                    "Description": issue["notes"],
                    "Severity": issue["severity"]
                })
        
        # Create a DataFrame from the issues
        df = pd.DataFrame(all_issues)
        
        # Save to file if specified
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Issues report saved to {output_file}")
            
        return df
        
    def generate_compliance_report(self, output_file: str = None) -> Dict[str, Any]:
        """
        Generate a compliance report showing conformance to WCAG levels.
        
        Args:
            output_file: Optional file path to save the report as JSON
            
        Returns:
            Dictionary containing the compliance report
        """
        # Initialize compliance report
        compliance_report = {
            "timestamp": self.test_timestamp,
            "wcag_version": self.results["test_info"]["wcag_version"],
            "target_conformance_level": self.results["test_info"]["target_conformance_level"],
            "components_tested": list(self.results["component_results"].keys()),
            "conformance": {
                "A": {
                    "status": PASS,
                    "issues": []
                },
                "AA": {
                    "status": PASS,
                    "issues": []
                },
                "AAA": {
                    "status": NOT_TESTED,
                    "issues": []
                }
            },
            "summary": {
                "total_components": len(self.results["component_results"]),
                "total_issues": 0,
                "issues_by_level": {
                    "A": 0,
                    "AA": 0,
                    "AAA": 0
                },
                "issues_by_category": {
                    "Perceivable": 0,
                    "Operable": 0,
                    "Understandable": 0,
                    "Robust": 0
                }
            }
        }
        
        # Collect all issues
        all_issues = []
        for component_name, component_data in self.results["component_results"].items():
            for issue in component_data["issues"]:
                all_issues.append(issue)
                compliance_report["summary"]["total_issues"] += 1
                compliance_report["summary"]["issues_by_level"][issue["level"]] += 1
                compliance_report["summary"]["issues_by_category"][issue["category"]] += 1
                
                # Add to conformance issues
                if issue["level"] == "A":
                    compliance_report["conformance"]["A"]["issues"].append({
                        "component": component_name,
                        "criterion_id": issue["criterion_id"],
                        "name": issue["name"],
                        "description": issue["notes"],
                        "severity": issue["severity"]
                    })
                elif issue["level"] == "AA":
                    compliance_report["conformance"]["AA"]["issues"].append({
                        "component": component_name,
                        "criterion_id": issue["criterion_id"],
                        "name": issue["name"],
                        "description": issue["notes"],
                        "severity": issue["severity"]
                    })
        
        # Determine conformance status
        if compliance_report["conformance"]["A"]["issues"]:
            compliance_report["conformance"]["A"]["status"] = FAIL
            compliance_report["conformance"]["AA"]["status"] = FAIL
        elif compliance_report["conformance"]["AA"]["issues"]:
            compliance_report["conformance"]["AA"]["status"] = FAIL
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(compliance_report, f, indent=2)
            print(f"Compliance report saved to {output_file}")
            
        return compliance_report


def audit_keyboard_navigation(auditor: AccessibilityAuditor, component_name: str) -> None:
    """
    Audit keyboard navigation for a component.
    
    Args:
        auditor: The AccessibilityAuditor instance
        component_name: The name of the component to audit
    """
    auditor.start_component_audit(component_name)
    
    # Test keyboard accessibility
    auditor.test_operable("2.1.1", None, "Manual check required: Verify all functionality is available from a keyboard")
    auditor.test_operable("2.1.2", None, "Manual check required: Verify keyboard focus can be moved away from all components using only a keyboard")
    
    # Test focus order
    auditor.test_operable("2.4.3", None, "Manual check required: Verify focus order preserves meaning and operability")
    
    # Test focus visibility
    auditor.test_operable("2.4.7", None, "Manual check required: Verify keyboard focus indicator is visible")
    
    auditor.end_component_audit()


def audit_color_contrast(auditor: AccessibilityAuditor, component_name: str) -> None:
    """
    Audit color contrast for a component.
    
    Args:
        auditor: The AccessibilityAuditor instance
        component_name: The name of the component to audit
    """
    auditor.start_component_audit(component_name)
    
    # Test text contrast
    auditor.test_perceivable("1.4.3", None, "Manual check required: Verify text has a contrast ratio of at least 4.5:1")
    
    # Test non-text contrast
    auditor.test_perceivable("1.4.11", None, "Manual check required: Verify UI components and graphical objects have a contrast ratio of at least 3:1")
    
    # Test use of color
    auditor.test_perceivable("1.4.1", None, "Manual check required: Verify color is not used as the only visual means of conveying information")
    
    auditor.end_component_audit()


def audit_screen_reader_compatibility(auditor: AccessibilityAuditor, component_name: str) -> None:
    """
    Audit screen reader compatibility for a component.
    
    Args:
        auditor: The AccessibilityAuditor instance
        component_name: The name of the component to audit
    """
    auditor.start_component_audit(component_name)
    
    # Test non-text content
    auditor.test_perceivable("1.1.1", None, "Manual check required: Verify all non-text content has a text alternative")
    
    # Test info and relationships
    auditor.test_perceivable("1.3.1", None, "Manual check required: Verify information, structure, and relationships can be programmatically determined")
    
    # Test name, role, value
    auditor.test_robust("4.1.2", None, "Manual check required: Verify name, role, and value can be programmatically determined for all UI components")
    
    # Test label in name
    auditor.test_operable("2.5.3", None, "Manual check required: Verify the name of each UI component contains the text that is presented visually")
    
    auditor.end_component_audit()


def run_accessibility_audit() -> AccessibilityAuditor:
    """
    Run a comprehensive accessibility audit.
    
    Returns:
        The AccessibilityAuditor instance with all audit results
    """
    print("=== Running Accessibility Audit ===")
    
    auditor = AccessibilityAuditor()
    
    # Audit keyboard navigation for key components
    audit_keyboard_navigation(auditor, "Sidebar Navigation")
    audit_keyboard_navigation(auditor, "Form Controls")
    audit_keyboard_navigation(auditor, "Data Tables")
    audit_keyboard_navigation(auditor, "Visualizations")
    
    # Audit color contrast for key components
    audit_color_contrast(auditor, "Text Content")
    audit_color_contrast(auditor, "UI Controls")
    audit_color_contrast(auditor, "Visualizations")
    
    # Audit screen reader compatibility for key components
    audit_screen_reader_compatibility(auditor, "Sidebar Navigation")
    audit_screen_reader_compatibility(auditor, "Form Controls")
    audit_screen_reader_compatibility(auditor, "Data Tables")
    audit_screen_reader_compatibility(auditor, "Visualizations")
    
    # Create results directory if it doesn't exist
    os.makedirs("science_data_kit/ui/tests/results", exist_ok=True)
    
    # Generate reports
    auditor.generate_report("science_data_kit/ui/tests/results/accessibility_audit_results.csv")
    auditor.generate_issues_report("science_data_kit/ui/tests/results/accessibility_audit_issues.csv")
    auditor.generate_compliance_report("science_data_kit/ui/tests/results/accessibility_compliance_report.json")
    
    print("\n=== Accessibility Audit Completed ===")
    print(f"Results saved to science_data_kit/ui/tests/results/")
    
    return auditor


if __name__ == "__main__":
    run_accessibility_audit()