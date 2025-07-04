"""
Background Processing Utilities for Science Data Kit

This module provides high-level utilities for running operations in the background,
making it easy to execute long-running tasks without blocking the main thread.
It builds on the parallel_processing module to provide a simpler interface for
common background processing needs.
"""

import logging
import time
from typing import Callable, Dict, List, Any, Optional, TypeVar, Tuple, Union
from functools import wraps

from science_data_kit.core.utils.parallel_processing import BackgroundTaskManager, TaskStatus

# Type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')

# Global BackgroundTaskManager instance
_global_task_manager = BackgroundTaskManager()
_logger = logging.getLogger(__name__)

def get_global_task_manager() -> BackgroundTaskManager:
    """
    Get the global BackgroundTaskManager instance.
    
    Returns:
        The global BackgroundTaskManager instance.
    """
    return _global_task_manager

def run_in_background(func: Callable[..., R]) -> Callable[..., str]:
    """
    Decorator to run a function in the background.
    
    This decorator wraps a function to run in the background using the global
    BackgroundTaskManager. It returns a task ID that can be used to check the
    status and retrieve the result.
    
    Args:
        func: The function to run in the background.
        
    Returns:
        A wrapper function that submits the original function to run in the
        background and returns a task ID.
    
    Example:
        @run_in_background
        def long_running_operation(param1, param2):
            # Do something time-consuming
            return result
            
        # Run the operation in the background
        task_id = long_running_operation(param1, param2)
        
        # Check status later
        status = get_task_status(task_id)
        
        # Get result when ready
        result = get_task_result(task_id)
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> str:
        _logger.info(f"Running {func.__name__} in background")
        return _global_task_manager.submit_task(func, *args, **kwargs)
    return wrapper

def run_task_in_background(task_func: Callable[..., R], *args, **kwargs) -> str:
    """
    Run a function in the background using the global BackgroundTaskManager.
    
    This is a convenience function that submits a task to the global
    BackgroundTaskManager and returns a task ID.
    
    Args:
        task_func: Function to execute in the background.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.
        
    Returns:
        Task ID that can be used to check status and retrieve results.
        
    Example:
        def long_running_operation(param1, param2):
            # Do something time-consuming
            return result
            
        # Run the operation in the background
        task_id = run_task_in_background(long_running_operation, param1, param2)
        
        # Check status later
        status = get_task_status(task_id)
        
        # Get result when ready
        result = get_task_result(task_id)
    """
    _logger.info(f"Running {task_func.__name__} in background")
    return _global_task_manager.submit_task(task_func, *args, **kwargs)

def get_task_status(task_id: str) -> TaskStatus:
    """
    Get the status of a background task.
    
    Args:
        task_id: ID of the task to check.
        
    Returns:
        Status of the task.
        
    Raises:
        KeyError: If the task ID is not found.
    """
    return _global_task_manager.get_task_status(task_id)

def get_task_result(task_id: str, timeout: Optional[float] = None, raise_exception: bool = True) -> Optional[R]:
    """
    Get the result of a completed background task.
    
    Args:
        task_id: ID of the task to get the result for.
        timeout: Optional timeout in seconds to wait for the task to complete.
        raise_exception: Whether to raise an exception if the task failed.
        
    Returns:
        Result of the task, or None if the task failed and raise_exception is False.
        
    Raises:
        KeyError: If the task ID is not found.
        TimeoutError: If the task does not complete within the timeout.
        Exception: If the task failed and raise_exception is True.
    """
    return _global_task_manager.get_task_result(task_id, timeout, raise_exception)

def cancel_task(task_id: str) -> bool:
    """
    Cancel a background task if it is still pending or running.
    
    Args:
        task_id: ID of the task to cancel.
        
    Returns:
        True if the task was cancelled, False if it could not be cancelled.
        
    Raises:
        KeyError: If the task ID is not found.
    """
    return _global_task_manager.cancel_task(task_id)

def get_all_tasks() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all background tasks.
    
    Returns:
        Dictionary mapping task IDs to task information.
    """
    return _global_task_manager.get_all_tasks()

def wait_for_task(task_id: str, timeout: Optional[float] = None, check_interval: float = 0.1) -> TaskStatus:
    """
    Wait for a background task to complete.
    
    Args:
        task_id: ID of the task to wait for.
        timeout: Optional timeout in seconds to wait for the task to complete.
        check_interval: Interval in seconds between status checks.
        
    Returns:
        Final status of the task.
        
    Raises:
        KeyError: If the task ID is not found.
        TimeoutError: If the task does not complete within the timeout.
    """
    start_time = time.time()
    while True:
        status = get_task_status(task_id)
        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return status
            
        if timeout is not None and time.time() - start_time > timeout:
            raise TimeoutError(f"Task {task_id} did not complete within the timeout")
            
        time.sleep(check_interval)

def wait_for_tasks(task_ids: List[str], timeout: Optional[float] = None, check_interval: float = 0.1) -> Dict[str, TaskStatus]:
    """
    Wait for multiple background tasks to complete.
    
    Args:
        task_ids: List of task IDs to wait for.
        timeout: Optional timeout in seconds to wait for all tasks to complete.
        check_interval: Interval in seconds between status checks.
        
    Returns:
        Dictionary mapping task IDs to their final statuses.
        
    Raises:
        KeyError: If any task ID is not found.
        TimeoutError: If all tasks do not complete within the timeout.
    """
    start_time = time.time()
    pending_tasks = set(task_ids)
    statuses = {}
    
    while pending_tasks:
        for task_id in list(pending_tasks):
            status = get_task_status(task_id)
            if status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                statuses[task_id] = status
                pending_tasks.remove(task_id)
                
        if not pending_tasks:
            break
            
        if timeout is not None and time.time() - start_time > timeout:
            # Add current status for remaining tasks
            for task_id in pending_tasks:
                statuses[task_id] = get_task_status(task_id)
            raise TimeoutError(f"Not all tasks completed within the timeout. Current statuses: {statuses}")
            
        time.sleep(check_interval)
        
    return statuses

def shutdown_background_processing(wait: bool = True):
    """
    Shut down the global BackgroundTaskManager.
    
    This should be called when the application is shutting down to ensure
    all background tasks are properly cleaned up.
    
    Args:
        wait: Whether to wait for pending tasks to complete.
    """
    _global_task_manager.shutdown(wait=wait)

def example_background_processing():
    """
    Example of using background processing utilities.
    
    Returns:
        Dictionary with example results.
    """
    import time
    
    # Define a long-running task
    def long_running_task(duration, return_value):
        """Simulate a long-running task."""
        time.sleep(duration)
        return return_value
    
    # Run tasks in the background
    task1_id = run_task_in_background(long_running_task, 2, "Task 1 completed")
    task2_id = run_task_in_background(long_running_task, 4, "Task 2 completed")
    
    # Check status immediately after submission
    initial_status = {
        'task1': get_task_status(task1_id).value,
        'task2': get_task_status(task2_id).value
    }
    
    # Wait for task 1 to complete
    wait_for_task(task1_id)
    result1 = get_task_result(task1_id)
    
    # Check status after task 1 completes
    mid_status = {
        'task1': get_task_status(task1_id).value,
        'task2': get_task_status(task2_id).value
    }
    
    # Cancel task 2
    cancelled = cancel_task(task2_id)
    
    # Check final status
    final_status = {
        'task1': get_task_status(task1_id).value,
        'task2': get_task_status(task2_id).value
    }
    
    return {
        'initial_status': initial_status,
        'mid_status': mid_status,
        'final_status': final_status,
        'task1_result': result1,
        'task2_cancelled': cancelled
    }

# Example with decorator
def example_decorator_usage():
    """
    Example of using the run_in_background decorator.
    
    Returns:
        Dictionary with example results.
    """
    import time
    
    @run_in_background
    def long_running_task(duration, return_value):
        """Simulate a long-running task."""
        time.sleep(duration)
        return return_value
    
    # Run tasks in the background
    task1_id = long_running_task(2, "Task 1 completed")
    task2_id = long_running_task(4, "Task 2 completed")
    
    # Wait for both tasks to complete or timeout after 3 seconds
    try:
        statuses = wait_for_tasks([task1_id, task2_id], timeout=3)
        all_completed = all(status == TaskStatus.COMPLETED for status in statuses.values())
    except TimeoutError:
        all_completed = False
    
    # Get results for completed tasks
    results = {}
    for task_id in [task1_id, task2_id]:
        try:
            status = get_task_status(task_id)
            if status == TaskStatus.COMPLETED:
                results[task_id] = get_task_result(task_id)
            else:
                results[task_id] = f"Task not completed: {status.value}"
        except Exception as e:
            results[task_id] = f"Error: {str(e)}"
    
    return {
        'all_completed': all_completed,
        'results': results
    }