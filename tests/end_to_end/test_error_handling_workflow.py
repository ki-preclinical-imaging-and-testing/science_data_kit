"""
End-to-end test for error handling in parallel processing workflows.

This module contains tests that simulate real-world error scenarios in parallel
processing workflows and verify that they are handled correctly.
"""

import time
import pandas as pd
import pytest
import logging
from unittest.mock import MagicMock

from science_data_kit.core.utils.error_handling import (
    ErrorCode,
    SDKError,
    ParallelExecutionError,
    TaskExecutionError,
    TaskTimeoutError,
    TaskNotFoundError,
    ExecutorShutdownError,
    ErrorHandler,
    PerformanceMonitor,
    retry
)
from science_data_kit.core.utils.parallel_processing import (
    parallel_map,
    parallel_process_dataframe,
    ParallelExecutor,
    ParallelDataProcessor,
    BackgroundTaskManager,
    TaskStatus,
    submit_background_task
)


def test_error_handling_in_parallel_map():
    """
    Test error handling in parallel_map.
    
    This test:
    1. Creates a dataset with values that will cause errors
    2. Processes it using parallel_map with error handling
    3. Verifies that errors are handled correctly
    """
    # Create a dataset with values that will cause errors
    data = [1, 2, 0, 4, 5]  # 0 will cause a division error
    
    # Define a processing function that will fail for certain inputs
    def divide_by_input(x):
        return 10 / x
    
    # Create an error handler
    error_handler = ErrorHandler()
    
    # Process the data with error handling
    results = error_handler.handle_operation(
        lambda: parallel_map(divide_by_input, data),
        error_code=ErrorCode.PARALLEL_EXECUTION_ERROR,
        error_message="Error in parallel map operation",
        default_value=[],
        raise_error=False
    )
    
    # Verify that the error was handled and the default value was returned
    assert results == []


def test_retry_with_parallel_processing():
    """
    Test retry mechanism with parallel processing.
    
    This test:
    1. Creates a function that fails initially but succeeds after retries
    2. Applies the retry decorator to the function
    3. Verifies that the function eventually succeeds
    """
    # Create a counter to track the number of attempts
    attempts = [0]
    
    # Define a function that fails initially but succeeds after retries
    @retry(max_retries=3, retry_delay=0.1, error_message="Parallel processing failed")
    def flaky_parallel_operation():
        attempts[0] += 1
        if attempts[0] < 3:
            # Simulate a failure in one of the parallel tasks
            data = [1, 2, 3, 4, 5]
            
            def failing_function(x):
                if x == 3:
                    raise ValueError(f"Error processing {x}")
                return x * 2
            
            return parallel_map(failing_function, data)
        else:
            # Succeed on the third attempt
            data = [1, 2, 3, 4, 5]
            return parallel_map(lambda x: x * 2, data)
    
    # Call the function and verify that it eventually succeeds
    results = flaky_parallel_operation()
    
    # Verify the results
    assert results == [2, 4, 6, 8, 10]
    assert attempts[0] == 3  # Function should have been called 3 times


def test_background_task_error_handling():
    """
    Test error handling in background tasks.
    
    This test:
    1. Creates a BackgroundTaskManager
    2. Submits a task that will fail
    3. Verifies that the error is handled correctly
    """
    # Create a BackgroundTaskManager
    manager = BackgroundTaskManager()
    
    try:
        # Submit a task that will fail
        task_id = manager.submit_task(lambda: 1/0)
        
        # Verify that the task status is initially PENDING or RUNNING
        status = manager.get_task_status(task_id)
        assert status in [TaskStatus.PENDING, TaskStatus.RUNNING]
        
        # Wait for the task to fail
        time.sleep(0.1)
        
        # Verify that the task status is now FAILED
        status = manager.get_task_status(task_id)
        assert status == TaskStatus.FAILED
        
        # Try to get the task result and verify that it raises the correct error
        with pytest.raises(TaskExecutionError) as excinfo:
            manager.get_task_result(task_id)
        
        # Verify that the error contains the relevant information
        error = excinfo.value
        assert error.code == ErrorCode.TASK_EXECUTION_ERROR
        assert "Task" in error.message
        assert "failed" in error.message
        assert "ZeroDivisionError" in str(error.details)
    
    finally:
        # Clean up
        manager.shutdown()


def test_parallel_dataframe_error_handling():
    """
    Test error handling in parallel dataframe processing.
    
    This test:
    1. Creates a dataframe with values that will cause errors
    2. Processes it using parallel_process_dataframe with error handling
    3. Verifies that errors are handled correctly
    """
    # Create a dataframe with values that will cause errors
    df = pd.DataFrame({
        'A': [1, 2, 0, 4, 5],  # 0 will cause a division error
        'group': ['X', 'X', 'Y', 'Y', 'Z']
    })
    
    # Define a processing function that will fail for certain inputs
    def process_group(group_df):
        group_df['B'] = 10 / group_df['A']
        return group_df
    
    # Create an error handler
    error_handler = ErrorHandler()
    
    # Process the dataframe with error handling
    result_df = error_handler.handle_operation(
        lambda: parallel_process_dataframe(df, process_group, by_column='group'),
        error_code=ErrorCode.PARALLEL_EXECUTION_ERROR,
        error_message="Error in parallel dataframe processing",
        default_value=pd.DataFrame(),
        raise_error=False
    )
    
    # Verify that the error was handled and the default value was returned
    assert result_df.empty


def test_performance_monitoring_with_error_handling():
    """
    Test performance monitoring with error handling.
    
    This test:
    1. Creates a PerformanceMonitor
    2. Measures the execution time of an operation that includes error handling
    3. Verifies that the execution time is measured correctly
    """
    # Create a logger and a performance monitor
    logger = MagicMock()
    monitor = PerformanceMonitor(logger)
    
    # Create an error handler
    error_handler = ErrorHandler()
    
    # Create a dataset with values that will cause errors
    data = [1, 2, 0, 4, 5]  # 0 will cause a division error
    
    # Define a processing function that will fail for certain inputs
    def divide_by_input(x):
        return 10 / x
    
    # Start the timer
    monitor.start_timer("error_handling_operation")
    
    # Process the data with error handling
    results = error_handler.handle_operation(
        lambda: parallel_map(divide_by_input, data),
        error_code=ErrorCode.PARALLEL_EXECUTION_ERROR,
        error_message="Error in parallel map operation",
        default_value=[],
        raise_error=False
    )
    
    # Stop the timer and log the results
    elapsed = monitor.stop_timer("error_handling_operation")
    
    # Verify that the error was handled and the default value was returned
    assert results == []
    
    # Verify that the elapsed time was measured
    assert elapsed > 0
    
    # Verify that the logger was called with the elapsed time
    logger.log.assert_called_once()
    assert "error_handling_operation" in logger.log.call_args[0][1]
    assert str(elapsed)[:4] in logger.log.call_args[0][1]


if __name__ == "__main__":
    # This allows running the tests directly
    pytest.main(["-xvs", __file__])