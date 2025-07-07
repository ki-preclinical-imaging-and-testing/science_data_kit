import streamlit as st
import pandas as pd
import os
import sys
import time
import json
import csv
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple
from io import StringIO, BytesIO

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import data import/export modules
try:
    from science_data_kit.core.data.data_import import import_csv, import_excel, import_json
    from science_data_kit.core.data.data_export import export_csv, export_excel, export_json
    HAS_DATA_MODULES = True
except ImportError:
    HAS_DATA_MODULES = False
    print("Warning: Data import/export modules not found. Some tests will be skipped.")


class DataImportExportTester:
    """
    A class for testing data import/export functionality in the Science Data Kit UI.
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
            
        issue_id = f"IE-{len(self.issues) + 1:03d}"
        
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


def test_csv_import_export(tester: DataImportExportTester):
    """
    Test CSV import and export functionality.
    
    Args:
        tester: The DataImportExportTester instance
    """
    tester.start_component_test("CSV Import/Export")
    
    # Create test data
    test_data = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["New York", "Los Angeles", "Chicago"]
    })
    
    # Test CSV import functionality
    if HAS_DATA_MODULES:
        # Test importing from string
        csv_string = test_data.to_csv(index=False)
        try:
            imported_df = import_csv(StringIO(csv_string))
            tester.test_functionality("Import CSV from string", 
                                     imported_df.equals(test_data),
                                     "Imported DataFrame should match original")
        except Exception as e:
            tester.test_functionality("Import CSV from string", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Import CSV from string", 
                               f"Failed to import CSV from string: {str(e)}", "High")
        
        # Test importing with different delimiters
        csv_tab_string = test_data.to_csv(index=False, sep="\t")
        try:
            imported_df = import_csv(StringIO(csv_tab_string), delimiter="\t")
            tester.test_functionality("Import CSV with custom delimiter", 
                                     imported_df.equals(test_data),
                                     "Imported DataFrame should match original")
        except Exception as e:
            tester.test_functionality("Import CSV with custom delimiter", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Import CSV with custom delimiter", 
                               f"Failed to import CSV with custom delimiter: {str(e)}", "Medium")
    else:
        tester.test_functionality("Import CSV from string", False, "Data import module not available")
        tester.test_functionality("Import CSV with custom delimiter", False, "Data import module not available")
    
    # Test CSV export functionality
    if HAS_DATA_MODULES:
        # Test exporting to string
        try:
            output = StringIO()
            export_csv(test_data, output)
            output.seek(0)
            exported_df = pd.read_csv(output)
            tester.test_functionality("Export CSV to string", 
                                     exported_df.equals(test_data),
                                     "Exported DataFrame should match original")
        except Exception as e:
            tester.test_functionality("Export CSV to string", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Export CSV to string", 
                               f"Failed to export CSV to string: {str(e)}", "High")
        
        # Test exporting with different delimiters
        try:
            output = StringIO()
            export_csv(test_data, output, sep="\t")
            output.seek(0)
            exported_df = pd.read_csv(output, sep="\t")
            tester.test_functionality("Export CSV with custom delimiter", 
                                     exported_df.equals(test_data),
                                     "Exported DataFrame should match original")
        except Exception as e:
            tester.test_functionality("Export CSV with custom delimiter", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Export CSV with custom delimiter", 
                               f"Failed to export CSV with custom delimiter: {str(e)}", "Medium")
    else:
        tester.test_functionality("Export CSV to string", False, "Data export module not available")
        tester.test_functionality("Export CSV with custom delimiter", False, "Data export module not available")
    
    # Test error handling
    if HAS_DATA_MODULES:
        # Test importing invalid CSV
        try:
            invalid_csv = "Name,Age,City\nAlice,twenty-five,New York"
            import_csv(StringIO(invalid_csv))
            tester.test_error_handling("Handle invalid CSV data", False, 
                                      "Should raise an error for invalid data")
            tester.record_issue("Error Handling", "Handle invalid CSV data", 
                               "Failed to raise error for invalid CSV data", "Medium")
        except Exception:
            tester.test_error_handling("Handle invalid CSV data", True, 
                                      "Correctly raised error for invalid data")
    else:
        tester.test_error_handling("Handle invalid CSV data", False, "Data import module not available")
    
    # Test performance with large dataset
    if HAS_DATA_MODULES:
        # Create large test dataset
        large_data = pd.DataFrame({
            "ID": range(10000),
            "Value1": [f"Value_{i}" for i in range(10000)],
            "Value2": [i * 2.5 for i in range(10000)]
        })
        
        # Test import performance
        try:
            start_time = time.time()
            csv_string = large_data.to_csv(index=False)
            import_csv(StringIO(csv_string))
            duration = time.time() - start_time
            tester.test_performance("Import large CSV dataset", 
                                   duration < 5,  # Assuming 5 seconds is acceptable
                                   f"Import took {duration:.2f} seconds")
            if duration >= 5:
                tester.record_issue("Performance", "Import large CSV dataset", 
                                   f"Import of large CSV dataset took {duration:.2f} seconds", "Medium")
        except Exception as e:
            tester.test_performance("Import large CSV dataset", False, f"Error: {str(e)}")
            tester.record_issue("Performance", "Import large CSV dataset", 
                               f"Failed to import large CSV dataset: {str(e)}", "Medium")
        
        # Test export performance
        try:
            start_time = time.time()
            output = StringIO()
            export_csv(large_data, output)
            duration = time.time() - start_time
            tester.test_performance("Export large CSV dataset", 
                                   duration < 5,  # Assuming 5 seconds is acceptable
                                   f"Export took {duration:.2f} seconds")
            if duration >= 5:
                tester.record_issue("Performance", "Export large CSV dataset", 
                                   f"Export of large CSV dataset took {duration:.2f} seconds", "Medium")
        except Exception as e:
            tester.test_performance("Export large CSV dataset", False, f"Error: {str(e)}")
            tester.record_issue("Performance", "Export large CSV dataset", 
                               f"Failed to export large CSV dataset: {str(e)}", "Medium")
    else:
        tester.test_performance("Import large CSV dataset", False, "Data import module not available")
        tester.test_performance("Export large CSV dataset", False, "Data export module not available")
    
    tester.end_component_test()


def test_excel_import_export(tester: DataImportExportTester):
    """
    Test Excel import and export functionality.
    
    Args:
        tester: The DataImportExportTester instance
    """
    tester.start_component_test("Excel Import/Export")
    
    # Create test data
    test_data = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["New York", "Los Angeles", "Chicago"]
    })
    
    # Test Excel import functionality
    if HAS_DATA_MODULES:
        # Test importing from bytes
        excel_bytes = BytesIO()
        test_data.to_excel(excel_bytes, index=False)
        excel_bytes.seek(0)
        
        try:
            imported_df = import_excel(excel_bytes)
            tester.test_functionality("Import Excel from bytes", 
                                     imported_df.equals(test_data),
                                     "Imported DataFrame should match original")
        except Exception as e:
            tester.test_functionality("Import Excel from bytes", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Import Excel from bytes", 
                               f"Failed to import Excel from bytes: {str(e)}", "High")
        
        # Test importing with sheet name
        excel_bytes = BytesIO()
        with pd.ExcelWriter(excel_bytes, engine='openpyxl') as writer:
            test_data.to_excel(writer, sheet_name="TestSheet", index=False)
        excel_bytes.seek(0)
        
        try:
            imported_df = import_excel(excel_bytes, sheet_name="TestSheet")
            tester.test_functionality("Import Excel with sheet name", 
                                     imported_df.equals(test_data),
                                     "Imported DataFrame should match original")
        except Exception as e:
            tester.test_functionality("Import Excel with sheet name", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Import Excel with sheet name", 
                               f"Failed to import Excel with sheet name: {str(e)}", "Medium")
    else:
        tester.test_functionality("Import Excel from bytes", False, "Data import module not available")
        tester.test_functionality("Import Excel with sheet name", False, "Data import module not available")
    
    # Test Excel export functionality
    if HAS_DATA_MODULES:
        # Test exporting to bytes
        try:
            output = BytesIO()
            export_excel(test_data, output)
            output.seek(0)
            exported_df = pd.read_excel(output)
            tester.test_functionality("Export Excel to bytes", 
                                     exported_df.equals(test_data),
                                     "Exported DataFrame should match original")
        except Exception as e:
            tester.test_functionality("Export Excel to bytes", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Export Excel to bytes", 
                               f"Failed to export Excel to bytes: {str(e)}", "High")
        
        # Test exporting with sheet name
        try:
            output = BytesIO()
            export_excel(test_data, output, sheet_name="CustomSheet")
            output.seek(0)
            exported_df = pd.read_excel(output, sheet_name="CustomSheet")
            tester.test_functionality("Export Excel with sheet name", 
                                     exported_df.equals(test_data),
                                     "Exported DataFrame should match original")
        except Exception as e:
            tester.test_functionality("Export Excel with sheet name", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Export Excel with sheet name", 
                               f"Failed to export Excel with sheet name: {str(e)}", "Medium")
    else:
        tester.test_functionality("Export Excel to bytes", False, "Data export module not available")
        tester.test_functionality("Export Excel with sheet name", False, "Data export module not available")
    
    # Test error handling
    if HAS_DATA_MODULES:
        # Test importing invalid Excel file
        try:
            invalid_excel = BytesIO(b"This is not an Excel file")
            import_excel(invalid_excel)
            tester.test_error_handling("Handle invalid Excel data", False, 
                                      "Should raise an error for invalid data")
            tester.record_issue("Error Handling", "Handle invalid Excel data", 
                               "Failed to raise error for invalid Excel data", "Medium")
        except Exception:
            tester.test_error_handling("Handle invalid Excel data", True, 
                                      "Correctly raised error for invalid data")
    else:
        tester.test_error_handling("Handle invalid Excel data", False, "Data import module not available")
    
    tester.end_component_test()


def test_json_import_export(tester: DataImportExportTester):
    """
    Test JSON import and export functionality.
    
    Args:
        tester: The DataImportExportTester instance
    """
    tester.start_component_test("JSON Import/Export")
    
    # Create test data
    test_data = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["New York", "Los Angeles", "Chicago"]
    })
    
    # Test JSON import functionality
    if HAS_DATA_MODULES:
        # Test importing from string
        json_string = test_data.to_json(orient="records")
        try:
            imported_df = import_json(StringIO(json_string))
            tester.test_functionality("Import JSON from string", 
                                     imported_df.equals(test_data),
                                     "Imported DataFrame should match original")
        except Exception as e:
            tester.test_functionality("Import JSON from string", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Import JSON from string", 
                               f"Failed to import JSON from string: {str(e)}", "High")
        
        # Test importing with different orient
        json_string = test_data.to_json(orient="split")
        try:
            imported_df = import_json(StringIO(json_string), orient="split")
            tester.test_functionality("Import JSON with custom orient", 
                                     imported_df.equals(test_data),
                                     "Imported DataFrame should match original")
        except Exception as e:
            tester.test_functionality("Import JSON with custom orient", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Import JSON with custom orient", 
                               f"Failed to import JSON with custom orient: {str(e)}", "Medium")
    else:
        tester.test_functionality("Import JSON from string", False, "Data import module not available")
        tester.test_functionality("Import JSON with custom orient", False, "Data import module not available")
    
    # Test JSON export functionality
    if HAS_DATA_MODULES:
        # Test exporting to string
        try:
            output = StringIO()
            export_json(test_data, output)
            output.seek(0)
            exported_json = json.loads(output.read())
            expected_json = json.loads(test_data.to_json(orient="records"))
            tester.test_functionality("Export JSON to string", 
                                     exported_json == expected_json,
                                     "Exported JSON should match original")
        except Exception as e:
            tester.test_functionality("Export JSON to string", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Export JSON to string", 
                               f"Failed to export JSON to string: {str(e)}", "High")
        
        # Test exporting with different orient
        try:
            output = StringIO()
            export_json(test_data, output, orient="split")
            output.seek(0)
            exported_json = json.loads(output.read())
            expected_json = json.loads(test_data.to_json(orient="split"))
            tester.test_functionality("Export JSON with custom orient", 
                                     exported_json == expected_json,
                                     "Exported JSON should match original")
        except Exception as e:
            tester.test_functionality("Export JSON with custom orient", False, f"Error: {str(e)}")
            tester.record_issue("Functionality", "Export JSON with custom orient", 
                               f"Failed to export JSON with custom orient: {str(e)}", "Medium")
    else:
        tester.test_functionality("Export JSON to string", False, "Data export module not available")
        tester.test_functionality("Export JSON with custom orient", False, "Data export module not available")
    
    # Test error handling
    if HAS_DATA_MODULES:
        # Test importing invalid JSON
        try:
            invalid_json = "This is not valid JSON"
            import_json(StringIO(invalid_json))
            tester.test_error_handling("Handle invalid JSON data", False, 
                                      "Should raise an error for invalid data")
            tester.record_issue("Error Handling", "Handle invalid JSON data", 
                               "Failed to raise error for invalid JSON data", "Medium")
        except Exception:
            tester.test_error_handling("Handle invalid JSON data", True, 
                                      "Correctly raised error for invalid data")
    else:
        tester.test_error_handling("Handle invalid JSON data", False, "Data import module not available")
    
    tester.end_component_test()


def run_all_tests():
    """
    Run all data import/export tests and generate reports.
    """
    print("=== Running Data Import/Export Tests ===")
    
    tester = DataImportExportTester()
    
    # Run all tests
    test_csv_import_export(tester)
    test_excel_import_export(tester)
    test_json_import_export(tester)
    
    # Create results directory if it doesn't exist
    os.makedirs("science_data_kit/ui/tests/results", exist_ok=True)
    
    # Generate reports
    results_df = tester.generate_report("science_data_kit/ui/tests/results/data_import_export_test_results.csv")
    issues_df = tester.generate_issues_report("science_data_kit/ui/tests/results/data_import_export_test_issues.csv")
    
    return results_df, issues_df


if __name__ == "__main__":
    run_all_tests()