"""
Tests for the streaming_processing module.
"""

import unittest
import tempfile
import os
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from science_data_kit.core.utils.streaming_processing import (
    StreamingProcessor,
    StreamingDataFrameProcessor,
    stream_process,
    stream_process_csv
)


class TestStreamingProcessor(unittest.TestCase):
    """Tests for the StreamingProcessor class."""

    def test_process_stream(self):
        """Test processing a stream of data items."""
        processor = StreamingProcessor(buffer_size=100)
        
        # Create a simple data source
        data_source = iter([1, 2, 3, 4, 5])
        
        # Define a simple processing function
        def process_func(x):
            return x * 2
        
        # Process the stream
        results = list(processor.process_stream(data_source, process_func))
        
        # Check the results
        self.assertEqual(results, [2, 4, 6, 8, 10])

    def test_process_stream_with_progress_callback(self):
        """Test processing a stream with a progress callback."""
        processor = StreamingProcessor(buffer_size=100)
        
        # Create a simple data source
        data_source = iter([1, 2, 3, 4, 5])
        
        # Define a simple processing function
        def process_func(x):
            return x * 2
        
        # Create a mock progress callback
        progress_callback = MagicMock()
        
        # Process the stream
        results = list(processor.process_stream(data_source, process_func, progress_callback))
        
        # Check the results
        self.assertEqual(results, [2, 4, 6, 8, 10])
        
        # Check that the progress callback was called
        self.assertGreaterEqual(progress_callback.call_count, 1)
        # Final call should be with the total count
        progress_callback.assert_called_with(5)

    def test_process_stream_with_exception(self):
        """Test processing a stream that raises an exception."""
        processor = StreamingProcessor(buffer_size=100)
        
        # Create a simple data source
        data_source = iter([1, 2, 0, 4, 5])  # 0 will cause a division by zero
        
        # Define a processing function that will raise an exception
        def process_func(x):
            return 10 / x
        
        # Process the stream and expect an exception
        with self.assertRaises(ZeroDivisionError):
            list(processor.process_stream(data_source, process_func))

    def test_process_stream_batched(self):
        """Test processing a stream in batches."""
        processor = StreamingProcessor(buffer_size=2)  # Small buffer for testing
        
        # Create a simple data source
        data_source = iter([1, 2, 3, 4, 5])
        
        # Define a batch processing function
        def process_func(batch):
            return [x * 2 for x in batch]
        
        # Process the stream in batches
        results = list(processor.process_stream_batched(data_source, process_func))
        
        # Check the results
        self.assertEqual(results, [2, 4, 6, 8, 10])

    def test_process_stream_batched_with_progress_callback(self):
        """Test processing a stream in batches with a progress callback."""
        processor = StreamingProcessor(buffer_size=2)  # Small buffer for testing
        
        # Create a simple data source
        data_source = iter([1, 2, 3, 4, 5])
        
        # Define a batch processing function
        def process_func(batch):
            return [x * 2 for x in batch]
        
        # Create a mock progress callback
        progress_callback = MagicMock()
        
        # Process the stream in batches
        results = list(processor.process_stream_batched(data_source, process_func, progress_callback))
        
        # Check the results
        self.assertEqual(results, [2, 4, 6, 8, 10])
        
        # Check that the progress callback was called
        self.assertGreaterEqual(progress_callback.call_count, 1)
        # Final call should be with the total count
        progress_callback.assert_called_with(5)


class TestStreamingDataFrameProcessor(unittest.TestCase):
    """Tests for the StreamingDataFrameProcessor class."""

    def setUp(self):
        """Set up test data."""
        # Create a temporary CSV file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.temp_dir, 'test.csv')
        
        # Create a test DataFrame
        self.df = pd.DataFrame({
            'A': range(100),
            'B': range(100, 200)
        })
        
        # Save the DataFrame to CSV
        self.df.to_csv(self.csv_file, index=False)

    def tearDown(self):
        """Clean up test data."""
        # Remove temporary files
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)
        os.rmdir(self.temp_dir)

    def test_process_csv(self):
        """Test processing a CSV file."""
        processor = StreamingDataFrameProcessor(chunk_size=10)  # Small chunk size for testing
        
        # Define a processing function
        def process_func(chunk):
            chunk['C'] = chunk['A'] + chunk['B']
            return chunk
        
        # Process the CSV file
        chunks = list(processor.process_csv(self.csv_file, process_func))
        
        # Check the results
        self.assertEqual(len(chunks), 10)  # 100 rows / 10 chunk size = 10 chunks
        
        # Combine chunks and check the result
        result_df = pd.concat(chunks)
        self.assertEqual(len(result_df), 100)
        self.assertTrue('C' in result_df.columns)
        self.assertTrue(all(result_df['C'] == result_df['A'] + result_df['B']))

    def test_process_csv_with_output_file(self):
        """Test processing a CSV file with an output file."""
        processor = StreamingDataFrameProcessor(chunk_size=10)  # Small chunk size for testing
        
        # Define a processing function
        def process_func(chunk):
            chunk['C'] = chunk['A'] + chunk['B']
            return chunk
        
        # Create an output file
        output_file = os.path.join(self.temp_dir, 'output.csv')
        
        # Process the CSV file and save to output
        result = processor.process_csv(self.csv_file, process_func, output_file=output_file)
        
        # Check that the result is None (data is saved to file)
        self.assertIsNone(result)
        
        # Check that the output file exists
        self.assertTrue(os.path.exists(output_file))
        
        # Read the output file and check the result
        result_df = pd.read_csv(output_file)
        self.assertEqual(len(result_df), 100)
        self.assertTrue('C' in result_df.columns)
        self.assertTrue(all(result_df['C'] == result_df['A'] + result_df['B']))
        
        # Clean up
        os.remove(output_file)

    def test_process_csv_with_progress_callback(self):
        """Test processing a CSV file with a progress callback."""
        processor = StreamingDataFrameProcessor(chunk_size=10)  # Small chunk size for testing
        
        # Define a processing function
        def process_func(chunk):
            chunk['C'] = chunk['A'] + chunk['B']
            return chunk
        
        # Create a mock progress callback
        progress_callback = MagicMock()
        
        # Process the CSV file
        chunks = list(processor.process_csv(self.csv_file, process_func, progress_callback=progress_callback))
        
        # Check that the progress callback was called
        self.assertGreaterEqual(progress_callback.call_count, 1)
        # Final call should be with the total count
        progress_callback.assert_called_with(100)

    def test_process_dataframe_in_chunks(self):
        """Test processing a DataFrame in chunks."""
        processor = StreamingDataFrameProcessor(chunk_size=10)  # Small chunk size for testing
        
        # Define a processing function
        def process_func(chunk):
            chunk['C'] = chunk['A'] + chunk['B']
            return chunk
        
        # Process the DataFrame in chunks
        chunks = list(processor.process_dataframe_in_chunks(self.df, process_func))
        
        # Check the results
        self.assertEqual(len(chunks), 10)  # 100 rows / 10 chunk size = 10 chunks
        
        # Combine chunks and check the result
        result_df = pd.concat(chunks)
        self.assertEqual(len(result_df), 100)
        self.assertTrue('C' in result_df.columns)
        self.assertTrue(all(result_df['C'] == result_df['A'] + result_df['B']))

    def test_process_dataframe_in_chunks_with_progress_callback(self):
        """Test processing a DataFrame in chunks with a progress callback."""
        processor = StreamingDataFrameProcessor(chunk_size=10)  # Small chunk size for testing
        
        # Define a processing function
        def process_func(chunk):
            chunk['C'] = chunk['A'] + chunk['B']
            return chunk
        
        # Create a mock progress callback
        progress_callback = MagicMock()
        
        # Process the DataFrame in chunks
        chunks = list(processor.process_dataframe_in_chunks(self.df, process_func, progress_callback))
        
        # Check that the progress callback was called
        self.assertGreaterEqual(progress_callback.call_count, 1)
        # Final call should be with the total count
        progress_callback.assert_called_with(100)


class TestConvenienceFunctions(unittest.TestCase):
    """Tests for convenience functions."""

    def setUp(self):
        """Set up test data."""
        # Create a temporary CSV file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.temp_dir, 'test.csv')
        
        # Create a test DataFrame
        self.df = pd.DataFrame({
            'A': range(100),
            'B': range(100, 200)
        })
        
        # Save the DataFrame to CSV
        self.df.to_csv(self.csv_file, index=False)

    def tearDown(self):
        """Clean up test data."""
        # Remove temporary files
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)
        os.rmdir(self.temp_dir)

    def test_stream_process(self):
        """Test the stream_process convenience function."""
        # Create a simple data source
        data_source = iter([1, 2, 3, 4, 5])
        
        # Define a simple processing function
        def process_func(x):
            return x * 2
        
        # Process the stream
        results = list(stream_process(data_source, process_func))
        
        # Check the results
        self.assertEqual(results, [2, 4, 6, 8, 10])

    def test_stream_process_csv(self):
        """Test the stream_process_csv convenience function."""
        # Define a processing function
        def process_func(chunk):
            chunk['C'] = chunk['A'] + chunk['B']
            return chunk
        
        # Process the CSV file
        chunks = list(stream_process_csv(self.csv_file, process_func, chunk_size=10))
        
        # Check the results
        self.assertEqual(len(chunks), 10)  # 100 rows / 10 chunk size = 10 chunks
        
        # Combine chunks and check the result
        result_df = pd.concat(chunks)
        self.assertEqual(len(result_df), 100)
        self.assertTrue('C' in result_df.columns)
        self.assertTrue(all(result_df['C'] == result_df['A'] + result_df['B']))

    def test_stream_process_csv_with_output_file(self):
        """Test the stream_process_csv convenience function with an output file."""
        # Define a processing function
        def process_func(chunk):
            chunk['C'] = chunk['A'] + chunk['B']
            return chunk
        
        # Create an output file
        output_file = os.path.join(self.temp_dir, 'output.csv')
        
        # Process the CSV file and save to output
        result = stream_process_csv(self.csv_file, process_func, chunk_size=10, output_file=output_file)
        
        # Check that the result is None (data is saved to file)
        self.assertIsNone(result)
        
        # Check that the output file exists
        self.assertTrue(os.path.exists(output_file))
        
        # Read the output file and check the result
        result_df = pd.read_csv(output_file)
        self.assertEqual(len(result_df), 100)
        self.assertTrue('C' in result_df.columns)
        self.assertTrue(all(result_df['C'] == result_df['A'] + result_df['B']))
        
        # Clean up
        os.remove(output_file)


if __name__ == '__main__':
    unittest.main()