"""
Run All Tests for Science Data Kit UI

This script runs all the test suites for the Science Data Kit UI components:
- Streamlit Page Tests
- Visualization Component Tests
- Input Form Tests
- Database Connectivity Tests
- Data Import/Export Tests
- Analysis Engine Tests
- Plugin System Tests
- Error Handling Tests
- State Management Tests

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
from data_import_export_tests import run_all_tests as run_data_import_export_tests
from analysis_engine_tests import run_all_tests as run_analysis_engine_tests
from plugin_system_tests import run_all_tests as run_plugin_system_tests
from error_handling_tests import run_all_tests as run_error_handling_tests
from state_management_tests import run_all_tests as run_state_management_tests
from visualization_workflow_tests import run_all_tests as run_visualization_workflow_tests
from cross_component_workflow_tests import run_all_tests as run_cross_component_workflow_tests
from performance_bottleneck_tests import run_all_tests as run_performance_bottleneck_tests

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

    print("\n--- Running Data Import/Export Tests ---\n")
    data_import_export_tester = run_data_import_export_tests()

    print("\n--- Running Analysis Engine Tests ---\n")
    analysis_engine_tester = run_analysis_engine_tests()

    print("\n--- Running Plugin System Tests ---\n")
    plugin_system_tester = run_plugin_system_tests()

    print("\n--- Running Error Handling Tests ---\n")
    error_handling_tester = run_error_handling_tests()

    print("\n--- Running State Management Tests ---\n")
    state_management_tester = run_state_management_tests()

    print("\n--- Running Visualization Workflow Tests ---\n")
    visualization_workflow_tester = run_visualization_workflow_tests()

    print("\n--- Running Cross-Component Workflow Tests ---\n")
    cross_component_workflow_tester = run_cross_component_workflow_tests()

    print("\n--- Running Performance Bottleneck Tests ---\n")
    performance_bottleneck_tester = run_performance_bottleneck_tests()

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

    # Add data import/export test results
    for result in data_import_export_tester[0].to_dict('records'):
        combined_results.append({
            "Test Suite": "Data Import/Export",
            "Component": result["Component"],
            "Category": result["Category"],
            "Test": result["Test Name"],
            "Status": result["Status"],
            "Notes": result["Notes"]
        })

    # Add analysis engine test results
    for result in analysis_engine_tester[0].to_dict('records'):
        combined_results.append({
            "Test Suite": "Analysis Engine",
            "Component": result["Component"],
            "Category": result["Category"],
            "Test": result["Test Name"],
            "Status": result["Status"],
            "Notes": result["Notes"]
        })

    # Add plugin system test results
    for result in plugin_system_tester[0].to_dict('records'):
        combined_results.append({
            "Test Suite": "Plugin System",
            "Component": result["Component"],
            "Category": result["Category"],
            "Test": result["Test Name"],
            "Status": result["Status"],
            "Notes": result["Notes"]
        })

    # Add error handling test results
    for result in error_handling_tester[0].to_dict('records'):
        combined_results.append({
            "Test Suite": "Error Handling",
            "Component": result["Component"],
            "Category": result["Category"],
            "Test": result["Test Name"],
            "Status": result["Status"],
            "Notes": result["Notes"]
        })

    # Add state management test results
    for result in state_management_tester[0].to_dict('records'):
        combined_results.append({
            "Test Suite": "State Management",
            "Component": result["Component"],
            "Category": result["Category"],
            "Test": result["Test Name"],
            "Status": result["Status"],
            "Notes": result["Notes"]
        })

    # Add visualization workflow test results
    for workflow in visualization_workflow_tester.results["workflow_results"]:
        for step in workflow["steps"]:
            combined_results.append({
                "Test Suite": "Visualization Workflows",
                "Component": workflow["workflow_name"],
                "Category": "Workflow Steps",
                "Test": step["step_name"],
                "Status": "Pass" if step["status"] else "Fail",
                "Notes": step["notes"]
            })

    # Add cross-component workflow test results
    for workflow in cross_component_workflow_tester.results["workflow_results"]:
        for step in workflow["steps"]:
            combined_results.append({
                "Test Suite": "Cross-Component Workflows",
                "Component": workflow["workflow_name"],
                "Category": "Workflow Steps",
                "Test": step["step_name"],
                "Status": "Pass" if step["status"] else "Fail",
                "Notes": step["notes"]
            })

    # Add performance bottleneck test results
    for test in performance_bottleneck_tester.results["performance_tests"]:
        combined_results.append({
            "Test Suite": "Performance Bottlenecks",
            "Component": test["test_name"],
            "Category": "Performance",
            "Test": "Performance Test",
            "Status": "Pass" if test["avg_duration"] <= test.get("threshold", float("inf")) else "Fail",
            "Notes": test["notes"]
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

    # Add data import/export test issues
    for issue in data_import_export_tester[1].to_dict('records'):
        combined_issues.append({
            "Test Suite": "Data Import/Export",
            "Component": issue["Component"],
            "Category": issue["Category"],
            "Test": issue["Test Name"],
            "Description": issue["Description"],
            "Severity": issue["Severity"]
        })

    # Add analysis engine test issues
    for issue in analysis_engine_tester[1].to_dict('records'):
        combined_issues.append({
            "Test Suite": "Analysis Engine",
            "Component": issue["Component"],
            "Category": issue["Category"],
            "Test": issue["Test Name"],
            "Description": issue["Description"],
            "Severity": issue["Severity"]
        })

    # Add plugin system test issues
    for issue in plugin_system_tester[1].to_dict('records'):
        combined_issues.append({
            "Test Suite": "Plugin System",
            "Component": issue["Component"],
            "Category": issue["Category"],
            "Test": issue["Test Name"],
            "Description": issue["Description"],
            "Severity": issue["Severity"]
        })

    # Add error handling test issues
    for issue in error_handling_tester[1].to_dict('records'):
        combined_issues.append({
            "Test Suite": "Error Handling",
            "Component": issue["Component"],
            "Category": issue["Category"],
            "Test": issue["Test Name"],
            "Description": issue["Description"],
            "Severity": issue["Severity"]
        })

    # Add state management test issues
    for issue in state_management_tester[1].to_dict('records'):
        combined_issues.append({
            "Test Suite": "State Management",
            "Component": issue["Component"],
            "Category": issue["Category"],
            "Test": issue["Test Name"],
            "Description": issue["Description"],
            "Severity": issue["Severity"]
        })

    # Add visualization workflow test issues
    for issue in visualization_workflow_tester.results["issues"]:
        combined_issues.append({
            "Test Suite": "Visualization Workflows",
            "Component": issue["workflow_name"],
            "Category": "Workflow",
            "Test": issue["step_name"],
            "Description": issue["description"],
            "Severity": issue["severity"]
        })

    # Add cross-component workflow test issues
    for issue in cross_component_workflow_tester.results["issues"]:
        combined_issues.append({
            "Test Suite": "Cross-Component Workflows",
            "Component": issue["workflow_name"],
            "Category": "Workflow",
            "Test": issue["step_name"],
            "Description": issue["description"],
            "Severity": issue["severity"]
        })

    # Add performance bottleneck issues
    for bottleneck in performance_bottleneck_tester.results["bottlenecks"]:
        combined_issues.append({
            "Test Suite": "Performance Bottlenecks",
            "Component": bottleneck["component"],
            "Category": "Performance",
            "Test": "Performance Test",
            "Description": bottleneck["description"],
            "Severity": bottleneck["severity"]
        })

    # Create DataFrame from combined issues
    combined_issues_df = pd.DataFrame(combined_issues)

    # Save combined issues to CSV
    combined_issues_df.to_csv("science_data_kit/ui/tests/results/combined_test_issues.csv", index=False)

    # Save component interactions to CSV
    interactions_df = cross_component_workflow_tester.generate_interactions_report("science_data_kit/ui/tests/results/component_interactions.csv")

    # Print summary
    print("\n=== All Test Suites Completed ===")
    print(f"Total Test Duration: {test_duration:.2f} seconds")
    print(f"Total Tests Run: {len(combined_df)}")
    print(f"Total Issues Found: {len(combined_issues_df)}")
    print(f"Total Component Interactions Recorded: {len(interactions_df)}")
    print(f"Total Performance Bottlenecks Identified: {len(performance_bottleneck_tester.results['bottlenecks'])}")
    print(f"Results saved to science_data_kit/ui/tests/results/combined_test_results.csv")
    print(f"Issues saved to science_data_kit/ui/tests/results/combined_test_issues.csv")
    print(f"Component Interactions saved to science_data_kit/ui/tests/results/component_interactions.csv")
    print(f"Performance Bottlenecks saved to science_data_kit/ui/tests/results/performance_bottlenecks.csv")

    # Return summary statistics
    return {
        "total_tests": len(combined_df),
        "total_issues": len(combined_issues_df),
        "total_interactions": len(interactions_df),
        "total_bottlenecks": len(performance_bottleneck_tester.results['bottlenecks']),
        "test_duration": test_duration,
        "results_df": combined_df,
        "issues_df": combined_issues_df,
        "interactions_df": interactions_df,
        "bottlenecks_df": bottlenecks_df
    }

if __name__ == "__main__":
    main()
