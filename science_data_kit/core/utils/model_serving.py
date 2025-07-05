"""
Machine Learning Model Serving Utilities for Science Data Kit

This module provides utilities for serving machine learning models,
supporting REST API endpoints, batch processing, and real-time inference.
It integrates with the model_inference, model_training, and model_serialization
modules to provide a complete solution for model deployment.
"""

import logging
import os
import json
import time
import threading
import queue
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, Type
from datetime import datetime
import uuid

from science_data_kit.core.utils.model_inference import ModelInferenceError, RealTimeInferenceService
from science_data_kit.core.utils.model_serialization import ModelSerializationError, ModelRegistry


class ModelServingError(Exception):
    """Exception raised for errors during model serving."""
    pass


class ModelServer:
    """
    Base class for serving machine learning models.
    
    This class provides methods for loading models, processing requests,
    and managing model lifecycle.
    """
    
    def __init__(
        self,
        model_registry: Optional[ModelRegistry] = None,
        registry_dir: str = "models",
        max_workers: int = 4,
        cache_size: int = 100
    ):
        """
        Initialize a model server.
        
        Args:
            model_registry: Optional ModelRegistry instance. If None, creates a new one.
            registry_dir: Directory for model registry if creating a new one.
            max_workers: Maximum number of worker threads for processing requests.
            cache_size: Size of the result cache.
        """
        self.model_registry = model_registry or ModelRegistry(registry_dir)
        self.max_workers = max_workers
        self.cache_size = cache_size
        self.logger = logging.getLogger(__name__)
        
        # Dictionary to store loaded models
        self.loaded_models: Dict[str, Dict[str, Any]] = {}
        
        # Dictionary to store inference services
        self.inference_services: Dict[str, RealTimeInferenceService] = {}
        
        # Request queue and worker threads
        self.request_queue = queue.Queue()
        self.workers = []
        self.running = False
    
    def start(self):
        """
        Start the model server.
        
        This method starts worker threads for processing requests.
        """
        if self.running:
            return
        
        self.running = True
        
        # Start worker threads
        for _ in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
        
        self.logger.info(f"Model server started with {self.max_workers} workers")
    
    def stop(self):
        """
        Stop the model server.
        
        This method stops worker threads and cleans up resources.
        """
        if not self.running:
            return
        
        self.running = False
        
        # Signal workers to stop
        for _ in range(self.max_workers):
            self.request_queue.put(None)
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join()
        
        self.workers = []
        
        self.logger.info("Model server stopped")
    
    def _worker_loop(self):
        """
        Worker thread loop for processing requests.
        """
        while self.running:
            try:
                # Get a request from the queue
                request = self.request_queue.get(timeout=1.0)
                
                # Check for stop signal
                if request is None:
                    break
                
                # Process the request
                model_id, input_data, callback = request
                
                try:
                    # Get the inference service
                    service = self._get_inference_service(model_id)
                    
                    # Process the request
                    result = service.predict(input_data)
                    
                    # Call the callback with the result
                    if callback:
                        callback(result, None)
                
                except Exception as e:
                    error_msg = f"Error processing request for model {model_id}: {str(e)}"
                    self.logger.error(error_msg)
                    
                    # Call the callback with the error
                    if callback:
                        callback(None, error_msg)
                
                finally:
                    # Mark the request as done
                    self.request_queue.task_done()
            
            except queue.Empty:
                # No requests in the queue, continue
                continue
            
            except Exception as e:
                error_msg = f"Error in worker loop: {str(e)}"
                self.logger.error(error_msg)
    
    def load_model(
        self,
        model_name: str,
        version: Optional[str] = None,
        model_format: Optional[str] = None,
        preprocessor: Optional[Callable[[Dict[str, Any]], Any]] = None,
        postprocessor: Optional[Callable[[Any], Dict[str, Any]]] = None,
        input_schema: Optional[Any] = None,
        **kwargs
    ) -> str:
        """
        Load a model for serving.
        
        Args:
            model_name: Name of the model to load.
            version: Version of the model to load. If None, loads the latest version.
            model_format: Format of the model. If None, determined from metadata.
            preprocessor: Optional function to preprocess input data.
            postprocessor: Optional function to postprocess inference results.
            input_schema: Optional schema class for validating input data.
            **kwargs: Additional arguments for model loading.
            
        Returns:
            Model ID for referencing the loaded model.
            
        Raises:
            ModelServingError: If the model cannot be loaded.
        """
        try:
            # Generate a unique model ID
            model_id = f"{model_name}_{version or 'latest'}_{uuid.uuid4().hex[:8]}"
            
            # Load the model from the registry
            model, metadata = self.model_registry.get_model(
                model_name, version, model_format, **kwargs
            )
            
            # Store the loaded model
            self.loaded_models[model_id] = {
                "model": model,
                "metadata": metadata,
                "loaded_at": datetime.now().isoformat()
            }
            
            # Create an inference service for the model
            service = RealTimeInferenceService(
                model,
                preprocessor=preprocessor,
                postprocessor=postprocessor,
                input_schema=input_schema,
                cache_size=self.cache_size
            )
            
            # Store the inference service
            self.inference_services[model_id] = service
            
            self.logger.info(f"Model {model_name} (version {version or 'latest'}) loaded with ID {model_id}")
            
            return model_id
        
        except Exception as e:
            error_msg = f"Error loading model {model_name}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelServingError(error_msg)
    
    def unload_model(self, model_id: str) -> bool:
        """
        Unload a model from the server.
        
        Args:
            model_id: ID of the model to unload.
            
        Returns:
            True if the model was unloaded, False otherwise.
            
        Raises:
            ModelServingError: If the model cannot be unloaded.
        """
        try:
            if model_id not in self.loaded_models:
                raise ModelServingError(f"Model with ID {model_id} not found")
            
            # Remove the model and inference service
            del self.loaded_models[model_id]
            del self.inference_services[model_id]
            
            self.logger.info(f"Model with ID {model_id} unloaded")
            
            return True
        
        except Exception as e:
            if isinstance(e, ModelServingError):
                raise
            
            error_msg = f"Error unloading model with ID {model_id}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelServingError(error_msg)
    
    def _get_inference_service(self, model_id: str) -> RealTimeInferenceService:
        """
        Get the inference service for a model.
        
        Args:
            model_id: ID of the model.
            
        Returns:
            RealTimeInferenceService for the model.
            
        Raises:
            ModelServingError: If the model is not found.
        """
        if model_id not in self.inference_services:
            raise ModelServingError(f"Model with ID {model_id} not found")
        
        return self.inference_services[model_id]
    
    def predict(
        self,
        model_id: str,
        input_data: Dict[str, Any],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Perform synchronous inference with a model.
        
        Args:
            model_id: ID of the model to use.
            input_data: Dictionary containing the input data.
            use_cache: Whether to use the result cache.
            
        Returns:
            Dictionary containing the inference results.
            
        Raises:
            ModelServingError: If inference fails.
        """
        try:
            # Get the inference service
            service = self._get_inference_service(model_id)
            
            # Perform inference
            result = service.predict(input_data, use_cache=use_cache)
            
            return result
        
        except Exception as e:
            error_msg = f"Error during inference with model {model_id}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelServingError(error_msg)
    
    def predict_async(
        self,
        model_id: str,
        input_data: Dict[str, Any],
        callback: Optional[Callable[[Dict[str, Any], Optional[str]], None]] = None,
        use_cache: bool = True
    ) -> str:
        """
        Perform asynchronous inference with a model.
        
        Args:
            model_id: ID of the model to use.
            input_data: Dictionary containing the input data.
            callback: Optional callback function to receive the result.
                     Takes two arguments: result and error message.
            use_cache: Whether to use the result cache.
            
        Returns:
            Request ID for tracking the request.
            
        Raises:
            ModelServingError: If the request cannot be queued.
        """
        try:
            # Check if the model exists
            if model_id not in self.inference_services:
                raise ModelServingError(f"Model with ID {model_id} not found")
            
            # Generate a request ID
            request_id = f"request_{uuid.uuid4().hex}"
            
            # Add use_cache to input_data
            request_data = {
                "data": input_data,
                "use_cache": use_cache
            }
            
            # Add the request to the queue
            self.request_queue.put((model_id, request_data, callback))
            
            return request_id
        
        except Exception as e:
            error_msg = f"Error queuing request for model {model_id}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelServingError(error_msg)
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get information about a loaded model.
        
        Args:
            model_id: ID of the model.
            
        Returns:
            Dictionary containing model information.
            
        Raises:
            ModelServingError: If the model is not found.
        """
        try:
            if model_id not in self.loaded_models:
                raise ModelServingError(f"Model with ID {model_id} not found")
            
            model_info = self.loaded_models[model_id]
            
            # Extract relevant information
            info = {
                "model_id": model_id,
                "model_name": model_info["metadata"].get("model_name", "unknown"),
                "model_format": model_info["metadata"].get("model_format", "unknown"),
                "version": model_info["metadata"].get("version", "unknown"),
                "loaded_at": model_info["loaded_at"],
                "metadata": model_info["metadata"]
            }
            
            return info
        
        except Exception as e:
            if isinstance(e, ModelServingError):
                raise
            
            error_msg = f"Error getting information for model {model_id}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelServingError(error_msg)
    
    def list_loaded_models(self) -> List[Dict[str, Any]]:
        """
        List all loaded models.
        
        Returns:
            List of dictionaries containing model information.
        """
        try:
            return [self.get_model_info(model_id) for model_id in self.loaded_models]
        
        except Exception as e:
            error_msg = f"Error listing loaded models: {str(e)}"
            self.logger.error(error_msg)
            return []


class BatchProcessor:
    """
    Processor for batch inference with machine learning models.
    
    This class provides methods for processing batches of data with
    machine learning models, with support for parallel processing.
    """
    
    def __init__(
        self,
        model_server: ModelServer,
        batch_size: int = 32,
        max_workers: int = 4
    ):
        """
        Initialize a batch processor.
        
        Args:
            model_server: ModelServer instance for serving models.
            batch_size: Size of batches for processing.
            max_workers: Maximum number of worker threads for parallel processing.
        """
        self.model_server = model_server
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
    
    def process_batch(
        self,
        model_id: str,
        batch: List[Dict[str, Any]],
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of data with a model.
        
        Args:
            model_id: ID of the model to use.
            batch: List of input data dictionaries.
            use_cache: Whether to use the result cache.
            
        Returns:
            List of inference results.
            
        Raises:
            ModelServingError: If batch processing fails.
        """
        try:
            results = []
            
            for item in batch:
                result = self.model_server.predict(model_id, item, use_cache=use_cache)
                results.append(result)
            
            return results
        
        except Exception as e:
            error_msg = f"Error processing batch with model {model_id}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelServingError(error_msg)
    
    def process_batch_parallel(
        self,
        model_id: str,
        batch: List[Dict[str, Any]],
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of data with a model in parallel.
        
        Args:
            model_id: ID of the model to use.
            batch: List of input data dictionaries.
            use_cache: Whether to use the result cache.
            
        Returns:
            List of inference results.
            
        Raises:
            ModelServingError: If batch processing fails.
        """
        try:
            import concurrent.futures
            
            results = [None] * len(batch)
            
            def process_item(index, item):
                try:
                    result = self.model_server.predict(model_id, item, use_cache=use_cache)
                    return index, result, None
                except Exception as e:
                    return index, None, str(e)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(process_item, i, item) for i, item in enumerate(batch)]
                
                for future in concurrent.futures.as_completed(futures):
                    index, result, error = future.result()
                    
                    if error:
                        raise ModelServingError(f"Error processing item {index}: {error}")
                    
                    results[index] = result
            
            return results
        
        except Exception as e:
            error_msg = f"Error processing batch in parallel with model {model_id}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelServingError(error_msg)
    
    def process_dataframe(
        self,
        model_id: str,
        df: 'pd.DataFrame',
        input_columns: List[str],
        output_column: str = 'prediction',
        use_cache: bool = True,
        parallel: bool = True
    ) -> 'pd.DataFrame':
        """
        Process a pandas DataFrame with a model.
        
        Args:
            model_id: ID of the model to use.
            df: DataFrame containing the data to process.
            input_columns: List of column names to use as input.
            output_column: Name of the column to store predictions.
            use_cache: Whether to use the result cache.
            parallel: Whether to process in parallel.
            
        Returns:
            DataFrame with predictions added as a new column.
            
        Raises:
            ModelServingError: If DataFrame processing fails.
        """
        try:
            import pandas as pd
            
            if df.empty:
                return df
            
            # Create a copy of the DataFrame
            result_df = df.copy()
            
            # Initialize the output column
            result_df[output_column] = None
            
            # Convert DataFrame to list of dictionaries
            rows = []
            for _, row in df.iterrows():
                input_data = {col: row[col] for col in input_columns}
                rows.append(input_data)
            
            # Process in batches
            all_results = []
            for i in range(0, len(rows), self.batch_size):
                batch = rows[i:i + self.batch_size]
                
                if parallel:
                    batch_results = self.process_batch_parallel(model_id, batch, use_cache=use_cache)
                else:
                    batch_results = self.process_batch(model_id, batch, use_cache=use_cache)
                
                all_results.extend(batch_results)
            
            # Update the DataFrame with results
            for i, result in enumerate(all_results):
                if "prediction" in result:
                    result_df.iloc[i, result_df.columns.get_loc(output_column)] = result["prediction"]
                else:
                    result_df.iloc[i, result_df.columns.get_loc(output_column)] = result
            
            return result_df
        
        except Exception as e:
            error_msg = f"Error processing DataFrame with model {model_id}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelServingError(error_msg)


class ModelServingAPI:
    """
    API for serving machine learning models.
    
    This class provides a simple API for serving machine learning models,
    with support for model management, inference, and batch processing.
    """
    
    def __init__(
        self,
        model_server: Optional[ModelServer] = None,
        registry_dir: str = "models",
        max_workers: int = 4,
        cache_size: int = 100
    ):
        """
        Initialize a model serving API.
        
        Args:
            model_server: Optional ModelServer instance. If None, creates a new one.
            registry_dir: Directory for model registry if creating a new one.
            max_workers: Maximum number of worker threads for processing requests.
            cache_size: Size of the result cache.
        """
        self.model_server = model_server or ModelServer(
            registry_dir=registry_dir,
            max_workers=max_workers,
            cache_size=cache_size
        )
        self.batch_processor = BatchProcessor(
            model_server=self.model_server,
            max_workers=max_workers
        )
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """
        Start the model serving API.
        """
        self.model_server.start()
        self.logger.info("Model serving API started")
    
    def stop(self):
        """
        Stop the model serving API.
        """
        self.model_server.stop()
        self.logger.info("Model serving API stopped")
    
    def load_model(
        self,
        model_name: str,
        version: Optional[str] = None,
        model_format: Optional[str] = None,
        preprocessor: Optional[Callable[[Dict[str, Any]], Any]] = None,
        postprocessor: Optional[Callable[[Any], Dict[str, Any]]] = None,
        input_schema: Optional[Any] = None,
        **kwargs
    ) -> str:
        """
        Load a model for serving.
        
        Args:
            model_name: Name of the model to load.
            version: Version of the model to load. If None, loads the latest version.
            model_format: Format of the model. If None, determined from metadata.
            preprocessor: Optional function to preprocess input data.
            postprocessor: Optional function to postprocess inference results.
            input_schema: Optional schema class for validating input data.
            **kwargs: Additional arguments for model loading.
            
        Returns:
            Model ID for referencing the loaded model.
            
        Raises:
            ModelServingError: If the model cannot be loaded.
        """
        return self.model_server.load_model(
            model_name,
            version,
            model_format,
            preprocessor,
            postprocessor,
            input_schema,
            **kwargs
        )
    
    def unload_model(self, model_id: str) -> bool:
        """
        Unload a model from the server.
        
        Args:
            model_id: ID of the model to unload.
            
        Returns:
            True if the model was unloaded, False otherwise.
            
        Raises:
            ModelServingError: If the model cannot be unloaded.
        """
        return self.model_server.unload_model(model_id)
    
    def predict(
        self,
        model_id: str,
        input_data: Dict[str, Any],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Perform synchronous inference with a model.
        
        Args:
            model_id: ID of the model to use.
            input_data: Dictionary containing the input data.
            use_cache: Whether to use the result cache.
            
        Returns:
            Dictionary containing the inference results.
            
        Raises:
            ModelServingError: If inference fails.
        """
        return self.model_server.predict(model_id, input_data, use_cache)
    
    def predict_async(
        self,
        model_id: str,
        input_data: Dict[str, Any],
        callback: Optional[Callable[[Dict[str, Any], Optional[str]], None]] = None,
        use_cache: bool = True
    ) -> str:
        """
        Perform asynchronous inference with a model.
        
        Args:
            model_id: ID of the model to use.
            input_data: Dictionary containing the input data.
            callback: Optional callback function to receive the result.
                     Takes two arguments: result and error message.
            use_cache: Whether to use the result cache.
            
        Returns:
            Request ID for tracking the request.
            
        Raises:
            ModelServingError: If the request cannot be queued.
        """
        return self.model_server.predict_async(model_id, input_data, callback, use_cache)
    
    def process_batch(
        self,
        model_id: str,
        batch: List[Dict[str, Any]],
        use_cache: bool = True,
        parallel: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of data with a model.
        
        Args:
            model_id: ID of the model to use.
            batch: List of input data dictionaries.
            use_cache: Whether to use the result cache.
            parallel: Whether to process in parallel.
            
        Returns:
            List of inference results.
            
        Raises:
            ModelServingError: If batch processing fails.
        """
        if parallel:
            return self.batch_processor.process_batch_parallel(model_id, batch, use_cache)
        else:
            return self.batch_processor.process_batch(model_id, batch, use_cache)
    
    def process_dataframe(
        self,
        model_id: str,
        df: 'pd.DataFrame',
        input_columns: List[str],
        output_column: str = 'prediction',
        use_cache: bool = True,
        parallel: bool = True
    ) -> 'pd.DataFrame':
        """
        Process a pandas DataFrame with a model.
        
        Args:
            model_id: ID of the model to use.
            df: DataFrame containing the data to process.
            input_columns: List of column names to use as input.
            output_column: Name of the column to store predictions.
            use_cache: Whether to use the result cache.
            parallel: Whether to process in parallel.
            
        Returns:
            DataFrame with predictions added as a new column.
            
        Raises:
            ModelServingError: If DataFrame processing fails.
        """
        return self.batch_processor.process_dataframe(
            model_id, df, input_columns, output_column, use_cache, parallel
        )
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get information about a loaded model.
        
        Args:
            model_id: ID of the model.
            
        Returns:
            Dictionary containing model information.
            
        Raises:
            ModelServingError: If the model is not found.
        """
        return self.model_server.get_model_info(model_id)
    
    def list_loaded_models(self) -> List[Dict[str, Any]]:
        """
        List all loaded models.
        
        Returns:
            List of dictionaries containing model information.
        """
        return self.model_server.list_loaded_models()
    
    def list_available_models(self) -> List[str]:
        """
        List all available models in the registry.
        
        Returns:
            List of model names.
        """
        return self.model_server.model_registry.list_models()
    
    def list_model_versions(self, model_name: str) -> List[str]:
        """
        List all versions for a model in the registry.
        
        Args:
            model_name: Name of the model.
            
        Returns:
            List of version strings.
            
        Raises:
            ModelServingError: If the model is not found.
        """
        try:
            return self.model_server.model_registry.list_versions(model_name)
        except Exception as e:
            error_msg = f"Error listing versions for model {model_name}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelServingError(error_msg)


def create_model_serving_api(
    registry_dir: str = "models",
    max_workers: int = 4,
    cache_size: int = 100
) -> ModelServingAPI:
    """
    Create a model serving API.
    
    This is a convenience function that creates a ModelServingAPI instance.
    
    Args:
        registry_dir: Directory for model registry.
        max_workers: Maximum number of worker threads for processing requests.
        cache_size: Size of the result cache.
        
    Returns:
        ModelServingAPI instance.
    """
    api = ModelServingAPI(
        registry_dir=registry_dir,
        max_workers=max_workers,
        cache_size=cache_size
    )
    api.start()
    return api


def example_model_serving():
    """
    Example of using model serving utilities.
    
    Returns:
        Dictionary with example results.
    """
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.datasets import make_regression
    import pandas as pd
    import tempfile
    import os
    
    # Create a temporary directory for models
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a synthetic regression dataset
        X, y = make_regression(n_samples=100, n_features=5, noise=0.1, random_state=42)
        
        # Train a scikit-learn model
        model = LinearRegression().fit(X, y)
        
        # Create a model registry and register the model
        from science_data_kit.core.utils.model_serialization import ModelRegistry
        registry = ModelRegistry(temp_dir)
        registry.register_model(model, "linear_regression")
        
        # Create a model serving API
        api = create_model_serving_api(registry_dir=temp_dir)
        
        # Load the model
        model_id = api.load_model("linear_regression")
        
        # Create a sample input
        input_data = {"features": X[0].tolist()}
        
        # Perform inference
        result = api.predict(model_id, input_data)
        
        # Create a batch of inputs
        batch = [{"features": x.tolist()} for x in X[:5]]
        
        # Process the batch
        batch_results = api.process_batch(model_id, batch)
        
        # Create a DataFrame
        df = pd.DataFrame(X[:5], columns=[f"feature_{i}" for i in range(5)])
        
        # Process the DataFrame
        df_result = api.process_dataframe(
            model_id,
            df,
            input_columns=[f"feature_{i}" for i in range(5)]
        )
        
        # Get model info
        model_info = api.get_model_info(model_id)
        
        # Stop the API
        api.stop()
        
        return {
            "model_id": model_id,
            "single_inference_result": result,
            "batch_inference_results": batch_results,
            "dataframe_inference_result": df_result["prediction"].tolist(),
            "model_info": model_info
        }
"""