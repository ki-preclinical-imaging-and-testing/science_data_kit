"""
Parallel Processing Utilities for Science Data Kit

This module provides utilities for parallel processing of data operations,
enabling improved performance for computationally intensive tasks.
"""

import concurrent.futures
import multiprocessing
import logging
import time
from typing import List, Callable, Any, Dict, Optional, Union, TypeVar, Generic, Iterable, Iterator

# Type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')


class ParallelExecutor:
    """
    Executor for parallel processing of data operations.
    
    This class provides methods for executing functions in parallel using
    either thread-based or process-based parallelism, depending on the
    nature of the workload.
    """
    
    def __init__(self, max_workers: Optional[int] = None, use_processes: bool = False):
        """
        Initialize a parallel executor.
        
        Args:
            max_workers: Maximum number of workers to use. If None, uses the number
                         of CPU cores available.
            use_processes: Whether to use process-based parallelism (True) or
                          thread-based parallelism (False).
        """
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.use_processes = use_processes
        self.logger = logging.getLogger(__name__)
    
    def map(self, func: Callable[[T], R], items: Iterable[T], timeout: Optional[float] = None) -> List[R]:
        """
        Apply a function to each item in parallel.
        
        Args:
            func: Function to apply to each item.
            items: Iterable of items to process.
            timeout: Optional timeout in seconds for the entire operation.
            
        Returns:
            List of results from applying the function to each item.
            
        Raises:
            TimeoutError: If the operation times out.
            Exception: If any worker raises an exception.
        """
        executor_class = concurrent.futures.ProcessPoolExecutor if self.use_processes else concurrent.futures.ThreadPoolExecutor
        
        start_time = time.time()
        results = []
        
        with executor_class(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {executor.submit(func, item): item for item in items}
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_item):
                # Check for timeout
                if timeout and time.time() - start_time > timeout:
                    executor.shutdown(wait=False)
                    raise TimeoutError(f"Operation timed out after {timeout} seconds")
                
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Task raised an exception: {str(e)}")
                    raise
        
        return results
    
    def execute_tasks(self, tasks: List[Callable[[], R]], timeout: Optional[float] = None) -> List[R]:
        """
        Execute a list of tasks in parallel.
        
        Args:
            tasks: List of task functions to execute.
            timeout: Optional timeout in seconds for the entire operation.
            
        Returns:
            List of results from executing each task.
            
        Raises:
            TimeoutError: If the operation times out.
            Exception: If any worker raises an exception.
        """
        executor_class = concurrent.futures.ProcessPoolExecutor if self.use_processes else concurrent.futures.ThreadPoolExecutor
        
        start_time = time.time()
        results = []
        
        with executor_class(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = [executor.submit(task) for task in tasks]
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(futures):
                # Check for timeout
                if timeout and time.time() - start_time > timeout:
                    executor.shutdown(wait=False)
                    raise TimeoutError(f"Operation timed out after {timeout} seconds")
                
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Task raised an exception: {str(e)}")
                    raise
        
        return results


class ParallelDataProcessor:
    """
    Processor for parallel data operations.
    
    This class provides methods for processing data in parallel,
    with support for chunking large datasets and progress tracking.
    """
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        use_processes: bool = False,
        chunk_size: Optional[int] = None
    ):
        """
        Initialize a parallel data processor.
        
        Args:
            max_workers: Maximum number of workers to use. If None, uses the number
                         of CPU cores available.
            use_processes: Whether to use process-based parallelism (True) or
                          thread-based parallelism (False).
            chunk_size: Size of chunks to process in parallel. If None, no chunking
                       is performed.
        """
        self.executor = ParallelExecutor(max_workers, use_processes)
        self.chunk_size = chunk_size
        self.logger = logging.getLogger(__name__)
    
    def process_data(
        self,
        data: List[T],
        process_func: Callable[[T], R],
        timeout: Optional[float] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[R]:
        """
        Process a list of data items in parallel.
        
        Args:
            data: List of data items to process.
            process_func: Function to apply to each data item.
            timeout: Optional timeout in seconds for the entire operation.
            progress_callback: Optional callback function to report progress.
                              Takes two arguments: current count and total count.
            
        Returns:
            List of results from processing each data item.
            
        Raises:
            TimeoutError: If the operation times out.
            Exception: If any worker raises an exception.
        """
        if not data:
            return []
        
        total_items = len(data)
        processed_items = 0
        results = []
        
        # Report initial progress
        if progress_callback:
            progress_callback(processed_items, total_items)
        
        # Process data in chunks if chunk_size is specified
        if self.chunk_size:
            chunks = [data[i:i + self.chunk_size] for i in range(0, len(data), self.chunk_size)]
            
            for chunk in chunks:
                # Process the chunk in parallel
                chunk_results = self.executor.map(process_func, chunk, timeout)
                results.extend(chunk_results)
                
                # Update progress
                processed_items += len(chunk)
                if progress_callback:
                    progress_callback(processed_items, total_items)
        else:
            # Process all data in parallel
            results = self.executor.map(process_func, data, timeout)
            
            # Update progress
            processed_items = total_items
            if progress_callback:
                progress_callback(processed_items, total_items)
        
        return results
    
    def process_dataframe(
        self,
        df: 'pd.DataFrame',
        process_func: Callable[['pd.DataFrame'], Any],
        by_column: Optional[str] = None,
        timeout: Optional[float] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> 'pd.DataFrame':
        """
        Process a pandas DataFrame in parallel.
        
        Args:
            df: DataFrame to process.
            process_func: Function to apply to each DataFrame chunk.
            by_column: Optional column to group by before processing.
            timeout: Optional timeout in seconds for the entire operation.
            progress_callback: Optional callback function to report progress.
                              Takes two arguments: current count and total count.
            
        Returns:
            Processed DataFrame.
            
        Raises:
            TimeoutError: If the operation times out.
            Exception: If any worker raises an exception.
        """
        import pandas as pd
        
        if df.empty:
            return df
        
        # If grouping by a column, process each group separately
        if by_column:
            groups = df.groupby(by_column)
            group_dfs = [group for _, group in groups]
            
            # Process each group in parallel
            processed_groups = self.process_data(
                group_dfs,
                process_func,
                timeout,
                progress_callback
            )
            
            # Combine the processed groups
            return pd.concat(processed_groups, ignore_index=True)
        
        # Otherwise, split the DataFrame into chunks and process each chunk
        if self.chunk_size:
            chunks = [df.iloc[i:i + self.chunk_size] for i in range(0, len(df), self.chunk_size)]
        else:
            # If no chunk_size is specified, split by number of workers
            n_chunks = min(self.executor.max_workers, len(df))
            chunk_size = len(df) // n_chunks
            chunks = [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
        
        # Process each chunk in parallel
        processed_chunks = self.process_data(
            chunks,
            process_func,
            timeout,
            progress_callback
        )
        
        # Combine the processed chunks
        return pd.concat(processed_chunks, ignore_index=True)


def parallel_map(func: Callable[[T], R], items: Iterable[T], max_workers: Optional[int] = None, use_processes: bool = False) -> List[R]:
    """
    Apply a function to each item in parallel.
    
    This is a convenience function that creates a ParallelExecutor and calls its map method.
    
    Args:
        func: Function to apply to each item.
        items: Iterable of items to process.
        max_workers: Maximum number of workers to use. If None, uses the number
                     of CPU cores available.
        use_processes: Whether to use process-based parallelism (True) or
                      thread-based parallelism (False).
        
    Returns:
        List of results from applying the function to each item.
        
    Raises:
        Exception: If any worker raises an exception.
    """
    executor = ParallelExecutor(max_workers, use_processes)
    return executor.map(func, items)


def parallel_process_dataframe(
    df: 'pd.DataFrame',
    process_func: Callable[['pd.DataFrame'], Any],
    by_column: Optional[str] = None,
    max_workers: Optional[int] = None,
    use_processes: bool = False,
    chunk_size: Optional[int] = None
) -> 'pd.DataFrame':
    """
    Process a pandas DataFrame in parallel.
    
    This is a convenience function that creates a ParallelDataProcessor and calls its process_dataframe method.
    
    Args:
        df: DataFrame to process.
        process_func: Function to apply to each DataFrame chunk.
        by_column: Optional column to group by before processing.
        max_workers: Maximum number of workers to use. If None, uses the number
                     of CPU cores available.
        use_processes: Whether to use process-based parallelism (True) or
                      thread-based parallelism (False).
        chunk_size: Size of chunks to process in parallel. If None, chunks are
                   determined based on the number of workers.
        
    Returns:
        Processed DataFrame.
        
    Raises:
        Exception: If any worker raises an exception.
    """
    processor = ParallelDataProcessor(max_workers, use_processes, chunk_size)
    return processor.process_dataframe(df, process_func, by_column)


def example_parallel_processing():
    """
    Example of using parallel processing utilities.
    
    Returns:
        Dictionary with example results.
    """
    import time
    import numpy as np
    import pandas as pd
    
    # Example 1: Parallel map
    def slow_square(x):
        time.sleep(0.1)  # Simulate a slow operation
        return x * x
    
    items = list(range(10))
    
    # Sequential processing
    start_time = time.time()
    sequential_results = [slow_square(x) for x in items]
    sequential_time = time.time() - start_time
    
    # Parallel processing
    start_time = time.time()
    parallel_results = parallel_map(slow_square, items)
    parallel_time = time.time() - start_time
    
    # Example 2: Parallel DataFrame processing
    def slow_process_df(df):
        time.sleep(0.1)  # Simulate a slow operation
        df['squared'] = df['value'] ** 2
        return df
    
    # Create a sample DataFrame
    df = pd.DataFrame({'value': np.random.rand(100)})
    
    # Sequential processing
    start_time = time.time()
    sequential_df = slow_process_df(df)
    sequential_df_time = time.time() - start_time
    
    # Parallel processing
    start_time = time.time()
    parallel_df = parallel_process_dataframe(df, slow_process_df, chunk_size=10)
    parallel_df_time = time.time() - start_time
    
    return {
        'example1': {
            'sequential_time': sequential_time,
            'parallel_time': parallel_time,
            'speedup': sequential_time / parallel_time if parallel_time > 0 else 0
        },
        'example2': {
            'sequential_time': sequential_df_time,
            'parallel_time': parallel_df_time,
            'speedup': sequential_df_time / parallel_df_time if parallel_df_time > 0 else 0
        }
    }