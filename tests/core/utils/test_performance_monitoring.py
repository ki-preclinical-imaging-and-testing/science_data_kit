"""
Tests for performance monitoring in real-world scenarios.

This module contains tests for the performance monitoring utilities in the
science_data_kit.core.utils.error_handling module, with a focus on real-world
scenarios.
"""

import time
import unittest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch

from science_data_kit.core.utils.error_handling import (
    PerformanceMonitor,
    measure_execution_time
)
from science_data_kit.core.utils.parallel_processing import (
    parallel_map,
    parallel_process_dataframe,
    ParallelExecutor,
    ParallelDataProcessor
)


class TestPerformanceMonitoringRealScenarios(unittest.TestCase):
    """Tests for performance monitoring in real-world scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = MagicMock()
        self.monitor = PerformanceMonitor(self.logger)

    def test_monitor_parallel_map(self):
        """Test monitoring the performance of parallel_map."""
        # Create a dataset
        data = list(range(1, 101))  # [1, 2, 3, ..., 100]
        
        # Define a processing function that simulates some work
        def slow_square(x):
            time.sleep(0.001)  # Simulate work
            return x * x
        
        # Start the timer
        self.monitor.start_timer("parallel_map")
        
        # Process the data using parallel processing
        results = parallel_map(slow_square, data)
        
        # Stop the timer and log the results
        elapsed = self.monitor.stop_timer("parallel_map")
        
        # Verify the results
        self.assertEqual(len(results), 100)
        self.assertEqual(results[0], 1)
        self.assertEqual(results[99], 10000)
        
        # Verify that the elapsed time was measured
        self.assertGreater(elapsed, 0)
        
        # Verify that the logger was called with the elapsed time
        self.logger.log.assert_called_once()
        self.assertIn("parallel_map", self.logger.log.call_args[0][1])
        self.assertIn(str(elapsed)[:4], self.logger.log.call_args[0][1])

    def test_monitor_dataframe_processing(self):
        """Test monitoring the performance of dataframe processing."""
        # Create a dataframe
        df = pd.DataFrame({
            'A': np.random.rand(1000),
            'B': np.random.rand(1000),
            'group': np.random.choice(['X', 'Y', 'Z'], 1000)
        })
        
        # Define a processing function that simulates some work
        def process_group(group_df):
            time.sleep(0.001)  # Simulate work
            group_df['C'] = group_df['A'] * group_df['B']
            return group_df
        
        # Start the timer
        self.monitor.start_timer("dataframe_processing")
        
        # Process the dataframe using parallel processing
        result_df = parallel_process_dataframe(df, process_group, by_column='group')
        
        # Stop the timer and log the results
        elapsed = self.monitor.stop_timer("dataframe_processing")
        
        # Verify the results
        self.assertEqual(len(result_df), 1000)
        self.assertTrue('C' in result_df.columns)
        
        # Verify that the elapsed time was measured
        self.assertGreater(elapsed, 0)
        
        # Verify that the logger was called with the elapsed time
        self.logger.log.assert_called_once()
        self.assertIn("dataframe_processing", self.logger.log.call_args[0][1])
        self.assertIn(str(elapsed)[:4], self.logger.log.call_args[0][1])

    def test_monitor_multiple_operations(self):
        """Test monitoring the performance of multiple operations."""
        # Create a dataset
        data = list(range(1, 101))  # [1, 2, 3, ..., 100]
        
        # Define a processing function that simulates some work
        def slow_square(x):
            time.sleep(0.001)  # Simulate work
            return x * x
        
        # Start the timer for the first operation
        self.monitor.start_timer("operation1")
        
        # Process the data using parallel processing
        results1 = parallel_map(slow_square, data)
        
        # Stop the timer for the first operation
        elapsed1 = self.monitor.stop_timer("operation1")
        
        # Start the timer for the second operation
        self.monitor.start_timer("operation2")
        
        # Process the data using parallel processing with a different function
        results2 = parallel_map(lambda x: x * 3, data)
        
        # Stop the timer for the second operation
        elapsed2 = self.monitor.stop_timer("operation2")
        
        # Verify the results
        self.assertEqual(len(results1), 100)
        self.assertEqual(results1[0], 1)
        self.assertEqual(results1[99], 10000)
        
        self.assertEqual(len(results2), 100)
        self.assertEqual(results2[0], 3)
        self.assertEqual(results2[99], 300)
        
        # Verify that the elapsed times were measured
        self.assertGreater(elapsed1, 0)
        self.assertGreater(elapsed2, 0)
        
        # Verify that the logger was called with the elapsed times
        self.assertEqual(self.logger.log.call_count, 2)
        
        # Check the first call
        self.assertIn("operation1", self.logger.log.call_args_list[0][0][1])
        self.assertIn(str(elapsed1)[:4], self.logger.log.call_args_list[0][0][1])
        
        # Check the second call
        self.assertIn("operation2", self.logger.log.call_args_list[1][0][1])
        self.assertIn(str(elapsed2)[:4], self.logger.log.call_args_list[1][0][1])

    def test_measure_execution_time_decorator_with_parallel_processing(self):
        """Test the measure_execution_time decorator with parallel processing."""
        logger = MagicMock()
        
        # Define a function that uses parallel processing
        @measure_execution_time(name="parallel_processing", logger=logger)
        def process_data(data):
            return parallel_map(lambda x: x * 2, data)
        
        # Create a dataset
        data = list(range(1, 101))  # [1, 2, 3, ..., 100]
        
        # Process the data
        results = process_data(data)
        
        # Verify the results
        self.assertEqual(len(results), 100)
        self.assertEqual(results[0], 2)
        self.assertEqual(results[99], 200)
        
        # Verify that the logger was called
        logger.log.assert_called_once()
        self.assertIn("parallel_processing", logger.log.call_args[0][1])

    def test_performance_comparison(self):
        """Test comparing the performance of different approaches."""
        # Create a dataset
        data = list(range(1, 101))  # [1, 2, 3, ..., 100]
        
        # Define a processing function that simulates some work
        def slow_square(x):
            time.sleep(0.001)  # Simulate work
            return x * x
        
        # Measure sequential processing time
        self.monitor.start_timer("sequential")
        sequential_results = [slow_square(x) for x in data]
        sequential_time = self.monitor.stop_timer("sequential")
        
        # Measure parallel processing time
        self.monitor.start_timer("parallel")
        parallel_results = parallel_map(slow_square, data)
        parallel_time = self.monitor.stop_timer("parallel")
        
        # Verify the results are the same
        self.assertEqual(sequential_results, parallel_results)
        
        # Verify that both times were measured
        self.assertGreater(sequential_time, 0)
        self.assertGreater(parallel_time, 0)
        
        # Log the comparison
        self.monitor.logger.info(
            f"Performance comparison: Sequential: {sequential_time:.4f}s, "
            f"Parallel: {parallel_time:.4f}s, "
            f"Speedup: {sequential_time / parallel_time:.2f}x"
        )
        
        # Verify that the logger was called for both timers
        self.assertEqual(self.logger.log.call_count, 2)
        
        # Check the first call (sequential)
        self.assertIn("sequential", self.logger.log.call_args_list[0][0][1])
        self.assertIn(str(sequential_time)[:4], self.logger.log.call_args_list[0][0][1])
        
        # Check the second call (parallel)
        self.assertIn("parallel", self.logger.log.call_args_list[1][0][1])
        self.assertIn(str(parallel_time)[:4], self.logger.log.call_args_list[1][0][1])


if __name__ == "__main__":
    unittest.main()