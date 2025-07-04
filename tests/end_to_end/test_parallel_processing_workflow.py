#!/usr/bin/env python
"""
End-to-end test for parallel processing workflows.
"""
import time
import pandas as pd
import pytest
from science_data_kit.core.utils.parallel_processing import (
    parallel_map,
    parallel_process_dataframe,
    ParallelExecutor,
    ParallelDataProcessor,
    BackgroundTaskManager,
)


def test_parallel_map_workflow():
    """
    Test a complete workflow using parallel_map.
    
    This test:
    1. Creates a dataset
    2. Processes it using parallel_map
    3. Verifies the results
    """
    # Create a dataset
    data = list(range(1, 11))  # [1, 2, 3, ..., 10]
    
    # Define a processing function that simulates some work
    def slow_square(x):
        time.sleep(0.01)  # Simulate work
        return x * x
    
    # Process the data using parallel processing
    start_time = time.time()
    results = parallel_map(slow_square, data)
    parallel_time = time.time() - start_time
    
    # Process the data sequentially for comparison
    start_time = time.time()
    sequential_results = [slow_square(x) for x in data]
    sequential_time = time.time() - start_time
    
    # Verify the results are correct
    assert results == [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
    assert results == sequential_results
    
    # Verify that parallel processing was faster (not always true for small datasets)
    # This is a soft assertion - we log but don't fail if it's not faster
    if parallel_time >= sequential_time:
        print(f"Warning: Parallel processing ({parallel_time:.4f}s) was not faster than sequential processing ({sequential_time:.4f}s)")


def test_parallel_dataframe_workflow():
    """
    Test a complete workflow using parallel_process_dataframe.
    
    This test:
    1. Creates a dataframe
    2. Processes it using parallel_process_dataframe
    3. Verifies the results
    """
    # Create a dataframe
    df = pd.DataFrame({
        'A': range(1, 11),
        'B': range(11, 21),
        'group': ['X', 'X', 'X', 'X', 'X', 'Y', 'Y', 'Y', 'Y', 'Y']
    })
    
    # Define a processing function that simulates some work
    def process_group(group_df):
        time.sleep(0.01)  # Simulate work
        group_df['C'] = group_df['A'] * group_df['B']
        return group_df
    
    # Process the dataframe using parallel processing
    result_df = parallel_process_dataframe(df, process_group, by_column='group')
    
    # Verify the results
    assert 'C' in result_df.columns
    assert result_df['C'].tolist() == [x * y for x, y in zip(df['A'], df['B'])]
    assert len(result_df) == len(df)


def test_background_task_workflow():
    """
    Test a complete workflow using BackgroundTaskManager.
    
    This test:
    1. Creates a BackgroundTaskManager
    2. Submits tasks to it
    3. Retrieves the results
    4. Verifies the results
    """
    # Create a BackgroundTaskManager
    manager = BackgroundTaskManager()
    
    # Define a task function that simulates some work
    def long_running_task(duration, return_value):
        time.sleep(duration)
        return return_value
    
    try:
        # Submit tasks
        task1_id = manager.submit_task(long_running_task, 0.01, "Task 1 Result")
        task2_id = manager.submit_task(long_running_task, 0.02, "Task 2 Result")
        
        # Check task status
        assert manager.get_task_status(task1_id) in ["PENDING", "RUNNING", "COMPLETED"]
        assert manager.get_task_status(task2_id) in ["PENDING", "RUNNING", "COMPLETED"]
        
        # Get task results
        result1 = manager.get_task_result(task1_id)
        result2 = manager.get_task_result(task2_id)
        
        # Verify the results
        assert result1 == "Task 1 Result"
        assert result2 == "Task 2 Result"
        
        # Check that all tasks are completed
        all_tasks = manager.get_all_tasks()
        assert len(all_tasks) == 2
        assert all(task["status"] == "COMPLETED" for task in all_tasks.values())
    
    finally:
        # Clean up
        manager.shutdown()


if __name__ == "__main__":
    # This allows running the tests directly
    pytest.main(["-xvs", __file__])