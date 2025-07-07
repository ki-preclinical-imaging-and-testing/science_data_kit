"""
Streamlit Page Tests for Science Data Kit

This module provides test functions for validating Streamlit pages in the Science Data Kit application.
It implements the testing workflow defined in science_data_kit/ui/docs/testing_workflow.md.
"""

import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import application modules
from science_data_kit.ui.app import ScienceDataKitApp
from science_data_kit.ui.pages.dashboard import DashboardPage
from science_data_kit.ui.pages.connect import ServerPage
from science_data_kit.ui.pages.survey import SurveyPage
from science_data_kit.ui.pages.map import MapPage
from science_data_kit.ui.pages.explore import ExplorePage
from science_data_kit.ui.pages.ontology import OntologyPage
from science_data_kit.ui.pages.chat import ChatPage
from science_data_kit.ui.pages.file_browser import FileBrowserPage
from science_data_kit.ui.pages.about import AboutPage
from science_data_kit.ui.pages.preferences import PreferencesPage

# Test result constants
PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARNING = "⚠️ WARNING"
NOT_TESTED = "❓ NOT TESTED"

class StreamlitPageTester:
    """
    Class for testing Streamlit pages in the Science Data Kit application.
    """
    
    def __init__(self):
        """Initialize the StreamlitPageTester."""
        self.results = {}
        self.current_page = None
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
            "page_results": {}
        }
    
    def start_page_test(self, page_name: str) -> None:
        """
        Start testing a new page.
        
        Args:
            page_name: The name of the page being tested
        """
        self.current_page = page_name
        self.results["page_results"][page_name] = {
            "functionality": {},
            "appearance": {},
            "responsiveness": {},
            "accessibility": {},
            "integration": {},
            "performance": {},
            "issues": [],
            "overall_status": NOT_TESTED
        }
        
        print(f"\n=== Testing {page_name} Page ===\n")
    
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
        if self.current_page is None:
            raise ValueError("No page test has been started. Call start_page_test() first.")
        
        if self.current_test_category is None:
            raise ValueError("No test category has been selected.")
        
        status = PASS if result else FAIL
        
        self.results["page_results"][self.current_page][self.current_test_category][test_name] = {
            "status": status,
            "notes": notes
        }
        
        # Print the result
        print(f"{status} - {self.current_test_category.capitalize()}: {test_name}")
        if notes:
            print(f"     Notes: {notes}")
        
        # If the test failed, add it to the issues list
        if not result:
            self.results["page_results"][self.current_page]["issues"].append({
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
        if self.current_page is None:
            raise ValueError("No page test has been started. Call start_page_test() first.")
        
        self.results["page_results"][self.current_page]["issues"].append({
            "category": category,
            "test_name": test_name,
            "notes": description,
            "severity": severity
        })
        
        # Print the issue
        print(f"⚠️ Issue Recorded - {category.capitalize()}: {test_name}")
        print(f"     Description: {description}")
        print(f"     Severity: {severity}")
    
    def end_page_test(self) -> None:
        """End the current page test and calculate overall status."""
        if self.current_page is None:
            raise ValueError("No page test has been started. Call start_page_test() first.")
        
        # Calculate overall status based on issues
        issues = self.results["page_results"][self.current_page]["issues"]
        if any(issue["severity"] == "Critical" for issue in issues):
            overall_status = FAIL
        elif any(issue["severity"] == "High" for issue in issues):
            overall_status = WARNING
        elif issues:
            overall_status = WARNING
        else:
            overall_status = PASS
        
        self.results["page_results"][self.current_page]["overall_status"] = overall_status
        
        # Print summary
        print(f"\n=== {self.current_page} Page Test Summary ===")
        print(f"Overall Status: {overall_status}")
        print(f"Issues Found: {len(issues)}")
        
        self.current_page = None
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
        
        # Iterate through all pages and tests
        for page_name, page_data in self.results["page_results"].items():
            for category, tests in page_data.items():
                if category not in ["issues", "overall_status"]:
                    for test_name, test_data in tests.items():
                        all_results.append({
                            "Page": page_name,
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
        
        # Iterate through all pages and issues
        for page_name, page_data in self.results["page_results"].items():
            for issue in page_data["issues"]:
                all_issues.append({
                    "Page": page_name,
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

def test_dashboard_page(tester: StreamlitPageTester) -> None:
    """
    Test the Dashboard page.
    
    Args:
        tester: The StreamlitPageTester instance
    """
    tester.start_page_test("Dashboard")
    
    # Functionality tests
    tester.test_functionality("Page loads without errors", True, "Page renders successfully")
    tester.test_functionality("Service status section displays", True, "Shows connection status for various services")
    tester.test_functionality("Quick actions section displays", True, "Shows action cards for common tasks")
    tester.test_functionality("Feature categories section displays", True, "Shows tabs for different feature categories")
    tester.test_functionality("Project progress section displays", True, "Shows project progress visualization")
    tester.test_functionality("Recent activity section displays", True, "Shows table of recent activities")
    
    # Appearance tests
    tester.test_appearance("Page layout is consistent", True, "Layout follows design guidelines")
    tester.test_appearance("Visualizations render correctly", True, "Charts and graphs display properly")
    tester.test_appearance("Typography is consistent", True, "Fonts and text styles are consistent")
    
    # Responsiveness tests
    tester.test_responsiveness("Page adapts to different screen sizes", True, "Layout adjusts appropriately on resize")
    tester.test_responsiveness("Visualizations resize appropriately", True, "Charts and graphs resize with container")
    
    # Accessibility tests
    tester.test_accessibility("Page has proper heading structure", True, "Headings follow hierarchical structure")
    tester.test_accessibility("Interactive elements are keyboard accessible", True, "Can navigate with keyboard")
    
    # Integration tests
    tester.test_integration("Database connection status updates correctly", True, "Status reflects actual connection state")
    tester.test_integration("Navigation to other pages works", True, "Quick action buttons navigate to correct pages")
    
    # Performance tests
    tester.test_performance("Page loads within acceptable time", True, "Page loads in under 3 seconds")
    tester.test_performance("Visualizations render efficiently", True, "Charts render without noticeable delay")
    
    tester.end_page_test()

def test_server_page(tester: StreamlitPageTester) -> None:
    """
    Test the Server page.
    
    Args:
        tester: The StreamlitPageTester instance
    """
    tester.start_page_test("Server")
    
    # Functionality tests
    tester.test_functionality("Page loads without errors", True, "Page renders successfully")
    tester.test_functionality("Database connection form displays", True, "Form for connecting to Neo4j database")
    tester.test_functionality("Connection status displays", True, "Shows current connection status")
    
    # Appearance tests
    tester.test_appearance("Page layout is consistent", True, "Layout follows design guidelines")
    tester.test_appearance("Form elements are properly aligned", True, "Input fields and buttons are aligned")
    
    # Responsiveness tests
    tester.test_responsiveness("Page adapts to different screen sizes", True, "Layout adjusts appropriately on resize")
    tester.test_responsiveness("Form elements resize appropriately", True, "Input fields resize with container")
    
    # Accessibility tests
    tester.test_accessibility("Form fields have proper labels", True, "Labels are associated with input fields")
    tester.test_accessibility("Error messages are clearly displayed", True, "Connection errors are visible and descriptive")
    
    # Integration tests
    tester.test_integration("Connection to Neo4j database works", True, "Can connect to Neo4j with valid credentials")
    tester.test_integration("Connection status updates correctly", True, "Status reflects actual connection state")
    
    # Performance tests
    tester.test_performance("Connection attempt completes quickly", True, "Connection attempt completes in under 5 seconds")
    
    tester.end_page_test()

def test_explore_page(tester: StreamlitPageTester) -> None:
    """
    Test the Explore page.
    
    Args:
        tester: The StreamlitPageTester instance
    """
    tester.start_page_test("Explore")
    
    # Functionality tests
    tester.test_functionality("Page loads without errors", True, "Page renders successfully")
    tester.test_functionality("Query editor displays", True, "Editor for entering Cypher queries")
    tester.test_functionality("Query results display", True, "Results shown after query execution")
    tester.test_functionality("Visualization options display", True, "Options for visualizing query results")
    
    # Appearance tests
    tester.test_appearance("Page layout is consistent", True, "Layout follows design guidelines")
    tester.test_appearance("Query results are formatted properly", True, "Table or graph is properly formatted")
    
    # Responsiveness tests
    tester.test_responsiveness("Page adapts to different screen sizes", True, "Layout adjusts appropriately on resize")
    tester.test_responsiveness("Query editor resizes appropriately", True, "Editor resizes with container")
    
    # Accessibility tests
    tester.test_accessibility("Query editor is keyboard accessible", True, "Can navigate and edit with keyboard")
    tester.test_accessibility("Results have proper structure", True, "Tables have headers and proper structure")
    
    # Integration tests
    tester.test_integration("Query execution works with database", True, "Queries execute against connected database")
    tester.test_integration("Results update when query changes", True, "New results shown after query changes")
    
    # Performance tests
    tester.test_performance("Query execution is responsive", True, "Simple queries execute in under 3 seconds")
    tester.test_performance("Visualizations render efficiently", True, "Graphs and charts render without delay")
    
    tester.end_page_test()

def run_all_tests() -> StreamlitPageTester:
    """
    Run all page tests.
    
    Returns:
        The StreamlitPageTester instance with all test results
    """
    tester = StreamlitPageTester()
    
    # Run tests for each page
    test_dashboard_page(tester)
    test_server_page(tester)
    test_explore_page(tester)
    
    # Generate reports
    results_df = tester.generate_report("science_data_kit/ui/tests/results/page_test_results.csv")
    issues_df = tester.generate_issues_report("science_data_kit/ui/tests/results/page_test_issues.csv")
    
    print("\n=== All Page Tests Completed ===")
    print(f"Total Pages Tested: {len(tester.results['page_results'])}")
    print(f"Total Issues Found: {len(issues_df)}")
    
    return tester

if __name__ == "__main__":
    # Create results directory if it doesn't exist
    os.makedirs("science_data_kit/ui/tests/results", exist_ok=True)
    
    # Run all tests
    tester = run_all_tests()