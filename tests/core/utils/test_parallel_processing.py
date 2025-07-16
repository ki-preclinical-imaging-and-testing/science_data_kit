"""
Tests for the parallel processing utilities.

This module contains tests for the parallel processing utilities in the
science_data_kit.core.utils.parallel_processing module, with a focus on
error handling and logging.
"""

import logging
import time
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
import numpy as np

from science_data_kit.core.utils.error_handling import (
    ErrorCode,
    ParallelExecutionError,
    TaskExecutionError,
    TaskNotFoundError,
    TaskTimeoutError,
    ExecutorShutdownError
)
from science_data_kit.core.utils.parallel_processing import (
    ParallelExecutor,
    ParallelDataProcessor,
    BackgroundTaskManager,
    TaskStatus,
    parallel_map,
    parallel_process_dataframe,
    submit_background_task
)


class TestParallelExecutor(unittest.TestCase):
    """Tests for the ParallelExecutor class."""

    def test_map_success(self):
        """Test that map returns the correct results when successful."""
        executor = ParallelExecutor(max_workers=2)
        results = executor.map(lambda x: x * 2, [1, 2, 3, 4, 5])
        self.assertEqual(results, [2, 4, 6, 8, 10])

    def test_map_empty_input(self):
        """Test that map handles empty input correctly."""
        executor = ParallelExecutor(max_workers=2)
        results = executor.map(lambda x: x * 2, [])
        self.assertEqual(results, [])

    def test_map_error_handling(self):
        """Test that map handles errors correctly."""
        executor = ParallelExecutor(max_workers=2)
        
        # Define a function that raises an exception for a specific input
        def failing_function(x):
            if x == 3:
                raise ValueError(f"Error processing {x}")
            return x * 2
        
        # Test that the error is properly wrapped in a ParallelExecutionError
        with self.assertRaises(ParallelExecutionError) as context:
            executor.map(failing_function, [1, 2, 3, 4, 5])
        
        # Check that the error message contains the relevant information
        error = context.exception
        self.assertIsInstance(error, ParallelExecutionError)
        self.assertIn("Task execution failed", error.message)
        self.assertIn("3", str(error.details))

    @patch('concurrent.futures.ThreadPoolExecutor.submit')
    def test_map_timeout(self, mock_submit):
        """Test that map handles timeouts correctly."""
        # Mock the submit method to simulate a long-running task
        def side_effect(func, item):
            mock_future = MagicMock()
            if item == 3:
                # Simulate a task that takes too long
                mock_future.result.side_effect = lambda: time.sleep(10)
            else:
                mock_future.result.return_value = func(item)
            return mock_future
        
        mock_submit.side_effect = side_effect
        
        executor = ParallelExecutor(max_workers=2)
        
        # Test that a timeout error is raised
        with self.assertRaises(TaskTimeoutError) as context:
            executor.map(lambda x: x * 2, [1, 2, 3, 4, 5], timeout=0.1)
        
        # Check that the error message contains the relevant information
        error = context.exception
        self.assertIsInstance(error, TaskTimeoutError)
        self.assertIn("timed out", error.message)
        self.assertEqual(error.code, ErrorCode.TASK_TIMEOUT)

    def test_execute_tasks_success(self):
        """Test that execute_tasks returns the correct results when successful."""
        executor = ParallelExecutor(max_workers=2)
        tasks = [lambda: 1, lambda: 2, lambda: 3, lambda: 4, lambda: 5]
        results = executor.execute_tasks(tasks)
        self.assertEqual(sorted(results), [1, 2, 3, 4, 5])

    def test_execute_tasks_error_handling(self):
        """Test that execute_tasks handles errors correctly."""
        executor = ParallelExecutor(max_workers=2)
        
        # Define tasks with one that fails
        tasks = [
            lambda: 1,
            lambda: 2,
            lambda: 1/0,  # This will raise a ZeroDivisionError
            lambda: 4,
            lambda: 5
        ]
        
        # Test that the error is properly wrapped in a TaskExecutionError
        with self.assertRaises(TaskExecutionError) as context:
            executor.execute_tasks(tasks)
        
        # Check that the error message contains the relevant information
        error = context.exception
        self.assertIsInstance(error, TaskExecutionError)
        self.assertIn("Task execution failed", error.message)

    def test_shutdown(self):
        """Test that operations fail after shutdown."""
        executor = ParallelExecutor(max_workers=2)
        executor.is_shutdown = True
        
        with self.assertRaises(ExecutorShutdownError) as context:
            executor.map(lambda x: x * 2, [1, 2, 3])
        
        error = context.exception
        self.assertIsInstance(error, ExecutorShutdownError)
        self.assertIn("shutdown", error.message.lower())


class TestParallelDataProcessor(unittest.TestCase):
    """Tests for the ParallelDataProcessor class."""

    def test_process_data_success(self):
        """Test that process_data returns the correct results when successful."""
        processor = ParallelDataProcessor(max_workers=2)
        results = processor.process_data([1, 2, 3, 4, 5], lambda x: x * 2)
        self.assertEqual(results, [2, 4, 6, 8, 10])

    def test_process_data_empty_input(self):
        """Test that process_data handles empty input correctly."""
        processor = ParallelDataProcessor(max_workers=2)
        results = processor.process_data([], lambda x: x * 2)
        self.assertEqual(results, [])

    def test_process_data_with_chunks(self):
        """Test that process_data handles chunking correctly."""
        processor = ParallelDataProcessor(max_workers=2, chunk_size=2)
        results = processor.process_data([1, 2, 3, 4, 5], lambda x: x * 2)
        self.assertEqual(results, [2, 4, 6, 8, 10])

    def test_process_data_with_progress_callback(self):
        """Test that process_data calls the progress callback correctly."""
        processor = ParallelDataProcessor(max_workers=2, chunk_size=2)
        
        # Create a mock progress callback
        progress_callback = MagicMock()
        
        results = processor.process_data(
            [1, 2, 3, 4, 5],
            lambda x: x * 2,
            progress_callback=progress_callback
        )
        
        # Check that the progress callback was called with the correct arguments
        self.assertEqual(results, [2, 4, 6, 8, 10])
        self.assertEqual(progress_callback.call_count, 4)  # Initial + 3 chunks
        
        # Check the first call (initial progress)
        args, _ = progress_callback.call_args_list[0]
        self.assertEqual(args, (0, 5))
        
        # Check the last call (final progress)
        args, _ = progress_callback.call_args_list[-1]
        self.assertEqual(args, (5, 5))

    def test_process_dataframe_success(self):
        """Test that process_dataframe returns the correct results when successful."""
        processor = ParallelDataProcessor(max_workers=2)
        
        # Create a test DataFrame
        df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})
        
        # Define a processing function
        def process_func(chunk_df):
            chunk_df['result'] = chunk_df['value'] * 2
            return chunk_df
        
        # Process the DataFrame
        result_df = processor.process_dataframe(df, process_func)
        
        # Check the results
        self.assertEqual(len(result_df), 5)
        self.assertTrue('result' in result_df.columns)
        self.assertEqual(list(result_df['result']), [2, 4, 6, 8, 10])

    def test_process_dataframe_with_groupby(self):
        """Test that process_dataframe handles groupby correctly."""
        processor = ParallelDataProcessor(max_workers=2)
        
        # Create a test DataFrame with groups
        df = pd.DataFrame({
            'group': ['A', 'A', 'B', 'B', 'C'],
            'value': [1, 2, 3, 4, 5]
        })
        
        # Define a processing function
        def process_func(chunk_df):
            chunk_df['result'] = chunk_df['value'] * 2
            return chunk_df
        
        # Process the DataFrame with groupby
        result_df = processor.process_dataframe(df, process_func, by_column='group')
        
        # Check the results
        self.assertEqual(len(result_df), 5)
        self.assertTrue('result' in result_df.columns)
        self.assertEqual(list(result_df['result']), [2, 4, 6, 8, 10])


class TestBackgroundTaskManager(unittest.TestCase):
    """Tests for the BackgroundTaskManager class."""

    def test_submit_task_success(self):
        """Test that submit_task returns a task ID and the task completes successfully."""
        manager = BackgroundTaskManager(max_workers=2)
        
        # Submit a simple task
        task_id = manager.submit_task(lambda: "success")
        
        # Check that a task ID was returned
        self.assertIsInstance(task_id, str)
        
        # Check that the task status is initially PENDING
        status = manager.get_task_status(task_id)
        self.assertEqual(status, TaskStatus.PENDING)
        
        # Wait for the task to complete
        result = manager.get_task_result(task_id)
        
        # Check that the task completed successfully
        self.assertEqual(result, "success")
        self.assertEqual(manager.get_task_status(task_id), TaskStatus.COMPLETED)

    def test_submit_task_failure(self):
        """Test that submit_task handles task failures correctly."""
        manager = BackgroundTaskManager(max_workers=2)
        
        # Submit a task that will fail
        task_id = manager.submit_task(lambda: 1/0)
        
        # Wait for the task to fail
        with self.assertRaises(TaskExecutionError) as context:
            manager.get_task_result(task_id)
        
        # Check that the task status is FAILED
        self.assertEqual(manager.get_task_status(task_id), TaskStatus.FAILED)
        
        # Check that the error message contains the relevant information
        error = context.exception
        self.assertIsInstance(error, TaskExecutionError)
        self.assertIn("Task", error.message)
        self.assertIn("failed", error.message)

    def test_get_task_result_not_found(self):
        """Test that get_task_result raises TaskNotFoundError for non-existent tasks."""
        manager = BackgroundTaskManager(max_workers=2)
        
        with self.assertRaises(TaskNotFoundError) as context:
            manager.get_task_result("non_existent_task_id")
        
        # Check that the error message contains the relevant information
        error = context.exception
        self.assertIsInstance(error, TaskNotFoundError)
        self.assertIn("not found", error.message)

    def test_cancel_task(self):
        """Test that cancel_task cancels a task correctly."""
        manager = BackgroundTaskManager(max_workers=2)
        
        # Submit a task that sleeps for a while
        task_id = manager.submit_task(lambda: time.sleep(10))
        
        # Cancel the task
        result = manager.cancel_task(task_id)
        
        # Check that the task was cancelled
        self.assertTrue(result)
        self.assertEqual(manager.get_task_status(task_id), TaskStatus.CANCELLED)

    def test_shutdown(self):
        """Test that shutdown shuts down the manager correctly."""
        manager = BackgroundTaskManager(max_workers=2)
        
        # Submit a task
        task_id = manager.submit_task(lambda: "success")
        
        # Shut down the manager
        manager.shutdown(wait=True)
        
        # Check that the manager is shut down
        self.assertTrue(manager.is_shutdown)
        
        # Check that submitting a new task raises an error
        with self.assertRaises(ExecutorShutdownError) as context:
            manager.submit_task(lambda: "failure")
        
        # Check that the error message contains the relevant information
        error = context.exception
        self.assertIsInstance(error, ExecutorShutdownError)
        self.assertIn("shut down", error.message)


class TestConvenienceFunctions(unittest.TestCase):
    """Tests for the convenience functions."""

    def test_parallel_map(self):
        """Test that parallel_map returns the correct results."""
        results = parallel_map(lambda x: x * 2, [1, 2, 3, 4, 5])
        self.assertEqual(results, [2, 4, 6, 8, 10])

    def test_parallel_process_dataframe(self):
        """Test that parallel_process_dataframe returns the correct results."""
        # Create a test DataFrame
        df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})
        
        # Define a processing function
        def process_func(chunk_df):
            chunk_df['result'] = chunk_df['value'] * 2
            return chunk_df
        
        # Process the DataFrame
        result_df = parallel_process_dataframe(df, process_func)
        
        # Check the results
        self.assertEqual(len(result_df), 5)
        self.assertTrue('result' in result_df.columns)
        self.assertEqual(list(result_df['result']), [2, 4, 6, 8, 10])

    def test_submit_background_task(self):
        """Test that submit_background_task returns a task ID and manager."""
        # Submit a simple task
        task_id, manager = submit_background_task(lambda: "success")
        
        # Check that a task ID and manager were returned
        self.assertIsInstance(task_id, str)
        self.assertIsInstance(manager, BackgroundTaskManager)
        
        # Wait for the task to complete
        result = manager.get_task_result(task_id)
        
        # Check that the task completed successfully
        self.assertEqual(result, "success")
        self.assertEqual(manager.get_task_status(task_id), TaskStatus.COMPLETED)
        
        # Clean up
        manager.shutdown()


if __name__ == "__main__":
    unittest.main()