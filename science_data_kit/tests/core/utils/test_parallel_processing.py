"""
Tests for the parallel_processing module.
"""

import unittest
import time
from unittest.mock import patch, MagicMock

from science_data_kit.core.utils.parallel_processing import (
    ParallelExecutor,
    ParallelDataProcessor,
    BackgroundTaskManager,
    TaskStatus,
    submit_background_task,
    parallel_map
)


class TestParallelExecutor(unittest.TestCase):
    """Tests for the ParallelExecutor class."""

    def test_map(self):
        """Test the map method."""
        executor = ParallelExecutor(max_workers=2)
        items = [1, 2, 3, 4, 5]
        results = executor.map(lambda x: x * 2, items)
        self.assertEqual(results, [2, 4, 6, 8, 10])

    def test_execute_tasks(self):
        """Test the execute_tasks method."""
        executor = ParallelExecutor(max_workers=2)
        tasks = [lambda: 1, lambda: 2, lambda: 3]
        results = executor.execute_tasks(tasks)
        self.assertEqual(sorted(results), [1, 2, 3])


class TestParallelDataProcessor(unittest.TestCase):
    """Tests for the ParallelDataProcessor class."""

    def test_process_data(self):
        """Test the process_data method."""
        processor = ParallelDataProcessor(max_workers=2)
        data = [1, 2, 3, 4, 5]
        results = processor.process_data(data, lambda x: x * 2)
        self.assertEqual(results, [2, 4, 6, 8, 10])

    def test_process_data_with_chunks(self):
        """Test the process_data method with chunking."""
        processor = ParallelDataProcessor(max_workers=2, chunk_size=2)
        data = [1, 2, 3, 4, 5]
        results = processor.process_data(data, lambda x: x * 2)
        self.assertEqual(results, [2, 4, 6, 8, 10])

    def test_process_data_with_progress_callback(self):
        """Test the process_data method with progress callback."""
        processor = ParallelDataProcessor(max_workers=2)
        data = [1, 2, 3, 4, 5]
        progress_callback = MagicMock()
        results = processor.process_data(data, lambda x: x * 2, progress_callback=progress_callback)
        self.assertEqual(results, [2, 4, 6, 8, 10])
        # Progress callback should be called at least twice (initial and final)
        self.assertGreaterEqual(progress_callback.call_count, 2)


class TestBackgroundTaskManager(unittest.TestCase):
    """Tests for the BackgroundTaskManager class."""

    def test_submit_task(self):
        """Test submitting a task."""
        manager = BackgroundTaskManager(max_workers=2)
        task_id = manager.submit_task(lambda: 42)
        self.assertIsNotNone(task_id)
        self.assertEqual(manager.get_task_status(task_id), TaskStatus.PENDING)

    def test_get_task_result(self):
        """Test getting a task result."""
        manager = BackgroundTaskManager(max_workers=2)
        task_id = manager.submit_task(lambda: 42)
        result = manager.get_task_result(task_id)
        self.assertEqual(result, 42)
        self.assertEqual(manager.get_task_status(task_id), TaskStatus.COMPLETED)

    def test_get_task_result_with_timeout(self):
        """Test getting a task result with timeout."""
        manager = BackgroundTaskManager(max_workers=2)
        
        # Submit a task that takes 1 second to complete
        task_id = manager.submit_task(lambda: time.sleep(1) or 42)
        
        # Get the result with a timeout of 2 seconds (should succeed)
        result = manager.get_task_result(task_id, timeout=2)
        self.assertEqual(result, 42)
        self.assertEqual(manager.get_task_status(task_id), TaskStatus.COMPLETED)

    def test_get_task_result_with_timeout_error(self):
        """Test getting a task result with timeout error."""
        manager = BackgroundTaskManager(max_workers=2)
        
        # Submit a task that takes 2 seconds to complete
        task_id = manager.submit_task(lambda: time.sleep(2) or 42)
        
        # Get the result with a timeout of 0.1 seconds (should fail)
        with self.assertRaises(TimeoutError):
            manager.get_task_result(task_id, timeout=0.1)

    def test_cancel_task(self):
        """Test cancelling a task."""
        manager = BackgroundTaskManager(max_workers=2)
        
        # Submit a task that takes 2 seconds to complete
        task_id = manager.submit_task(lambda: time.sleep(2) or 42)
        
        # Cancel the task
        cancelled = manager.cancel_task(task_id)
        
        # The task may or may not be cancelled depending on timing
        if cancelled:
            self.assertEqual(manager.get_task_status(task_id), TaskStatus.CANCELLED)
        else:
            # If not cancelled, the task should eventually complete
            result = manager.get_task_result(task_id)
            self.assertEqual(result, 42)
            self.assertEqual(manager.get_task_status(task_id), TaskStatus.COMPLETED)

    def test_get_all_tasks(self):
        """Test getting all tasks."""
        manager = BackgroundTaskManager(max_workers=2)
        
        # Submit two tasks
        task1_id = manager.submit_task(lambda: 42)
        task2_id = manager.submit_task(lambda: 84)
        
        # Get all tasks
        tasks = manager.get_all_tasks()
        
        # Should have two tasks
        self.assertEqual(len(tasks), 2)
        self.assertIn(task1_id, tasks)
        self.assertIn(task2_id, tasks)

    def test_shutdown(self):
        """Test shutting down the manager."""
        manager = BackgroundTaskManager(max_workers=2)
        
        # Submit a task
        task_id = manager.submit_task(lambda: 42)
        
        # Shutdown the manager
        manager.shutdown()
        
        # The manager should be shut down
        self.assertTrue(manager.is_shutdown)
        
        # Submitting a new task should raise an exception
        with self.assertRaises(RuntimeError):
            manager.submit_task(lambda: 84)

    def test_task_error_handling(self):
        """Test error handling in tasks."""
        manager = BackgroundTaskManager(max_workers=2)
        
        # Submit a task that raises an exception
        task_id = manager.submit_task(lambda: 1/0)
        
        # Get the result (should raise an exception)
        with self.assertRaises(ZeroDivisionError):
            manager.get_task_result(task_id)
        
        # The task status should be FAILED
        self.assertEqual(manager.get_task_status(task_id), TaskStatus.FAILED)
        
        # Get the result with raise_exception=False
        result = manager.get_task_result(task_id, raise_exception=False)
        self.assertIsNone(result)


class TestConvenienceFunctions(unittest.TestCase):
    """Tests for convenience functions."""

    def test_parallel_map(self):
        """Test the parallel_map function."""
        items = [1, 2, 3, 4, 5]
        results = parallel_map(lambda x: x * 2, items)
        self.assertEqual(results, [2, 4, 6, 8, 10])

    def test_submit_background_task(self):
        """Test the submit_background_task function."""
        task_id, manager = submit_background_task(lambda: 42)
        self.assertIsNotNone(task_id)
        self.assertIsInstance(manager, BackgroundTaskManager)
        
        # Get the result
        result = manager.get_task_result(task_id)
        self.assertEqual(result, 42)
        
        # Shutdown the manager
        manager.shutdown()


if __name__ == '__main__':
    unittest.main()