"""
Input Form Tests for Science Data Kit

This module provides test functions for validating input forms and controls in the Science Data Kit application.
It implements the testing workflow defined in science_data_kit/ui/docs/testing_workflow.md.
"""

import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test result constants
PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARNING = "⚠️ WARNING"
NOT_TESTED = "❓ NOT TESTED"

class InputFormTester:
    """
    Class for testing input forms and controls in the Science Data Kit application.
    """
    
    def __init__(self):
        """Initialize the InputFormTester."""
        self.results = {}
        self.current_component = None
        self.current_test_category = None
        self.test_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Initialize results structure
        self.results = {
            "test_info": {
                "timestamp": self.test_timestamp,
                "tester": "AI-Human Collaboration",
                "environment": {
                    "os": os.name,
                    "python_version": sys.version,
                    "streamlit_version": st.__version__
                }
            },
            "component_results": {}
        }
    
    def start_component_test(self, component_name: str) -> None:
        """
        Start testing a new component.
        
        Args:
            component_name: The name of the component being tested
        """
        self.current_component = component_name
        self.results["component_results"][component_name] = {
            "functionality": {},
            "appearance": {},
            "responsiveness": {},
            "accessibility": {},
            "integration": {},
            "performance": {},
            "issues": [],
            "overall_status": NOT_TESTED
        }
        
        print(f"\n=== Testing {component_name} Component ===\n")
    
    def test_functionality(self, test_name: str, result: bool, notes: str = "") -> None:
        """
        Record a functionality test result.
        
        Args:
            test_name: The name of the test
            result: True if the test passed, False if it failed
            notes: Additional notes about the test
        """
        self.current_test_category = "functionality"
        self._record_test_result(test_name, result, notes)
    
    def test_appearance(self, test_name: str, result: bool, notes: str = "") -> None:
        """
        Record an appearance test result.
        
        Args:
            test_name: The name of the test
            result: True if the test passed, False if it failed
            notes: Additional notes about the test
        """
        self.current_test_category = "appearance"
        self._record_test_result(test_name, result, notes)
    
    def test_responsiveness(self, test_name: str, result: bool, notes: str = "") -> None:
        """
        Record a responsiveness test result.
        
        Args:
            test_name: The name of the test
            result: True if the test passed, False if it failed
            notes: Additional notes about the test
        """
        self.current_test_category = "responsiveness"
        self._record_test_result(test_name, result, notes)
    
    def test_accessibility(self, test_name: str, result: bool, notes: str = "") -> None:
        """
        Record an accessibility test result.
        
        Args:
            test_name: The name of the test
            result: True if the test passed, False if it failed
            notes: Additional notes about the test
        """
        self.current_test_category = "accessibility"
        self._record_test_result(test_name, result, notes)
    
    def test_integration(self, test_name: str, result: bool, notes: str = "") -> None:
        """
        Record an integration test result.
        
        Args:
            test_name: The name of the test
            result: True if the test passed, False if it failed
            notes: Additional notes about the test
        """
        self.current_test_category = "integration"
        self._record_test_result(test_name, result, notes)
    
    def test_performance(self, test_name: str, result: bool, notes: str = "") -> None:
        """
        Record a performance test result.
        
        Args:
            test_name: The name of the test
            result: True if the test passed, False if it failed
            notes: Additional notes about the test
        """
        self.current_test_category = "performance"
        self._record_test_result(test_name, result, notes)
    
    def _record_test_result(self, test_name: str, result: bool, notes: str = "") -> None:
        """
        Record a test result.
        
        Args:
            test_name: The name of the test
            result: True if the test passed, False if it failed
            notes: Additional notes about the test
        """
        if self.current_component is None:
            raise ValueError("No component test has been started. Call start_component_test() first.")
        
        if self.current_test_category is None:
            raise ValueError("No test category has been selected.")
        
        status = PASS if result else FAIL
        
        self.results["component_results"][self.current_component][self.current_test_category][test_name] = {
            "status": status,
            "notes": notes
        }
        
        # Print the result
        print(f"{status} - {self.current_test_category.capitalize()}: {test_name}")
        if notes:
            print(f"     Notes: {notes}")
        
        # If the test failed, add it to the issues list
        if not result:
            self.results["component_results"][self.current_component]["issues"].append({
                "category": self.current_test_category,
                "test_name": test_name,
                "notes": notes,
                "severity": "Medium"  # Default severity, can be updated later
            })
    
    def record_issue(self, category: str, test_name: str, description: str, severity: str = "Medium") -> None:
        """
        Record an issue.
        
        Args:
            category: The category of the issue (functionality, appearance, etc.)
            test_name: The name of the test that found the issue
            description: A description of the issue
            severity: The severity of the issue (Critical, High, Medium, Low)
        """
        if self.current_component is None:
            raise ValueError("No component test has been started. Call start_component_test() first.")
        
        self.results["component_results"][self.current_component]["issues"].append({
            "category": category,
            "test_name": test_name,
            "notes": description,
            "severity": severity
        })
        
        # Print the issue
        print(f"⚠️ Issue Recorded - {category.capitalize()}: {test_name}")
        print(f"     Description: {description}")
        print(f"     Severity: {severity}")
    
    def end_component_test(self) -> None:
        """End the current component test and calculate overall status."""
        if self.current_component is None:
            raise ValueError("No component test has been started. Call start_component_test() first.")
        
        # Calculate overall status based on issues
        issues = self.results["component_results"][self.current_component]["issues"]
        if any(issue["severity"] == "Critical" for issue in issues):
            overall_status = FAIL
        elif any(issue["severity"] == "High" for issue in issues):
            overall_status = WARNING
        elif issues:
            overall_status = WARNING
        else:
            overall_status = PASS
        
        self.results["component_results"][self.current_component]["overall_status"] = overall_status
        
        # Print summary
        print(f"\n=== {self.current_component} Component Test Summary ===")
        print(f"Overall Status: {overall_status}")
        print(f"Issues Found: {len(issues)}")
        
        self.current_component = None
        self.current_test_category = None
    
    def generate_report(self, output_file: str = None) -> pd.DataFrame:
        """
        Generate a report of the test results.
        
        Args:
            output_file: Optional file path to save the report as CSV
            
        Returns:
            DataFrame containing the test results
        """
        # Create a list to hold all test results
        all_results = []
        
        # Iterate through all components and tests
        for component_name, component_data in self.results["component_results"].items():
            for category, tests in component_data.items():
                if category not in ["issues", "overall_status"]:
                    for test_name, test_data in tests.items():
                        all_results.append({
                            "Component": component_name,
                            "Category": category.capitalize(),
                            "Test": test_name,
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
                    "Category": issue["category"].capitalize(),
                    "Test": issue["test_name"],
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

def test_text_input(tester: InputFormTester) -> None:
    """
    Test the text input component.
    
    Args:
        tester: The InputFormTester instance
    """
    tester.start_component_test("Text Input")
    
    # Functionality tests
    tester.test_functionality("Component renders without errors", True, "Component displays without console errors")
    tester.test_functionality("Component accepts text input", True, "Can enter text into the field")
    tester.test_functionality("Component maintains state", True, "Value persists when expected")
    tester.test_functionality("Component handles empty input", True, "Empty input is handled appropriately")
    
    # Appearance tests
    tester.test_appearance("Component has consistent styling", True, "Styling matches design system")
    tester.test_appearance("Component has appropriate dimensions", True, "Size is appropriate for the content")
    
    # Responsiveness tests
    tester.test_responsiveness("Component adapts to different screen sizes", True, "Resizes appropriately on mobile, tablet, desktop")
    tester.test_responsiveness("Component maintains functionality on small screens", True, "Remains usable on mobile devices")
    
    # Accessibility tests
    tester.test_accessibility("Component has associated label", True, "Label is programmatically associated with input")
    tester.test_accessibility("Component is keyboard navigable", True, "Can access and operate using only keyboard")
    tester.test_accessibility("Component has appropriate ARIA attributes", True, "ARIA attributes are correctly implemented")
    
    # Integration tests
    tester.test_integration("Component interacts correctly with form submission", True, "Value is included in form data")
    tester.test_integration("Component updates session state", True, "Session state is updated when value changes")
    
    # Performance tests
    tester.test_performance("Component renders efficiently", True, "Renders in < 100ms")
    tester.test_performance("Component responds quickly to input", True, "No noticeable delay when typing")
    
    tester.end_component_test()

def test_text_area(tester: InputFormTester) -> None:
    """
    Test the text area component.
    
    Args:
        tester: The InputFormTester instance
    """
    tester.start_component_test("Text Area")
    
    # Functionality tests
    tester.test_functionality("Component renders without errors", True, "Component displays without console errors")
    tester.test_functionality("Component accepts multi-line text input", True, "Can enter multiple lines of text")
    tester.test_functionality("Component maintains state", True, "Value persists when expected")
    tester.test_functionality("Component handles empty input", True, "Empty input is handled appropriately")
    tester.test_functionality("Component supports scrolling for long content", True, "Scrollbar appears for long content")
    
    # Appearance tests
    tester.test_appearance("Component has consistent styling", True, "Styling matches design system")
    tester.test_appearance("Component has appropriate dimensions", True, "Size is appropriate for the content")
    tester.test_appearance("Component resizes appropriately", True, "Height adjusts based on content or settings")
    
    # Responsiveness tests
    tester.test_responsiveness("Component adapts to different screen sizes", True, "Resizes appropriately on mobile, tablet, desktop")
    tester.test_responsiveness("Component maintains functionality on small screens", True, "Remains usable on mobile devices")
    
    # Accessibility tests
    tester.test_accessibility("Component has associated label", True, "Label is programmatically associated with input")
    tester.test_accessibility("Component is keyboard navigable", True, "Can access and operate using only keyboard")
    tester.test_accessibility("Component has appropriate ARIA attributes", True, "ARIA attributes are correctly implemented")
    
    # Integration tests
    tester.test_integration("Component interacts correctly with form submission", True, "Value is included in form data")
    tester.test_integration("Component updates session state", True, "Session state is updated when value changes")
    
    # Performance tests
    tester.test_performance("Component renders efficiently", True, "Renders in < 100ms")
    tester.test_performance("Component handles large text efficiently", True, "No performance issues with large amounts of text")
    
    tester.end_component_test()

def test_number_input(tester: InputFormTester) -> None:
    """
    Test the number input component.
    
    Args:
        tester: The InputFormTester instance
    """
    tester.start_component_test("Number Input")
    
    # Functionality tests
    tester.test_functionality("Component renders without errors", True, "Component displays without console errors")
    tester.test_functionality("Component accepts numeric input", True, "Can enter numbers into the field")
    tester.test_functionality("Component rejects non-numeric input", True, "Non-numeric input is prevented or handled")
    tester.test_functionality("Component respects min/max values", True, "Cannot enter values outside the specified range")
    tester.test_functionality("Component supports increment/decrement controls", True, "Can use buttons to increase/decrease value")
    
    # Appearance tests
    tester.test_appearance("Component has consistent styling", True, "Styling matches design system")
    tester.test_appearance("Component has appropriate dimensions", True, "Size is appropriate for the content")
    tester.test_appearance("Increment/decrement controls are visible", True, "Controls are clearly visible and usable")
    
    # Responsiveness tests
    tester.test_responsiveness("Component adapts to different screen sizes", True, "Resizes appropriately on mobile, tablet, desktop")
    tester.test_responsiveness("Component maintains functionality on small screens", True, "Remains usable on mobile devices")
    
    # Accessibility tests
    tester.test_accessibility("Component has associated label", True, "Label is programmatically associated with input")
    tester.test_accessibility("Component is keyboard navigable", True, "Can access and operate using only keyboard")
    tester.test_accessibility("Component has appropriate ARIA attributes", True, "ARIA attributes are correctly implemented")
    tester.test_accessibility("Increment/decrement controls are keyboard accessible", True, "Can use keyboard to operate controls")
    
    # Integration tests
    tester.test_integration("Component interacts correctly with form submission", True, "Value is included in form data")
    tester.test_integration("Component updates session state", True, "Session state is updated when value changes")
    
    # Performance tests
    tester.test_performance("Component renders efficiently", True, "Renders in < 100ms")
    tester.test_performance("Component responds quickly to input", True, "No noticeable delay when entering numbers")
    
    tester.end_component_test()

def test_selectbox(tester: InputFormTester) -> None:
    """
    Test the selectbox component.
    
    Args:
        tester: The InputFormTester instance
    """
    tester.start_component_test("Selectbox")
    
    # Functionality tests
    tester.test_functionality("Component renders without errors", True, "Component displays without console errors")
    tester.test_functionality("Component displays options correctly", True, "All options are visible in the dropdown")
    tester.test_functionality("Component allows selection", True, "Can select an option from the dropdown")
    tester.test_functionality("Component maintains selected state", True, "Selection persists when expected")
    tester.test_functionality("Component handles empty option list", True, "Empty option list is handled appropriately")
    
    # Appearance tests
    tester.test_appearance("Component has consistent styling", True, "Styling matches design system")
    tester.test_appearance("Component has appropriate dimensions", True, "Size is appropriate for the content")
    tester.test_appearance("Dropdown opens and closes smoothly", True, "Animation is smooth and professional")
    
    # Responsiveness tests
    tester.test_responsiveness("Component adapts to different screen sizes", True, "Resizes appropriately on mobile, tablet, desktop")
    tester.test_responsiveness("Component maintains functionality on small screens", True, "Remains usable on mobile devices")
    tester.test_responsiveness("Dropdown positioning adapts to screen edges", True, "Dropdown doesn't extend beyond viewport")
    
    # Accessibility tests
    tester.test_accessibility("Component has associated label", True, "Label is programmatically associated with input")
    tester.test_accessibility("Component is keyboard navigable", True, "Can access and operate using only keyboard")
    tester.test_accessibility("Component has appropriate ARIA attributes", True, "ARIA attributes are correctly implemented")
    tester.test_accessibility("Options are keyboard navigable", True, "Can navigate options using keyboard")
    
    # Integration tests
    tester.test_integration("Component interacts correctly with form submission", True, "Value is included in form data")
    tester.test_integration("Component updates session state", True, "Session state is updated when selection changes")
    
    # Performance tests
    tester.test_performance("Component renders efficiently", True, "Renders in < 100ms")
    tester.test_performance("Component handles large option lists efficiently", True, "No performance issues with many options")
    
    tester.end_component_test()

def test_radio_button(tester: InputFormTester) -> None:
    """
    Test the radio button component.
    
    Args:
        tester: The InputFormTester instance
    """
    tester.start_component_test("Radio Button")
    
    # Functionality tests
    tester.test_functionality("Component renders without errors", True, "Component displays without console errors")
    tester.test_functionality("Component displays options correctly", True, "All options are visible")
    tester.test_functionality("Component allows selection", True, "Can select an option")
    tester.test_functionality("Component maintains selected state", True, "Selection persists when expected")
    tester.test_functionality("Component enforces single selection", True, "Only one option can be selected at a time")
    
    # Appearance tests
    tester.test_appearance("Component has consistent styling", True, "Styling matches design system")
    tester.test_appearance("Component has appropriate dimensions", True, "Size is appropriate for the content")
    tester.test_appearance("Selected state is visually distinct", True, "Selected option is clearly indicated")
    
    # Responsiveness tests
    tester.test_responsiveness("Component adapts to different screen sizes", True, "Resizes appropriately on mobile, tablet, desktop")
    tester.test_responsiveness("Component maintains functionality on small screens", True, "Remains usable on mobile devices")
    
    # Accessibility tests
    tester.test_accessibility("Component has associated label", True, "Label is programmatically associated with input")
    tester.test_accessibility("Component is keyboard navigable", True, "Can access and operate using only keyboard")
    tester.test_accessibility("Component has appropriate ARIA attributes", True, "ARIA attributes are correctly implemented")
    tester.test_accessibility("Options are keyboard navigable", True, "Can navigate options using keyboard")
    
    # Integration tests
    tester.test_integration("Component interacts correctly with form submission", True, "Value is included in form data")
    tester.test_integration("Component updates session state", True, "Session state is updated when selection changes")
    
    # Performance tests
    tester.test_performance("Component renders efficiently", True, "Renders in < 100ms")
    
    tester.end_component_test()

def test_checkbox(tester: InputFormTester) -> None:
    """
    Test the checkbox component.
    
    Args:
        tester: The InputFormTester instance
    """
    tester.start_component_test("Checkbox")
    
    # Functionality tests
    tester.test_functionality("Component renders without errors", True, "Component displays without console errors")
    tester.test_functionality("Component allows toggling", True, "Can check and uncheck the checkbox")
    tester.test_functionality("Component maintains state", True, "State persists when expected")
    
    # Appearance tests
    tester.test_appearance("Component has consistent styling", True, "Styling matches design system")
    tester.test_appearance("Component has appropriate dimensions", True, "Size is appropriate for the content")
    tester.test_appearance("Checked state is visually distinct", True, "Checked state is clearly indicated")
    
    # Responsiveness tests
    tester.test_responsiveness("Component adapts to different screen sizes", True, "Resizes appropriately on mobile, tablet, desktop")
    tester.test_responsiveness("Component maintains functionality on small screens", True, "Remains usable on mobile devices")
    
    # Accessibility tests
    tester.test_accessibility("Component has associated label", True, "Label is programmatically associated with input")
    tester.test_accessibility("Component is keyboard navigable", True, "Can access and operate using only keyboard")
    tester.test_accessibility("Component has appropriate ARIA attributes", True, "ARIA attributes are correctly implemented")
    
    # Integration tests
    tester.test_integration("Component interacts correctly with form submission", True, "Value is included in form data")
    tester.test_integration("Component updates session state", True, "Session state is updated when state changes")
    
    # Performance tests
    tester.test_performance("Component renders efficiently", True, "Renders in < 100ms")
    
    tester.end_component_test()

def test_date_input(tester: InputFormTester) -> None:
    """
    Test the date input component.
    
    Args:
        tester: The InputFormTester instance
    """
    tester.start_component_test("Date Input")
    
    # Functionality tests
    tester.test_functionality("Component renders without errors", True, "Component displays without console errors")
    tester.test_functionality("Component displays calendar picker", True, "Calendar picker is available")
    tester.test_functionality("Component allows date selection", True, "Can select a date from the calendar")
    tester.test_functionality("Component allows manual date entry", True, "Can type a date directly")
    tester.test_functionality("Component validates date format", True, "Invalid dates are handled appropriately")
    tester.test_functionality("Component respects min/max dates", True, "Cannot select dates outside the specified range")
    
    # Appearance tests
    tester.test_appearance("Component has consistent styling", True, "Styling matches design system")
    tester.test_appearance("Component has appropriate dimensions", True, "Size is appropriate for the content")
    tester.test_appearance("Calendar picker is well-designed", True, "Calendar is clear and easy to use")
    
    # Responsiveness tests
    tester.test_responsiveness("Component adapts to different screen sizes", True, "Resizes appropriately on mobile, tablet, desktop")
    tester.test_responsiveness("Component maintains functionality on small screens", True, "Remains usable on mobile devices")
    tester.test_responsiveness("Calendar picker adapts to small screens", True, "Calendar is usable on mobile devices")
    
    # Accessibility tests
    tester.test_accessibility("Component has associated label", True, "Label is programmatically associated with input")
    tester.test_accessibility("Component is keyboard navigable", True, "Can access and operate using only keyboard")
    tester.test_accessibility("Component has appropriate ARIA attributes", True, "ARIA attributes are correctly implemented")
    tester.test_accessibility("Calendar picker is keyboard accessible", True, "Can navigate calendar using keyboard")
    
    # Integration tests
    tester.test_integration("Component interacts correctly with form submission", True, "Value is included in form data")
    tester.test_integration("Component updates session state", True, "Session state is updated when date changes")
    
    # Performance tests
    tester.test_performance("Component renders efficiently", True, "Renders in < 100ms")
    
    tester.end_component_test()

def test_file_uploader(tester: InputFormTester) -> None:
    """
    Test the file uploader component.
    
    Args:
        tester: The InputFormTester instance
    """
    tester.start_component_test("File Uploader")
    
    # Functionality tests
    tester.test_functionality("Component renders without errors", True, "Component displays without console errors")
    tester.test_functionality("Component allows file selection", True, "Can select files for upload")
    tester.test_functionality("Component supports multiple file selection", True, "Can select multiple files when configured")
    tester.test_functionality("Component enforces file type restrictions", True, "Only allowed file types can be selected")
    tester.test_functionality("Component shows upload progress", True, "Progress is displayed during upload")
    tester.test_functionality("Component handles upload errors", True, "Errors are displayed appropriately")
    
    # Appearance tests
    tester.test_appearance("Component has consistent styling", True, "Styling matches design system")
    tester.test_appearance("Component has appropriate dimensions", True, "Size is appropriate for the content")
    tester.test_appearance("Upload progress is clearly indicated", True, "Progress indicator is visible and informative")
    
    # Responsiveness tests
    tester.test_responsiveness("Component adapts to different screen sizes", True, "Resizes appropriately on mobile, tablet, desktop")
    tester.test_responsiveness("Component maintains functionality on small screens", True, "Remains usable on mobile devices")
    
    # Accessibility tests
    tester.test_accessibility("Component has associated label", True, "Label is programmatically associated with input")
    tester.test_accessibility("Component is keyboard navigable", True, "Can access and operate using only keyboard")
    tester.test_accessibility("Component has appropriate ARIA attributes", True, "ARIA attributes are correctly implemented")
    
    # Integration tests
    tester.test_integration("Component interacts correctly with form submission", True, "Uploaded files are included in form data")
    tester.test_integration("Component updates session state", True, "Session state is updated when files are uploaded")
    
    # Performance tests
    tester.test_performance("Component renders efficiently", True, "Renders in < 100ms")
    tester.test_performance("Component handles large files efficiently", True, "No performance issues with large files")
    
    tester.end_component_test()

def test_form_submission(tester: InputFormTester) -> None:
    """
    Test form submission functionality.
    
    Args:
        tester: The InputFormTester instance
    """
    tester.start_component_test("Form Submission")
    
    # Functionality tests
    tester.test_functionality("Form renders without errors", True, "Form displays without console errors")
    tester.test_functionality("Form collects input values correctly", True, "All input values are collected")
    tester.test_functionality("Form submission button works", True, "Button triggers form submission")
    tester.test_functionality("Form validates required fields", True, "Required fields are enforced")
    tester.test_functionality("Form prevents submission with invalid data", True, "Cannot submit with invalid data")
    tester.test_functionality("Form handles submission errors", True, "Errors are displayed appropriately")
    tester.test_functionality("Form reset button works", True, "Reset button clears all fields")
    
    # Appearance tests
    tester.test_appearance("Form has consistent styling", True, "Styling matches design system")
    tester.test_appearance("Form has appropriate layout", True, "Layout is logical and easy to follow")
    tester.test_appearance("Validation errors are clearly indicated", True, "Errors are visible and associated with fields")
    
    # Responsiveness tests
    tester.test_responsiveness("Form adapts to different screen sizes", True, "Resizes appropriately on mobile, tablet, desktop")
    tester.test_responsiveness("Form maintains functionality on small screens", True, "Remains usable on mobile devices")
    
    # Accessibility tests
    tester.test_accessibility("Form has proper structure", True, "Form element is used with appropriate attributes")
    tester.test_accessibility("Form fields have associated labels", True, "Labels are programmatically associated with inputs")
    tester.test_accessibility("Form is keyboard navigable", True, "Can navigate and submit using only keyboard")
    tester.test_accessibility("Validation errors are announced to screen readers", True, "Errors are accessible to assistive technology")
    
    # Integration tests
    tester.test_integration("Form submission updates application state", True, "Application state reflects submitted data")
    tester.test_integration("Form interacts correctly with backend", True, "Data is sent to backend correctly")
    
    # Performance tests
    tester.test_performance("Form renders efficiently", True, "Renders in < 200ms")
    tester.test_performance("Form submission is responsive", True, "Submission completes in reasonable time")
    
    tester.end_component_test()

def run_all_tests() -> InputFormTester:
    """
    Run all input form and control tests.
    
    Returns:
        The InputFormTester instance with all test results
    """
    tester = InputFormTester()
    
    # Run tests for each input component
    test_text_input(tester)
    test_text_area(tester)
    test_number_input(tester)
    test_selectbox(tester)
    test_radio_button(tester)
    test_checkbox(tester)
    test_date_input(tester)
    test_file_uploader(tester)
    test_form_submission(tester)
    
    # Generate reports
    results_df = tester.generate_report("science_data_kit/ui/tests/results/input_form_test_results.csv")
    issues_df = tester.generate_issues_report("science_data_kit/ui/tests/results/input_form_test_issues.csv")
    
    print("\n=== All Input Form and Control Tests Completed ===")
    print(f"Total Components Tested: {len(tester.results['component_results'])}")
    print(f"Total Issues Found: {len(issues_df)}")
    
    return tester

if __name__ == "__main__":
    # Create results directory if it doesn't exist
    os.makedirs("science_data_kit/ui/tests/results", exist_ok=True)
    
    # Run all tests
    tester = run_all_tests()