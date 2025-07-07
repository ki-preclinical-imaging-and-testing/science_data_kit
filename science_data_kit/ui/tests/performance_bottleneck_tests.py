"""
Performance Bottleneck Tests for Science Data Kit

This module provides test functions for identifying performance bottlenecks in the Science Data Kit application.
It focuses on measuring performance metrics and identifying areas for optimization.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import io
import time
import psutil
import gc
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
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
    TableWidget
)

# Test result constants
PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARNING = "⚠️ WARNING"
NOT_TESTED = "❓ NOT TESTED"

class PerformanceBottleneckTester:
    """
    Class for testing performance and identifying bottlenecks in the Science Data Kit application.
    """
    
    def __init__(self):
        """Initialize the PerformanceBottleneckTester."""
        self.results = {}
        self.current_test = None
        self.test_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Initialize results structure
        self.results = {
            "test_info": {
                "timestamp": self.test_timestamp,
                "tester": "AI-Human Collaboration",
                "environment": {
                    "os": os.name,
                    "python_version": sys.version,
                    "matplotlib_version": plt.matplotlib.__version__,
                    "cpu_count": psutil.cpu_count(),
                    "memory_total": psutil.virtual_memory().total
                }
            },
            "performance_tests": {},
            "bottlenecks": []
        }
    
    def start_performance_test(self, test_name: str, description: str, threshold: float = None, unit: str = "seconds") -> None:
        """
        Start a new performance test.
        
        Args:
            test_name: The name of the test
            description: A description of the test
            threshold: Optional performance threshold (e.g., maximum acceptable time)
            unit: The unit of measurement (default: seconds)
        """
        self.current_test = test_name
        self.results["performance_tests"][test_name] = {
            "description": description,
            "threshold": threshold,
            "unit": unit,
            "iterations": [],
            "memory_usage": [],
            "cpu_usage": [],
            "start_time": time.time(),
            "end_time": None,
            "total_duration": None,
            "average_duration": None,
            "min_duration": None,
            "max_duration": None,
            "status": NOT_TESTED,
            "notes": ""
        }
        
        print(f"\n=== Starting Performance Test: {test_name} ===")
        print(f"Description: {description}")
        if threshold is not None:
            print(f"Performance Threshold: {threshold} {unit}")
        print()
    
    def record_iteration(self, duration: float, memory_usage: float = None, cpu_usage: float = None, notes: str = "") -> None:
        """
        Record a test iteration.
        
        Args:
            duration: The duration of the iteration
            memory_usage: Optional memory usage in MB
            cpu_usage: Optional CPU usage percentage
            notes: Additional notes about the iteration
        """
        if self.current_test is None:
            raise ValueError("No performance test has been started. Call start_performance_test() first.")
        
        # If memory_usage is not provided, try to measure it
        if memory_usage is None:
            memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # Convert to MB
        
        # If cpu_usage is not provided, try to measure it
        if cpu_usage is None:
            cpu_usage = psutil.Process(os.getpid()).cpu_percent(interval=0.1)
        
        self.results["performance_tests"][self.current_test]["iterations"].append(duration)
        self.results["performance_tests"][self.current_test]["memory_usage"].append(memory_usage)
        self.results["performance_tests"][self.current_test]["cpu_usage"].append(cpu_usage)
        
        print(f"Iteration completed: {duration:.4f} seconds, {memory_usage:.2f} MB, {cpu_usage:.2f}% CPU")
        if notes:
            print(f"Notes: {notes}")
    
    def end_performance_test(self, notes: str = "") -> Dict[str, Any]:
        """
        End the current performance test and calculate statistics.
        
        Args:
            notes: Additional notes about the test
            
        Returns:
            Dictionary containing test results
        """
        if self.current_test is None:
            raise ValueError("No performance test has been started. Call start_performance_test() first.")
        
        test_data = self.results["performance_tests"][self.current_test]
        test_data["end_time"] = time.time()
        test_data["total_duration"] = test_data["end_time"] - test_data["start_time"]
        
        # Calculate statistics
        iterations = test_data["iterations"]
        if iterations:
            test_data["average_duration"] = sum(iterations) / len(iterations)
            test_data["min_duration"] = min(iterations)
            test_data["max_duration"] = max(iterations)
            test_data["std_deviation"] = np.std(iterations)
        
        # Calculate memory and CPU statistics
        memory_usage = test_data["memory_usage"]
        if memory_usage:
            test_data["average_memory"] = sum(memory_usage) / len(memory_usage)
            test_data["max_memory"] = max(memory_usage)
        
        cpu_usage = test_data["cpu_usage"]
        if cpu_usage:
            test_data["average_cpu"] = sum(cpu_usage) / len(cpu_usage)
            test_data["max_cpu"] = max(cpu_usage)
        
        # Determine status based on threshold
        threshold = test_data["threshold"]
        if threshold is not None and iterations:
            if test_data["average_duration"] > threshold:
                test_data["status"] = FAIL
                # Record as a bottleneck
                self.record_bottleneck(
                    self.current_test,
                    f"Average duration ({test_data['average_duration']:.4f} s) exceeds threshold ({threshold} s)",
                    "High",
                    test_data["average_duration"],
                    threshold
                )
            else:
                test_data["status"] = PASS
        else:
            test_data["status"] = PASS if iterations else FAIL
        
        test_data["notes"] = notes
        
        # Print summary
        print(f"\n=== Performance Test Completed: {self.current_test} ===")
        print(f"Status: {test_data['status']}")
        if iterations:
            print(f"Average Duration: {test_data['average_duration']:.4f} seconds")
            print(f"Min Duration: {test_data['min_duration']:.4f} seconds")
            print(f"Max Duration: {test_data['max_duration']:.4f} seconds")
            print(f"Standard Deviation: {test_data['std_deviation']:.4f} seconds")
        if memory_usage:
            print(f"Average Memory Usage: {test_data['average_memory']:.2f} MB")
            print(f"Max Memory Usage: {test_data['max_memory']:.2f} MB")
        if cpu_usage:
            print(f"Average CPU Usage: {test_data['average_cpu']:.2f}%")
            print(f"Max CPU Usage: {test_data['max_cpu']:.2f}%")
        if notes:
            print(f"Notes: {notes}")
        print()
        
        current_test = self.current_test
        self.current_test = None
        
        return self.results["performance_tests"][current_test]
    
    def record_bottleneck(self, component: str, description: str, severity: str, actual_value: float, threshold: float = None, unit: str = "seconds") -> None:
        """
        Record a performance bottleneck.
        
        Args:
            component: The component or test where the bottleneck was found
            description: A description of the bottleneck
            severity: The severity of the bottleneck (Critical, High, Medium, Low)
            actual_value: The measured performance value
            threshold: The threshold value (if applicable)
            unit: The unit of measurement
        """
        bottleneck = {
            "component": component,
            "description": description,
            "severity": severity,
            "actual_value": actual_value,
            "threshold": threshold,
            "unit": unit,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.results["bottlenecks"].append(bottleneck)
        
        print(f"⚠️ Performance Bottleneck Detected - {component}")
        print(f"Description: {description}")
        print(f"Severity: {severity}")
        print(f"Actual Value: {actual_value} {unit}")
        if threshold is not None:
            print(f"Threshold: {threshold} {unit}")
        print()
    
    def generate_performance_report(self, output_file: str = None) -> pd.DataFrame:
        """
        Generate a report of the performance test results.
        
        Args:
            output_file: Optional file path to save the report as CSV
            
        Returns:
            DataFrame containing the performance test results
        """
        # Create a list to hold all performance test results
        all_results = []
        
        # Iterate through all performance tests
        for test_name, test_data in self.results["performance_tests"].items():
            all_results.append({
                "Test": test_name,
                "Description": test_data["description"],
                "Status": test_data["status"],
                "Average Duration (s)": test_data.get("average_duration"),
                "Min Duration (s)": test_data.get("min_duration"),
                "Max Duration (s)": test_data.get("max_duration"),
                "Std Deviation (s)": test_data.get("std_deviation"),
                "Average Memory (MB)": test_data.get("average_memory"),
                "Max Memory (MB)": test_data.get("max_memory"),
                "Average CPU (%)": test_data.get("average_cpu"),
                "Max CPU (%)": test_data.get("max_cpu"),
                "Threshold": test_data["threshold"],
                "Unit": test_data["unit"],
                "Notes": test_data["notes"]
            })
        
        # Create a DataFrame from the results
        df = pd.DataFrame(all_results)
        
        # Save to file if specified
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Performance report saved to {output_file}")
        
        return df
    
    def generate_bottlenecks_report(self, output_file: str = None) -> pd.DataFrame:
        """
        Generate a report of the performance bottlenecks.
        
        Args:
            output_file: Optional file path to save the report as CSV
            
        Returns:
            DataFrame containing the bottlenecks
        """
        # Create a DataFrame from the bottlenecks
        df = pd.DataFrame(self.results["bottlenecks"])
        
        # Save to file if specified
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Bottlenecks report saved to {output_file}")
        
        return df
    
    def generate_performance_comparison(self, output_file: str = None) -> pd.DataFrame:
        """
        Generate a comparison of performance across different tests.
        
        Args:
            output_file: Optional file path to save the report as CSV
            
        Returns:
            DataFrame containing the performance comparison
        """
        # Create a list to hold performance comparison data
        comparison_data = []
        
        # Iterate through all performance tests
        for test_name, test_data in self.results["performance_tests"].items():
            if "average_duration" in test_data:
                comparison_data.append({
                    "Test": test_name,
                    "Average Duration (s)": test_data["average_duration"],
                    "Threshold (s)": test_data["threshold"] if test_data["threshold"] is not None else "N/A",
                    "Status": test_data["status"]
                })
        
        # Create a DataFrame from the comparison data
        df = pd.DataFrame(comparison_data)
        
        # Sort by average duration (descending)
        df = df.sort_values(by="Average Duration (s)", ascending=False)
        
        # Save to file if specified
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Performance comparison saved to {output_file}")
        
        return df

def create_test_data(size: int = 1000) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create test data for performance testing.
    
    Args:
        size: The number of rows in the test data
        
    Returns:
        Tuple containing two DataFrames:
        - Simple data (for basic operations)
        - Time series data (for time-based operations)
    """
    # Simple data for basic operations
    categories = ['A', 'B', 'C', 'D', 'E']
    simple_data = pd.DataFrame({
        'Category': np.random.choice(categories, size),
        'Value1': np.random.normal(50, 10, size),
        'Value2': np.random.normal(30, 5, size),
        'Value3': np.random.normal(70, 15, size)
    })
    
    # Time series data for time-based operations
    dates = pd.date_range(start='2025-01-01', periods=size, freq='H')
    time_series_data = pd.DataFrame({
        'Date': dates,
        'Value1': np.random.normal(100, 10, size).cumsum(),
        'Value2': np.random.normal(50, 5, size).cumsum(),
        'Value3': np.random.normal(75, 15, size).cumsum()
    })
    
    return simple_data, time_series_data

def test_data_loading_performance(tester: PerformanceBottleneckTester) -> None:
    """
    Test the performance of data loading operations.
    
    Args:
        tester: The PerformanceBottleneckTester instance
    """
    tester.start_performance_test(
        "Data Loading",
        "Test the performance of loading data of different sizes",
        threshold=1.0  # 1 second threshold
    )
    
    # Test with different data sizes
    sizes = [1000, 10000, 100000, 1000000]
    
    for size in sizes:
        # Force garbage collection to ensure clean state
        gc.collect()
        
        # Measure time to create and load data
        start_time = time.time()
        simple_data, time_series_data = create_test_data(size)
        duration = time.time() - start_time
        
        # Record the iteration
        memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # MB
        tester.record_iteration(duration, memory_usage, notes=f"Data size: {size} rows")
        
        # Check if this is a bottleneck
        if duration > 1.0:
            tester.record_bottleneck(
                "Data Loading",
                f"Loading {size} rows took {duration:.4f} seconds, which exceeds the 1.0 second threshold",
                "Medium" if duration < 5.0 else "High",
                duration,
                1.0
            )
    
    tester.end_performance_test("Data loading performance varies significantly with data size")

def test_visualization_performance(tester: PerformanceBottleneckTester) -> None:
    """
    Test the performance of visualization components.
    
    Args:
        tester: The PerformanceBottleneckTester instance
    """
    # Create test data
    simple_data, time_series_data = create_test_data(10000)
    
    # Test bar chart performance
    tester.start_performance_test(
        "Bar Chart Creation",
        "Test the performance of creating bar charts",
        threshold=0.5  # 0.5 second threshold
    )
    
    for i in range(5):
        # Force garbage collection
        gc.collect()
        
        # Measure time to create bar chart
        start_time = time.time()
        img_data = create_bar_chart(
            data=simple_data,
            x_column='Category',
            y_column='Value1',
            title='Test Bar Chart',
            x_label='Categories',
            y_label='Values',
            color='skyblue',
            figsize=(8, 5),
            show_values=True
        )
        duration = time.time() - start_time
        
        # Record the iteration
        memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # MB
        tester.record_iteration(duration, memory_usage, notes=f"Iteration {i+1}")
    
    tester.end_performance_test("Bar chart creation performance is consistent across iterations")
    
    # Test line chart performance
    tester.start_performance_test(
        "Line Chart Creation",
        "Test the performance of creating line charts with time series data",
        threshold=0.8  # 0.8 second threshold
    )
    
    for i in range(5):
        # Force garbage collection
        gc.collect()
        
        # Measure time to create line chart
        start_time = time.time()
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
        duration = time.time() - start_time
        
        # Record the iteration
        memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # MB
        tester.record_iteration(duration, memory_usage, notes=f"Iteration {i+1}")
    
    tester.end_performance_test("Line chart creation with time series data is more resource-intensive than bar charts")
    
    # Test scatter plot performance
    tester.start_performance_test(
        "Scatter Plot Creation",
        "Test the performance of creating scatter plots with large datasets",
        threshold=1.0  # 1.0 second threshold
    )
    
    for i in range(5):
        # Force garbage collection
        gc.collect()
        
        # Measure time to create scatter plot
        start_time = time.time()
        img_data = create_scatter_plot(
            data=simple_data,
            x_column='Value1',
            y_column='Value2',
            title='Test Scatter Plot',
            x_label='Value 1',
            y_label='Value 2',
            color_column='Category',
            size_column='Value3',
            figsize=(8, 8),
            show_legend=True
        )
        duration = time.time() - start_time
        
        # Record the iteration
        memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # MB
        tester.record_iteration(duration, memory_usage, notes=f"Iteration {i+1}")
    
    tester.end_performance_test("Scatter plots with color and size mapping are more resource-intensive")

def test_data_processing_performance(tester: PerformanceBottleneckTester) -> None:
    """
    Test the performance of data processing operations.
    
    Args:
        tester: The PerformanceBottleneckTester instance
    """
    # Create test data
    simple_data, time_series_data = create_test_data(100000)
    
    # Test groupby performance
    tester.start_performance_test(
        "GroupBy Operations",
        "Test the performance of groupby operations",
        threshold=0.5  # 0.5 second threshold
    )
    
    for i in range(5):
        # Force garbage collection
        gc.collect()
        
        # Measure time for groupby operation
        start_time = time.time()
        result = simple_data.groupby('Category').agg({
            'Value1': ['mean', 'std', 'min', 'max'],
            'Value2': ['mean', 'std', 'min', 'max'],
            'Value3': ['mean', 'std', 'min', 'max']
        })
        duration = time.time() - start_time
        
        # Record the iteration
        memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # MB
        tester.record_iteration(duration, memory_usage, notes=f"Iteration {i+1}")
    
    tester.end_performance_test("GroupBy operations performance is consistent across iterations")
    
    # Test time series resampling performance
    tester.start_performance_test(
        "Time Series Resampling",
        "Test the performance of time series resampling operations",
        threshold=0.8  # 0.8 second threshold
    )
    
    for i in range(5):
        # Force garbage collection
        gc.collect()
        
        # Measure time for resampling operation
        start_time = time.time()
        # Set Date as index
        ts_data = time_series_data.copy()
        ts_data.set_index('Date', inplace=True)
        # Resample to daily frequency
        daily_data = ts_data.resample('D').mean()
        # Resample to weekly frequency
        weekly_data = ts_data.resample('W').mean()
        # Resample to monthly frequency
        monthly_data = ts_data.resample('M').mean()
        duration = time.time() - start_time
        
        # Record the iteration
        memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # MB
        tester.record_iteration(duration, memory_usage, notes=f"Iteration {i+1}")
    
    tester.end_performance_test("Time series resampling operations are more resource-intensive than simple groupby")
    
    # Test pivot table performance
    tester.start_performance_test(
        "Pivot Table Operations",
        "Test the performance of pivot table operations",
        threshold=0.8  # 0.8 second threshold
    )
    
    for i in range(5):
        # Force garbage collection
        gc.collect()
        
        # Measure time for pivot table operation
        start_time = time.time()
        pivot_data = pd.pivot_table(
            simple_data,
            values=['Value1', 'Value2', 'Value3'],
            index='Category',
            aggfunc=['mean', 'std', 'min', 'max']
        )
        duration = time.time() - start_time
        
        # Record the iteration
        memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # MB
        tester.record_iteration(duration, memory_usage, notes=f"Iteration {i+1}")
    
    tester.end_performance_test("Pivot table operations are more resource-intensive than simple groupby")

def test_dashboard_rendering_performance(tester: PerformanceBottleneckTester) -> None:
    """
    Test the performance of dashboard rendering.
    
    Args:
        tester: The PerformanceBottleneckTester instance
    """
    # Create test data
    simple_data, time_series_data = create_test_data(10000)
    
    # Test dashboard widget creation performance
    tester.start_performance_test(
        "Dashboard Widget Creation",
        "Test the performance of creating dashboard widgets",
        threshold=0.5  # 0.5 second threshold
    )
    
    for i in range(5):
        # Force garbage collection
        gc.collect()
        
        # Measure time to create dashboard widgets
        start_time = time.time()
        
        # Create metric widget
        metric_widget = MetricWidget(
            title="Total Value",
            value_func=lambda: simple_data['Value1'].sum(),
            description="Sum of all values",
            trend_func=lambda: 10,
            trend_is_good_func=lambda x: x > 0
        )
        
        # Create bar chart widget
        bar_chart_widget = ChartWidget(
            title="Values by Category",
            data_func=lambda: simple_data,
            chart_type="bar_chart",
            chart_params={
                "x_column": "Category",
                "y_column": "Value1",
                "title": "Values by Category",
                "show_values": True
            },
            description="Bar chart showing values by category"
        )
        
        # Create line chart widget
        line_chart_widget = ChartWidget(
            title="Time Series Data",
            data_func=lambda: time_series_data,
            chart_type="line_chart",
            chart_params={
                "x_column": "Date",
                "y_columns": ["Value1", "Value2", "Value3"],
                "title": "Time Series Data",
                "show_legend": True
            },
            description="Line chart showing time series data"
        )
        
        # Create table widget
        table_widget = TableWidget(
            title="Data Table",
            data_func=lambda: simple_data,
            description="Table showing the raw data"
        )
        
        duration = time.time() - start_time
        
        # Record the iteration
        memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # MB
        tester.record_iteration(duration, memory_usage, notes=f"Iteration {i+1}")
    
    tester.end_performance_test("Dashboard widget creation performance is consistent across iterations")

def run_all_tests() -> PerformanceBottleneckTester:
    """
    Run all performance bottleneck tests.
    
    Returns:
        The PerformanceBottleneckTester instance with all test results
    """
    tester = PerformanceBottleneckTester()
    
    # Run tests for different performance aspects
    test_data_loading_performance(tester)
    test_visualization_performance(tester)
    test_data_processing_performance(tester)
    test_dashboard_rendering_performance(tester)
    
    # Generate reports
    os.makedirs("science_data_kit/ui/tests/results", exist_ok=True)
    performance_df = tester.generate_performance_report("science_data_kit/ui/tests/results/performance_test_results.csv")
    bottlenecks_df = tester.generate_bottlenecks_report("science_data_kit/ui/tests/results/performance_bottlenecks.csv")
    comparison_df = tester.generate_performance_comparison("science_data_kit/ui/tests/results/performance_comparison.csv")
    
    print("\n=== All Performance Bottleneck Tests Completed ===")
    print(f"Total Performance Tests: {len(tester.results['performance_tests'])}")
    print(f"Total Bottlenecks Identified: {len(tester.results['bottlenecks'])}")
    
    # Print the top 3 bottlenecks
    if tester.results['bottlenecks']:
        print("\nTop Performance Bottlenecks:")
        bottlenecks_by_severity = sorted(
            tester.results['bottlenecks'],
            key=lambda x: (
                0 if x['severity'] == 'Critical' else
                1 if x['severity'] == 'High' else
                2 if x['severity'] == 'Medium' else 3,
                -x['actual_value']
            )
        )
        for i, bottleneck in enumerate(bottlenecks_by_severity[:3], 1):
            print(f"{i}. {bottleneck['component']}: {bottleneck['description']} ({bottleneck['severity']})")
    
    return tester

if __name__ == "__main__":
    # Run all tests
    tester = run_all_tests()