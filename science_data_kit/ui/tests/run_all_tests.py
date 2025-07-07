"""
Run All Tests for Science Data Kit UI

This script runs all the test suites for the Science Data Kit UI components:
- Streamlit Page Tests
- Visualization Component Tests
- Input Form Tests
- Database Connectivity Tests

It collects the results from each test suite and generates a combined report.
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from streamlit_page_tests import run_all_tests as run_page_tests
from visualization_component_tests import run_all_tests as run_visualization_tests
from input_form_tests import run_all_tests as run_input_form_tests
from database_connectivity_tests import run_all_tests as run_database_tests

def main():
    """Run all test suites and generate combined reports."""
    print("\n=== Running All Science Data Kit UI Tests ===\n")
    
    # Create results directory if it doesn't exist
    os.makedirs("science_data_kit/ui/tests/results", exist_ok=True)
    
    # Record start time
    start_time = datetime.now()
    
    # Run each test suite
    print("\n--- Running Streamlit Page Tests ---\n")
    page_tester = run_page_tests()
    
    print("\n--- Running Visualization Component Tests ---\n")
    visualization_tester = run_visualization_tests()
    
    print("\n--- Running Input Form Tests ---\n")
    input_form_tester = run_input_form_tests()
    
    print("\n--- Running Database Connectivity Tests ---\n")
    database_tester = run_database_tests()
    
    # Record end time
    end_time = datetime.now()
    test_duration = (end_time - start_time).total_seconds()
    
    # Generate combined results report
    combined_results = []
    
    # Add page test results
    for page_name, page_data in page_tester.results["page_results"].items():
        for category, tests in page_data.items():
            if category not in ["issues", "overall_status"]:
                for test_name, test_data in tests.items():
                    combined_results.append({
                        "Test Suite": "Streamlit Pages",
                        "Component": page_name,
                        "Category": category.capitalize(),
                        "Test": test_name,
                        "Status": test_data["status"],
                        "Notes": test_data["notes"]
                    })
    
    # Add visualization test results
    for component_name, component_data in visualization_tester.results["component_results"].items():
        for category, tests in component_data.items():
            if category not in ["issues", "overall_status"]:
                for test_name, test_data in tests.items():
                    combined_results.append({
                        "Test Suite": "Visualization Components",
                        "Component": component_name,
                        "Category": category.capitalize(),
                        "Test": test_name,
                        "Status": test_data["status"],
                        "Notes": test_data["notes"]
                    })
    
    # Add input form test results
    for component_name, component_data in input_form_tester.results["component_results"].items():
        for category, tests in component_data.items():
            if category not in ["issues", "overall_status"]:
                for test_name, test_data in tests.items():
                    combined_results.append({
                        "Test Suite": "Input Forms",
                        "Component": component_name,
                        "Category": category.capitalize(),
                        "Test": test_name,
                        "Status": test_data["status"],
                        "Notes": test_data["notes"]
                    })
    
    # Add database connectivity test results
    for component_name, component_data in database_tester.results["component_results"].items():
        for category, tests in component_data.items():
            if category not in ["issues", "overall_status"]:
                for test_name, test_data in tests.items():
                    combined_results.append({
                        "Test Suite": "Database Connectivity",
                        "Component": component_name,
                        "Category": category.capitalize(),
                        "Test": test_name,
                        "Status": test_data["status"],
                        "Notes": test_data["notes"]
                    })
    
    # Create DataFrame from combined results
    combined_df = pd.DataFrame(combined_results)
    
    # Save combined results to CSV
    combined_df.to_csv("science_data_kit/ui/tests/results/combined_test_results.csv", index=False)
    
    # Generate combined issues report
    combined_issues = []
    
    # Add page test issues
    for page_name, page_data in page_tester.results["page_results"].items():
        for issue in page_data["issues"]:
            combined_issues.append({
                "Test Suite": "Streamlit Pages",
                "Component": page_name,
                "Category": issue["category"].capitalize(),
                "Test": issue["test_name"],
                "Description": issue["notes"],
                "Severity": issue["severity"]
            })
    
    # Add visualization test issues
    for component_name, component_data in visualization_tester.results["component_results"].items():
        for issue in component_data["issues"]:
            combined_issues.append({
                "Test Suite": "Visualization Components",
                "Component": component_name,
                "Category": issue["category"].capitalize(),
                "Test": issue["test_name"],
                "Description": issue["notes"],
                "Severity": issue["severity"]
            })
    
    # Add input form test issues
    for component_name, component_data in input_form_tester.results["component_results"].items():
        for issue in component_data["issues"]:
            combined_issues.append({
                "Test Suite": "Input Forms",
                "Component": component_name,
                "Category": issue["category"].capitalize(),
                "Test": issue["test_name"],
                "Description": issue["notes"],
                "Severity": issue["severity"]
            })
    
    # Add database connectivity test issues
    for component_name, component_data in database_tester.results["component_results"].items():
        for issue in component_data["issues"]:
            combined_issues.append({
                "Test Suite": "Database Connectivity",
                "Component": component_name,
                "Category": issue["category"].capitalize(),
                "Test": issue["test_name"],
                "Description": issue["notes"],
                "Severity": issue["severity"]
            })
    
    # Create DataFrame from combined issues
    combined_issues_df = pd.DataFrame(combined_issues)
    
    # Save combined issues to CSV
    combined_issues_df.to_csv("science_data_kit/ui/tests/results/combined_test_issues.csv", index=False)
    
    # Print summary
    print("\n=== All Test Suites Completed ===")
    print(f"Total Test Duration: {test_duration:.2f} seconds")
    print(f"Total Tests Run: {len(combined_df)}")
    print(f"Total Issues Found: {len(combined_issues_df)}")
    print(f"Results saved to science_data_kit/ui/tests/results/combined_test_results.csv")
    print(f"Issues saved to science_data_kit/ui/tests/results/combined_test_issues.csv")
    
    # Return summary statistics
    return {
        "total_tests": len(combined_df),
        "total_issues": len(combined_issues_df),
        "test_duration": test_duration,
        "results_df": combined_df,
        "issues_df": combined_issues_df
    }

if __name__ == "__main__":
    main()