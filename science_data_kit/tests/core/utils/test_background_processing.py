"""
Tests for the background_processing module.
"""

import unittest
import time
from unittest.mock import patch, MagicMock

from science_data_kit.core.utils.background_processing import (
    get_global_task_manager,
    run_in_background,
    run_task_in_background,
    get_task_status,
    get_task_result,
    cancel_task,
    get_all_tasks,
    wait_for_task,
    wait_for_tasks,
    shutdown_background_processing,
    TaskStatus
)


class TestGlobalTaskManager(unittest.TestCase):
    """Tests for the global task manager."""

    def test_get_global_task_manager(self):
        """Test getting the global task manager."""
        manager = get_global_task_manager()
        self.assertIsNotNone(manager)
        # Verify it's a singleton
        manager2 = get_global_task_manager()
        self.assertIs(manager, manager2)


class TestRunInBackground(unittest.TestCase):
    """Tests for the run_in_background decorator."""

    def setUp(self):
        """Set up the test."""
        # Reset the global task manager before each test
        self.original_manager = get_global_task_manager()
        
    def tearDown(self):
        """Clean up after the test."""
        # Shutdown the task manager
        shutdown_background_processing(wait=True)

    def test_run_in_background_decorator(self):
        """Test the run_in_background decorator."""
        @run_in_background
        def test_func(x, y):
            return x + y

        # Run the function in the background
        task_id = test_func(2, 3)
        self.assertIsNotNone(task_id)
        
        # Get the result
        result = get_task_result(task_id)
        self.assertEqual(result, 5)
        
        # Check the status
        status = get_task_status(task_id)
        self.assertEqual(status, TaskStatus.COMPLETED)


class TestRunTaskInBackground(unittest.TestCase):
    """Tests for the run_task_in_background function."""

    def setUp(self):
        """Set up the test."""
        # Reset the global task manager before each test
        self.original_manager = get_global_task_manager()
        
    def tearDown(self):
        """Clean up after the test."""
        # Shutdown the task manager
        shutdown_background_processing(wait=True)

    def test_run_task_in_background(self):
        """Test running a task in the background."""
        def test_func(x, y):
            return x + y

        # Run the function in the background
        task_id = run_task_in_background(test_func, 2, 3)
        self.assertIsNotNone(task_id)
        
        # Get the result
        result = get_task_result(task_id)
        self.assertEqual(result, 5)
        
        # Check the status
        status = get_task_status(task_id)
        self.assertEqual(status, TaskStatus.COMPLETED)


class TestTaskManagement(unittest.TestCase):
    """Tests for task management functions."""

    def setUp(self):
        """Set up the test."""
        # Reset the global task manager before each test
        self.original_manager = get_global_task_manager()
        
    def tearDown(self):
        """Clean up after the test."""
        # Shutdown the task manager
        shutdown_background_processing(wait=True)

    def test_get_task_status(self):
        """Test getting a task's status."""
        def test_func():
            time.sleep(0.5)
            return 42

        # Run the function in the background
        task_id = run_task_in_background(test_func)
        
        # Check the initial status
        initial_status = get_task_status(task_id)
        self.assertIn(initial_status, [TaskStatus.PENDING, TaskStatus.RUNNING])
        
        # Wait for the task to complete
        time.sleep(1)
        
        # Check the final status
        final_status = get_task_status(task_id)
        self.assertEqual(final_status, TaskStatus.COMPLETED)

    def test_get_task_result(self):
        """Test getting a task's result."""
        def test_func():
            return 42

        # Run the function in the background
        task_id = run_task_in_background(test_func)
        
        # Get the result
        result = get_task_result(task_id)
        self.assertEqual(result, 42)

    def test_get_task_result_with_timeout(self):
        """Test getting a task's result with a timeout."""
        def test_func():
            time.sleep(0.5)
            return 42

        # Run the function in the background
        task_id = run_task_in_background(test_func)
        
        # Get the result with a timeout
        result = get_task_result(task_id, timeout=1)
        self.assertEqual(result, 42)

    def test_get_task_result_with_timeout_error(self):
        """Test getting a task's result with a timeout error."""
        def test_func():
            time.sleep(1)
            return 42

        # Run the function in the background
        task_id = run_task_in_background(test_func)
        
        # Get the result with a timeout that's too short
        with self.assertRaises(TimeoutError):
            get_task_result(task_id, timeout=0.1)

    def test_cancel_task(self):
        """Test cancelling a task."""
        def test_func():
            time.sleep(1)
            return 42

        # Run the function in the background
        task_id = run_task_in_background(test_func)
        
        # Cancel the task
        cancelled = cancel_task(task_id)
        
        # The task may or may not be cancelled depending on timing
        if cancelled:
            self.assertEqual(get_task_status(task_id), TaskStatus.CANCELLED)
        else:
            # If not cancelled, the task should eventually complete
            result = get_task_result(task_id)
            self.assertEqual(result, 42)
            self.assertEqual(get_task_status(task_id), TaskStatus.COMPLETED)

    def test_get_all_tasks(self):
        """Test getting all tasks."""
        def test_func(value):
            return value

        # Run two functions in the background
        task1_id = run_task_in_background(test_func, 42)
        task2_id = run_task_in_background(test_func, 84)
        
        # Get all tasks
        tasks = get_all_tasks()
        
        # Should have at least two tasks
        self.assertGreaterEqual(len(tasks), 2)
        self.assertIn(task1_id, tasks)
        self.assertIn(task2_id, tasks)


class TestWaitFunctions(unittest.TestCase):
    """Tests for wait functions."""

    def setUp(self):
        """Set up the test."""
        # Reset the global task manager before each test
        self.original_manager = get_global_task_manager()
        
    def tearDown(self):
        """Clean up after the test."""
        # Shutdown the task manager
        shutdown_background_processing(wait=True)

    def test_wait_for_task(self):
        """Test waiting for a task to complete."""
        def test_func():
            time.sleep(0.5)
            return 42

        # Run the function in the background
        task_id = run_task_in_background(test_func)
        
        # Wait for the task to complete
        status = wait_for_task(task_id)
        self.assertEqual(status, TaskStatus.COMPLETED)
        
        # Get the result
        result = get_task_result(task_id)
        self.assertEqual(result, 42)

    def test_wait_for_task_with_timeout(self):
        """Test waiting for a task to complete with a timeout."""
        def test_func():
            time.sleep(1)
            return 42

        # Run the function in the background
        task_id = run_task_in_background(test_func)
        
        # Wait for the task to complete with a timeout that's too short
        with self.assertRaises(TimeoutError):
            wait_for_task(task_id, timeout=0.1)

    def test_wait_for_tasks(self):
        """Test waiting for multiple tasks to complete."""
        def test_func(value):
            time.sleep(0.5)
            return value

        # Run two functions in the background
        task1_id = run_task_in_background(test_func, 42)
        task2_id = run_task_in_background(test_func, 84)
        
        # Wait for both tasks to complete
        statuses = wait_for_tasks([task1_id, task2_id])
        self.assertEqual(statuses[task1_id], TaskStatus.COMPLETED)
        self.assertEqual(statuses[task2_id], TaskStatus.COMPLETED)
        
        # Get the results
        result1 = get_task_result(task1_id)
        result2 = get_task_result(task2_id)
        self.assertEqual(result1, 42)
        self.assertEqual(result2, 84)

    def test_wait_for_tasks_with_timeout(self):
        """Test waiting for multiple tasks to complete with a timeout."""
        def test_func(sleep_time):
            time.sleep(sleep_time)
            return sleep_time

        # Run two functions in the background with different sleep times
        task1_id = run_task_in_background(test_func, 0.1)  # Should complete within timeout
        task2_id = run_task_in_background(test_func, 1.0)  # Should not complete within timeout
        
        # Wait for both tasks to complete with a timeout
        with self.assertRaises(TimeoutError):
            wait_for_tasks([task1_id, task2_id], timeout=0.5)


class TestShutdown(unittest.TestCase):
    """Tests for shutdown function."""

    def setUp(self):
        """Set up the test."""
        # Reset the global task manager before each test
        self.original_manager = get_global_task_manager()
        
    def test_shutdown_background_processing(self):
        """Test shutting down background processing."""
        def test_func():
            time.sleep(0.5)
            return 42

        # Run the function in the background
        task_id = run_task_in_background(test_func)
        
        # Shutdown background processing
        shutdown_background_processing(wait=True)
        
        # The manager should be shut down
        manager = get_global_task_manager()
        self.assertTrue(manager.is_shutdown)
        
        # Submitting a new task should raise an exception
        with self.assertRaises(RuntimeError):
            run_task_in_background(test_func)


if __name__ == '__main__':
    unittest.main()