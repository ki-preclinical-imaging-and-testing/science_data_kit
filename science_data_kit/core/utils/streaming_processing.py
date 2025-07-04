"""
Streaming Data Processing Utilities for Science Data Kit

This module provides utilities for streaming data processing operations,
enabling efficient handling of large datasets that don't fit in memory.
It implements generator-based processing pipelines that load and process
data incrementally.
"""

import logging
import time
from typing import Iterator, Callable, TypeVar, Generic, List, Optional, Dict, Any, Union, Iterable, Generator

# Type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')
U = TypeVar('U')


class StreamingProcessor:
    """
    Processor for streaming data operations.

    This class provides methods for processing data in a streaming fashion,
    where data is loaded and processed incrementally without requiring the
    entire dataset to be in memory at once.
    """

    def __init__(self, buffer_size: int = 1000):
        """
        Initialize a streaming processor.

        Args:
            buffer_size: Size of the internal buffer for batch processing.
                         Larger values may improve performance but increase memory usage.
        """
        self.buffer_size = buffer_size
        self.logger = logging.getLogger(__name__)

    def process_stream(
        self,
        data_source: Iterator[T],
        process_func: Callable[[T], R],
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Generator[R, None, None]:
        """
        Process a stream of data items incrementally.

        Args:
            data_source: Iterator providing the data items to process.
            process_func: Function to apply to each data item.
            progress_callback: Optional callback function to report progress.
                              Takes one argument: the count of processed items.

        Yields:
            Processed data items, one at a time.

        Raises:
            Exception: If any processing raises an exception.
        """
        processed_count = 0

        try:
            # Process items one at a time
            for item in data_source:
                # Process the item
                result = process_func(item)
                
                # Update progress
                processed_count += 1
                if progress_callback and processed_count % 100 == 0:
                    progress_callback(processed_count)
                
                # Yield the result
                yield result
                
        except Exception as e:
            self.logger.error(f"Error processing stream: {str(e)}")
            raise

        # Final progress update
        if progress_callback:
            progress_callback(processed_count)

    def process_stream_batched(
        self,
        data_source: Iterator[T],
        process_func: Callable[[List[T]], List[R]],
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Generator[R, None, None]:
        """
        Process a stream of data items in batches.

        This method buffers items from the data source and processes them in batches,
        which can be more efficient for some operations while still maintaining
        streaming behavior.

        Args:
            data_source: Iterator providing the data items to process.
            process_func: Function to apply to each batch of data items.
            progress_callback: Optional callback function to report progress.
                              Takes one argument: the count of processed items.

        Yields:
            Processed data items, one at a time.

        Raises:
            Exception: If any processing raises an exception.
        """
        processed_count = 0
        buffer = []

        try:
            # Fill the buffer and process in batches
            for item in data_source:
                buffer.append(item)
                
                # When buffer is full, process the batch
                if len(buffer) >= self.buffer_size:
                    # Process the batch
                    results = process_func(buffer)
                    
                    # Update progress
                    processed_count += len(buffer)
                    if progress_callback:
                        progress_callback(processed_count)
                    
                    # Yield the results
                    for result in results:
                        yield result
                    
                    # Clear the buffer
                    buffer = []
            
            # Process any remaining items in the buffer
            if buffer:
                results = process_func(buffer)
                
                # Update progress
                processed_count += len(buffer)
                if progress_callback:
                    progress_callback(processed_count)
                
                # Yield the results
                for result in results:
                    yield result
                
        except Exception as e:
            self.logger.error(f"Error processing stream in batches: {str(e)}")
            raise

        # Final progress update
        if progress_callback:
            progress_callback(processed_count)


class StreamingDataFrameProcessor:
    """
    Processor for streaming DataFrame operations.

    This class provides methods for processing pandas DataFrames in a streaming fashion,
    where data is loaded and processed in chunks without requiring the entire
    DataFrame to be in memory at once.
    """

    def __init__(self, chunk_size: int = 10000):
        """
        Initialize a streaming DataFrame processor.

        Args:
            chunk_size: Size of chunks to process at a time.
                       Larger values may improve performance but increase memory usage.
        """
        self.chunk_size = chunk_size
        self.logger = logging.getLogger(__name__)

    def process_csv(
        self,
        csv_file: str,
        process_func: Callable[['pd.DataFrame'], 'pd.DataFrame'],
        output_file: Optional[str] = None,
        progress_callback: Optional[Callable[[int], None]] = None,
        **csv_kwargs
    ) -> Optional[Generator['pd.DataFrame', None, None]]:
        """
        Process a CSV file in streaming chunks.

        Args:
            csv_file: Path to the CSV file to process.
            process_func: Function to apply to each DataFrame chunk.
            output_file: Optional path to save the processed data.
                        If provided, processed chunks are saved to this file.
            progress_callback: Optional callback function to report progress.
                              Takes one argument: the count of processed rows.
            **csv_kwargs: Additional keyword arguments to pass to pandas.read_csv.

        Returns:
            If output_file is None, returns a generator yielding processed DataFrame chunks.
            If output_file is provided, returns None (data is saved to the file).

        Raises:
            Exception: If any processing raises an exception.
        """
        import pandas as pd
        
        processed_rows = 0
        first_chunk = True

        try:
            # Create a reader for the CSV file
            reader = pd.read_csv(csv_file, chunksize=self.chunk_size, **csv_kwargs)
            
            # If output_file is provided, process and save chunks
            if output_file:
                for chunk in reader:
                    # Process the chunk
                    processed_chunk = process_func(chunk)
                    
                    # Update progress
                    processed_rows += len(chunk)
                    if progress_callback:
                        progress_callback(processed_rows)
                    
                    # Save the processed chunk
                    mode = 'w' if first_chunk else 'a'
                    header = first_chunk
                    processed_chunk.to_csv(output_file, mode=mode, header=header, index=False)
                    first_chunk = False
                
                return None
            
            # If no output_file, yield processed chunks
            else:
                for chunk in reader:
                    # Process the chunk
                    processed_chunk = process_func(chunk)
                    
                    # Update progress
                    processed_rows += len(chunk)
                    if progress_callback:
                        progress_callback(processed_rows)
                    
                    # Yield the processed chunk
                    yield processed_chunk
                    
        except Exception as e:
            self.logger.error(f"Error processing CSV file: {str(e)}")
            raise

    def process_dataframe_in_chunks(
        self,
        df: 'pd.DataFrame',
        process_func: Callable[['pd.DataFrame'], 'pd.DataFrame'],
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Generator['pd.DataFrame', None, None]:
        """
        Process an existing DataFrame in streaming chunks.

        This method is useful when you already have a DataFrame in memory
        but want to process it in chunks to avoid creating large intermediate
        DataFrames.

        Args:
            df: DataFrame to process.
            process_func: Function to apply to each DataFrame chunk.
            progress_callback: Optional callback function to report progress.
                              Takes one argument: the count of processed rows.

        Yields:
            Processed DataFrame chunks.

        Raises:
            Exception: If any processing raises an exception.
        """
        processed_rows = 0

        try:
            # Process the DataFrame in chunks
            for i in range(0, len(df), self.chunk_size):
                # Get the chunk
                chunk = df.iloc[i:i + self.chunk_size].copy()
                
                # Process the chunk
                processed_chunk = process_func(chunk)
                
                # Update progress
                processed_rows += len(chunk)
                if progress_callback:
                    progress_callback(processed_rows)
                
                # Yield the processed chunk
                yield processed_chunk
                
        except Exception as e:
            self.logger.error(f"Error processing DataFrame in chunks: {str(e)}")
            raise


def stream_process(
    data_source: Iterator[T],
    process_func: Callable[[T], R],
    buffer_size: int = 1000,
    progress_callback: Optional[Callable[[int], None]] = None
) -> Generator[R, None, None]:
    """
    Process a stream of data items incrementally.

    This is a convenience function that creates a StreamingProcessor and calls its process_stream method.

    Args:
        data_source: Iterator providing the data items to process.
        process_func: Function to apply to each data item.
        buffer_size: Size of the internal buffer for batch processing.
        progress_callback: Optional callback function to report progress.

    Yields:
        Processed data items, one at a time.

    Raises:
        Exception: If any processing raises an exception.
    """
    processor = StreamingProcessor(buffer_size)
    yield from processor.process_stream(data_source, process_func, progress_callback)


def stream_process_csv(
    csv_file: str,
    process_func: Callable[['pd.DataFrame'], 'pd.DataFrame'],
    chunk_size: int = 10000,
    output_file: Optional[str] = None,
    progress_callback: Optional[Callable[[int], None]] = None,
    **csv_kwargs
) -> Optional[Generator['pd.DataFrame', None, None]]:
    """
    Process a CSV file in streaming chunks.

    This is a convenience function that creates a StreamingDataFrameProcessor and calls its process_csv method.

    Args:
        csv_file: Path to the CSV file to process.
        process_func: Function to apply to each DataFrame chunk.
        chunk_size: Size of chunks to process at a time.
        output_file: Optional path to save the processed data.
        progress_callback: Optional callback function to report progress.
        **csv_kwargs: Additional keyword arguments to pass to pandas.read_csv.

    Returns:
        If output_file is None, returns a generator yielding processed DataFrame chunks.
        If output_file is provided, returns None (data is saved to the file).

    Raises:
        Exception: If any processing raises an exception.
    """
    processor = StreamingDataFrameProcessor(chunk_size)
    return processor.process_csv(csv_file, process_func, output_file, progress_callback, **csv_kwargs)


def example_streaming_processing():
    """
    Example of using streaming processing utilities.

    Returns:
        Dictionary with example results.
    """
    import pandas as pd
    import numpy as np
    import tempfile
    import os
    
    # Example 1: Stream processing of items
    def generate_data(n):
        for i in range(n):
            yield i
    
    def square(x):
        return x * x
    
    # Process a stream of numbers
    start_time = time.time()
    results = list(stream_process(generate_data(10000), square))
    stream_time = time.time() - start_time
    
    # Example 2: Stream processing of a CSV file
    # Create a sample CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        temp_path = temp_file.name
        df = pd.DataFrame({'value': np.random.rand(50000)})
        df.to_csv(temp_path, index=False)
    
    def process_chunk(chunk):
        chunk['squared'] = chunk['value'] ** 2
        return chunk
    
    # Process the CSV file in streaming chunks
    start_time = time.time()
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as output_file:
        output_path = output_file.name
        stream_process_csv(temp_path, process_chunk, output_file=output_path)
    csv_time = time.time() - start_time
    
    # Clean up temporary files
    os.unlink(temp_path)
    os.unlink(output_path)
    
    return {
        'example1': {
            'stream_time': stream_time,
            'num_items': 10000,
            'first_10_results': results[:10]
        },
        'example2': {
            'csv_time': csv_time,
            'num_rows': 50000
        }
    }