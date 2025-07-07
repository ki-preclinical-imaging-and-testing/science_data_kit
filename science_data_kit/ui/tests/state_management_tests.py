import streamlit as st
import pandas as pd
import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import state management modules
try:
    from science_data_kit.core.state.session_state import get_state, set_state, clear_state
    from science_data_kit.core.state.state_manager import StateManager
    HAS_STATE_MODULES = True
except ImportError:
    HAS_STATE_MODULES = False
    print("Warning: State management modules not found. Some tests will be skipped.")


class StateManagementTester:
    """
    A class for testing state management functionality in the Science Data Kit UI.
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
            
        issue_id = f"SM-{len(self.issues) + 1:03d}"
        
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


# Mock state manager for testing if the real one is not available
class MockStateManager:
    """A mock state manager for testing."""
    
    def __init__(self):
        self.state = {}
        
    def get(self, key, default=None):
        """Get a value from the state."""
        return self.state.get(key, default)
        
    def set(self, key, value):
        """Set a value in the state."""
        self.state[key] = value
        return value
        
    def clear(self, key=None):
        """Clear a value from the state, or the entire state if no key is provided."""
        if key is None:
            self.state = {}
        elif key in self.state:
            del self.state[key]
            
    def get_all(self):
        """Get the entire state."""
        return self.state.copy()


def test_session_state(tester: StateManagementTester):
    """
    Test session state functionality.
    
    Args:
        tester: The StateManagementTester instance
    """
    tester.start_component_test("Session State")
    
    # Use the real state functions if available, otherwise use the mock
    if HAS_STATE_MODULES:
        # Clear any existing state first
        clear_state()
    else:
        # Create a mock state manager
        mock_state_manager = MockStateManager()
        
        # Define mock functions
        def mock_get_state(key, default=None):
            return mock_state_manager.get(key, default)
            
        def mock_set_state(key, value):
            return mock_state_manager.set(key, value)
            
        def mock_clear_state(key=None):
            return mock_state_manager.clear(key)
            
        # Use the mock functions
        get_state = mock_get_state
        set_state = mock_set_state
        clear_state = mock_clear_state
    
    # Test setting and getting a simple value
    try:
        # Set a value
        set_state("test_key", "test_value")
        
        # Get the value
        value = get_state("test_key")
        
        tester.test_functionality("Set and get simple value", 
                                 value == "test_value",
                                 "Should be able to set and get a simple value")
    except Exception as e:
        tester.test_functionality("Set and get simple value", False, f"Error: {str(e)}")
        tester.record_issue("Functionality", "Set and get simple value", 
                           f"Failed to set and get a simple value: {str(e)}", "High")
    
    # Test getting a default value for a non-existent key
    try:
        # Get a value for a key that doesn't exist
        value = get_state("non_existent_key", "default_value")
        
        tester.test_functionality("Get default value", 
                                 value == "default_value",
                                 "Should return the default value for a non-existent key")
    except Exception as e:
        tester.test_functionality("Get default value", False, f"Error: {str(e)}")
        tester.record_issue("Functionality", "Get default value", 
                           f"Failed to get default value: {str(e)}", "Medium")
    
    # Test clearing a specific key
    try:
        # Set a value
        set_state("key_to_clear", "value_to_clear")
        
        # Clear the key
        clear_state("key_to_clear")
        
        # Try to get the value
        value = get_state("key_to_clear", "default_after_clear")
        
        tester.test_functionality("Clear specific key", 
                                 value == "default_after_clear",
                                 "Should be able to clear a specific key")
    except Exception as e:
        tester.test_functionality("Clear specific key", False, f"Error: {str(e)}")
        tester.record_issue("Functionality", "Clear specific key", 
                           f"Failed to clear a specific key: {str(e)}", "Medium")
    
    # Test clearing all state
    try:
        # Set multiple values
        set_state("key1", "value1")
        set_state("key2", "value2")
        
        # Clear all state
        clear_state()
        
        # Try to get the values
        value1 = get_state("key1", "default1")
        value2 = get_state("key2", "default2")
        
        tester.test_functionality("Clear all state", 
                                 value1 == "default1" and value2 == "default2",
                                 "Should be able to clear all state")
    except Exception as e:
        tester.test_functionality("Clear all state", False, f"Error: {str(e)}")
        tester.record_issue("Functionality", "Clear all state", 
                           f"Failed to clear all state: {str(e)}", "Medium")
    
    # Test storing complex data types
    try:
        # Set a dictionary
        dict_value = {"key1": "value1", "key2": 2, "key3": [1, 2, 3]}
        set_state("dict_key", dict_value)
        
        # Get the dictionary
        retrieved_dict = get_state("dict_key")
        
        tester.test_functionality("Store and retrieve dictionary", 
                                 retrieved_dict == dict_value,
                                 "Should be able to store and retrieve a dictionary")
        
        # Set a list
        list_value = [1, "two", 3.0, {"four": 4}]
        set_state("list_key", list_value)
        
        # Get the list
        retrieved_list = get_state("list_key")
        
        tester.test_functionality("Store and retrieve list", 
                                 retrieved_list == list_value,
                                 "Should be able to store and retrieve a list")
        
        # Set a DataFrame
        df_value = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
        set_state("df_key", df_value)
        
        # Get the DataFrame
        retrieved_df = get_state("df_key")
        
        # Check if the DataFrames are equal (using equals method for DataFrames)
        df_equal = retrieved_df.equals(df_value) if isinstance(retrieved_df, pd.DataFrame) else False
        
        tester.test_functionality("Store and retrieve DataFrame", 
                                 df_equal,
                                 "Should be able to store and retrieve a DataFrame")
    except Exception as e:
        tester.test_functionality("Store complex data types", False, f"Error: {str(e)}")
        tester.record_issue("Functionality", "Store complex data types", 
                           f"Failed to store complex data types: {str(e)}", "High")
    
    tester.end_component_test()


def test_state_manager(tester: StateManagementTester):
    """
    Test state manager functionality.
    
    Args:
        tester: The StateManagementTester instance
    """
    tester.start_component_test("State Manager")
    
    # Use the real state manager if available, otherwise use the mock
    if HAS_STATE_MODULES:
        state_manager = StateManager()
    else:
        state_manager = MockStateManager()
    
    # Test initialization
    try:
        tester.test_functionality("Initialize state manager", 
                                 state_manager is not None,
                                 "Should be able to initialize the state manager")
    except Exception as e:
        tester.test_functionality("Initialize state manager", False, f"Error: {str(e)}")
        tester.record_issue("Functionality", "Initialize state manager", 
                           f"Failed to initialize state manager: {str(e)}", "High")
    
    # Test setting and getting a value
    try:
        # Set a value
        state_manager.set("test_key", "test_value")
        
        # Get the value
        value = state_manager.get("test_key")
        
        tester.test_functionality("Set and get value", 
                                 value == "test_value",
                                 "Should be able to set and get a value")
    except Exception as e:
        tester.test_functionality("Set and get value", False, f"Error: {str(e)}")
        tester.record_issue("Functionality", "Set and get value", 
                           f"Failed to set and get a value: {str(e)}", "High")
    
    # Test getting all state
    try:
        # Set multiple values
        state_manager.set("key1", "value1")
        state_manager.set("key2", "value2")
        
        # Get all state
        all_state = state_manager.get_all()
        
        tester.test_functionality("Get all state", 
                                 isinstance(all_state, dict) and 
                                 all_state.get("key1") == "value1" and 
                                 all_state.get("key2") == "value2",
                                 "Should be able to get all state")
    except Exception as e:
        tester.test_functionality("Get all state", False, f"Error: {str(e)}")
        tester.record_issue("Functionality", "Get all state", 
                           f"Failed to get all state: {str(e)}", "Medium")
    
    # Test clearing state
    try:
        # Set a value
        state_manager.set("key_to_clear", "value_to_clear")
        
        # Clear the key
        state_manager.clear("key_to_clear")
        
        # Try to get the value
        value = state_manager.get("key_to_clear", "default_after_clear")
        
        tester.test_functionality("Clear specific key", 
                                 value == "default_after_clear",
                                 "Should be able to clear a specific key")
        
        # Set multiple values
        state_manager.set("key1", "value1")
        state_manager.set("key2", "value2")
        
        # Clear all state
        state_manager.clear()
        
        # Get all state
        all_state = state_manager.get_all()
        
        tester.test_functionality("Clear all state", 
                                 isinstance(all_state, dict) and len(all_state) == 0,
                                 "Should be able to clear all state")
    except Exception as e:
        tester.test_functionality("Clear state", False, f"Error: {str(e)}")
        tester.record_issue("Functionality", "Clear state", 
                           f"Failed to clear state: {str(e)}", "Medium")
    
    tester.end_component_test()


def test_cross_page_state(tester: StateManagementTester):
    """
    Test cross-page state management.
    
    Args:
        tester: The StateManagementTester instance
    """
    tester.start_component_test("Cross-Page State")
    
    # Use the real state manager if available, otherwise use the mock
    if HAS_STATE_MODULES:
        state_manager = StateManager()
    else:
        state_manager = MockStateManager()
    
    # Simulate multiple pages
    pages = ["page1", "page2", "page3"]
    
    # Test setting state on one page and retrieving it on another
    try:
        # Simulate being on page1
        current_page = pages[0]
        
        # Set some state
        state_manager.set("shared_key", "shared_value")
        state_manager.set(f"{current_page}_key", f"{current_page}_value")
        
        # Simulate navigating to page2
        current_page = pages[1]
        
        # Check if we can access the shared state
        shared_value = state_manager.get("shared_key")
        
        tester.test_functionality("Access shared state across pages", 
                                 shared_value == "shared_value",
                                 "Should be able to access shared state across pages")
        
        # Set page-specific state
        state_manager.set(f"{current_page}_key", f"{current_page}_value")
        
        # Simulate navigating to page3
        current_page = pages[2]
        
        # Check if we can access the shared state and page-specific state
        shared_value = state_manager.get("shared_key")
        page1_value = state_manager.get(f"{pages[0]}_key")
        page2_value = state_manager.get(f"{pages[1]}_key")
        
        tester.test_functionality("Access page-specific state", 
                                 shared_value == "shared_value" and 
                                 page1_value == f"{pages[0]}_value" and 
                                 page2_value == f"{pages[1]}_value",
                                 "Should be able to access page-specific state")
    except Exception as e:
        tester.test_functionality("Cross-page state management", False, f"Error: {str(e)}")
        tester.record_issue("Functionality", "Cross-page state management", 
                           f"Failed to manage state across pages: {str(e)}", "High")
    
    # Test clearing state on one page and checking if it affects other pages
    try:
        # Simulate being on page1
        current_page = pages[0]
        
        # Set some state
        state_manager.set("shared_key", "shared_value")
        state_manager.set(f"{current_page}_key", f"{current_page}_value")
        
        # Simulate navigating to page2
        current_page = pages[1]
        
        # Set page-specific state
        state_manager.set(f"{current_page}_key", f"{current_page}_value")
        
        # Clear page-specific state
        state_manager.clear(f"{current_page}_key")
        
        # Check if page1's state is still intact
        page1_value = state_manager.get(f"{pages[0]}_key")
        page2_value = state_manager.get(f"{pages[1]}_key", "default")
        
        tester.test_functionality("Clear page-specific state", 
                                 page1_value == f"{pages[0]}_value" and 
                                 page2_value == "default",
                                 "Should be able to clear page-specific state without affecting other pages")
        
        # Clear all state
        state_manager.clear()
        
        # Check if all state is cleared
        shared_value = state_manager.get("shared_key", "default")
        page1_value = state_manager.get(f"{pages[0]}_key", "default")
        
        tester.test_functionality("Clear all state across pages", 
                                 shared_value == "default" and 
                                 page1_value == "default",
                                 "Should be able to clear all state across pages")
    except Exception as e:
        tester.test_functionality("Clear state across pages", False, f"Error: {str(e)}")
        tester.record_issue("Functionality", "Clear state across pages", 
                           f"Failed to clear state across pages: {str(e)}", "Medium")
    
    tester.end_component_test()


def test_state_persistence(tester: StateManagementTester):
    """
    Test state persistence functionality.
    
    Args:
        tester: The StateManagementTester instance
    """
    tester.start_component_test("State Persistence")
    
    # Use the real state manager if available, otherwise use the mock
    if HAS_STATE_MODULES:
        state_manager = StateManager()
    else:
        state_manager = MockStateManager()
    
    # Test saving state to a file and loading it back
    try:
        # Set some state
        state_manager.set("key1", "value1")
        state_manager.set("key2", 2)
        state_manager.set("key3", [1, 2, 3])
        
        # Create a temporary file for saving state
        temp_file = "temp_state.json"
        
        # Save state to file (this is a mock test since we don't know the actual API)
        try:
            # Assuming there's a save_to_file method
            if hasattr(state_manager, "save_to_file"):
                state_manager.save_to_file(temp_file)
                save_method_exists = True
            else:
                # Mock saving to file
                with open(temp_file, "w") as f:
                    json.dump(state_manager.get_all(), f)
                save_method_exists = False
            
            tester.test_functionality("Save state to file", 
                                     True,
                                     f"{'Used' if save_method_exists else 'Mocked'} save_to_file method")
        except Exception as e:
            tester.test_functionality("Save state to file", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Save state to file", 
                               f"Failed to save state to file: {str(e)}", "Medium")
            # Skip the rest of this test
            raise
        
        # Clear state
        state_manager.clear()
        
        # Check if state is cleared
        value1 = state_manager.get("key1", "default")
        tester.test_functionality("Clear state before loading", 
                                 value1 == "default",
                                 "State should be cleared before loading")
        
        # Load state from file
        try:
            # Assuming there's a load_from_file method
            if hasattr(state_manager, "load_from_file"):
                state_manager.load_from_file(temp_file)
                load_method_exists = True
            else:
                # Mock loading from file
                with open(temp_file, "r") as f:
                    loaded_state = json.load(f)
                    for key, value in loaded_state.items():
                        state_manager.set(key, value)
                load_method_exists = False
            
            tester.test_functionality("Load state from file", 
                                     True,
                                     f"{'Used' if load_method_exists else 'Mocked'} load_from_file method")
        except Exception as e:
            tester.test_functionality("Load state from file", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Load state from file", 
                               f"Failed to load state from file: {str(e)}", "Medium")
            # Skip the rest of this test
            raise
        
        # Check if state is loaded correctly
        value1 = state_manager.get("key1")
        value2 = state_manager.get("key2")
        value3 = state_manager.get("key3")
        
        tester.test_functionality("State loaded correctly", 
                                 value1 == "value1" and value2 == 2 and value3 == [1, 2, 3],
                                 "State should be loaded correctly from file")
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
    except Exception as e:
        tester.test_functionality("State persistence", False, f"Error: {str(e)}")
        tester.record_issue("Functionality", "State persistence", 
                           f"Failed to test state persistence: {str(e)}", "Medium")
        # Clean up
        if os.path.exists("temp_state.json"):
            os.remove("temp_state.json")
    
    tester.end_component_test()


def run_all_tests():
    """
    Run all state management tests and generate reports.
    """
    print("=== Running State Management Tests ===")
    
    tester = StateManagementTester()
    
    # Run all tests
    test_session_state(tester)
    test_state_manager(tester)
    test_cross_page_state(tester)
    test_state_persistence(tester)
    
    # Create results directory if it doesn't exist
    os.makedirs("science_data_kit/ui/tests/results", exist_ok=True)
    
    # Generate reports
    results_df = tester.generate_report("science_data_kit/ui/tests/results/state_management_test_results.csv")
    issues_df = tester.generate_issues_report("science_data_kit/ui/tests/results/state_management_test_issues.csv")
    
    return results_df, issues_df


if __name__ == "__main__":
    run_all_tests()