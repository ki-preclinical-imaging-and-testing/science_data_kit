"""
Machine Learning Model Inference Utilities for Science Data Kit

This module provides utilities for performing inference with machine learning models,
supporting both batch inference for large datasets and real-time inference for
streaming data. It integrates with the streaming_processing and schema_validation
modules to ensure efficient and validated data processing.
"""

import logging
import time
import os
import pickle
from typing import Any, Callable, Dict, Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar, Union, Generator
import numpy as np

from science_data_kit.core.utils.streaming_processing import StreamingProcessor
from science_data_kit.core.utils.schema_validation import validate_schema

# Type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')


class ModelInferenceError(Exception):
    """Exception raised for errors during model inference."""
    pass


class ModelLoader:
    """
    Utility for loading machine learning models from various formats.
    
    This class provides methods for loading models from files or objects,
    with support for different model formats and frameworks.
    """
    
    def __init__(self):
        """Initialize a model loader."""
        self.logger = logging.getLogger(__name__)
    
    def load_from_pickle(self, model_path: str) -> Any:
        """
        Load a model from a pickle file.
        
        Args:
            model_path: Path to the pickle file containing the model.
            
        Returns:
            The loaded model.
            
        Raises:
            ModelInferenceError: If the model cannot be loaded.
        """
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            return model
        except Exception as e:
            error_msg = f"Failed to load model from {model_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelInferenceError(error_msg)
    
    def load_from_joblib(self, model_path: str) -> Any:
        """
        Load a model from a joblib file.
        
        Args:
            model_path: Path to the joblib file containing the model.
            
        Returns:
            The loaded model.
            
        Raises:
            ModelInferenceError: If the model cannot be loaded.
        """
        try:
            import joblib
            model = joblib.load(model_path)
            return model
        except Exception as e:
            error_msg = f"Failed to load model from {model_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelInferenceError(error_msg)
    
    def load_from_keras(self, model_path: str) -> Any:
        """
        Load a Keras model from a file.
        
        Args:
            model_path: Path to the file containing the Keras model.
            
        Returns:
            The loaded Keras model.
            
        Raises:
            ModelInferenceError: If the model cannot be loaded.
        """
        try:
            from tensorflow import keras
            model = keras.models.load_model(model_path)
            return model
        except Exception as e:
            error_msg = f"Failed to load Keras model from {model_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelInferenceError(error_msg)
    
    def load_from_pytorch(self, model_path: str, model_class: Any) -> Any:
        """
        Load a PyTorch model from a file.
        
        Args:
            model_path: Path to the file containing the PyTorch model weights.
            model_class: The PyTorch model class to instantiate.
            
        Returns:
            The loaded PyTorch model.
            
        Raises:
            ModelInferenceError: If the model cannot be loaded.
        """
        try:
            import torch
            model = model_class()
            model.load_state_dict(torch.load(model_path))
            model.eval()  # Set the model to evaluation mode
            return model
        except Exception as e:
            error_msg = f"Failed to load PyTorch model from {model_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelInferenceError(error_msg)


class ModelInferenceProcessor:
    """
    Processor for machine learning model inference.
    
    This class provides methods for performing inference with machine learning models,
    with support for both batch processing and streaming inference.
    """
    
    def __init__(self, model: Any, batch_size: int = 32):
        """
        Initialize a model inference processor.
        
        Args:
            model: The machine learning model to use for inference.
            batch_size: Size of batches for batch processing.
        """
        self.model = model
        self.batch_size = batch_size
        self.logger = logging.getLogger(__name__)
        self.streaming_processor = StreamingProcessor(buffer_size=batch_size)
    
    def preprocess_data(self, data: T) -> Any:
        """
        Preprocess data before inference.
        
        This method should be overridden by subclasses to implement
        specific preprocessing logic for the model.
        
        Args:
            data: The data to preprocess.
            
        Returns:
            The preprocessed data.
        """
        return data
    
    def postprocess_results(self, results: Any) -> R:
        """
        Postprocess inference results.
        
        This method should be overridden by subclasses to implement
        specific postprocessing logic for the model's outputs.
        
        Args:
            results: The raw inference results.
            
        Returns:
            The postprocessed results.
        """
        return results
    
    def predict_batch(self, batch: List[T]) -> List[R]:
        """
        Perform inference on a batch of data.
        
        Args:
            batch: List of data items to process.
            
        Returns:
            List of inference results.
            
        Raises:
            ModelInferenceError: If inference fails.
        """
        try:
            # Preprocess the batch
            preprocessed_batch = [self.preprocess_data(item) for item in batch]
            
            # Convert to numpy array if needed
            if hasattr(self.model, 'predict') and not isinstance(preprocessed_batch, np.ndarray):
                try:
                    preprocessed_batch = np.array(preprocessed_batch)
                except Exception as e:
                    self.logger.warning(f"Could not convert batch to numpy array: {str(e)}")
            
            # Perform inference
            if hasattr(self.model, 'predict'):
                raw_results = self.model.predict(preprocessed_batch)
            elif callable(self.model):
                raw_results = self.model(preprocessed_batch)
            else:
                raise ModelInferenceError("Model does not have a predict method and is not callable")
            
            # Postprocess the results
            if isinstance(raw_results, np.ndarray) and len(raw_results) == len(batch):
                return [self.postprocess_results(result) for result in raw_results]
            else:
                return [self.postprocess_results(raw_results) for _ in batch]
        
        except Exception as e:
            error_msg = f"Error during batch inference: {str(e)}"
            self.logger.error(error_msg)
            raise ModelInferenceError(error_msg)
    
    def predict_stream(
        self,
        data_source: Iterator[T],
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Generator[R, None, None]:
        """
        Perform inference on a stream of data.
        
        Args:
            data_source: Iterator providing the data items to process.
            progress_callback: Optional callback function to report progress.
                              Takes one argument: the count of processed items.
            
        Yields:
            Inference results, one at a time.
            
        Raises:
            ModelInferenceError: If inference fails.
        """
        try:
            # Use the streaming processor to process data in batches
            yield from self.streaming_processor.process_stream_batched(
                data_source,
                self.predict_batch,
                progress_callback
            )
        except Exception as e:
            error_msg = f"Error during stream inference: {str(e)}"
            self.logger.error(error_msg)
            raise ModelInferenceError(error_msg)
    
    def predict_dataframe(
        self,
        df: 'pd.DataFrame',
        feature_columns: List[str],
        output_column: str = 'prediction',
        batch_size: Optional[int] = None,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> 'pd.DataFrame':
        """
        Perform inference on a pandas DataFrame.
        
        Args:
            df: DataFrame containing the data to process.
            feature_columns: List of column names to use as features.
            output_column: Name of the column to store predictions.
            batch_size: Size of batches for processing. If None, uses self.batch_size.
            progress_callback: Optional callback function to report progress.
                              Takes one argument: the count of processed rows.
            
        Returns:
            DataFrame with predictions added as a new column.
            
        Raises:
            ModelInferenceError: If inference fails.
        """
        import pandas as pd
        
        if df.empty:
            return df
        
        try:
            # Process the DataFrame in batches
            batch_size = batch_size or self.batch_size
            processed_rows = 0
            result_df = df.copy()
            
            # Initialize the output column
            result_df[output_column] = None
            
            # Process in batches
            for i in range(0, len(df), batch_size):
                # Get the batch
                batch_df = df.iloc[i:i + batch_size]
                
                # Extract features
                features = batch_df[feature_columns].values
                
                # Perform inference
                if hasattr(self.model, 'predict'):
                    predictions = self.model.predict(features)
                elif callable(self.model):
                    predictions = self.model(features)
                else:
                    raise ModelInferenceError("Model does not have a predict method and is not callable")
                
                # Postprocess and store predictions
                for j, prediction in enumerate(predictions):
                    result_df.iloc[i + j, result_df.columns.get_loc(output_column)] = self.postprocess_results(prediction)
                
                # Update progress
                processed_rows += len(batch_df)
                if progress_callback:
                    progress_callback(processed_rows)
            
            return result_df
        
        except Exception as e:
            error_msg = f"Error during DataFrame inference: {str(e)}"
            self.logger.error(error_msg)
            raise ModelInferenceError(error_msg)


class RealTimeInferenceService:
    """
    Service for real-time inference with machine learning models.
    
    This class provides methods for performing real-time inference with
    machine learning models, with support for input validation and
    result caching.
    """
    
    def __init__(
        self,
        model: Any,
        preprocessor: Optional[Callable[[Dict[str, Any]], Any]] = None,
        postprocessor: Optional[Callable[[Any], Dict[str, Any]]] = None,
        input_schema: Optional[Any] = None,
        cache_size: int = 100
    ):
        """
        Initialize a real-time inference service.
        
        Args:
            model: The machine learning model to use for inference.
            preprocessor: Optional function to preprocess input data.
            postprocessor: Optional function to postprocess inference results.
            input_schema: Optional schema class for validating input data.
            cache_size: Size of the result cache.
        """
        self.model = model
        self.preprocessor = preprocessor
        self.postprocessor = postprocessor
        self.input_schema = input_schema
        self.cache_size = cache_size
        self.logger = logging.getLogger(__name__)
        
        # Initialize cache
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_keys: List[str] = []
    
    def _generate_cache_key(self, input_data: Dict[str, Any]) -> str:
        """
        Generate a cache key for input data.
        
        Args:
            input_data: The input data.
            
        Returns:
            A string key for the cache.
        """
        import hashlib
        import json
        
        # Sort the input data to ensure consistent keys
        sorted_data = {k: input_data[k] for k in sorted(input_data.keys())}
        
        # Generate a hash of the serialized data
        data_str = json.dumps(sorted_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _add_to_cache(self, key: str, result: Dict[str, Any]):
        """
        Add a result to the cache.
        
        Args:
            key: The cache key.
            result: The result to cache.
        """
        # If the cache is full, remove the oldest entry
        if len(self.cache_keys) >= self.cache_size:
            oldest_key = self.cache_keys.pop(0)
            del self.cache[oldest_key]
        
        # Add the new entry
        self.cache[key] = result
        self.cache_keys.append(key)
    
    def predict(self, input_data: Dict[str, Any], use_cache: bool = True) -> Dict[str, Any]:
        """
        Perform inference on input data.
        
        Args:
            input_data: Dictionary containing the input data.
            use_cache: Whether to use the result cache.
            
        Returns:
            Dictionary containing the inference results.
            
        Raises:
            ModelInferenceError: If inference fails or input validation fails.
        """
        try:
            # Validate input data if a schema is provided
            if self.input_schema:
                errors = validate_schema(input_data, self.input_schema)
                if errors:
                    error_msg = f"Input validation failed: {', '.join(errors)}"
                    self.logger.error(error_msg)
                    raise ModelInferenceError(error_msg)
            
            # Check cache if enabled
            if use_cache:
                cache_key = self._generate_cache_key(input_data)
                if cache_key in self.cache:
                    return self.cache[cache_key]
            
            # Preprocess input data
            if self.preprocessor:
                processed_input = self.preprocessor(input_data)
            else:
                processed_input = input_data
            
            # Perform inference
            start_time = time.time()
            
            if hasattr(self.model, 'predict'):
                raw_result = self.model.predict(processed_input)
            elif callable(self.model):
                raw_result = self.model(processed_input)
            else:
                raise ModelInferenceError("Model does not have a predict method and is not callable")
            
            inference_time = time.time() - start_time
            
            # Postprocess result
            if self.postprocessor:
                result = self.postprocessor(raw_result)
            else:
                result = {"prediction": raw_result}
            
            # Add metadata
            result["metadata"] = {
                "inference_time": inference_time,
                "timestamp": time.time()
            }
            
            # Cache the result if enabled
            if use_cache:
                cache_key = self._generate_cache_key(input_data)
                self._add_to_cache(cache_key, result)
            
            return result
        
        except Exception as e:
            if isinstance(e, ModelInferenceError):
                raise
            
            error_msg = f"Error during real-time inference: {str(e)}"
            self.logger.error(error_msg)
            raise ModelInferenceError(error_msg)


def load_model(model_path: str, model_format: str = 'pickle', model_class: Any = None) -> Any:
    """
    Load a machine learning model from a file.
    
    This is a convenience function that creates a ModelLoader and calls the appropriate loading method.
    
    Args:
        model_path: Path to the file containing the model.
        model_format: Format of the model file ('pickle', 'joblib', 'keras', or 'pytorch').
        model_class: For PyTorch models, the model class to instantiate.
        
    Returns:
        The loaded model.
        
    Raises:
        ModelInferenceError: If the model cannot be loaded.
    """
    loader = ModelLoader()
    
    if model_format == 'pickle':
        return loader.load_from_pickle(model_path)
    elif model_format == 'joblib':
        return loader.load_from_joblib(model_path)
    elif model_format == 'keras':
        return loader.load_from_keras(model_path)
    elif model_format == 'pytorch':
        if model_class is None:
            raise ModelInferenceError("model_class must be provided for PyTorch models")
        return loader.load_from_pytorch(model_path, model_class)
    else:
        raise ModelInferenceError(f"Unsupported model format: {model_format}")


def batch_inference(
    model: Any,
    data: List[T],
    preprocessor: Optional[Callable[[T], Any]] = None,
    postprocessor: Optional[Callable[[Any], R]] = None,
    batch_size: int = 32
) -> List[R]:
    """
    Perform batch inference with a machine learning model.
    
    This is a convenience function that creates a ModelInferenceProcessor and calls its predict_batch method.
    
    Args:
        model: The machine learning model to use for inference.
        data: List of data items to process.
        preprocessor: Optional function to preprocess input data.
        postprocessor: Optional function to postprocess inference results.
        batch_size: Size of batches for processing.
        
    Returns:
        List of inference results.
        
    Raises:
        ModelInferenceError: If inference fails.
    """
    class CustomInferenceProcessor(ModelInferenceProcessor):
        def preprocess_data(self, data: T) -> Any:
            if preprocessor:
                return preprocessor(data)
            return data
        
        def postprocess_results(self, results: Any) -> R:
            if postprocessor:
                return postprocessor(results)
            return results
    
    processor = CustomInferenceProcessor(model, batch_size)
    return processor.predict_batch(data)


def stream_inference(
    model: Any,
    data_source: Iterator[T],
    preprocessor: Optional[Callable[[T], Any]] = None,
    postprocessor: Optional[Callable[[Any], R]] = None,
    batch_size: int = 32,
    progress_callback: Optional[Callable[[int], None]] = None
) -> Generator[R, None, None]:
    """
    Perform streaming inference with a machine learning model.
    
    This is a convenience function that creates a ModelInferenceProcessor and calls its predict_stream method.
    
    Args:
        model: The machine learning model to use for inference.
        data_source: Iterator providing the data items to process.
        preprocessor: Optional function to preprocess input data.
        postprocessor: Optional function to postprocess inference results.
        batch_size: Size of batches for processing.
        progress_callback: Optional callback function to report progress.
                          Takes one argument: the count of processed items.
        
    Yields:
        Inference results, one at a time.
        
    Raises:
        ModelInferenceError: If inference fails.
    """
    class CustomInferenceProcessor(ModelInferenceProcessor):
        def preprocess_data(self, data: T) -> Any:
            if preprocessor:
                return preprocessor(data)
            return data
        
        def postprocess_results(self, results: Any) -> R:
            if postprocessor:
                return postprocessor(results)
            return results
    
    processor = CustomInferenceProcessor(model, batch_size)
    yield from processor.predict_stream(data_source, progress_callback)


def example_model_inference():
    """
    Example of using model inference utilities.
    
    Returns:
        Dictionary with example results.
    """
    import pandas as pd
    import numpy as np
    from sklearn.linear_model import LinearRegression
    import tempfile
    import os
    
    # Create a simple linear regression model
    X = np.array([[1], [2], [3], [4], [5]])
    y = np.array([2, 4, 6, 8, 10])
    model = LinearRegression().fit(X, y)
    
    # Save the model to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as temp_file:
        model_path = temp_file.name
        pickle.dump(model, open(model_path, 'wb'))
    
    # Example 1: Batch inference
    test_data = [[6], [7], [8], [9], [10]]
    
    # Load the model
    loaded_model = load_model(model_path)
    
    # Perform batch inference
    batch_results = batch_inference(loaded_model, test_data)
    
    # Example 2: Streaming inference
    def generate_data(n):
        for i in range(n):
            yield [i + 1]
    
    # Perform streaming inference
    stream_results = list(stream_inference(loaded_model, generate_data(5)))
    
    # Example 3: DataFrame inference
    df = pd.DataFrame({'x': [6, 7, 8, 9, 10]})
    
    # Create a custom inference processor
    processor = ModelInferenceProcessor(loaded_model)
    
    # Perform DataFrame inference
    df_results = processor.predict_dataframe(df, ['x'], 'prediction')
    
    # Example 4: Real-time inference
    service = RealTimeInferenceService(loaded_model)
    
    # Perform real-time inference
    rt_result = service.predict({'input': [6]})
    
    # Clean up
    os.unlink(model_path)
    
    return {
        'batch_inference': {
            'input': test_data,
            'output': batch_results.tolist() if isinstance(batch_results, np.ndarray) else batch_results
        },
        'stream_inference': {
            'output': stream_results
        },
        'dataframe_inference': {
            'output': df_results['prediction'].tolist()
        },
        'real_time_inference': {
            'input': {'input': [6]},
            'output': rt_result
        }
    }
"""