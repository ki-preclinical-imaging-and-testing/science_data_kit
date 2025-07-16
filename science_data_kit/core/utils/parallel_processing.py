"""
Parallel Processing Utilities for Science Data Kit

This module provides utilities for parallel processing of data operations,
enabling improved performance for computationally intensive tasks.
It also includes background processing capabilities for long-running tasks.

The module offers several key components:
- ParallelExecutor: For executing functions in parallel using threads or processes
- ParallelDataProcessor: For processing data in parallel with chunking and progress tracking
- BackgroundTaskManager: For running tasks in the background and tracking their status
- Convenience functions: For common parallel processing operations

Usage:
    ```python
    from science_data_kit.core.utils.parallel_processing import parallel_map, BackgroundTaskManager

    # Example 1: Parallel map
    results = parallel_map(lambda x: x * x, range(100))

    # Example 2: Background processing
    manager = BackgroundTaskManager()
    task_id = manager.submit_task(long_running_function, arg1, arg2)

    # Check status later
    status = manager.get_task_status(task_id)

    # Get result when ready
    result = manager.get_task_result(task_id)
    ```
"""

# Standard library imports (alphabetical order)
import concurrent.futures
import logging
import multiprocessing
import threading
import time
import uuid
from enum import Enum
from typing import Any, Callable, Dict, Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar, Union

# SDK imports
from science_data_kit.core.utils.error_handling import (
    ErrorCode,
    ErrorHandler,
    ExecutorShutdownError,
    ParallelExecutionError,
    PerformanceMonitor,
    SDKError,
    TaskExecutionError,
    TaskNotFoundError,
    TaskTimeoutError,
    get_logger,
    log_debug,
    log_error,
    log_info,
    log_warning,
    measure_execution_time
)

# Type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')


class TaskStatus(Enum):
    """Status of a background task."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


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
        self.logger = get_logger(__name__)
        self.is_shutdown = False
        self.performance_monitor = PerformanceMonitor(self.logger)

        log_info(
            f"Initialized ParallelExecutor with {self.max_workers} workers "
            f"using {'processes' if self.use_processes else 'threads'}",
            self.logger
        )

    @measure_execution_time(name="parallel_map", level=logging.DEBUG)
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
            TaskTimeoutError: If the operation times out.
            ParallelExecutionError: If any worker raises an exception.
            ExecutorShutdownError: If the executor has been shut down.
        """
        if self.is_shutdown:
            raise ExecutorShutdownError(
                message="Cannot execute tasks on a shutdown executor",
                details={"executor_type": "ProcessPoolExecutor" if self.use_processes else "ThreadPoolExecutor"}
            )

        executor_class = concurrent.futures.ProcessPoolExecutor if self.use_processes else concurrent.futures.ThreadPoolExecutor
        items_list = list(items)  # Convert to list to get length and for logging

        log_info(
            f"Starting parallel map operation with {len(items_list)} items",
            self.logger,
            details={
                "num_items": len(items_list),
                "max_workers": self.max_workers,
                "timeout": timeout,
                "use_processes": self.use_processes
            }
        )

        start_time = time.time()
        results = []
        error_handler = ErrorHandler(self.logger)

        try:
            with executor_class(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_item = {executor.submit(func, item): item for item in items_list}

                log_debug(f"Submitted {len(future_to_item)} tasks to executor", self.logger)

                # Process results as they complete
                for i, future in enumerate(concurrent.futures.as_completed(future_to_item)):
                    # Check for timeout
                    if timeout and time.time() - start_time > timeout:
                        executor.shutdown(wait=False)
                        raise TaskTimeoutError(
                            message=f"Parallel operation timed out after {timeout} seconds",
                            details={
                                "timeout": timeout,
                                "elapsed_time": time.time() - start_time,
                                "completed_tasks": i,
                                "total_tasks": len(items_list)
                            }
                        )

                    item = future_to_item[future]
                    try:
                        result = future.result()
                        results.append(result)

                        if (i + 1) % max(1, len(items_list) // 10) == 0:  # Log progress every 10%
                            log_debug(
                                f"Processed {i + 1}/{len(items_list)} items ({(i + 1) / len(items_list) * 100:.1f}%)",
                                self.logger
                            )
                    except Exception as e:
                        log_error(
                            f"Task raised an exception while processing item: {str(e)}",
                            self.logger,
                            details={"item": str(item)[:100], "exception": str(e)},
                            include_traceback=True
                        )
                        raise ParallelExecutionError(
                            message="Task execution failed",
                            details={"item": str(item)[:100]},
                            cause=e
                        )
        except TaskTimeoutError:
            # Re-raise TaskTimeoutError without wrapping
            raise
        except Exception as e:
            # Wrap other exceptions in ParallelExecutionError
            if not isinstance(e, ParallelExecutionError):
                raise ParallelExecutionError(
                    message="Parallel execution failed",
                    details={"exception": str(e)},
                    cause=e
                )
            raise
        finally:
            elapsed_time = time.time() - start_time
            log_info(
                f"Completed parallel map operation in {elapsed_time:.2f} seconds",
                self.logger,
                details={
                    "elapsed_time": elapsed_time,
                    "num_results": len(results),
                    "num_items": len(items_list)
                }
            )

        return results

    @measure_execution_time(name="execute_tasks", level=logging.DEBUG)
    def execute_tasks(self, tasks: List[Callable[[], R]], timeout: Optional[float] = None) -> List[R]:
        """
        Execute a list of tasks in parallel.

        Args:
            tasks: List of task functions to execute.
            timeout: Optional timeout in seconds for the entire operation.

        Returns:
            List of results from executing each task.

        Raises:
            TaskTimeoutError: If the operation times out.
            ParallelExecutionError: If any worker raises an exception.
            ExecutorShutdownError: If the executor has been shut down.
        """
        if self.is_shutdown:
            raise ExecutorShutdownError(
                message="Cannot execute tasks on a shutdown executor",
                details={"executor_type": "ProcessPoolExecutor" if self.use_processes else "ThreadPoolExecutor"}
            )

        executor_class = concurrent.futures.ProcessPoolExecutor if self.use_processes else concurrent.futures.ThreadPoolExecutor

        log_info(
            f"Starting parallel execution of {len(tasks)} tasks",
            self.logger,
            details={
                "num_tasks": len(tasks),
                "max_workers": self.max_workers,
                "timeout": timeout,
                "use_processes": self.use_processes
            }
        )

        start_time = time.time()
        results = []
        error_handler = ErrorHandler(self.logger)

        try:
            with executor_class(max_workers=self.max_workers) as executor:
                # Submit all tasks
                futures = [executor.submit(task) for task in tasks]

                log_debug(f"Submitted {len(futures)} tasks to executor", self.logger)

                # Process results as they complete
                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    # Check for timeout
                    if timeout and time.time() - start_time > timeout:
                        executor.shutdown(wait=False)
                        raise TaskTimeoutError(
                            message=f"Task execution timed out after {timeout} seconds",
                            details={
                                "timeout": timeout,
                                "elapsed_time": time.time() - start_time,
                                "completed_tasks": i,
                                "total_tasks": len(tasks)
                            }
                        )

                    try:
                        result = future.result()
                        results.append(result)

                        if (i + 1) % max(1, len(tasks) // 10) == 0:  # Log progress every 10%
                            log_debug(
                                f"Executed {i + 1}/{len(tasks)} tasks ({(i + 1) / len(tasks) * 100:.1f}%)",
                                self.logger
                            )
                    except Exception as e:
                        log_error(
                            f"Task raised an exception: {str(e)}",
                            self.logger,
                            details={"task_index": i, "exception": str(e)},
                            include_traceback=True
                        )
                        raise TaskExecutionError(
                            message="Task execution failed",
                            details={"task_index": i},
                            cause=e
                        )
        except TaskTimeoutError:
            # Re-raise TaskTimeoutError without wrapping
            raise
        except Exception as e:
            # Wrap other exceptions in ParallelExecutionError
            if not isinstance(e, (TaskExecutionError, ParallelExecutionError)):
                raise ParallelExecutionError(
                    message="Parallel task execution failed",
                    details={"exception": str(e)},
                    cause=e
                )
            raise
        finally:
            elapsed_time = time.time() - start_time
            log_info(
                f"Completed parallel task execution in {elapsed_time:.2f} seconds",
                self.logger,
                details={
                    "elapsed_time": elapsed_time,
                    "num_results": len(results),
                    "num_tasks": len(tasks)
                }
            )

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
        self.logger = get_logger(__name__)
        self.performance_monitor = PerformanceMonitor(self.logger)

        log_info(
            f"Initialized ParallelDataProcessor with chunk_size={chunk_size}",
            self.logger,
            details={
                "max_workers": self.executor.max_workers,
                "use_processes": use_processes,
                "chunk_size": chunk_size
            }
        )

    @measure_execution_time(name="process_data", level=logging.DEBUG)
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
            TaskTimeoutError: If the operation times out.
            ParallelExecutionError: If any worker raises an exception.
            SDKError: If the input data is invalid.
        """
        if not data:
            log_warning("Empty data provided to process_data", self.logger)
            return []

        total_items = len(data)
        processed_items = 0
        results = []

        log_info(
            f"Starting parallel data processing of {total_items} items",
            self.logger,
            details={
                "total_items": total_items,
                "chunk_size": self.chunk_size,
                "timeout": timeout
            }
        )

        # Report initial progress
        if progress_callback:
            try:
                progress_callback(processed_items, total_items)
            except Exception as e:
                log_warning(
                    "Progress callback raised an exception",
                    self.logger,
                    details={"exception": str(e)}
                )

        # Process data in chunks if chunk_size is specified
        if self.chunk_size:
            chunks = [data[i:i + self.chunk_size] for i in range(0, len(data), self.chunk_size)]
            num_chunks = len(chunks)

            log_info(
                f"Processing data in {num_chunks} chunks of size {self.chunk_size}",
                self.logger
            )

            for chunk_index, chunk in enumerate(chunks):
                chunk_start_time = time.time()
                log_debug(
                    f"Processing chunk {chunk_index + 1}/{num_chunks} with {len(chunk)} items",
                    self.logger
                )

                try:
                    # Process the chunk in parallel
                    chunk_results = self.executor.map(process_func, chunk, timeout)
                    results.extend(chunk_results)

                    # Update progress
                    processed_items += len(chunk)
                    if progress_callback:
                        try:
                            progress_callback(processed_items, total_items)
                        except Exception as e:
                            log_warning(
                                "Progress callback raised an exception",
                                self.logger,
                                details={"exception": str(e)}
                            )

                    chunk_elapsed_time = time.time() - chunk_start_time
                    log_debug(
                        f"Completed chunk {chunk_index + 1}/{num_chunks} in {chunk_elapsed_time:.2f} seconds",
                        self.logger,
                        details={
                            "chunk_index": chunk_index,
                            "chunk_size": len(chunk),
                            "elapsed_time": chunk_elapsed_time,
                            "items_per_second": len(chunk) / chunk_elapsed_time if chunk_elapsed_time > 0 else 0
                        }
                    )
                except Exception as e:
                    log_error(
                        f"Error processing chunk {chunk_index + 1}/{num_chunks}",
                        self.logger,
                        details={
                            "chunk_index": chunk_index,
                            "chunk_size": len(chunk),
                            "exception": str(e)
                        }
                    )
                    raise
        else:
            # Process all data in parallel
            log_info(f"Processing all {total_items} items in parallel", self.logger)

            try:
                results = self.executor.map(process_func, data, timeout)

                # Update progress
                processed_items = total_items
                if progress_callback:
                    try:
                        progress_callback(processed_items, total_items)
                    except Exception as e:
                        log_warning(
                            "Progress callback raised an exception",
                            self.logger,
                            details={"exception": str(e)}
                        )
            except Exception as e:
                log_error(
                    "Error processing data in parallel",
                    self.logger,
                    details={"exception": str(e)}
                )
                raise

        log_info(
            f"Completed parallel data processing of {total_items} items",
            self.logger,
            details={
                "total_items": total_items,
                "processed_items": processed_items,
                "num_results": len(results)
            }
        )
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


@measure_execution_time(name="parallel_map_convenience", level=logging.DEBUG)
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
        ParallelExecutionError: If any worker raises an exception.
        TaskTimeoutError: If the operation times out.
    """
    logger = get_logger(__name__)
    log_info(
        f"Starting parallel_map with {'processes' if use_processes else 'threads'}",
        logger,
        details={
            "max_workers": max_workers,
            "use_processes": use_processes,
            "function": getattr(func, "__name__", str(func))
        }
    )

    try:
        executor = ParallelExecutor(max_workers, use_processes)
        return executor.map(func, items)
    except Exception as e:
        log_error(
            f"Error in parallel_map: {str(e)}",
            logger,
            details={"exception": str(e)},
            include_traceback=True
        )
        raise


@measure_execution_time(name="parallel_process_dataframe_convenience", level=logging.DEBUG)
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
        ParallelExecutionError: If any worker raises an exception.
        TaskTimeoutError: If the operation times out.
        SDKError: If the input DataFrame is invalid.
    """
    logger = get_logger(__name__)

    if df is None:
        log_error("DataFrame is None", logger)
        raise SDKError(
            code=ErrorCode.INVALID_ARGUMENT,
            message="DataFrame cannot be None",
            details={"argument": "df"}
        )

    if df.empty:
        log_warning("Empty DataFrame provided to parallel_process_dataframe", logger)

    log_info(
        f"Starting parallel_process_dataframe with {'processes' if use_processes else 'threads'}",
        logger,
        details={
            "max_workers": max_workers,
            "use_processes": use_processes,
            "chunk_size": chunk_size,
            "by_column": by_column,
            "df_shape": df.shape,
            "function": getattr(process_func, "__name__", str(process_func))
        }
    )

    try:
        processor = ParallelDataProcessor(max_workers, use_processes, chunk_size)
        result = processor.process_dataframe(df, process_func, by_column)

        log_info(
            "Completed parallel_process_dataframe",
            logger,
            details={
                "input_shape": df.shape,
                "output_shape": result.shape
            }
        )

        return result
    except Exception as e:
        log_error(
            f"Error in parallel_process_dataframe: {str(e)}",
            logger,
            details={"exception": str(e)},
            include_traceback=True
        )
        raise


class BackgroundTaskManager:
    """
    Manager for background processing of long-running tasks.

    This class provides methods for submitting tasks to run in the background,
    tracking their status, and retrieving results when they are completed.
    It is designed for long-running tasks that should not block the main thread.
    """

    def __init__(self, max_workers: Optional[int] = None, use_processes: bool = False):
        """
        Initialize a background task manager.

        Args:
            max_workers: Maximum number of workers to use. If None, uses the number
                         of CPU cores available.
            use_processes: Whether to use process-based parallelism (True) or
                          thread-based parallelism (False).
        """
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.use_processes = use_processes
        self.logger = get_logger(__name__)
        self.performance_monitor = PerformanceMonitor(self.logger)

        # Dictionary to store task information
        self.tasks: Dict[str, Dict[str, Any]] = {}

        # Lock for thread-safe access to the tasks dictionary
        self.tasks_lock = threading.RLock()

        # Executor for running tasks
        executor_class = concurrent.futures.ProcessPoolExecutor if use_processes else concurrent.futures.ThreadPoolExecutor
        self.executor = executor_class(max_workers=self.max_workers)

        # Flag to indicate if the manager has been shut down
        self.is_shutdown = False

        log_info(
            f"Initialized BackgroundTaskManager with {self.max_workers} workers "
            f"using {'processes' if self.use_processes else 'threads'}",
            self.logger
        )

    def submit_task(self, task_func: Callable[..., R], *args, **kwargs) -> str:
        """
        Submit a task to run in the background.

        Args:
            task_func: Function to execute in the background.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            Task ID that can be used to check status and retrieve results.

        Raises:
            ExecutorShutdownError: If the manager has been shut down.
        """
        if self.is_shutdown:
            raise ExecutorShutdownError(
                message="Background task manager has been shut down",
                details={"executor_type": "ProcessPoolExecutor" if self.use_processes else "ThreadPoolExecutor"}
            )

        # Generate a unique task ID
        task_id = str(uuid.uuid4())

        # Get function name for logging
        func_name = getattr(task_func, "__name__", str(task_func))

        log_info(
            f"Submitting task {func_name} with ID {task_id}",
            self.logger,
            details={
                "task_id": task_id,
                "function": func_name,
                "args_count": len(args),
                "kwargs_count": len(kwargs)
            }
        )

        # Create a wrapper function that updates task status and measures performance
        def task_wrapper():
            start_time = time.time()
            try:
                # Update task status to RUNNING
                with self.tasks_lock:
                    if self.tasks[task_id]['status'] == TaskStatus.PENDING:
                        self.tasks[task_id]['status'] = TaskStatus.RUNNING
                        self.tasks[task_id]['start_time'] = start_time

                log_debug(f"Starting execution of task {task_id}", self.logger)

                # Execute the task
                result = task_func(*args, **kwargs)

                # Calculate execution time
                execution_time = time.time() - start_time

                # Update task status to COMPLETED and store result
                with self.tasks_lock:
                    self.tasks[task_id]['status'] = TaskStatus.COMPLETED
                    self.tasks[task_id]['result'] = result
                    self.tasks[task_id]['end_time'] = time.time()
                    self.tasks[task_id]['execution_time'] = execution_time

                log_info(
                    f"Task {task_id} completed successfully in {execution_time:.2f} seconds",
                    self.logger,
                    details={
                        "task_id": task_id,
                        "execution_time": execution_time,
                        "function": func_name
                    }
                )

                return result
            except Exception as e:
                # Calculate execution time
                execution_time = time.time() - start_time

                # Update task status to FAILED and store exception
                with self.tasks_lock:
                    self.tasks[task_id]['status'] = TaskStatus.FAILED
                    self.tasks[task_id]['error'] = e
                    self.tasks[task_id]['end_time'] = time.time()
                    self.tasks[task_id]['execution_time'] = execution_time

                # Log the error
                log_error(
                    f"Task {task_id} failed with error: {str(e)}",
                    self.logger,
                    details={
                        "task_id": task_id,
                        "execution_time": execution_time,
                        "function": func_name,
                        "exception": str(e)
                    },
                    include_traceback=True
                )

                # Re-raise the exception to be captured by the future
                raise TaskExecutionError(
                    message=f"Task {task_id} execution failed",
                    details={
                        "task_id": task_id,
                        "function": func_name,
                        "execution_time": execution_time
                    },
                    cause=e
                )

        # Submit the task to the executor
        future = self.executor.submit(task_wrapper)

        # Store task information
        with self.tasks_lock:
            self.tasks[task_id] = {
                'future': future,
                'status': TaskStatus.PENDING,
                'submit_time': time.time(),
                'start_time': None,
                'end_time': None,
                'execution_time': None,
                'result': None,
                'error': None,
                'function': func_name
            }

        return task_id

    def get_task_status(self, task_id: str) -> TaskStatus:
        """
        Get the status of a task.

        Args:
            task_id: ID of the task to check.

        Returns:
            Status of the task.

        Raises:
            TaskNotFoundError: If the task ID is not found.
        """
        with self.tasks_lock:
            if task_id not in self.tasks:
                log_warning(
                    f"Task ID {task_id} not found",
                    self.logger,
                    details={"task_id": task_id, "available_tasks": list(self.tasks.keys())}
                )
                raise TaskNotFoundError(
                    message=f"Task ID {task_id} not found",
                    details={"task_id": task_id}
                )

            status = self.tasks[task_id]['status']
            log_debug(
                f"Task {task_id} status: {status.value}",
                self.logger,
                details={"task_id": task_id, "status": status.value}
            )
            return status

    def get_task_result(self, task_id: str, timeout: Optional[float] = None, raise_exception: bool = True) -> Optional[R]:
        """
        Get the result of a completed task.

        Args:
            task_id: ID of the task to get the result for.
            timeout: Optional timeout in seconds to wait for the task to complete.
            raise_exception: Whether to raise an exception if the task failed.

        Returns:
            Result of the task, or None if the task failed and raise_exception is False.

        Raises:
            TaskNotFoundError: If the task ID is not found.
            TaskTimeoutError: If the task does not complete within the timeout.
            TaskExecutionError: If the task failed and raise_exception is True.
        """
        log_debug(
            f"Getting result for task {task_id}",
            self.logger,
            details={"task_id": task_id, "timeout": timeout, "raise_exception": raise_exception}
        )

        with self.tasks_lock:
            if task_id not in self.tasks:
                log_warning(
                    f"Task ID {task_id} not found",
                    self.logger,
                    details={"task_id": task_id, "available_tasks": list(self.tasks.keys())}
                )
                raise TaskNotFoundError(
                    message=f"Task ID {task_id} not found",
                    details={"task_id": task_id}
                )

            task = self.tasks[task_id]
            future = task['future']
            function_name = task.get('function', 'unknown')

        start_time = time.time()
        try:
            # Wait for the task to complete
            log_debug(f"Waiting for task {task_id} to complete", self.logger)
            result = future.result(timeout=timeout)

            wait_time = time.time() - start_time
            log_info(
                f"Retrieved result for task {task_id} in {wait_time:.2f} seconds",
                self.logger,
                details={
                    "task_id": task_id,
                    "wait_time": wait_time,
                    "function": function_name
                }
            )

            # Return the result
            return result
        except concurrent.futures.TimeoutError:
            wait_time = time.time() - start_time
            log_warning(
                f"Task {task_id} did not complete within the timeout of {timeout} seconds",
                self.logger,
                details={
                    "task_id": task_id,
                    "timeout": timeout,
                    "wait_time": wait_time,
                    "function": function_name
                }
            )
            raise TaskTimeoutError(
                message=f"Task {task_id} did not complete within the timeout",
                details={
                    "task_id": task_id,
                    "timeout": timeout,
                    "wait_time": wait_time,
                    "function": function_name
                }
            )
        except Exception as e:
            wait_time = time.time() - start_time
            log_error(
                f"Error retrieving result for task {task_id}: {str(e)}",
                self.logger,
                details={
                    "task_id": task_id,
                    "wait_time": wait_time,
                    "function": function_name,
                    "exception": str(e)
                },
                include_traceback=True
            )

            if raise_exception:
                if isinstance(e, TaskExecutionError):
                    # Re-raise TaskExecutionError without wrapping
                    raise
                else:
                    # Wrap other exceptions in TaskExecutionError
                    raise TaskExecutionError(
                        message=f"Error retrieving result for task {task_id}",
                        details={
                            "task_id": task_id,
                            "function": function_name
                        },
                        cause=e
                    )

            # If we don't want to raise an exception, return None
            return None

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task if it is still pending or running.

        Args:
            task_id: ID of the task to cancel.

        Returns:
            True if the task was cancelled, False if it could not be cancelled.

        Raises:
            TaskNotFoundError: If the task ID is not found.
        """
        log_info(f"Attempting to cancel task {task_id}", self.logger)

        with self.tasks_lock:
            if task_id not in self.tasks:
                log_warning(
                    f"Task ID {task_id} not found",
                    self.logger,
                    details={"task_id": task_id, "available_tasks": list(self.tasks.keys())}
                )
                raise TaskNotFoundError(
                    message=f"Task ID {task_id} not found",
                    details={"task_id": task_id}
                )

            task = self.tasks[task_id]
            future = task['future']
            function_name = task.get('function', 'unknown')

            # Try to cancel the task
            if future.cancel():
                task['status'] = TaskStatus.CANCELLED
                task['end_time'] = time.time()

                log_info(
                    f"Successfully cancelled task {task_id}",
                    self.logger,
                    details={
                        "task_id": task_id,
                        "function": function_name,
                        "elapsed_time": task['end_time'] - task['submit_time']
                    }
                )
                return True

            log_warning(
                f"Could not cancel task {task_id}, it may have already completed or failed",
                self.logger,
                details={
                    "task_id": task_id,
                    "function": function_name,
                    "status": task['status'].value
                }
            )
            return False

    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all tasks.

        Returns:
            Dictionary mapping task IDs to task information.
        """
        with self.tasks_lock:
            # Create a copy of the tasks dictionary to avoid modification during iteration
            return {
                task_id: {
                    'status': task_info['status'],
                    'submit_time': task_info['submit_time'],
                    'elapsed_time': time.time() - task_info['submit_time']
                }
                for task_id, task_info in self.tasks.items()
            }

    def shutdown(self, wait: bool = True):
        """
        Shut down the task manager and its executor.

        Args:
            wait: Whether to wait for pending tasks to complete.
        """
        if not self.is_shutdown:
            log_info(
                f"Shutting down BackgroundTaskManager (wait={wait})",
                self.logger,
                details={
                    "active_tasks": len([t for t in self.tasks.values() if t['status'] in (TaskStatus.PENDING, TaskStatus.RUNNING)]),
                    "total_tasks": len(self.tasks)
                }
            )
            self.is_shutdown = True
            self.executor.shutdown(wait=wait)
            log_info("BackgroundTaskManager shutdown complete", self.logger)


@measure_execution_time(name="submit_background_task_convenience", level=logging.DEBUG)
def submit_background_task(task_func: Callable[..., R], *args, **kwargs) -> Tuple[str, BackgroundTaskManager]:
    """
    Submit a task to run in the background using a new BackgroundTaskManager.

    This is a convenience function that creates a BackgroundTaskManager and submits a task to it.

    Args:
        task_func: Function to execute in the background.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Tuple containing the task ID and the BackgroundTaskManager instance.

    Raises:
        TaskExecutionError: If there is an error submitting the task.
    """
    logger = get_logger(__name__)
    func_name = getattr(task_func, "__name__", str(task_func))

    log_info(
        f"Creating BackgroundTaskManager and submitting task {func_name}",
        logger,
        details={
            "function": func_name,
            "args_count": len(args),
            "kwargs_count": len(kwargs)
        }
    )

    try:
        manager = BackgroundTaskManager()
        task_id = manager.submit_task(task_func, *args, **kwargs)

        log_info(
            f"Successfully submitted background task {func_name} with ID {task_id}",
            logger,
            details={"task_id": task_id, "function": func_name}
        )

        return task_id, manager
    except Exception as e:
        log_error(
            f"Error submitting background task {func_name}: {str(e)}",
            logger,
            details={"exception": str(e)},
            include_traceback=True
        )

        if isinstance(e, (TaskExecutionError, ExecutorShutdownError)):
            # Re-raise without wrapping
            raise
        else:
            # Wrap other exceptions
            raise TaskExecutionError(
                message=f"Error submitting background task {func_name}",
                details={"function": func_name},
                cause=e
            )


def example_parallel_processing() -> Dict[str, Dict[str, float]]:
    """
    Example of using parallel processing utilities.

    This function demonstrates how to use the parallel processing utilities
    in this module to improve performance for computationally intensive tasks.
    It compares sequential and parallel processing for two examples:
    1. Applying a function to a list of items
    2. Processing a pandas DataFrame

    Returns:
        Dictionary with example results, including execution times and speedup factors.

    Examples:
        >>> results = example_parallel_processing()
        >>> print(f"Speedup for list processing: {results['example1']['speedup']:.2f}x")
        >>> print(f"Speedup for DataFrame processing: {results['example2']['speedup']:.2f}x")
    """
    # Third-party imports
    import numpy as np
    import pandas as pd

    # Example 1: Parallel map
    def slow_square(x: int) -> int:
        """Square a number with a simulated delay."""
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
    def slow_process_df(df: 'pd.DataFrame') -> 'pd.DataFrame':
        """Process a DataFrame with a simulated delay."""
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


def example_background_processing() -> Dict[str, Any]:
    """
    Example of using background processing utilities.

    This function demonstrates how to use the BackgroundTaskManager to run
    tasks in the background, check their status, retrieve results, and cancel
    tasks. It simulates long-running tasks and shows how to interact with them
    asynchronously.

    Returns:
        Dictionary with example results, including task statuses at different
        points in time, task results, and cancellation status.

    Examples:
        >>> results = example_background_processing()
        >>> print(f"Initial status of task 1: {results['initial_status']['task1']}")
        >>> print(f"Task 1 result: {results['task1_result']}")
        >>> print(f"Was task 2 cancelled? {results['task2_cancelled']}")
    """
    # Define a long-running task
    def long_running_task(duration: float, return_value: str) -> str:
        """
        Simulate a long-running task.

        Args:
            duration: Time in seconds to sleep.
            return_value: Value to return after sleeping.

        Returns:
            The return_value after sleeping for duration seconds.
        """
        time.sleep(duration)
        return return_value

    # Create a background task manager
    manager = BackgroundTaskManager()

    # Submit tasks
    task1_id = manager.submit_task(long_running_task, 2, "Task 1 completed")
    task2_id = manager.submit_task(long_running_task, 4, "Task 2 completed")

    # Check status immediately after submission
    initial_status = {
        'task1': manager.get_task_status(task1_id).value,
        'task2': manager.get_task_status(task2_id).value
    }

    # Wait for task 1 to complete
    result1 = manager.get_task_result(task1_id)

    # Check status after task 1 completes
    mid_status = {
        'task1': manager.get_task_status(task1_id).value,
        'task2': manager.get_task_status(task2_id).value
    }

    # Cancel task 2
    cancelled = manager.cancel_task(task2_id)

    # Check final status
    final_status = {
        'task1': manager.get_task_status(task1_id).value,
        'task2': manager.get_task_status(task2_id).value
    }

    # Shutdown the manager
    manager.shutdown()

    return {
        'initial_status': initial_status,
        'mid_status': mid_status,
        'final_status': final_status,
        'task1_result': result1,
        'task2_cancelled': cancelled
    }
