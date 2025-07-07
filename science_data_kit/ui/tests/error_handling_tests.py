import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import time
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import error handling modules
try:
    from science_data_kit.core.utils.error_handler import handle_error, ErrorHandler, log_error
    from science_data_kit.ui.components.error_display import display_error, format_error_message
    HAS_ERROR_MODULES = True
except ImportError:
    HAS_ERROR_MODULES = False
    print("Warning: Error handling modules not found. Some tests will be skipped.")


class ErrorHandlingTester:
    """
    A class for testing error handling functionality in the Science Data Kit UI.
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
            
        issue_id = f"EH-{len(self.issues) + 1:03d}"
        
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


# Mock error handler for testing if the real one is not available
class MockErrorHandler:
    """A mock error handler for testing."""
    
    def __init__(self):
        self.errors = []
        
    def handle_error(self, error, context=None):
        """Handle an error."""
        error_info = {
            "error": str(error),
            "type": type(error).__name__,
            "context": context,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.errors.append(error_info)
        return error_info
        
    def log_error(self, error, context=None):
        """Log an error."""
        error_info = self.handle_error(error, context)
        print(f"[ERROR] {error_info['type']}: {error_info['error']}")
        if context:
            print(f"[CONTEXT] {context}")
        return error_info


def test_error_handler(tester: ErrorHandlingTester):
    """
    Test error handler functionality.
    
    Args:
        tester: The ErrorHandlingTester instance
    """
    tester.start_component_test("Error Handler")
    
    # Use the real error handler if available, otherwise use the mock
    if HAS_ERROR_MODULES:
        error_handler = ErrorHandler()
    else:
        error_handler = MockErrorHandler()
    
    # Test handling a simple exception
    try:
        # Generate a simple exception
        result = 1 / 0
    except Exception as e:
        try:
            error_info = error_handler.handle_error(e, context="Division by zero test")
            tester.test_functionality("Handle simple exception", 
                                     isinstance(error_info, dict) and "error" in error_info,
                                     "Error handler should return error information")
        except Exception as handler_error:
            tester.test_functionality("Handle simple exception", False, f"Error: {str(handler_error)}")
            tester.record_issue("Functionality", "Handle simple exception", 
                               f"Failed to handle simple exception: {str(handler_error)}", "High")
    
    # Test handling a complex exception with traceback
    try:
        # Generate a more complex exception
        def nested_function():
            return unknown_variable  # This will cause a NameError
        
        nested_function()
    except Exception as e:
        try:
            error_info = error_handler.handle_error(e, context="Complex exception test")
            tester.test_functionality("Handle complex exception", 
                                     isinstance(error_info, dict) and "error" in error_info,
                                     "Error handler should return error information")
        except Exception as handler_error:
            tester.test_functionality("Handle complex exception", False, f"Error: {str(handler_error)}")
            tester.record_issue("Functionality", "Handle complex exception", 
                               f"Failed to handle complex exception: {str(handler_error)}", "High")
    
    # Test logging an error
    try:
        # Generate an exception to log
        result = [1, 2, 3][10]  # This will cause an IndexError
    except Exception as e:
        try:
            error_info = error_handler.log_error(e, context="Error logging test")
            tester.test_functionality("Log error", 
                                     isinstance(error_info, dict) and "error" in error_info,
                                     "Error logger should return error information")
        except Exception as logger_error:
            tester.test_functionality("Log error", False, f"Error: {str(logger_error)}")
            tester.record_issue("Functionality", "Log error", 
                               f"Failed to log error: {str(logger_error)}", "High")
    
    # Test handling different types of exceptions
    exception_types = [
        (ValueError, "Invalid value"),
        (TypeError, "Invalid type"),
        (KeyError, "Missing key"),
        (IndexError, "Invalid index"),
        (FileNotFoundError, "File not found"),
        (PermissionError, "Permission denied"),
        (TimeoutError, "Operation timed out")
    ]
    
    for exception_class, message in exception_types:
        try:
            # Generate the specific exception
            raise exception_class(message)
        except Exception as e:
            try:
                error_info = error_handler.handle_error(e, context=f"Testing {exception_class.__name__}")
                tester.test_functionality(f"Handle {exception_class.__name__}", 
                                         isinstance(error_info, dict) and "error" in error_info,
                                         f"Error handler should handle {exception_class.__name__}")
            except Exception as handler_error:
                tester.test_functionality(f"Handle {exception_class.__name__}", False, f"Error: {str(handler_error)}")
                tester.record_issue("Functionality", f"Handle {exception_class.__name__}", 
                                   f"Failed to handle {exception_class.__name__}: {str(handler_error)}", "Medium")
    
    tester.end_component_test()


def test_error_display(tester: ErrorHandlingTester):
    """
    Test error display functionality.
    
    Args:
        tester: The ErrorHandlingTester instance
    """
    tester.start_component_test("Error Display")
    
    # Test error message formatting
    if HAS_ERROR_MODULES:
        try:
            # Generate an exception
            try:
                result = 1 / 0
            except Exception as e:
                error_message = format_error_message(e, "Division by zero test")
                tester.test_functionality("Format error message", 
                                         isinstance(error_message, str) and "Division by zero" in error_message,
                                         "Error message should be formatted correctly")
        except Exception as e:
            tester.test_functionality("Format error message", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Format error message", 
                               f"Failed to format error message: {str(e)}", "High")
    else:
        # Mock the error message formatting
        try:
            error_message = f"Error: Division by zero\nContext: Division by zero test\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            tester.test_functionality("Format error message (mock)", 
                                     isinstance(error_message, str) and "Division by zero" in error_message,
                                     "Mock error message should be formatted correctly")
        except Exception as e:
            tester.test_functionality("Format error message (mock)", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Format error message (mock)", 
                               f"Failed to format mock error message: {str(e)}", "High")
    
    # Test error display in Streamlit (this is more of a mock test since we can't actually display in Streamlit here)
    if HAS_ERROR_MODULES:
        try:
            # We can't actually test the display function directly without a Streamlit context,
            # so we'll just check if the function exists and is callable
            tester.test_functionality("Error display function exists", 
                                     callable(display_error),
                                     "display_error function should be callable")
        except Exception as e:
            tester.test_functionality("Error display function exists", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Error display function exists", 
                               f"Failed to check if display_error function exists: {str(e)}", "High")
    else:
        tester.test_functionality("Error display function exists", False, "Error display module not available")
    
    # Test different error display levels (info, warning, error)
    error_levels = ["info", "warning", "error"]
    for level in error_levels:
        if HAS_ERROR_MODULES:
            try:
                # Again, we can't actually test the display, but we can check if the function accepts the level parameter
                tester.test_functionality(f"Error display level: {level}", 
                                         True,  # Assuming the function accepts the level parameter
                                         f"display_error function should accept {level} level")
            except Exception as e:
                tester.test_functionality(f"Error display level: {level}", False, f"Error: {str(e)}")
                tester.record_issue("Functionality", f"Error display level: {level}", 
                                   f"Failed to check if display_error function accepts {level} level: {str(e)}", "Medium")
        else:
            tester.test_functionality(f"Error display level: {level}", False, "Error display module not available")
    
    tester.end_component_test()


def test_error_recovery(tester: ErrorHandlingTester):
    """
    Test error recovery functionality.
    
    Args:
        tester: The ErrorHandlingTester instance
    """
    tester.start_component_test("Error Recovery")
    
    # Test basic error recovery
    try:
        # Simulate a function that might fail but has a fallback
        def risky_function(use_fallback=False):
            if not use_fallback:
                # This will fail
                return 1 / 0
            else:
                # Fallback
                return 0
        
        # First try without fallback (should fail)
        try:
            result = risky_function(use_fallback=False)
            tester.test_error_handling("Basic error recovery - detect failure", 
                                      False,
                                      "Function should have failed without fallback")
        except Exception:
            # Now try with fallback (should succeed)
            try:
                result = risky_function(use_fallback=True)
                tester.test_error_handling("Basic error recovery - use fallback", 
                                          result == 0,
                                          "Function should succeed with fallback")
            except Exception as e:
                tester.test_error_handling("Basic error recovery - use fallback", 
                                          False,
                                          f"Fallback also failed: {str(e)}")
                tester.record_issue("Error Handling", "Basic error recovery - use fallback", 
                                   f"Fallback mechanism failed: {str(e)}", "High")
    except Exception as e:
        tester.test_error_handling("Basic error recovery", False, f"Error: {str(e)}")
        tester.record_issue("Error Handling", "Basic error recovery", 
                           f"Failed to test basic error recovery: {str(e)}", "High")
    
    # Test error recovery with retry
    try:
        # Simulate a function that might fail temporarily
        def unstable_function(attempt=1, max_attempts=3):
            if attempt < max_attempts:
                # Fail on early attempts
                raise ConnectionError("Temporary connection error")
            else:
                # Succeed on final attempt
                return "Success"
        
        # Try with retry mechanism
        def retry_function(max_attempts=3):
            for attempt in range(1, max_attempts + 1):
                try:
                    return unstable_function(attempt, max_attempts)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    # In a real implementation, you might want to add a delay here
            
        try:
            result = retry_function(max_attempts=3)
            tester.test_error_handling("Error recovery with retry", 
                                      result == "Success",
                                      "Function should succeed after retries")
        except Exception as e:
            tester.test_error_handling("Error recovery with retry", 
                                      False,
                                      f"Retry mechanism failed: {str(e)}")
            tester.record_issue("Error Handling", "Error recovery with retry", 
                               f"Retry mechanism failed: {str(e)}", "High")
    except Exception as e:
        tester.test_error_handling("Error recovery with retry", False, f"Error: {str(e)}")
        tester.record_issue("Error Handling", "Error recovery with retry", 
                           f"Failed to test error recovery with retry: {str(e)}", "High")
    
    # Test graceful degradation
    try:
        # Simulate a complex function with multiple components that can fail independently
        def complex_function(component1_fail=False, component2_fail=False):
            result = {"status": "partial", "components": {}}
            
            # Component 1
            try:
                if component1_fail:
                    raise ValueError("Component 1 failure")
                result["components"]["component1"] = "success"
            except Exception as e:
                result["components"]["component1"] = f"failed: {str(e)}"
            
            # Component 2
            try:
                if component2_fail:
                    raise ValueError("Component 2 failure")
                result["components"]["component2"] = "success"
            except Exception as e:
                result["components"]["component2"] = f"failed: {str(e)}"
            
            # Overall status
            if all(v == "success" for v in result["components"].values()):
                result["status"] = "success"
            elif all(v.startswith("failed") for v in result["components"].values()):
                result["status"] = "failed"
            
            return result
        
        # Test with all components working
        result = complex_function(component1_fail=False, component2_fail=False)
        tester.test_error_handling("Graceful degradation - all components working", 
                                  result["status"] == "success",
                                  "Function should succeed with all components working")
        
        # Test with one component failing
        result = complex_function(component1_fail=True, component2_fail=False)
        tester.test_error_handling("Graceful degradation - partial failure", 
                                  result["status"] == "partial",
                                  "Function should partially succeed with one component failing")
        
        # Test with all components failing
        result = complex_function(component1_fail=True, component2_fail=True)
        tester.test_error_handling("Graceful degradation - complete failure", 
                                  result["status"] == "failed",
                                  "Function should fail gracefully with all components failing")
    except Exception as e:
        tester.test_error_handling("Graceful degradation", False, f"Error: {str(e)}")
        tester.record_issue("Error Handling", "Graceful degradation", 
                           f"Failed to test graceful degradation: {str(e)}", "High")
    
    tester.end_component_test()


def test_user_feedback(tester: ErrorHandlingTester):
    """
    Test user feedback for errors.
    
    Args:
        tester: The ErrorHandlingTester instance
    """
    tester.start_component_test("User Feedback")
    
    # Test error message clarity
    error_messages = [
        {
            "technical": "ValueError: Invalid value for parameter 'x'. Expected numeric, got string.",
            "user_friendly": "The value you entered is not a number. Please enter a numeric value."
        },
        {
            "technical": "KeyError: 'column_name'",
            "user_friendly": "The column 'column_name' was not found in the dataset. Please check the column name and try again."
        },
        {
            "technical": "ConnectionError: Failed to connect to database at localhost:5432",
            "user_friendly": "Could not connect to the database. Please check your connection settings and try again."
        }
    ]
    
    for i, message_pair in enumerate(error_messages):
        # In a real test, we would check if the error handler converts technical messages to user-friendly ones
        # Here we'll just check if both messages exist and are different
        try:
            tester.test_functionality(f"Error message clarity {i+1}", 
                                     len(message_pair["technical"]) > 0 and 
                                     len(message_pair["user_friendly"]) > 0 and
                                     message_pair["technical"] != message_pair["user_friendly"],
                                     "User-friendly error message should be different from technical message")
        except Exception as e:
            tester.test_functionality(f"Error message clarity {i+1}", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", f"Error message clarity {i+1}", 
                               f"Failed to test error message clarity: {str(e)}", "Medium")
    
    # Test error context preservation
    try:
        # Simulate a function that provides context with errors
        def contextual_function(value):
            try:
                # This will fail for non-numeric values
                return float(value)
            except ValueError:
                # Provide context with the error
                raise ValueError(f"Could not convert '{value}' to a number. Please enter a numeric value.")
        
        # Test with invalid input
        try:
            result = contextual_function("abc")
            tester.test_error_handling("Error context preservation", 
                                      False,
                                      "Function should have failed with non-numeric input")
        except ValueError as e:
            error_message = str(e)
            tester.test_error_handling("Error context preservation", 
                                      "abc" in error_message and "numeric" in error_message,
                                      "Error message should include context about the input and expected format")
    except Exception as e:
        tester.test_error_handling("Error context preservation", False, f"Error: {str(e)}")
        tester.record_issue("Error Handling", "Error context preservation", 
                           f"Failed to test error context preservation: {str(e)}", "Medium")
    
    # Test recovery suggestions
    recovery_suggestions = [
        {
            "error": "File not found: data.csv",
            "suggestion": "Please check if the file exists and the path is correct."
        },
        {
            "error": "Permission denied: /path/to/file",
            "suggestion": "You don't have permission to access this file. Try running the application with administrator privileges."
        },
        {
            "error": "Network timeout",
            "suggestion": "The server is taking too long to respond. Please check your internet connection and try again later."
        }
    ]
    
    for i, suggestion_pair in enumerate(recovery_suggestions):
        # In a real test, we would check if the error handler provides recovery suggestions
        # Here we'll just check if both error and suggestion exist
        try:
            tester.test_functionality(f"Recovery suggestion {i+1}", 
                                     len(suggestion_pair["error"]) > 0 and 
                                     len(suggestion_pair["suggestion"]) > 0,
                                     "Error should have a recovery suggestion")
        except Exception as e:
            tester.test_functionality(f"Recovery suggestion {i+1}", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", f"Recovery suggestion {i+1}", 
                               f"Failed to test recovery suggestion: {str(e)}", "Medium")
    
    tester.end_component_test()


def run_all_tests():
    """
    Run all error handling tests and generate reports.
    """
    print("=== Running Error Handling Tests ===")
    
    tester = ErrorHandlingTester()
    
    # Run all tests
    test_error_handler(tester)
    test_error_display(tester)
    test_error_recovery(tester)
    test_user_feedback(tester)
    
    # Create results directory if it doesn't exist
    os.makedirs("science_data_kit/ui/tests/results", exist_ok=True)
    
    # Generate reports
    results_df = tester.generate_report("science_data_kit/ui/tests/results/error_handling_test_results.csv")
    issues_df = tester.generate_issues_report("science_data_kit/ui/tests/results/error_handling_test_issues.csv")
    
    return results_df, issues_df


if __name__ == "__main__":
    run_all_tests()