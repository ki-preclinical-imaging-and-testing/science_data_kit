"""
Tests for specific error types in the error handling module.

This module contains tests for the specific error types defined in the
science_data_kit.core.utils.error_handling module.
"""

import unittest
from unittest.mock import patch, MagicMock

from science_data_kit.core.utils.error_handling import (
    ErrorCode,
    SDKError,
    ParallelExecutionError,
    TaskExecutionError,
    TaskTimeoutError,
    TaskNotFoundError,
    ExecutorShutdownError,
    get_logger
)


class TestSpecificErrorTypes(unittest.TestCase):
    """Tests for specific error types."""

    def test_parallel_execution_error(self):
        """Test that ParallelExecutionError initializes correctly."""
        error = ParallelExecutionError(
            message="Parallel execution failed",
            details={"task_id": "123"},
            cause=ValueError("Original error")
        )
        
        self.assertEqual(error.code, ErrorCode.PARALLEL_EXECUTION_ERROR)
        self.assertEqual(error.message, "Parallel execution failed")
        self.assertEqual(error.details, {"task_id": "123"})
        self.assertIsInstance(error.cause, ValueError)
        
        # Check that the error message includes all the information
        error_str = str(error)
        self.assertIn("PARALLEL_EXECUTION_ERROR", error_str)
        self.assertIn("Parallel execution failed", error_str)
        self.assertIn("task_id", error_str)
        self.assertIn("123", error_str)
        self.assertIn("Original error", error_str)

    def test_task_execution_error(self):
        """Test that TaskExecutionError initializes correctly."""
        error = TaskExecutionError(
            message="Task execution failed",
            details={"task_id": "123"},
            cause=ValueError("Original error")
        )
        
        self.assertEqual(error.code, ErrorCode.TASK_EXECUTION_ERROR)
        self.assertEqual(error.message, "Task execution failed")
        self.assertEqual(error.details, {"task_id": "123"})
        self.assertIsInstance(error.cause, ValueError)
        
        # Check that the error message includes all the information
        error_str = str(error)
        self.assertIn("TASK_EXECUTION_ERROR", error_str)
        self.assertIn("Task execution failed", error_str)
        self.assertIn("task_id", error_str)
        self.assertIn("123", error_str)
        self.assertIn("Original error", error_str)

    def test_task_timeout_error(self):
        """Test that TaskTimeoutError initializes correctly."""
        error = TaskTimeoutError(
            message="Task timed out",
            details={"task_id": "123", "timeout": 10},
            cause=TimeoutError("Original timeout error")
        )
        
        self.assertEqual(error.code, ErrorCode.TASK_TIMEOUT)
        self.assertEqual(error.message, "Task timed out")
        self.assertEqual(error.details, {"task_id": "123", "timeout": 10})
        self.assertIsInstance(error.cause, TimeoutError)
        
        # Check that the error message includes all the information
        error_str = str(error)
        self.assertIn("TASK_TIMEOUT", error_str)
        self.assertIn("Task timed out", error_str)
        self.assertIn("task_id", error_str)
        self.assertIn("123", error_str)
        self.assertIn("timeout", error_str)
        self.assertIn("10", error_str)
        self.assertIn("Original timeout error", error_str)

    def test_task_not_found_error(self):
        """Test that TaskNotFoundError initializes correctly."""
        error = TaskNotFoundError(
            message="Task not found",
            details={"task_id": "123"},
            cause=None
        )
        
        self.assertEqual(error.code, ErrorCode.TASK_NOT_FOUND)
        self.assertEqual(error.message, "Task not found")
        self.assertEqual(error.details, {"task_id": "123"})
        self.assertIsNone(error.cause)
        
        # Check that the error message includes all the information
        error_str = str(error)
        self.assertIn("TASK_NOT_FOUND", error_str)
        self.assertIn("Task not found", error_str)
        self.assertIn("task_id", error_str)
        self.assertIn("123", error_str)

    def test_executor_shutdown_error(self):
        """Test that ExecutorShutdownError initializes correctly."""
        error = ExecutorShutdownError(
            message="Executor has been shut down",
            details={"executor_id": "123"},
            cause=None
        )
        
        self.assertEqual(error.code, ErrorCode.EXECUTOR_SHUTDOWN)
        self.assertEqual(error.message, "Executor has been shut down")
        self.assertEqual(error.details, {"executor_id": "123"})
        self.assertIsNone(error.cause)
        
        # Check that the error message includes all the information
        error_str = str(error)
        self.assertIn("EXECUTOR_SHUTDOWN", error_str)
        self.assertIn("Executor has been shut down", error_str)
        self.assertIn("executor_id", error_str)
        self.assertIn("123", error_str)


class TestGetLogger(unittest.TestCase):
    """Tests for the get_logger function."""

    def test_get_logger_with_name(self):
        """Test that get_logger returns a logger with the specified name."""
        logger = get_logger("test_logger")
        self.assertEqual(logger.name, "test_logger")

    @patch('inspect.currentframe')
    def test_get_logger_without_name(self, mock_currentframe):
        """Test that get_logger derives the name from the calling module."""
        # Mock the frame objects to simulate the call stack
        mock_frame = MagicMock()
        mock_frame.f_globals = {'__name__': 'test_module'}
        mock_currentframe.return_value = mock_frame
        
        logger = get_logger()
        self.assertEqual(logger.name, 'test_module')

    def test_get_logger_returns_same_logger(self):
        """Test that get_logger returns the same logger for the same name."""
        logger1 = get_logger("test_logger")
        logger2 = get_logger("test_logger")
        self.assertIs(logger1, logger2)


if __name__ == "__main__":
    unittest.main()