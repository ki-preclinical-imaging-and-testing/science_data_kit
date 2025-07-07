import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import analysis engine modules
try:
    from science_data_kit.core.analysis.analysis_engine import run_analysis, get_available_analyses
    from science_data_kit.core.analysis.statistical_analysis import run_statistical_analysis
    from science_data_kit.core.analysis.machine_learning import run_ml_analysis
    HAS_ANALYSIS_MODULES = True
except ImportError:
    HAS_ANALYSIS_MODULES = False
    print("Warning: Analysis engine modules not found. Some tests will be skipped.")


class AnalysisEngineTester:
    """
    A class for testing analysis engine integration in the Science Data Kit UI.
    """
    
    def __init__(self):
        """
        Initialize the tester with empty test results and issues lists.
        """
        self.test_results = []
        self.issues = []
        self.current_component = None
        self.component_start_time = None
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        
    def start_component_test(self, component_name: str):
        """
        Start testing a new component.
        
        Args:
            component_name: The name of the component being tested
        """
        self.current_component = component_name
        self.component_start_time = time.time()
        print(f"\n=== Testing {component_name} ===")
        
    def test_functionality(self, test_name: str, result: bool, notes: str = ""):
        """
        Record a functionality test result.
        
        Args:
            test_name: The name of the test
            result: True if the test passed, False if it failed
            notes: Additional notes about the test
        """
        self._record_test_result(test_name, result, notes, "Functionality")
        
    def test_security(self, test_name: str, result: bool, notes: str = ""):
        """
        Record a security test result.
        
        Args:
            test_name: The name of the test
            result: True if the test passed, False if it failed
            notes: Additional notes about the test
        """
        self._record_test_result(test_name, result, notes, "Security")
        
    def test_performance(self, test_name: str, result: bool, notes: str = ""):
        """
        Record a performance test result.
        
        Args:
            test_name: The name of the test
            result: True if the test passed, False if it failed
            notes: Additional notes about the test
        """
        self._record_test_result(test_name, result, notes, "Performance")
        
    def test_error_handling(self, test_name: str, result: bool, notes: str = ""):
        """
        Record an error handling test result.
        
        Args:
            test_name: The name of the test
            result: True if the test passed, False if it failed
            notes: Additional notes about the test
        """
        self._record_test_result(test_name, result, notes, "Error Handling")
        
    def test_integration(self, test_name: str, result: bool, notes: str = ""):
        """
        Record an integration test result.
        
        Args:
            test_name: The name of the test
            result: True if the test passed, False if it failed
            notes: Additional notes about the test
        """
        self._record_test_result(test_name, result, notes, "Integration")
        
    def _record_test_result(self, test_name: str, result: bool, notes: str = "", category: str = "Functionality"):
        """
        Record a test result.
        
        Args:
            test_name: The name of the test
            result: True if the test passed, False if it failed
            notes: Additional notes about the test
            category: The category of the test
        """
        if self.current_component is None:
            raise ValueError("No component test started. Call start_component_test first.")
            
        self.test_count += 1
        if result:
            self.pass_count += 1
            status = "Pass"
            print(f"✅ {test_name}: PASS")
        else:
            self.fail_count += 1
            status = "Fail"
            print(f"❌ {test_name}: FAIL - {notes}")
            
        self.test_results.append({
            "Component": self.current_component,
            "Test Name": test_name,
            "Category": category,
            "Status": status,
            "Notes": notes,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    def record_issue(self, category: str, test_name: str, description: str, severity: str = "Medium"):
        """
        Record an issue found during testing.
        
        Args:
            category: The category of the issue
            test_name: The name of the test that found the issue
            description: A description of the issue
            severity: The severity of the issue (Low, Medium, High, Critical)
        """
        if self.current_component is None:
            raise ValueError("No component test started. Call start_component_test first.")
            
        issue_id = f"AE-{len(self.issues) + 1:03d}"
        
        self.issues.append({
            "Issue ID": issue_id,
            "Component": self.current_component,
            "Test Name": test_name,
            "Category": category,
            "Description": description,
            "Severity": severity,
            "Status": "Open",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        print(f"⚠️ Issue {issue_id} ({severity}): {description}")
        
    def end_component_test(self):
        """
        End testing for the current component and print a summary.
        """
        if self.current_component is None:
            raise ValueError("No component test started. Call start_component_test first.")
            
        duration = time.time() - self.component_start_time
        
        print(f"\n=== {self.current_component} Testing Summary ===")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Tests: {self.test_count}")
        print(f"Passed: {self.pass_count}")
        print(f"Failed: {self.fail_count}")
        print(f"Pass Rate: {(self.pass_count / self.test_count) * 100:.2f}%")
        
        self.current_component = None
        self.component_start_time = None
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        
    def generate_report(self, output_file: str = None):
        """
        Generate a report of all test results.
        
        Args:
            output_file: The file to write the report to. If None, the report is returned as a DataFrame.
            
        Returns:
            A pandas DataFrame containing the test results.
        """
        if not self.test_results:
            print("No test results to report.")
            return pd.DataFrame()
            
        df = pd.DataFrame(self.test_results)
        
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Test results saved to {output_file}")
            
        # Print summary
        total_tests = len(df)
        passed_tests = len(df[df["Status"] == "Pass"])
        failed_tests = len(df[df["Status"] == "Fail"])
        pass_rate = (passed_tests / total_tests) * 100
        
        print("\n=== Test Results Summary ===")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Pass Rate: {pass_rate:.2f}%")
        
        return df
        
    def generate_issues_report(self, output_file: str = None):
        """
        Generate a report of all issues found during testing.
        
        Args:
            output_file: The file to write the report to. If None, the report is returned as a DataFrame.
            
        Returns:
            A pandas DataFrame containing the issues.
        """
        if not self.issues:
            print("No issues to report.")
            return pd.DataFrame()
            
        df = pd.DataFrame(self.issues)
        
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Issues saved to {output_file}")
            
        # Print summary
        total_issues = len(df)
        by_severity = df["Severity"].value_counts()
        
        print("\n=== Issues Summary ===")
        print(f"Total Issues: {total_issues}")
        for severity, count in by_severity.items():
            print(f"{severity}: {count}")
            
        return df


def test_analysis_engine_core(tester: AnalysisEngineTester):
    """
    Test core analysis engine functionality.
    
    Args:
        tester: The AnalysisEngineTester instance
    """
    tester.start_component_test("Analysis Engine Core")
    
    # Create test data
    test_data = pd.DataFrame({
        "Numeric1": [10, 20, 30, 40, 50],
        "Numeric2": [5, 15, 25, 35, 45],
        "Category": ["A", "B", "A", "B", "A"]
    })
    
    # Test available analyses
    if HAS_ANALYSIS_MODULES:
        try:
            available_analyses = get_available_analyses()
            tester.test_functionality("Get available analyses", 
                                     len(available_analyses) > 0,
                                     f"Found {len(available_analyses)} available analyses")
        except Exception as e:
            tester.test_functionality("Get available analyses", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Get available analyses", 
                               f"Failed to get available analyses: {str(e)}", "High")
    else:
        tester.test_functionality("Get available analyses", False, "Analysis engine module not available")
    
    # Test running a basic analysis
    if HAS_ANALYSIS_MODULES:
        try:
            result = run_analysis(test_data, "basic_statistics")
            tester.test_functionality("Run basic statistics analysis", 
                                     isinstance(result, dict) and "mean" in result,
                                     "Analysis result should contain basic statistics")
        except Exception as e:
            tester.test_functionality("Run basic statistics analysis", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Run basic statistics analysis", 
                               f"Failed to run basic statistics analysis: {str(e)}", "High")
    else:
        tester.test_functionality("Run basic statistics analysis", False, "Analysis engine module not available")
    
    # Test error handling with invalid analysis type
    if HAS_ANALYSIS_MODULES:
        try:
            run_analysis(test_data, "nonexistent_analysis")
            tester.test_error_handling("Handle invalid analysis type", False, 
                                      "Should raise an error for invalid analysis type")
            tester.record_issue("Error Handling", "Handle invalid analysis type", 
                               "Failed to raise error for invalid analysis type", "Medium")
        except Exception:
            tester.test_error_handling("Handle invalid analysis type", True, 
                                      "Correctly raised error for invalid analysis type")
    else:
        tester.test_error_handling("Handle invalid analysis type", False, "Analysis engine module not available")
    
    # Test error handling with invalid data
    if HAS_ANALYSIS_MODULES:
        try:
            invalid_data = pd.DataFrame({"Text": ["a", "b", "c"]})
            run_analysis(invalid_data, "correlation")
            tester.test_error_handling("Handle invalid data for analysis", False, 
                                      "Should raise an error for invalid data")
            tester.record_issue("Error Handling", "Handle invalid data for analysis", 
                               "Failed to raise error for invalid data", "Medium")
        except Exception:
            tester.test_error_handling("Handle invalid data for analysis", True, 
                                      "Correctly raised error for invalid data")
    else:
        tester.test_error_handling("Handle invalid data for analysis", False, "Analysis engine module not available")
    
    # Test performance with large dataset
    if HAS_ANALYSIS_MODULES:
        # Create large test dataset
        large_data = pd.DataFrame({
            "Value1": np.random.rand(10000),
            "Value2": np.random.rand(10000),
            "Value3": np.random.rand(10000)
        })
        
        try:
            start_time = time.time()
            run_analysis(large_data, "basic_statistics")
            duration = time.time() - start_time
            tester.test_performance("Analyze large dataset", 
                                   duration < 5,  # Assuming 5 seconds is acceptable
                                   f"Analysis took {duration:.2f} seconds")
            if duration >= 5:
                tester.record_issue("Performance", "Analyze large dataset", 
                                   f"Analysis of large dataset took {duration:.2f} seconds", "Medium")
        except Exception as e:
            tester.test_performance("Analyze large dataset", False, f"Error: {str(e)}")
            tester.record_issue("Performance", "Analyze large dataset", 
                               f"Failed to analyze large dataset: {str(e)}", "Medium")
    else:
        tester.test_performance("Analyze large dataset", False, "Analysis engine module not available")
    
    tester.end_component_test()


def test_statistical_analysis(tester: AnalysisEngineTester):
    """
    Test statistical analysis functionality.
    
    Args:
        tester: The AnalysisEngineTester instance
    """
    tester.start_component_test("Statistical Analysis")
    
    # Create test data
    test_data = pd.DataFrame({
        "Numeric1": [10, 20, 30, 40, 50],
        "Numeric2": [5, 15, 25, 35, 45],
        "Category": ["A", "B", "A", "B", "A"]
    })
    
    # Test descriptive statistics
    if HAS_ANALYSIS_MODULES:
        try:
            result = run_statistical_analysis(test_data, "descriptive")
            tester.test_functionality("Run descriptive statistics", 
                                     isinstance(result, dict) and "mean" in result and "std" in result,
                                     "Result should contain mean and standard deviation")
        except Exception as e:
            tester.test_functionality("Run descriptive statistics", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Run descriptive statistics", 
                               f"Failed to run descriptive statistics: {str(e)}", "High")
    else:
        tester.test_functionality("Run descriptive statistics", False, "Statistical analysis module not available")
    
    # Test correlation analysis
    if HAS_ANALYSIS_MODULES:
        try:
            result = run_statistical_analysis(test_data, "correlation")
            tester.test_functionality("Run correlation analysis", 
                                     isinstance(result, pd.DataFrame) and result.shape[0] > 0,
                                     "Result should be a non-empty DataFrame")
        except Exception as e:
            tester.test_functionality("Run correlation analysis", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Run correlation analysis", 
                               f"Failed to run correlation analysis: {str(e)}", "High")
    else:
        tester.test_functionality("Run correlation analysis", False, "Statistical analysis module not available")
    
    # Test hypothesis testing
    if HAS_ANALYSIS_MODULES:
        try:
            result = run_statistical_analysis(test_data, "ttest", columns=["Numeric1", "Numeric2"])
            tester.test_functionality("Run t-test analysis", 
                                     isinstance(result, dict) and "p_value" in result,
                                     "Result should contain p-value")
        except Exception as e:
            tester.test_functionality("Run t-test analysis", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Run t-test analysis", 
                               f"Failed to run t-test analysis: {str(e)}", "Medium")
    else:
        tester.test_functionality("Run t-test analysis", False, "Statistical analysis module not available")
    
    # Test ANOVA
    if HAS_ANALYSIS_MODULES:
        try:
            result = run_statistical_analysis(test_data, "anova", 
                                             target="Numeric1", groupby="Category")
            tester.test_functionality("Run ANOVA analysis", 
                                     isinstance(result, dict) and "p_value" in result,
                                     "Result should contain p-value")
        except Exception as e:
            tester.test_functionality("Run ANOVA analysis", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Run ANOVA analysis", 
                               f"Failed to run ANOVA analysis: {str(e)}", "Medium")
    else:
        tester.test_functionality("Run ANOVA analysis", False, "Statistical analysis module not available")
    
    # Test error handling with invalid analysis type
    if HAS_ANALYSIS_MODULES:
        try:
            run_statistical_analysis(test_data, "nonexistent_analysis")
            tester.test_error_handling("Handle invalid statistical analysis type", False, 
                                      "Should raise an error for invalid analysis type")
            tester.record_issue("Error Handling", "Handle invalid statistical analysis type", 
                               "Failed to raise error for invalid analysis type", "Medium")
        except Exception:
            tester.test_error_handling("Handle invalid statistical analysis type", True, 
                                      "Correctly raised error for invalid analysis type")
    else:
        tester.test_error_handling("Handle invalid statistical analysis type", False, 
                                  "Statistical analysis module not available")
    
    tester.end_component_test()


def test_machine_learning_analysis(tester: AnalysisEngineTester):
    """
    Test machine learning analysis functionality.
    
    Args:
        tester: The AnalysisEngineTester instance
    """
    tester.start_component_test("Machine Learning Analysis")
    
    # Create test data
    np.random.seed(42)
    X = np.random.rand(100, 5)
    y = X[:, 0] + X[:, 1] * 2 + np.random.randn(100) * 0.1
    test_data = pd.DataFrame(
        np.column_stack([X, y]), 
        columns=["feature1", "feature2", "feature3", "feature4", "feature5", "target"]
    )
    
    # Test regression analysis
    if HAS_ANALYSIS_MODULES:
        try:
            result = run_ml_analysis(test_data, "regression", 
                                    target="target", features=["feature1", "feature2", "feature3", "feature4", "feature5"])
            tester.test_functionality("Run regression analysis", 
                                     isinstance(result, dict) and "model" in result and "metrics" in result,
                                     "Result should contain model and metrics")
        except Exception as e:
            tester.test_functionality("Run regression analysis", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Run regression analysis", 
                               f"Failed to run regression analysis: {str(e)}", "High")
    else:
        tester.test_functionality("Run regression analysis", False, "Machine learning module not available")
    
    # Test classification analysis
    if HAS_ANALYSIS_MODULES:
        # Create classification data
        X = np.random.rand(100, 5)
        y = (X[:, 0] + X[:, 1] > 1).astype(int)
        classification_data = pd.DataFrame(
            np.column_stack([X, y]), 
            columns=["feature1", "feature2", "feature3", "feature4", "feature5", "target"]
        )
        
        try:
            result = run_ml_analysis(classification_data, "classification", 
                                    target="target", features=["feature1", "feature2", "feature3", "feature4", "feature5"])
            tester.test_functionality("Run classification analysis", 
                                     isinstance(result, dict) and "model" in result and "metrics" in result,
                                     "Result should contain model and metrics")
        except Exception as e:
            tester.test_functionality("Run classification analysis", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Run classification analysis", 
                               f"Failed to run classification analysis: {str(e)}", "High")
    else:
        tester.test_functionality("Run classification analysis", False, "Machine learning module not available")
    
    # Test clustering analysis
    if HAS_ANALYSIS_MODULES:
        try:
            result = run_ml_analysis(test_data, "clustering", 
                                    features=["feature1", "feature2", "feature3", "feature4", "feature5"])
            tester.test_functionality("Run clustering analysis", 
                                     isinstance(result, dict) and "clusters" in result,
                                     "Result should contain clusters")
        except Exception as e:
            tester.test_functionality("Run clustering analysis", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Run clustering analysis", 
                               f"Failed to run clustering analysis: {str(e)}", "Medium")
    else:
        tester.test_functionality("Run clustering analysis", False, "Machine learning module not available")
    
    # Test feature importance
    if HAS_ANALYSIS_MODULES:
        try:
            result = run_ml_analysis(test_data, "feature_importance", 
                                    target="target", features=["feature1", "feature2", "feature3", "feature4", "feature5"])
            tester.test_functionality("Run feature importance analysis", 
                                     isinstance(result, dict) and "importance" in result,
                                     "Result should contain feature importance")
        except Exception as e:
            tester.test_functionality("Run feature importance analysis", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Run feature importance analysis", 
                               f"Failed to run feature importance analysis: {str(e)}", "Medium")
    else:
        tester.test_functionality("Run feature importance analysis", False, "Machine learning module not available")
    
    # Test error handling with invalid analysis type
    if HAS_ANALYSIS_MODULES:
        try:
            run_ml_analysis(test_data, "nonexistent_analysis", 
                           target="target", features=["feature1", "feature2"])
            tester.test_error_handling("Handle invalid ML analysis type", False, 
                                      "Should raise an error for invalid analysis type")
            tester.record_issue("Error Handling", "Handle invalid ML analysis type", 
                               "Failed to raise error for invalid analysis type", "Medium")
        except Exception:
            tester.test_error_handling("Handle invalid ML analysis type", True, 
                                      "Correctly raised error for invalid analysis type")
    else:
        tester.test_error_handling("Handle invalid ML analysis type", False, 
                                  "Machine learning module not available")
    
    # Test performance with large dataset
    if HAS_ANALYSIS_MODULES:
        # Create large test dataset
        np.random.seed(42)
        X_large = np.random.rand(1000, 10)
        y_large = X_large[:, 0] + X_large[:, 1] * 2 + np.random.randn(1000) * 0.1
        large_data = pd.DataFrame(
            np.column_stack([X_large, y_large]), 
            columns=[f"feature{i}" for i in range(1, 11)] + ["target"]
        )
        
        try:
            start_time = time.time()
            run_ml_analysis(large_data, "regression", 
                           target="target", features=[f"feature{i}" for i in range(1, 11)])
            duration = time.time() - start_time
            tester.test_performance("Run ML analysis on large dataset", 
                                   duration < 10,  # Assuming 10 seconds is acceptable
                                   f"Analysis took {duration:.2f} seconds")
            if duration >= 10:
                tester.record_issue("Performance", "Run ML analysis on large dataset", 
                                   f"ML analysis on large dataset took {duration:.2f} seconds", "Medium")
        except Exception as e:
            tester.test_performance("Run ML analysis on large dataset", False, f"Error: {str(e)}")
            tester.record_issue("Performance", "Run ML analysis on large dataset", 
                               f"Failed to run ML analysis on large dataset: {str(e)}", "Medium")
    else:
        tester.test_performance("Run ML analysis on large dataset", False, "Machine learning module not available")
    
    tester.end_component_test()


def run_all_tests():
    """
    Run all analysis engine tests and generate reports.
    """
    print("=== Running Analysis Engine Tests ===")
    
    tester = AnalysisEngineTester()
    
    # Run all tests
    test_analysis_engine_core(tester)
    test_statistical_analysis(tester)
    test_machine_learning_analysis(tester)
    
    # Create results directory if it doesn't exist
    os.makedirs("science_data_kit/ui/tests/results", exist_ok=True)
    
    # Generate reports
    results_df = tester.generate_report("science_data_kit/ui/tests/results/analysis_engine_test_results.csv")
    issues_df = tester.generate_issues_report("science_data_kit/ui/tests/results/analysis_engine_test_issues.csv")
    
    return results_df, issues_df


if __name__ == "__main__":
    run_all_tests()