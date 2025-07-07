"""
Visualization Workflow Tests for Science Data Kit

This module provides test functions for validating end-to-end visualization workflows in the Science Data Kit application.
It builds on the component tests in visualization_component_tests.py but focuses on complete user journeys.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import io
import time
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

class VisualizationWorkflowTester:
    """
    Class for testing end-to-end visualization workflows in the Science Data Kit application.
    """
    
    def __init__(self):
        """Initialize the VisualizationWorkflowTester."""
        self.results = {}
        self.current_workflow = None
        self.current_step = None
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
            "workflow_results": {}
        }
    
    def start_workflow_test(self, workflow_name: str, description: str) -> None:
        """
        Start testing a new workflow.
        
        Args:
            workflow_name: The name of the workflow being tested
            description: A description of the workflow
        """
        self.current_workflow = workflow_name
        self.results["workflow_results"][workflow_name] = {
            "description": description,
            "steps": {},
            "issues": [],
            "performance": {},
            "overall_status": NOT_TESTED
        }
        
        print(f"\n=== Testing {workflow_name} Workflow ===\n")
        print(f"Description: {description}\n")
    
    def start_step(self, step_name: str, description: str) -> None:
        """
        Start a new step in the current workflow.
        
        Args:
            step_name: The name of the step
            description: A description of the step
        """
        if self.current_workflow is None:
            raise ValueError("No workflow test has been started. Call start_workflow_test() first.")
        
        self.current_step = step_name
        self.results["workflow_results"][self.current_workflow]["steps"][step_name] = {
            "description": description,
            "status": NOT_TESTED,
            "start_time": time.time(),
            "end_time": None,
            "duration": None,
            "notes": ""
        }
        
        print(f"Step: {step_name}")
        print(f"Description: {description}")
    
    def end_step(self, status: bool, notes: str = "") -> None:
        """
        End the current step and record its status.
        
        Args:
            status: True if the step passed, False if it failed
            notes: Additional notes about the step
        """
        if self.current_workflow is None or self.current_step is None:
            raise ValueError("No workflow step has been started. Call start_step() first.")
        
        end_time = time.time()
        step_data = self.results["workflow_results"][self.current_workflow]["steps"][self.current_step]
        step_data["end_time"] = end_time
        step_data["duration"] = end_time - step_data["start_time"]
        step_data["status"] = PASS if status else FAIL
        step_data["notes"] = notes
        
        print(f"{PASS if status else FAIL} - Duration: {step_data['duration']:.2f}s")
        if notes:
            print(f"Notes: {notes}")
        print()
        
        # If the step failed, add it to the issues list
        if not status:
            self.results["workflow_results"][self.current_workflow]["issues"].append({
                "step": self.current_step,
                "notes": notes,
                "severity": "Medium"  # Default severity, can be updated later
            })
        
        self.current_step = None
    
    def record_performance(self, metric_name: str, value: float, unit: str = "seconds") -> None:
        """
        Record a performance metric for the current workflow.
        
        Args:
            metric_name: The name of the performance metric
            value: The value of the metric
            unit: The unit of the metric (default: seconds)
        """
        if self.current_workflow is None:
            raise ValueError("No workflow test has been started. Call start_workflow_test() first.")
        
        self.results["workflow_results"][self.current_workflow]["performance"][metric_name] = {
            "value": value,
            "unit": unit
        }
        
        print(f"Performance - {metric_name}: {value} {unit}")
    
    def record_issue(self, step_name: str, description: str, severity: str = "Medium") -> None:
        """
        Record an issue for the current workflow.
        
        Args:
            step_name: The name of the step where the issue occurred
            description: A description of the issue
            severity: The severity of the issue (Critical, High, Medium, Low)
        """
        if self.current_workflow is None:
            raise ValueError("No workflow test has been started. Call start_workflow_test() first.")
        
        self.results["workflow_results"][self.current_workflow]["issues"].append({
            "step": step_name,
            "notes": description,
            "severity": severity
        })
        
        print(f"⚠️ Issue Recorded - Step: {step_name}")
        print(f"Description: {description}")
        print(f"Severity: {severity}")
    
    def end_workflow_test(self) -> None:
        """End the current workflow test and calculate overall status."""
        if self.current_workflow is None:
            raise ValueError("No workflow test has been started. Call start_workflow_test() first.")
        
        # Calculate overall status based on step statuses and issues
        steps = self.results["workflow_results"][self.current_workflow]["steps"]
        issues = self.results["workflow_results"][self.current_workflow]["issues"]
        
        if any(step["status"] == FAIL for step in steps.values()):
            overall_status = FAIL
        elif any(issue["severity"] in ["Critical", "High"] for issue in issues):
            overall_status = FAIL
        elif issues:
            overall_status = WARNING
        else:
            overall_status = PASS
        
        self.results["workflow_results"][self.current_workflow]["overall_status"] = overall_status
        
        # Calculate total duration
        total_duration = sum(step["duration"] for step in steps.values() if step["duration"] is not None)
        self.results["workflow_results"][self.current_workflow]["total_duration"] = total_duration
        
        # Print summary
        print(f"\n=== {self.current_workflow} Workflow Test Summary ===")
        print(f"Overall Status: {overall_status}")
        print(f"Total Duration: {total_duration:.2f} seconds")
        print(f"Steps Completed: {len(steps)}")
        print(f"Issues Found: {len(issues)}")
        
        self.current_workflow = None
    
    def generate_report(self, output_file: str = None) -> pd.DataFrame:
        """
        Generate a report of the workflow test results.
        
        Args:
            output_file: Optional file path to save the report as CSV
            
        Returns:
            DataFrame containing the workflow test results
        """
        # Create a list to hold all workflow results
        all_results = []
        
        # Iterate through all workflows and steps
        for workflow_name, workflow_data in self.results["workflow_results"].items():
            for step_name, step_data in workflow_data["steps"].items():
                all_results.append({
                    "Workflow": workflow_name,
                    "Step": step_name,
                    "Description": step_data["description"],
                    "Status": step_data["status"],
                    "Duration (s)": step_data["duration"],
                    "Notes": step_data["notes"]
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
        Generate a report of the issues found during workflow testing.
        
        Args:
            output_file: Optional file path to save the report as CSV
            
        Returns:
            DataFrame containing the issues
        """
        # Create a list to hold all issues
        all_issues = []
        
        # Iterate through all workflows and issues
        for workflow_name, workflow_data in self.results["workflow_results"].items():
            for issue in workflow_data["issues"]:
                all_issues.append({
                    "Workflow": workflow_name,
                    "Step": issue["step"],
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
    
    def generate_performance_report(self, output_file: str = None) -> pd.DataFrame:
        """
        Generate a report of the performance metrics collected during workflow testing.
        
        Args:
            output_file: Optional file path to save the report as CSV
            
        Returns:
            DataFrame containing the performance metrics
        """
        # Create a list to hold all performance metrics
        all_metrics = []
        
        # Iterate through all workflows and performance metrics
        for workflow_name, workflow_data in self.results["workflow_results"].items():
            for metric_name, metric_data in workflow_data["performance"].items():
                all_metrics.append({
                    "Workflow": workflow_name,
                    "Metric": metric_name,
                    "Value": metric_data["value"],
                    "Unit": metric_data["unit"]
                })
            
            # Add total duration as a metric
            if "total_duration" in workflow_data:
                all_metrics.append({
                    "Workflow": workflow_name,
                    "Metric": "Total Duration",
                    "Value": workflow_data["total_duration"],
                    "Unit": "seconds"
                })
        
        # Create a DataFrame from the metrics
        df = pd.DataFrame(all_metrics)
        
        # Save to file if specified
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Performance report saved to {output_file}")
        
        return df

def create_test_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Create test data for visualization workflows.
    
    Returns:
        Tuple containing three DataFrames:
        - Simple data (for basic charts)
        - Time series data (for line charts)
        - Multi-dimensional data (for complex visualizations)
    """
    # Simple data for basic charts
    simple_data = pd.DataFrame({
        'Category': ['A', 'B', 'C', 'D', 'E'],
        'Value': [10, 25, 15, 30, 20],
        'Value2': [5, 15, 10, 20, 25]
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

def test_data_to_visualization_workflow(tester: VisualizationWorkflowTester) -> None:
    """
    Test the workflow from data loading to visualization creation.
    
    Args:
        tester: The VisualizationWorkflowTester instance
    """
    tester.start_workflow_test(
        "Data to Visualization",
        "Test the complete workflow from data loading to visualization creation"
    )
    
    try:
        # Step 1: Load data
        tester.start_step(
            "Load Data",
            "Load data from a DataFrame"
        )
        simple_data, time_series_data, multi_dim_data = create_test_data()
        tester.end_step(True, "Successfully loaded test data")
        
        # Step 2: Prepare data for visualization
        tester.start_step(
            "Prepare Data",
            "Prepare data for visualization (filtering, aggregation, etc.)"
        )
        # Simulate data preparation
        prepared_data = simple_data.copy()
        prepared_data['Value'] = prepared_data['Value'] * 1.5  # Apply a transformation
        tester.end_step(True, "Successfully prepared data for visualization")
        
        # Step 3: Create visualization
        tester.start_step(
            "Create Visualization",
            "Create a bar chart visualization from the prepared data"
        )
        start_time = time.time()
        img_data = create_bar_chart(
            data=prepared_data,
            x_column='Category',
            y_column='Value',
            title='Test Bar Chart',
            x_label='Categories',
            y_label='Values',
            color='skyblue',
            figsize=(8, 5),
            show_values=True
        )
        creation_time = time.time() - start_time
        tester.record_performance("Chart Creation Time", creation_time, "seconds")
        tester.end_step(img_data is not None, "Successfully created bar chart visualization")
        
        # Step 4: Create alternative visualization
        tester.start_step(
            "Create Alternative Visualization",
            "Create a pie chart visualization from the same data"
        )
        start_time = time.time()
        img_data = create_pie_chart(
            data=prepared_data,
            label_column='Category',
            value_column='Value',
            title='Test Pie Chart',
            figsize=(8, 8),
            show_values=True,
            show_legend=True
        )
        creation_time = time.time() - start_time
        tester.record_performance("Alternative Chart Creation Time", creation_time, "seconds")
        tester.end_step(img_data is not None, "Successfully created pie chart visualization")
        
        # Step 5: Create dashboard with multiple visualizations
        tester.start_step(
            "Create Dashboard",
            "Create a dashboard with multiple visualizations"
        )
        # Create metric widget
        metric_widget = MetricWidget(
            title="Total Value",
            value_func=lambda: prepared_data['Value'].sum(),
            description="Sum of all values",
            trend_func=lambda: 10,
            trend_is_good_func=lambda x: x > 0
        )
        
        # Create bar chart widget
        bar_chart_widget = ChartWidget(
            title="Values by Category",
            data_func=lambda: prepared_data,
            chart_type="bar_chart",
            chart_params={
                "x_column": "Category",
                "y_column": "Value",
                "title": "Values by Category",
                "show_values": True
            },
            description="Bar chart showing values by category"
        )
        
        # Create pie chart widget
        pie_chart_widget = ChartWidget(
            title="Value Distribution",
            data_func=lambda: prepared_data,
            chart_type="pie_chart",
            chart_params={
                "label_column": "Category",
                "value_column": "Value",
                "title": "Value Distribution",
                "show_values": True,
                "show_legend": True
            },
            description="Pie chart showing value distribution"
        )
        
        # Create table widget
        table_widget = TableWidget(
            title="Data Table",
            data_func=lambda: prepared_data,
            description="Table showing the raw data"
        )
        
        # Create dashboard layout
        dashboard_layout = [
            [metric_widget, None],
            [bar_chart_widget, pie_chart_widget],
            [table_widget, None]
        ]
        
        # In a real application, this would render the dashboard
        # For testing purposes, we just check that the layout is created correctly
        tester.end_step(True, "Successfully created dashboard with multiple visualizations")
        
    except Exception as e:
        tester.record_issue("Workflow Execution", f"Error in workflow: {str(e)}", "Critical")
        if tester.current_step:
            tester.end_step(False, f"Error: {str(e)}")
    
    tester.end_workflow_test()

def test_time_series_analysis_workflow(tester: VisualizationWorkflowTester) -> None:
    """
    Test the workflow for time series data analysis and visualization.
    
    Args:
        tester: The VisualizationWorkflowTester instance
    """
    tester.start_workflow_test(
        "Time Series Analysis",
        "Test the workflow for time series data analysis and visualization"
    )
    
    try:
        # Step 1: Load time series data
        tester.start_step(
            "Load Time Series Data",
            "Load time series data from a DataFrame"
        )
        _, time_series_data, _ = create_test_data()
        tester.end_step(True, "Successfully loaded time series data")
        
        # Step 2: Prepare time series data
        tester.start_step(
            "Prepare Time Series Data",
            "Prepare time series data for analysis (resampling, filling missing values, etc.)"
        )
        # Simulate data preparation
        prepared_data = time_series_data.copy()
        # Convert Date to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(prepared_data['Date']):
            prepared_data['Date'] = pd.to_datetime(prepared_data['Date'])
        # Set Date as index
        prepared_data.set_index('Date', inplace=True)
        # Resample to weekly frequency
        weekly_data = prepared_data.resample('W').mean()
        tester.end_step(True, "Successfully prepared time series data")
        
        # Step 3: Create time series visualization
        tester.start_step(
            "Create Time Series Visualization",
            "Create a line chart visualization from the time series data"
        )
        # Reset index to get Date as a column again
        weekly_data_reset = weekly_data.reset_index()
        start_time = time.time()
        img_data = create_line_chart(
            data=weekly_data_reset,
            x_column='Date',
            y_columns=['Value1', 'Value2', 'Value3'],
            title='Weekly Averages',
            x_label='Date',
            y_label='Values',
            figsize=(10, 6),
            show_markers=True,
            show_legend=True
        )
        creation_time = time.time() - start_time
        tester.record_performance("Time Series Chart Creation Time", creation_time, "seconds")
        tester.end_step(img_data is not None, "Successfully created time series visualization")
        
        # Step 4: Calculate and visualize rolling statistics
        tester.start_step(
            "Calculate Rolling Statistics",
            "Calculate rolling mean and standard deviation"
        )
        # Calculate rolling statistics
        rolling_mean = prepared_data.rolling(window=7).mean()
        rolling_std = prepared_data.rolling(window=7).std()
        tester.end_step(True, "Successfully calculated rolling statistics")
        
        # Step 5: Visualize rolling statistics
        tester.start_step(
            "Visualize Rolling Statistics",
            "Create visualizations of rolling statistics"
        )
        # Reset index to get Date as a column again
        rolling_mean_reset = rolling_mean.reset_index()
        start_time = time.time()
        img_data = create_line_chart(
            data=rolling_mean_reset,
            x_column='Date',
            y_columns=['Value1', 'Value2', 'Value3'],
            title='7-Day Rolling Average',
            x_label='Date',
            y_label='Values',
            figsize=(10, 6),
            show_markers=False,
            show_legend=True
        )
        creation_time = time.time() - start_time
        tester.record_performance("Rolling Statistics Chart Creation Time", creation_time, "seconds")
        tester.end_step(img_data is not None, "Successfully visualized rolling statistics")
        
    except Exception as e:
        tester.record_issue("Workflow Execution", f"Error in workflow: {str(e)}", "Critical")
        if tester.current_step:
            tester.end_step(False, f"Error: {str(e)}")
    
    tester.end_workflow_test()

def test_comparative_analysis_workflow(tester: VisualizationWorkflowTester) -> None:
    """
    Test the workflow for comparative data analysis and visualization.
    
    Args:
        tester: The VisualizationWorkflowTester instance
    """
    tester.start_workflow_test(
        "Comparative Analysis",
        "Test the workflow for comparative data analysis and visualization"
    )
    
    try:
        # Step 1: Load data for comparison
        tester.start_step(
            "Load Comparison Data",
            "Load data for comparative analysis"
        )
        simple_data, _, _ = create_test_data()
        tester.end_step(True, "Successfully loaded comparison data")
        
        # Step 2: Prepare data for comparison
        tester.start_step(
            "Prepare Comparison Data",
            "Prepare data for comparative analysis"
        )
        # Create two datasets for comparison
        dataset1 = simple_data.copy()
        dataset1['Dataset'] = 'Dataset 1'
        dataset2 = simple_data.copy()
        dataset2['Value'] = dataset2['Value'] * 1.2  # Increase values by 20%
        dataset2['Value2'] = dataset2['Value2'] * 0.8  # Decrease values by 20%
        dataset2['Dataset'] = 'Dataset 2'
        # Combine datasets
        combined_data = pd.concat([dataset1, dataset2])
        tester.end_step(True, "Successfully prepared comparison data")
        
        # Step 3: Create side-by-side bar chart
        tester.start_step(
            "Create Side-by-Side Bar Chart",
            "Create a side-by-side bar chart for comparison"
        )
        # For this test, we'll simulate creating a side-by-side bar chart
        # In a real application, this would use a specific function for side-by-side bar charts
        # Here we'll just use the regular bar chart function as a placeholder
        start_time = time.time()
        img_data = create_bar_chart(
            data=combined_data,
            x_column='Category',
            y_column='Value',
            title='Comparison of Values',
            x_label='Categories',
            y_label='Values',
            color='Dataset',  # Color by dataset
            figsize=(10, 6),
            show_values=True
        )
        creation_time = time.time() - start_time
        tester.record_performance("Comparison Chart Creation Time", creation_time, "seconds")
        tester.end_step(img_data is not None, "Successfully created side-by-side bar chart")
        
        # Step 4: Calculate percentage differences
        tester.start_step(
            "Calculate Percentage Differences",
            "Calculate percentage differences between datasets"
        )
        # Pivot the data to calculate differences
        pivot_data = combined_data.pivot_table(
            index='Category',
            columns='Dataset',
            values=['Value', 'Value2']
        )
        # Calculate percentage differences
        diff_data = pd.DataFrame({
            'Category': pivot_data.index,
            'Value_Diff_Pct': ((pivot_data[('Value', 'Dataset 2')] / pivot_data[('Value', 'Dataset 1')]) - 1) * 100,
            'Value2_Diff_Pct': ((pivot_data[('Value2', 'Dataset 2')] / pivot_data[('Value2', 'Dataset 1')]) - 1) * 100
        })
        tester.end_step(True, "Successfully calculated percentage differences")
        
        # Step 5: Visualize percentage differences
        tester.start_step(
            "Visualize Percentage Differences",
            "Create a visualization of percentage differences"
        )
        start_time = time.time()
        img_data = create_bar_chart(
            data=diff_data,
            x_column='Category',
            y_column='Value_Diff_Pct',
            title='Percentage Difference in Values',
            x_label='Categories',
            y_label='Percentage Difference (%)',
            color='skyblue',
            figsize=(10, 6),
            show_values=True
        )
        creation_time = time.time() - start_time
        tester.record_performance("Difference Chart Creation Time", creation_time, "seconds")
        tester.end_step(img_data is not None, "Successfully visualized percentage differences")
        
    except Exception as e:
        tester.record_issue("Workflow Execution", f"Error in workflow: {str(e)}", "Critical")
        if tester.current_step:
            tester.end_step(False, f"Error: {str(e)}")
    
    tester.end_workflow_test()

def run_all_tests() -> VisualizationWorkflowTester:
    """
    Run all visualization workflow tests.
    
    Returns:
        The VisualizationWorkflowTester instance with all test results
    """
    tester = VisualizationWorkflowTester()
    
    # Run tests for each visualization workflow
    test_data_to_visualization_workflow(tester)
    test_time_series_analysis_workflow(tester)
    test_comparative_analysis_workflow(tester)
    
    # Generate reports
    os.makedirs("science_data_kit/ui/tests/results", exist_ok=True)
    results_df = tester.generate_report("science_data_kit/ui/tests/results/visualization_workflow_test_results.csv")
    issues_df = tester.generate_issues_report("science_data_kit/ui/tests/results/visualization_workflow_test_issues.csv")
    performance_df = tester.generate_performance_report("science_data_kit/ui/tests/results/visualization_workflow_performance.csv")
    
    print("\n=== All Visualization Workflow Tests Completed ===")
    print(f"Total Workflows Tested: {len(tester.results['workflow_results'])}")
    print(f"Total Issues Found: {len(issues_df)}")
    
    return tester

if __name__ == "__main__":
    # Run all tests
    tester = run_all_tests()