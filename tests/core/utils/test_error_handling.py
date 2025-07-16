"""
Tests for the error handling utilities.

This module contains tests for the error handling utilities in the
science_data_kit.core.utils.error_handling module.
"""

import logging
import time
import unittest
from unittest.mock import MagicMock, patch

from science_data_kit.core.utils.error_handling import (
    ErrorCode,
    ErrorHandler,
    ParallelExecutionError,
    PerformanceMonitor,
    SDKError,
    TaskExecutionError,
    TaskTimeoutError,
    get_logger,
    log_debug,
    log_error,
    log_info,
    log_warning,
    measure_execution_time,
    retry
)


class TestSDKError(unittest.TestCase):
    """Tests for the SDKError class."""

    def test_sdk_error_init(self):
        """Test that SDKError initializes correctly."""
        error = SDKError(
            code=ErrorCode.INVALID_ARGUMENT,
            message="Invalid argument",
            details={"arg": "value"},
            cause=ValueError("Original error")
        )
        
        self.assertEqual(error.code, ErrorCode.INVALID_ARGUMENT)
        self.assertEqual(error.message, "Invalid argument")
        self.assertEqual(error.details, {"arg": "value"})
        self.assertIsInstance(error.cause, ValueError)
        self.assertIsInstance(error.timestamp, float)
        
        # Check that the error message includes all the information
        error_str = str(error)
        self.assertIn("INVALID_ARGUMENT", error_str)
        self.assertIn("Invalid argument", error_str)
        self.assertIn("arg", error_str)
        self.assertIn("value", error_str)
        self.assertIn("Original error", error_str)


class TestErrorHandler(unittest.TestCase):
    """Tests for the ErrorHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = MagicMock()
        self.handler = ErrorHandler(self.logger)

    def test_handle_operation_success(self):
        """Test that handle_operation returns the result of the operation when it succeeds."""
        result = self.handler.handle_operation(lambda: "success")
        self.assertEqual(result, "success")
        self.logger.log.assert_not_called()

    def test_handle_operation_failure(self):
        """Test that handle_operation handles exceptions correctly."""
        # Test with raise_error=False
        result = self.handler.handle_operation(
            lambda: 1/0,  # This will raise a ZeroDivisionError
            error_code=ErrorCode.INVALID_OPERATION,
            error_message="Division by zero",
            default_value="default",
            raise_error=False
        )
        self.assertEqual(result, "default")
        self.logger.log.assert_called_once()
        
        # Test with raise_error=True
        self.logger.reset_mock()
        with self.assertRaises(SDKError) as context:
            self.handler.handle_operation(
                lambda: 1/0,  # This will raise a ZeroDivisionError
                error_code=ErrorCode.INVALID_OPERATION,
                error_message="Division by zero",
                raise_error=True
            )
        
        error = context.exception
        self.assertEqual(error.code, ErrorCode.INVALID_OPERATION)
        self.assertEqual(error.message, "Division by zero")
        self.assertIsInstance(error.cause, ZeroDivisionError)
        self.logger.log.assert_called_once()

    def test_retry_operation_success(self):
        """Test that retry_operation returns the result when the operation succeeds."""
        result = self.handler.retry_operation(lambda: "success")
        self.assertEqual(result, "success")
        self.logger.log.assert_not_called()

    def test_retry_operation_failure_then_success(self):
        """Test that retry_operation retries the operation when it fails."""
        # Create a function that fails twice then succeeds
        counter = [0]
        
        def flaky_function():
            counter[0] += 1
            if counter[0] < 3:
                raise ValueError(f"Attempt {counter[0]} failed")
            return "success"
        
        result = self.handler.retry_operation(
            flaky_function,
            max_retries=3,
            retry_delay=0.01,  # Use a small delay for testing
            error_message="Flaky function failed"
        )
        
        self.assertEqual(result, "success")
        self.assertEqual(counter[0], 3)  # Function should have been called 3 times
        self.assertEqual(self.logger.log.call_count, 2)  # Two warnings for the failures

    def test_retry_operation_all_failures(self):
        """Test that retry_operation handles the case where all retries fail."""
        # Create a function that always fails
        def failing_function():
            raise ValueError("Always fails")
        
        # Test with raise_error=False
        result = self.handler.retry_operation(
            failing_function,
            max_retries=2,
            retry_delay=0.01,  # Use a small delay for testing
            error_message="All retries failed",
            default_value="default",
            raise_error=False
        )
        
        self.assertEqual(result, "default")
        self.assertEqual(self.logger.log.call_count, 3)  # Two warnings and one error
        
        # Test with raise_error=True
        self.logger.reset_mock()
        with self.assertRaises(SDKError) as context:
            self.handler.retry_operation(
                failing_function,
                max_retries=2,
                retry_delay=0.01,  # Use a small delay for testing
                error_code=ErrorCode.OPERATION_FAILED,
                error_message="All retries failed",
                raise_error=True
            )
        
        error = context.exception
        self.assertEqual(error.code, ErrorCode.OPERATION_FAILED)
        self.assertEqual(error.message, "All retries failed")
        self.assertEqual(self.logger.log.call_count, 3)  # Two warnings and one error


class TestRetryDecorator(unittest.TestCase):
    """Tests for the retry decorator."""

    def test_retry_decorator_success(self):
        """Test that the retry decorator returns the result when the function succeeds."""
        @retry(max_retries=3, retry_delay=0.01)
        def successful_function():
            return "success"
        
        result = successful_function()
        self.assertEqual(result, "success")

    def test_retry_decorator_failure_then_success(self):
        """Test that the retry decorator retries the function when it fails."""
        # Create a function that fails twice then succeeds
        counter = [0]
        
        @retry(max_retries=3, retry_delay=0.01)
        def flaky_function():
            counter[0] += 1
            if counter[0] < 3:
                raise ValueError(f"Attempt {counter[0]} failed")
            return "success"
        
        result = flaky_function()
        self.assertEqual(result, "success")
        self.assertEqual(counter[0], 3)  # Function should have been called 3 times

    def test_retry_decorator_all_failures(self):
        """Test that the retry decorator handles the case where all retries fail."""
        # Create a function that always fails
        @retry(
            max_retries=2,
            retry_delay=0.01,
            error_code=ErrorCode.OPERATION_FAILED,
            error_message="All retries failed"
        )
        def failing_function():
            raise ValueError("Always fails")
        
        with self.assertRaises(SDKError) as context:
            failing_function()
        
        error = context.exception
        self.assertEqual(error.code, ErrorCode.OPERATION_FAILED)
        self.assertEqual(error.message, "All retries failed")


class TestPerformanceMonitor(unittest.TestCase):
    """Tests for the PerformanceMonitor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = MagicMock()
        self.monitor = PerformanceMonitor(self.logger)

    def test_start_stop_timer(self):
        """Test that start_timer and stop_timer work correctly."""
        self.monitor.start_timer("test_timer")
        self.assertIn("test_timer", self.monitor.timers)
        
        time.sleep(0.01)  # Sleep a bit to ensure elapsed time is measurable
        
        elapsed = self.monitor.stop_timer("test_timer")
        self.assertGreater(elapsed, 0)
        self.assertNotIn("test_timer", self.monitor.timers)

    def test_log_timer(self):
        """Test that log_timer logs the elapsed time."""
        self.monitor.start_timer("test_timer")
        time.sleep(0.01)  # Sleep a bit to ensure elapsed time is measurable
        
        elapsed = self.monitor.log_timer("test_timer")
        self.assertGreater(elapsed, 0)
        self.logger.log.assert_called_once()
        self.assertIn("test_timer", self.logger.log.call_args[0][1])
        self.assertIn(str(elapsed)[:4], self.logger.log.call_args[0][1])

    def test_measure_execution_time(self):
        """Test that measure_execution_time measures and logs the execution time."""
        result = self.monitor.measure_execution_time(
            lambda: "result",
            name="test_operation"
        )
        
        self.assertEqual(result, "result")
        self.logger.log.assert_called_once()
        self.assertIn("test_operation", self.logger.log.call_args[0][1])


class TestMeasureExecutionTimeDecorator(unittest.TestCase):
    """Tests for the measure_execution_time decorator."""

    def test_measure_execution_time_decorator(self):
        """Test that the measure_execution_time decorator measures and logs the execution time."""
        logger = MagicMock()
        
        @measure_execution_time(name="test_function", logger=logger)
        def test_function():
            time.sleep(0.01)  # Sleep a bit to ensure elapsed time is measurable
            return "result"
        
        result = test_function()
        
        self.assertEqual(result, "result")
        logger.log.assert_called_once()
        self.assertIn("test_function", logger.log.call_args[0][1])


class TestLoggingFunctions(unittest.TestCase):
    """Tests for the logging functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = MagicMock()

    def test_log_debug(self):
        """Test that log_debug calls logger.debug with the correct message."""
        log_debug("Debug message", self.logger, {"key": "value"})
        self.logger.debug.assert_called_once_with("Debug message - Details: {'key': 'value'}")

    def test_log_info(self):
        """Test that log_info calls logger.info with the correct message."""
        log_info("Info message", self.logger)
        self.logger.info.assert_called_once_with("Info message")

    def test_log_warning(self):
        """Test that log_warning calls logger.warning with the correct message."""
        log_warning("Warning message", self.logger, {"key": "value"})
        self.logger.warning.assert_called_once_with("Warning message - Details: {'key': 'value'}")

    def test_log_error(self):
        """Test that log_error calls logger.error with the correct message."""
        # Test with string message
        log_error("Error message", self.logger, {"key": "value"})
        self.logger.error.assert_called_once_with("Error message - Details: {'key': 'value'}")
        
        # Test with exception
        self.logger.reset_mock()
        exception = ValueError("Test error")
        log_error(exception, self.logger)
        self.logger.error.assert_called_once()
        self.assertIn("ValueError", self.logger.error.call_args[0][0])
        self.assertIn("Test error", self.logger.error.call_args[0][0])


if __name__ == "__main__":
    unittest.main()