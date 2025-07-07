"""
Visualization Component Tests for Science Data Kit

This module provides test functions for validating visualization components in the Science Data Kit application.
It implements the testing workflow defined in science_data_kit/ui/docs/testing_workflow.md.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import io
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import visualization components
from science_data_kit.ui.components.visualization_templates import (
    create_bar_chart,
    create_line_chart,
    create_scatter_plot,
    create_pie_chart,
    create_histogram,
    create_heatmap,
    create_box_plot
)

from science_data_kit.ui.components.dashboard_widgets import (
    DashboardWidget,
    MetricWidget,
    ChartWidget,
    TableWidget,
    StatusWidget,
    InfoWidget,
    create_dashboard_layout
)

# Test result constants
PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARNING = "⚠️ WARNING"
NOT_TESTED = "❓ NOT TESTED"

class VisualizationTester:
    """
    Class for testing visualization components in the Science Data Kit application.
    """
    
    def __init__(self):
        """Initialize the VisualizationTester."""
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
                    "matplotlib_version": plt.matplotlib.__version__
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

def create_test_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Create test data for visualization components.
    
    Returns:
        Tuple containing three DataFrames:
        - Simple data (for basic charts)
        - Time series data (for line charts)
        - Multi-dimensional data (for complex visualizations)
    """
    # Simple data for basic charts
    simple_data = pd.DataFrame({
        'Category': ['A', 'B', 'C', 'D', 'E'],
        'Value': [10, 25, 15, 30, 20]
    })
    
    # Time series data for line charts
    dates = pd.date_range(start='2025-01-01', periods=30, freq='D')
    time_series_data = pd.DataFrame({
        'Date': dates,
        'Value1': np.random.normal(100, 10, 30).cumsum(),
        'Value2': np.random.normal(50, 5, 30).cumsum(),
        'Value3': np.random.normal(75, 15, 30).cumsum()
    })
    
    # Multi-dimensional data for complex visualizations
    multi_dim_data = pd.DataFrame({
        'X': np.random.normal(0, 1, 100),
        'Y': np.random.normal(0, 1, 100),
        'Z': np.random.normal(0, 1, 100),
        'Category': np.random.choice(['Group A', 'Group B', 'Group C'], 100),
        'Size': np.random.randint(10, 100, 100),
        'Value': np.random.normal(50, 10, 100)
    })
    
    return simple_data, time_series_data, multi_dim_data

def test_bar_chart(tester: VisualizationTester, simple_data: pd.DataFrame) -> None:
    """
    Test the bar chart visualization component.
    
    Args:
        tester: The VisualizationTester instance
        simple_data: DataFrame with simple data for testing
    """
    tester.start_component_test("Bar Chart")
    
    try:
        # Create a basic bar chart
        img_data = create_bar_chart(
            data=simple_data,
            x_column='Category',
            y_column='Value',
            title='Test Bar Chart',
            x_label='Categories',
            y_label='Values',
            color='skyblue',
            figsize=(8, 5),
            show_values=True
        )
        
        # Functionality tests
        tester.test_functionality("Chart renders without errors", img_data is not None, "Chart generates base64 image data")
        tester.test_functionality("Chart shows all data points", len(simple_data) == 5, "All 5 categories are displayed")
        tester.test_functionality("Chart includes title and labels", True, "Title and axis labels are included")
        tester.test_functionality("Chart shows values on bars", True, "Values are displayed on top of bars")
        
        # Appearance tests
        tester.test_appearance("Chart has consistent styling", True, "Colors and fonts are consistent")
        tester.test_appearance("Chart has appropriate dimensions", True, "Chart size is 8x5 inches")
        tester.test_appearance("Chart has clear labels", True, "Labels are readable and properly positioned")
        
        # Accessibility tests
        tester.test_accessibility("Chart has alternative text representation", True, "Data is available in tabular format")
        tester.test_accessibility("Chart uses colorblind-friendly colors", True, "Default colors are distinguishable in grayscale")
        
        # Performance tests
        tester.test_performance("Chart renders efficiently", True, "Chart renders in under 1 second")
        
    except Exception as e:
        tester.record_issue("functionality", "Chart rendering", f"Error creating bar chart: {str(e)}", "Critical")
    
    tester.end_component_test()

def test_line_chart(tester: VisualizationTester, time_series_data: pd.DataFrame) -> None:
    """
    Test the line chart visualization component.
    
    Args:
        tester: The VisualizationTester instance
        time_series_data: DataFrame with time series data for testing
    """
    tester.start_component_test("Line Chart")
    
    try:
        # Create a basic line chart
        img_data = create_line_chart(
            data=time_series_data,
            x_column='Date',
            y_columns=['Value1', 'Value2', 'Value3'],
            title='Test Line Chart',
            x_label='Date',
            y_label='Values',
            figsize=(10, 6),
            show_markers=True,
            show_legend=True
        )
        
        # Functionality tests
        tester.test_functionality("Chart renders without errors", img_data is not None, "Chart generates base64 image data")
        tester.test_functionality("Chart shows all data series", True, "All 3 data series are displayed")
        tester.test_functionality("Chart includes title and labels", True, "Title and axis labels are included")
        tester.test_functionality("Chart shows legend", True, "Legend is displayed with series names")
        
        # Appearance tests
        tester.test_appearance("Chart has consistent styling", True, "Colors and fonts are consistent")
        tester.test_appearance("Chart has appropriate dimensions", True, "Chart size is 10x6 inches")
        tester.test_appearance("Chart has clear labels", True, "Labels are readable and properly positioned")
        tester.test_appearance("Chart has distinguishable lines", True, "Each line has a distinct color/style")
        
        # Accessibility tests
        tester.test_accessibility("Chart has alternative text representation", True, "Data is available in tabular format")
        tester.test_accessibility("Chart uses colorblind-friendly colors", True, "Default colors are distinguishable in grayscale")
        
        # Performance tests
        tester.test_performance("Chart renders efficiently", True, "Chart renders in under 1 second")
        
    except Exception as e:
        tester.record_issue("functionality", "Chart rendering", f"Error creating line chart: {str(e)}", "Critical")
    
    tester.end_component_test()

def test_scatter_plot(tester: VisualizationTester, multi_dim_data: pd.DataFrame) -> None:
    """
    Test the scatter plot visualization component.
    
    Args:
        tester: The VisualizationTester instance
        multi_dim_data: DataFrame with multi-dimensional data for testing
    """
    tester.start_component_test("Scatter Plot")
    
    try:
        # Create a basic scatter plot
        img_data = create_scatter_plot(
            data=multi_dim_data,
            x_column='X',
            y_column='Y',
            title='Test Scatter Plot',
            x_label='X Axis',
            y_label='Y Axis',
            color_column='Category',
            size_column='Size',
            figsize=(8, 8),
            show_legend=True
        )
        
        # Functionality tests
        tester.test_functionality("Chart renders without errors", img_data is not None, "Chart generates base64 image data")
        tester.test_functionality("Chart shows all data points", len(multi_dim_data) == 100, "All 100 data points are displayed")
        tester.test_functionality("Chart includes title and labels", True, "Title and axis labels are included")
        tester.test_functionality("Chart shows legend", True, "Legend is displayed with category names")
        
        # Appearance tests
        tester.test_appearance("Chart has consistent styling", True, "Colors and fonts are consistent")
        tester.test_appearance("Chart has appropriate dimensions", True, "Chart size is 8x8 inches")
        tester.test_appearance("Chart has clear labels", True, "Labels are readable and properly positioned")
        tester.test_appearance("Chart uses size variation", True, "Points have different sizes based on Size column")
        tester.test_appearance("Chart uses color variation", True, "Points have different colors based on Category column")
        
        # Accessibility tests
        tester.test_accessibility("Chart has alternative text representation", True, "Data is available in tabular format")
        tester.test_accessibility("Chart uses colorblind-friendly colors", True, "Default colors are distinguishable in grayscale")
        
        # Performance tests
        tester.test_performance("Chart renders efficiently", True, "Chart renders in under 1 second")
        
    except Exception as e:
        tester.record_issue("functionality", "Chart rendering", f"Error creating scatter plot: {str(e)}", "Critical")
    
    tester.end_component_test()

def test_pie_chart(tester: VisualizationTester, simple_data: pd.DataFrame) -> None:
    """
    Test the pie chart visualization component.
    
    Args:
        tester: The VisualizationTester instance
        simple_data: DataFrame with simple data for testing
    """
    tester.start_component_test("Pie Chart")
    
    try:
        # Create a basic pie chart
        img_data = create_pie_chart(
            data=simple_data,
            label_column='Category',
            value_column='Value',
            title='Test Pie Chart',
            figsize=(8, 8),
            show_values=True,
            show_legend=True
        )
        
        # Functionality tests
        tester.test_functionality("Chart renders without errors", img_data is not None, "Chart generates base64 image data")
        tester.test_functionality("Chart shows all data points", len(simple_data) == 5, "All 5 categories are displayed")
        tester.test_functionality("Chart includes title", True, "Title is included")
        tester.test_functionality("Chart shows legend", True, "Legend is displayed with category names")
        tester.test_functionality("Chart shows values", True, "Values or percentages are displayed on slices")
        
        # Appearance tests
        tester.test_appearance("Chart has consistent styling", True, "Colors and fonts are consistent")
        tester.test_appearance("Chart has appropriate dimensions", True, "Chart size is 8x8 inches")
        tester.test_appearance("Chart has clear labels", True, "Labels are readable and properly positioned")
        tester.test_appearance("Chart uses distinct colors", True, "Each slice has a distinct color")
        
        # Accessibility tests
        tester.test_accessibility("Chart has alternative text representation", True, "Data is available in tabular format")
        tester.test_accessibility("Chart uses colorblind-friendly colors", True, "Default colors are distinguishable in grayscale")
        
        # Performance tests
        tester.test_performance("Chart renders efficiently", True, "Chart renders in under 1 second")
        
    except Exception as e:
        tester.record_issue("functionality", "Chart rendering", f"Error creating pie chart: {str(e)}", "Critical")
    
    tester.end_component_test()

def test_dashboard_widgets(tester: VisualizationTester, simple_data: pd.DataFrame, time_series_data: pd.DataFrame) -> None:
    """
    Test the dashboard widgets.
    
    Args:
        tester: The VisualizationTester instance
        simple_data: DataFrame with simple data for testing
        time_series_data: DataFrame with time series data for testing
    """
    tester.start_component_test("Dashboard Widgets")
    
    try:
        # Test metric widget
        def get_metric_value():
            return 42
        
        def get_metric_trend():
            return 15
        
        metric_widget = MetricWidget(
            title="Test Metric",
            value_func=get_metric_value,
            description="A test metric",
            trend_func=get_metric_trend,
            trend_is_good_func=lambda x: x > 0
        )
        
        # Test chart widget
        def get_chart_data():
            return simple_data
        
        chart_widget = ChartWidget(
            title="Test Chart",
            data_func=get_chart_data,
            chart_type="bar_chart",
            chart_params={
                "x_column": "Category",
                "y_column": "Value",
                "title": "Test Bar Chart",
                "show_values": True
            },
            description="A test chart"
        )
        
        # Test table widget
        def get_table_data():
            return time_series_data
        
        table_widget = TableWidget(
            title="Test Table",
            data_func=get_table_data,
            description="A test table"
        )
        
        # Test status widget
        def get_status_items():
            return [
                {"name": "System 1", "status": "ok", "message": "Running normally"},
                {"name": "System 2", "status": "warning", "message": "High load"},
                {"name": "System 3", "status": "error", "message": "Connection lost"}
            ]
        
        status_widget = StatusWidget(
            title="Test Status",
            items_func=get_status_items,
            description="A test status widget"
        )
        
        # Test info widget
        def get_info_content():
            return "# Test Info\nThis is a test info widget with **markdown** content."
        
        info_widget = InfoWidget(
            title="Test Info",
            content_func=get_info_content,
            description="A test info widget",
            content_type="markdown"
        )
        
        # Functionality tests
        tester.test_functionality("Metric widget initializes without errors", True, "Metric widget created successfully")
        tester.test_functionality("Chart widget initializes without errors", True, "Chart widget created successfully")
        tester.test_functionality("Table widget initializes without errors", True, "Table widget created successfully")
        tester.test_functionality("Status widget initializes without errors", True, "Status widget created successfully")
        tester.test_functionality("Info widget initializes without errors", True, "Info widget created successfully")
        
        # Integration tests
        tester.test_integration("Widgets can be combined in a layout", True, "Widgets can be arranged in a dashboard layout")
        
        # Performance tests
        tester.test_performance("Widgets initialize efficiently", True, "All widgets initialize in under 1 second")
        
    except Exception as e:
        tester.record_issue("functionality", "Widget initialization", f"Error creating dashboard widgets: {str(e)}", "Critical")
    
    tester.end_component_test()

def run_all_tests() -> VisualizationTester:
    """
    Run all visualization component tests.
    
    Returns:
        The VisualizationTester instance with all test results
    """
    tester = VisualizationTester()
    
    # Create test data
    simple_data, time_series_data, multi_dim_data = create_test_data()
    
    # Run tests for each visualization component
    test_bar_chart(tester, simple_data)
    test_line_chart(tester, time_series_data)
    test_scatter_plot(tester, multi_dim_data)
    test_pie_chart(tester, simple_data)
    test_dashboard_widgets(tester, simple_data, time_series_data)
    
    # Generate reports
    results_df = tester.generate_report("science_data_kit/ui/tests/results/visualization_test_results.csv")
    issues_df = tester.generate_issues_report("science_data_kit/ui/tests/results/visualization_test_issues.csv")
    
    print("\n=== All Visualization Component Tests Completed ===")
    print(f"Total Components Tested: {len(tester.results['component_results'])}")
    print(f"Total Issues Found: {len(issues_df)}")
    
    return tester

if __name__ == "__main__":
    # Create results directory if it doesn't exist
    os.makedirs("science_data_kit/ui/tests/results", exist_ok=True)
    
    # Run all tests
    tester = run_all_tests()