import streamlit as st
import pandas as pd
import os
import sys
import time
import importlib
import inspect
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import plugin system modules
try:
    from science_data_kit.core.plugins.plugin_manager import PluginManager, load_plugin, get_available_plugins
    from science_data_kit.core.plugins.plugin_interface import PluginInterface
    HAS_PLUGIN_MODULES = True
except ImportError:
    HAS_PLUGIN_MODULES = False
    print("Warning: Plugin system modules not found. Some tests will be skipped.")


class PluginSystemTester:
    """
    A class for testing plugin system functionality in the Science Data Kit UI.
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
            
        issue_id = f"PS-{len(self.issues) + 1:03d}"
        
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


# Create a mock plugin for testing
class MockPlugin(PluginInterface):
    """A mock plugin for testing the plugin system."""
    
    @classmethod
    def get_name(cls):
        return "MockPlugin"
    
    @classmethod
    def get_description(cls):
        return "A mock plugin for testing the plugin system"
    
    @classmethod
    def get_version(cls):
        return "1.0.0"
    
    def process_data(self, data):
        """Process the input data."""
        if isinstance(data, pd.DataFrame):
            return data.describe()
        return None


def test_plugin_manager(tester: PluginSystemTester):
    """
    Test plugin manager functionality.
    
    Args:
        tester: The PluginSystemTester instance
    """
    tester.start_component_test("Plugin Manager")
    
    # Test plugin manager initialization
    if HAS_PLUGIN_MODULES:
        try:
            plugin_manager = PluginManager()
            tester.test_functionality("Initialize plugin manager", 
                                     isinstance(plugin_manager, PluginManager),
                                     "Plugin manager should be initialized successfully")
        except Exception as e:
            tester.test_functionality("Initialize plugin manager", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Initialize plugin manager", 
                               f"Failed to initialize plugin manager: {str(e)}", "High")
    else:
        tester.test_functionality("Initialize plugin manager", False, "Plugin system module not available")
    
    # Test getting available plugins
    if HAS_PLUGIN_MODULES:
        try:
            available_plugins = get_available_plugins()
            tester.test_functionality("Get available plugins", 
                                     isinstance(available_plugins, list),
                                     f"Found {len(available_plugins)} available plugins")
        except Exception as e:
            tester.test_functionality("Get available plugins", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Get available plugins", 
                               f"Failed to get available plugins: {str(e)}", "High")
    else:
        tester.test_functionality("Get available plugins", False, "Plugin system module not available")
    
    # Test registering a plugin
    if HAS_PLUGIN_MODULES:
        try:
            plugin_manager = PluginManager()
            plugin_manager.register_plugin(MockPlugin)
            registered_plugins = plugin_manager.get_registered_plugins()
            tester.test_functionality("Register plugin", 
                                     "MockPlugin" in registered_plugins,
                                     "MockPlugin should be registered successfully")
        except Exception as e:
            tester.test_functionality("Register plugin", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Register plugin", 
                               f"Failed to register plugin: {str(e)}", "High")
    else:
        tester.test_functionality("Register plugin", False, "Plugin system module not available")
    
    # Test loading a plugin
    if HAS_PLUGIN_MODULES:
        try:
            plugin = load_plugin("MockPlugin")
            tester.test_functionality("Load plugin", 
                                     plugin is not None and plugin.get_name() == "MockPlugin",
                                     "MockPlugin should be loaded successfully")
        except Exception as e:
            tester.test_functionality("Load plugin", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Load plugin", 
                               f"Failed to load plugin: {str(e)}", "High")
    else:
        tester.test_functionality("Load plugin", False, "Plugin system module not available")
    
    # Test error handling with invalid plugin
    if HAS_PLUGIN_MODULES:
        try:
            load_plugin("NonexistentPlugin")
            tester.test_error_handling("Handle invalid plugin", False, 
                                      "Should raise an error for invalid plugin")
            tester.record_issue("Error Handling", "Handle invalid plugin", 
                               "Failed to raise error for invalid plugin", "Medium")
        except Exception:
            tester.test_error_handling("Handle invalid plugin", True, 
                                      "Correctly raised error for invalid plugin")
    else:
        tester.test_error_handling("Handle invalid plugin", False, "Plugin system module not available")
    
    tester.end_component_test()


def test_plugin_interface(tester: PluginSystemTester):
    """
    Test plugin interface functionality.
    
    Args:
        tester: The PluginSystemTester instance
    """
    tester.start_component_test("Plugin Interface")
    
    # Test plugin interface methods
    if HAS_PLUGIN_MODULES:
        try:
            # Check if PluginInterface has the required methods
            required_methods = ["get_name", "get_description", "get_version", "process_data"]
            has_methods = all(hasattr(PluginInterface, method) for method in required_methods)
            tester.test_functionality("Plugin interface has required methods", 
                                     has_methods,
                                     "PluginInterface should have all required methods")
            if not has_methods:
                missing_methods = [method for method in required_methods if not hasattr(PluginInterface, method)]
                tester.record_issue("Functionality", "Plugin interface has required methods", 
                                   f"Missing methods: {', '.join(missing_methods)}", "High")
        except Exception as e:
            tester.test_functionality("Plugin interface has required methods", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Plugin interface has required methods", 
                               f"Failed to check plugin interface methods: {str(e)}", "High")
    else:
        tester.test_functionality("Plugin interface has required methods", False, "Plugin system module not available")
    
    # Test plugin implementation
    if HAS_PLUGIN_MODULES:
        try:
            mock_plugin = MockPlugin()
            tester.test_functionality("Create plugin instance", 
                                     isinstance(mock_plugin, PluginInterface),
                                     "Plugin instance should be created successfully")
        except Exception as e:
            tester.test_functionality("Create plugin instance", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Create plugin instance", 
                               f"Failed to create plugin instance: {str(e)}", "High")
    else:
        tester.test_functionality("Create plugin instance", False, "Plugin system module not available")
    
    # Test plugin metadata methods
    if HAS_PLUGIN_MODULES:
        try:
            mock_plugin = MockPlugin()
            name = mock_plugin.get_name()
            description = mock_plugin.get_description()
            version = mock_plugin.get_version()
            
            tester.test_functionality("Plugin metadata methods", 
                                     name == "MockPlugin" and 
                                     description == "A mock plugin for testing the plugin system" and
                                     version == "1.0.0",
                                     "Plugin metadata methods should return correct values")
        except Exception as e:
            tester.test_functionality("Plugin metadata methods", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Plugin metadata methods", 
                               f"Failed to call plugin metadata methods: {str(e)}", "Medium")
    else:
        tester.test_functionality("Plugin metadata methods", False, "Plugin system module not available")
    
    # Test plugin process_data method
    if HAS_PLUGIN_MODULES:
        try:
            mock_plugin = MockPlugin()
            test_data = pd.DataFrame({
                "A": [1, 2, 3, 4, 5],
                "B": [10, 20, 30, 40, 50]
            })
            result = mock_plugin.process_data(test_data)
            
            tester.test_functionality("Plugin process_data method", 
                                     isinstance(result, pd.DataFrame) and result.shape[0] > 0,
                                     "process_data method should return a non-empty DataFrame")
        except Exception as e:
            tester.test_functionality("Plugin process_data method", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Plugin process_data method", 
                               f"Failed to call process_data method: {str(e)}", "High")
    else:
        tester.test_functionality("Plugin process_data method", False, "Plugin system module not available")
    
    tester.end_component_test()


def test_plugin_integration(tester: PluginSystemTester):
    """
    Test plugin integration with the application.
    
    Args:
        tester: The PluginSystemTester instance
    """
    tester.start_component_test("Plugin Integration")
    
    # Test plugin registration and usage
    if HAS_PLUGIN_MODULES:
        try:
            # Register the plugin
            plugin_manager = PluginManager()
            plugin_manager.register_plugin(MockPlugin)
            
            # Get the plugin
            plugin_name = MockPlugin.get_name()
            plugin = plugin_manager.get_plugin(plugin_name)
            
            # Use the plugin
            test_data = pd.DataFrame({
                "A": [1, 2, 3, 4, 5],
                "B": [10, 20, 30, 40, 50]
            })
            result = plugin.process_data(test_data)
            
            tester.test_integration("Plugin registration and usage", 
                                   plugin is not None and isinstance(result, pd.DataFrame),
                                   "Plugin should be registered and used successfully")
        except Exception as e:
            tester.test_integration("Plugin registration and usage", False, f"Error: {str(e)}")
            tester.record_issue("Integration", "Plugin registration and usage", 
                               f"Failed to register and use plugin: {str(e)}", "High")
    else:
        tester.test_integration("Plugin registration and usage", False, "Plugin system module not available")
    
    # Test multiple plugin registration
    if HAS_PLUGIN_MODULES:
        try:
            # Create a second mock plugin class
            class MockPlugin2(PluginInterface):
                @classmethod
                def get_name(cls):
                    return "MockPlugin2"
                
                @classmethod
                def get_description(cls):
                    return "Another mock plugin for testing"
                
                @classmethod
                def get_version(cls):
                    return "1.0.0"
                
                def process_data(self, data):
                    if isinstance(data, pd.DataFrame):
                        return data.sum()
                    return None
            
            # Register both plugins
            plugin_manager = PluginManager()
            plugin_manager.register_plugin(MockPlugin)
            plugin_manager.register_plugin(MockPlugin2)
            
            # Get registered plugins
            registered_plugins = plugin_manager.get_registered_plugins()
            
            tester.test_integration("Multiple plugin registration", 
                                   "MockPlugin" in registered_plugins and "MockPlugin2" in registered_plugins,
                                   "Multiple plugins should be registered successfully")
        except Exception as e:
            tester.test_integration("Multiple plugin registration", False, f"Error: {str(e)}")
            tester.record_issue("Integration", "Multiple plugin registration", 
                               f"Failed to register multiple plugins: {str(e)}", "Medium")
    else:
        tester.test_integration("Multiple plugin registration", False, "Plugin system module not available")
    
    # Test plugin discovery
    if HAS_PLUGIN_MODULES:
        try:
            # This test assumes that the plugin system has a discovery mechanism
            # that can find plugins in a specific directory
            available_plugins = get_available_plugins()
            
            tester.test_integration("Plugin discovery", 
                                   isinstance(available_plugins, list),
                                   f"Plugin discovery found {len(available_plugins)} plugins")
        except Exception as e:
            tester.test_integration("Plugin discovery", False, f"Error: {str(e)}")
            tester.record_issue("Integration", "Plugin discovery", 
                               f"Failed to discover plugins: {str(e)}", "Medium")
    else:
        tester.test_integration("Plugin discovery", False, "Plugin system module not available")
    
    tester.end_component_test()


def run_all_tests():
    """
    Run all plugin system tests and generate reports.
    """
    print("=== Running Plugin System Tests ===")
    
    tester = PluginSystemTester()
    
    # Run all tests
    test_plugin_manager(tester)
    test_plugin_interface(tester)
    test_plugin_integration(tester)
    
    # Create results directory if it doesn't exist
    os.makedirs("science_data_kit/ui/tests/results", exist_ok=True)
    
    # Generate reports
    results_df = tester.generate_report("science_data_kit/ui/tests/results/plugin_system_test_results.csv")
    issues_df = tester.generate_issues_report("science_data_kit/ui/tests/results/plugin_system_test_issues.csv")
    
    return results_df, issues_df


if __name__ == "__main__":
    run_all_tests()