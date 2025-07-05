"""
Machine Learning Model Serialization Utilities for Science Data Kit

This module provides utilities for serializing and deserializing machine learning models,
supporting different formats and frameworks. It includes functionality for model versioning,
metadata management, and model registry.
"""

import logging
import os
import json
import pickle
import time
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime
import shutil


class ModelSerializationError(Exception):
    """Exception raised for errors during model serialization or deserialization."""
    pass


class ModelSerializer:
    """
    Base class for serializing and deserializing machine learning models.
    
    This class provides methods for saving and loading models in various formats,
    with support for metadata and versioning.
    """
    
    def __init__(self, base_dir: str = "models"):
        """
        Initialize a model serializer.
        
        Args:
            base_dir: Base directory for storing models.
        """
        self.base_dir = base_dir
        self.logger = logging.getLogger(__name__)
        
        # Create base directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)
    
    def save_model(
        self,
        model: Any,
        model_name: str,
        model_format: str = "pickle",
        metadata: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Save a model to disk.
        
        Args:
            model: The model to save.
            model_name: Name of the model.
            model_format: Format to save the model in ("pickle", "joblib", "keras", "pytorch", "onnx").
            metadata: Optional metadata to save with the model.
            version: Optional version string. If None, a timestamp-based version is generated.
            **kwargs: Additional arguments for specific serialization methods.
            
        Returns:
            Path to the saved model.
            
        Raises:
            ModelSerializationError: If the model cannot be saved.
        """
        try:
            # Generate version if not provided
            if version is None:
                version = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create model directory
            model_dir = os.path.join(self.base_dir, model_name, version)
            os.makedirs(model_dir, exist_ok=True)
            
            # Save model based on format
            if model_format == "pickle":
                model_path = self._save_pickle(model, model_dir, **kwargs)
            elif model_format == "joblib":
                model_path = self._save_joblib(model, model_dir, **kwargs)
            elif model_format == "keras":
                model_path = self._save_keras(model, model_dir, **kwargs)
            elif model_format == "pytorch":
                model_path = self._save_pytorch(model, model_dir, **kwargs)
            elif model_format == "onnx":
                model_path = self._save_onnx(model, model_dir, **kwargs)
            else:
                raise ModelSerializationError(f"Unsupported model format: {model_format}")
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            # Add standard metadata
            metadata.update({
                "model_name": model_name,
                "model_format": model_format,
                "version": version,
                "timestamp": datetime.now().isoformat(),
                "model_path": os.path.relpath(model_path, model_dir)
            })
            
            # Add model type information if available
            if hasattr(model, "__class__"):
                metadata["model_type"] = model.__class__.__name__
            
            # Save metadata
            metadata_path = os.path.join(model_dir, "metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Model {model_name} (version {version}) saved to {model_path}")
            
            return model_path
        
        except Exception as e:
            error_msg = f"Error saving model {model_name}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def load_model(
        self,
        model_name: str,
        version: Optional[str] = None,
        model_format: Optional[str] = None,
        **kwargs
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Load a model from disk.
        
        Args:
            model_name: Name of the model to load.
            version: Version of the model to load. If None, loads the latest version.
            model_format: Format of the model. If None, determined from metadata.
            **kwargs: Additional arguments for specific deserialization methods.
            
        Returns:
            Tuple of (loaded model, metadata).
            
        Raises:
            ModelSerializationError: If the model cannot be loaded.
        """
        try:
            # Find model directory
            model_base_dir = os.path.join(self.base_dir, model_name)
            
            if not os.path.exists(model_base_dir):
                raise ModelSerializationError(f"Model {model_name} not found")
            
            # Get version directory
            if version is None:
                # Find latest version
                versions = [d for d in os.listdir(model_base_dir) 
                           if os.path.isdir(os.path.join(model_base_dir, d))]
                if not versions:
                    raise ModelSerializationError(f"No versions found for model {model_name}")
                
                # Sort versions (assuming timestamp-based versioning)
                versions.sort(reverse=True)
                version = versions[0]
            
            model_dir = os.path.join(model_base_dir, version)
            
            if not os.path.exists(model_dir):
                raise ModelSerializationError(f"Version {version} not found for model {model_name}")
            
            # Load metadata
            metadata_path = os.path.join(model_dir, "metadata.json")
            if not os.path.exists(metadata_path):
                raise ModelSerializationError(f"Metadata not found for model {model_name} version {version}")
            
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            
            # Determine model format
            if model_format is None:
                if "model_format" in metadata:
                    model_format = metadata["model_format"]
                else:
                    raise ModelSerializationError("Model format not specified and not found in metadata")
            
            # Get model path
            if "model_path" in metadata:
                model_rel_path = metadata["model_path"]
                model_path = os.path.join(model_dir, model_rel_path)
            else:
                # Try to find model file based on format
                if model_format == "pickle":
                    model_path = os.path.join(model_dir, "model.pkl")
                elif model_format == "joblib":
                    model_path = os.path.join(model_dir, "model.joblib")
                elif model_format == "keras":
                    model_path = os.path.join(model_dir, "model.keras")
                elif model_format == "pytorch":
                    model_path = os.path.join(model_dir, "model.pt")
                elif model_format == "onnx":
                    model_path = os.path.join(model_dir, "model.onnx")
                else:
                    raise ModelSerializationError(f"Unsupported model format: {model_format}")
            
            if not os.path.exists(model_path):
                raise ModelSerializationError(f"Model file not found at {model_path}")
            
            # Load model based on format
            if model_format == "pickle":
                model = self._load_pickle(model_path, **kwargs)
            elif model_format == "joblib":
                model = self._load_joblib(model_path, **kwargs)
            elif model_format == "keras":
                model = self._load_keras(model_path, **kwargs)
            elif model_format == "pytorch":
                model = self._load_pytorch(model_path, **kwargs)
            elif model_format == "onnx":
                model = self._load_onnx(model_path, **kwargs)
            else:
                raise ModelSerializationError(f"Unsupported model format: {model_format}")
            
            self.logger.info(f"Model {model_name} (version {version}) loaded from {model_path}")
            
            return model, metadata
        
        except Exception as e:
            error_msg = f"Error loading model {model_name}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def _save_pickle(self, model: Any, model_dir: str, **kwargs) -> str:
        """
        Save a model using pickle.
        
        Args:
            model: The model to save.
            model_dir: Directory to save the model in.
            **kwargs: Additional arguments for pickle.dump.
            
        Returns:
            Path to the saved model.
            
        Raises:
            ModelSerializationError: If the model cannot be saved.
        """
        try:
            model_path = os.path.join(model_dir, "model.pkl")
            
            # Extract pickle-specific kwargs
            protocol = kwargs.get("protocol", pickle.HIGHEST_PROTOCOL)
            
            with open(model_path, "wb") as f:
                pickle.dump(model, f, protocol=protocol)
            
            return model_path
        
        except Exception as e:
            error_msg = f"Error saving model with pickle: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def _load_pickle(self, model_path: str, **kwargs) -> Any:
        """
        Load a model using pickle.
        
        Args:
            model_path: Path to the model file.
            **kwargs: Additional arguments (not used).
            
        Returns:
            The loaded model.
            
        Raises:
            ModelSerializationError: If the model cannot be loaded.
        """
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            
            return model
        
        except Exception as e:
            error_msg = f"Error loading model with pickle: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def _save_joblib(self, model: Any, model_dir: str, **kwargs) -> str:
        """
        Save a model using joblib.
        
        Args:
            model: The model to save.
            model_dir: Directory to save the model in.
            **kwargs: Additional arguments for joblib.dump.
            
        Returns:
            Path to the saved model.
            
        Raises:
            ModelSerializationError: If the model cannot be saved.
        """
        try:
            import joblib
            
            model_path = os.path.join(model_dir, "model.joblib")
            
            # Extract joblib-specific kwargs
            compress = kwargs.get("compress", 3)
            
            joblib.dump(model, model_path, compress=compress)
            
            return model_path
        
        except ImportError:
            error_msg = "joblib not installed. Install it with 'pip install joblib'"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
        
        except Exception as e:
            error_msg = f"Error saving model with joblib: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def _load_joblib(self, model_path: str, **kwargs) -> Any:
        """
        Load a model using joblib.
        
        Args:
            model_path: Path to the model file.
            **kwargs: Additional arguments (not used).
            
        Returns:
            The loaded model.
            
        Raises:
            ModelSerializationError: If the model cannot be loaded.
        """
        try:
            import joblib
            
            model = joblib.load(model_path)
            
            return model
        
        except ImportError:
            error_msg = "joblib not installed. Install it with 'pip install joblib'"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
        
        except Exception as e:
            error_msg = f"Error loading model with joblib: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def _save_keras(self, model: Any, model_dir: str, **kwargs) -> str:
        """
        Save a Keras model.
        
        Args:
            model: The Keras model to save.
            model_dir: Directory to save the model in.
            **kwargs: Additional arguments for model.save.
            
        Returns:
            Path to the saved model.
            
        Raises:
            ModelSerializationError: If the model cannot be saved.
        """
        try:
            model_path = os.path.join(model_dir, "model.keras")
            
            # Save the model
            model.save(model_path, **kwargs)
            
            return model_path
        
        except Exception as e:
            error_msg = f"Error saving Keras model: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def _load_keras(self, model_path: str, **kwargs) -> Any:
        """
        Load a Keras model.
        
        Args:
            model_path: Path to the model file or directory.
            **kwargs: Additional arguments for keras.models.load_model.
            
        Returns:
            The loaded Keras model.
            
        Raises:
            ModelSerializationError: If the model cannot be loaded.
        """
        try:
            from tensorflow import keras
            
            model = keras.models.load_model(model_path, **kwargs)
            
            return model
        
        except ImportError:
            error_msg = "TensorFlow not installed. Install it with 'pip install tensorflow'"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
        
        except Exception as e:
            error_msg = f"Error loading Keras model: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def _save_pytorch(self, model: Any, model_dir: str, **kwargs) -> str:
        """
        Save a PyTorch model.
        
        Args:
            model: The PyTorch model to save.
            model_dir: Directory to save the model in.
            **kwargs: Additional arguments.
                save_weights_only: If True, save only the model weights.
            
        Returns:
            Path to the saved model.
            
        Raises:
            ModelSerializationError: If the model cannot be saved.
        """
        try:
            import torch
            
            model_path = os.path.join(model_dir, "model.pt")
            
            # Check if we should save only weights
            save_weights_only = kwargs.get("save_weights_only", False)
            
            if save_weights_only:
                torch.save(model.state_dict(), model_path)
            else:
                torch.save(model, model_path)
            
            return model_path
        
        except ImportError:
            error_msg = "PyTorch not installed. Install it with 'pip install torch'"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
        
        except Exception as e:
            error_msg = f"Error saving PyTorch model: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def _load_pytorch(self, model_path: str, **kwargs) -> Any:
        """
        Load a PyTorch model.
        
        Args:
            model_path: Path to the model file.
            **kwargs: Additional arguments.
                model_class: For loading weights only, the model class to instantiate.
                map_location: Device to load the model onto.
            
        Returns:
            The loaded PyTorch model.
            
        Raises:
            ModelSerializationError: If the model cannot be loaded.
        """
        try:
            import torch
            
            # Extract PyTorch-specific kwargs
            model_class = kwargs.get("model_class", None)
            map_location = kwargs.get("map_location", None)
            
            if model_class is not None:
                # Load weights into a new model instance
                model = model_class()
                model.load_state_dict(torch.load(model_path, map_location=map_location))
                model.eval()  # Set the model to evaluation mode
            else:
                # Load the entire model
                model = torch.load(model_path, map_location=map_location)
                if hasattr(model, "eval"):
                    model.eval()  # Set the model to evaluation mode
            
            return model
        
        except ImportError:
            error_msg = "PyTorch not installed. Install it with 'pip install torch'"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
        
        except Exception as e:
            error_msg = f"Error loading PyTorch model: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def _save_onnx(self, model: Any, model_dir: str, **kwargs) -> str:
        """
        Save a model in ONNX format.
        
        Args:
            model: The model to save.
            model_dir: Directory to save the model in.
            **kwargs: Additional arguments for onnx.save.
                input_sample: Sample input for tracing (required for PyTorch models).
                input_names: Names of input nodes.
                output_names: Names of output nodes.
                dynamic_axes: Dynamic axes for variable length inputs/outputs.
            
        Returns:
            Path to the saved model.
            
        Raises:
            ModelSerializationError: If the model cannot be saved.
        """
        try:
            import onnx
            
            model_path = os.path.join(model_dir, "model.onnx")
            
            # Check model type and convert accordingly
            if hasattr(model, "__module__") and "torch" in model.__module__:
                # PyTorch model
                import torch
                
                input_sample = kwargs.get("input_sample")
                if input_sample is None:
                    raise ModelSerializationError("input_sample is required for PyTorch models")
                
                input_names = kwargs.get("input_names", ["input"])
                output_names = kwargs.get("output_names", ["output"])
                dynamic_axes = kwargs.get("dynamic_axes", None)
                
                torch.onnx.export(
                    model,
                    input_sample,
                    model_path,
                    input_names=input_names,
                    output_names=output_names,
                    dynamic_axes=dynamic_axes,
                    export_params=True,
                    opset_version=kwargs.get("opset_version", 11),
                    do_constant_folding=True,
                    verbose=False
                )
            
            elif hasattr(model, "__module__") and ("keras" in model.__module__ or "tensorflow" in model.__module__):
                # Keras/TensorFlow model
                import tensorflow as tf
                
                input_signature = kwargs.get("input_signature")
                if input_signature is None:
                    raise ModelSerializationError("input_signature is required for TensorFlow models")
                
                # Create a concrete function from the model
                concrete_func = tf.function(lambda x: model(x)).get_concrete_function(input_signature)
                
                # Convert the model
                from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2
                frozen_func = convert_variables_to_constants_v2(concrete_func)
                
                # Save the model
                from tensorflow.python.saved_model import signature_constants
                from tensorflow.python.saved_model import tag_constants
                from tensorflow.python.saved_model.builder import SavedModelBuilder
                from tensorflow.python.saved_model.signature_def_utils import predict_signature_def
                from tensorflow.python.saved_model.signature_def_utils import build_signature_def
                from tensorflow.python.saved_model.utils import build_tensor_info
                
                # Create a temporary directory for the SavedModel
                import tempfile
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save the model
                    tf.saved_model.save(
                        model,
                        temp_dir,
                        signatures=concrete_func
                    )
                    
                    # Convert to ONNX
                    import tf2onnx
                    import tf2onnx.convert
                    
                    tf2onnx.convert.from_saved_model(
                        temp_dir,
                        output_path=model_path,
                        opset=kwargs.get("opset_version", 11)
                    )
            
            elif hasattr(model, "predict") and hasattr(model, "fit"):
                # Scikit-learn model
                from skl2onnx import convert_sklearn
                from skl2onnx.common.data_types import FloatTensorType
                
                # Get initial types
                initial_types = kwargs.get("initial_types")
                if initial_types is None:
                    # Try to infer from model
                    n_features = 1
                    if hasattr(model, "n_features_in_"):
                        n_features = model.n_features_in_
                    elif hasattr(model, "feature_importances_"):
                        n_features = len(model.feature_importances_)
                    
                    initial_types = [("input", FloatTensorType([None, n_features]))]
                
                # Convert the model
                onx = convert_sklearn(
                    model,
                    initial_types=initial_types,
                    target_opset=kwargs.get("opset_version", 11)
                )
                
                # Save the model
                with open(model_path, "wb") as f:
                    f.write(onx.SerializeToString())
            
            else:
                raise ModelSerializationError(f"Unsupported model type for ONNX conversion: {type(model)}")
            
            return model_path
        
        except ImportError as e:
            error_msg = f"Required package not installed: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
        
        except Exception as e:
            error_msg = f"Error saving model in ONNX format: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def _load_onnx(self, model_path: str, **kwargs) -> Any:
        """
        Load a model in ONNX format.
        
        Args:
            model_path: Path to the model file.
            **kwargs: Additional arguments.
                provider: ONNX Runtime execution provider.
            
        Returns:
            ONNX Runtime InferenceSession.
            
        Raises:
            ModelSerializationError: If the model cannot be loaded.
        """
        try:
            import onnxruntime as ort
            
            # Extract ONNX-specific kwargs
            provider = kwargs.get("provider", None)
            providers = kwargs.get("providers", None)
            
            if provider is not None:
                session = ort.InferenceSession(model_path, providers=[provider])
            elif providers is not None:
                session = ort.InferenceSession(model_path, providers=providers)
            else:
                session = ort.InferenceSession(model_path)
            
            return session
        
        except ImportError:
            error_msg = "ONNX Runtime not installed. Install it with 'pip install onnxruntime'"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
        
        except Exception as e:
            error_msg = f"Error loading ONNX model: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def list_models(self) -> List[str]:
        """
        List all available models.
        
        Returns:
            List of model names.
        """
        try:
            if not os.path.exists(self.base_dir):
                return []
            
            return [d for d in os.listdir(self.base_dir) 
                   if os.path.isdir(os.path.join(self.base_dir, d))]
        
        except Exception as e:
            error_msg = f"Error listing models: {str(e)}"
            self.logger.error(error_msg)
            return []
    
    def list_versions(self, model_name: str) -> List[str]:
        """
        List all available versions for a model.
        
        Args:
            model_name: Name of the model.
            
        Returns:
            List of version strings.
            
        Raises:
            ModelSerializationError: If the model is not found.
        """
        try:
            model_dir = os.path.join(self.base_dir, model_name)
            
            if not os.path.exists(model_dir):
                raise ModelSerializationError(f"Model {model_name} not found")
            
            versions = [d for d in os.listdir(model_dir) 
                       if os.path.isdir(os.path.join(model_dir, d))]
            
            # Sort versions (assuming timestamp-based versioning)
            versions.sort(reverse=True)
            
            return versions
        
        except Exception as e:
            if isinstance(e, ModelSerializationError):
                raise
            
            error_msg = f"Error listing versions for model {model_name}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def get_metadata(self, model_name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metadata for a model.
        
        Args:
            model_name: Name of the model.
            version: Version of the model. If None, gets metadata for the latest version.
            
        Returns:
            Dictionary of metadata.
            
        Raises:
            ModelSerializationError: If the model or metadata is not found.
        """
        try:
            # Find model directory
            model_base_dir = os.path.join(self.base_dir, model_name)
            
            if not os.path.exists(model_base_dir):
                raise ModelSerializationError(f"Model {model_name} not found")
            
            # Get version directory
            if version is None:
                # Find latest version
                versions = [d for d in os.listdir(model_base_dir) 
                           if os.path.isdir(os.path.join(model_base_dir, d))]
                if not versions:
                    raise ModelSerializationError(f"No versions found for model {model_name}")
                
                # Sort versions (assuming timestamp-based versioning)
                versions.sort(reverse=True)
                version = versions[0]
            
            model_dir = os.path.join(model_base_dir, version)
            
            if not os.path.exists(model_dir):
                raise ModelSerializationError(f"Version {version} not found for model {model_name}")
            
            # Load metadata
            metadata_path = os.path.join(model_dir, "metadata.json")
            if not os.path.exists(metadata_path):
                raise ModelSerializationError(f"Metadata not found for model {model_name} version {version}")
            
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            
            return metadata
        
        except Exception as e:
            if isinstance(e, ModelSerializationError):
                raise
            
            error_msg = f"Error getting metadata for model {model_name}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def delete_model(self, model_name: str, version: Optional[str] = None) -> bool:
        """
        Delete a model.
        
        Args:
            model_name: Name of the model to delete.
            version: Version of the model to delete. If None, deletes all versions.
            
        Returns:
            True if the model was deleted, False otherwise.
            
        Raises:
            ModelSerializationError: If the model cannot be deleted.
        """
        try:
            model_base_dir = os.path.join(self.base_dir, model_name)
            
            if not os.path.exists(model_base_dir):
                raise ModelSerializationError(f"Model {model_name} not found")
            
            if version is None:
                # Delete all versions
                shutil.rmtree(model_base_dir)
                self.logger.info(f"Model {model_name} (all versions) deleted")
            else:
                # Delete specific version
                version_dir = os.path.join(model_base_dir, version)
                
                if not os.path.exists(version_dir):
                    raise ModelSerializationError(f"Version {version} not found for model {model_name}")
                
                shutil.rmtree(version_dir)
                self.logger.info(f"Model {model_name} (version {version}) deleted")
                
                # Check if there are any versions left
                versions = [d for d in os.listdir(model_base_dir) 
                           if os.path.isdir(os.path.join(model_base_dir, d))]
                
                if not versions:
                    # No versions left, delete the model directory
                    shutil.rmtree(model_base_dir)
            
            return True
        
        except Exception as e:
            if isinstance(e, ModelSerializationError):
                raise
            
            error_msg = f"Error deleting model {model_name}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)


class ModelRegistry:
    """
    Registry for managing machine learning models.
    
    This class provides methods for registering, retrieving, and managing
    models in a centralized registry.
    """
    
    def __init__(self, base_dir: str = "models"):
        """
        Initialize a model registry.
        
        Args:
            base_dir: Base directory for storing models.
        """
        self.serializer = ModelSerializer(base_dir)
        self.logger = logging.getLogger(__name__)
    
    def register_model(
        self,
        model: Any,
        model_name: str,
        model_format: str = "pickle",
        metadata: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Register a model in the registry.
        
        Args:
            model: The model to register.
            model_name: Name of the model.
            model_format: Format to save the model in.
            metadata: Optional metadata to save with the model.
            version: Optional version string.
            **kwargs: Additional arguments for serialization.
            
        Returns:
            Path to the registered model.
            
        Raises:
            ModelSerializationError: If the model cannot be registered.
        """
        try:
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            # Add registry-specific metadata
            metadata.update({
                "registered_at": datetime.now().isoformat(),
                "registered_by": os.environ.get("USER", "unknown")
            })
            
            # Save the model
            model_path = self.serializer.save_model(
                model, model_name, model_format, metadata, version, **kwargs
            )
            
            self.logger.info(f"Model {model_name} registered in registry")
            
            return model_path
        
        except Exception as e:
            error_msg = f"Error registering model {model_name}: {str(e)}"
            self.logger.error(error_msg)
            raise ModelSerializationError(error_msg)
    
    def get_model(
        self,
        model_name: str,
        version: Optional[str] = None,
        model_format: Optional[str] = None,
        **kwargs
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Get a model from the registry.
        
        Args:
            model_name: Name of the model to get.
            version: Version of the model to get. If None, gets the latest version.
            model_format: Format of the model. If None, determined from metadata.
            **kwargs: Additional arguments for deserialization.
            
        Returns:
            Tuple of (model, metadata).
            
        Raises:
            ModelSerializationError: If the model cannot be retrieved.
        """
        return self.serializer.load_model(model_name, version, model_format, **kwargs)
    
    def list_models(self) -> List[str]:
        """
        List all models in the registry.
        
        Returns:
            List of model names.
        """
        return self.serializer.list_models()
    
    def list_versions(self, model_name: str) -> List[str]:
        """
        List all versions for a model in the registry.
        
        Args:
            model_name: Name of the model.
            
        Returns:
            List of version strings.
            
        Raises:
            ModelSerializationError: If the model is not found.
        """
        return self.serializer.list_versions(model_name)
    
    def get_metadata(self, model_name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metadata for a model in the registry.
        
        Args:
            model_name: Name of the model.
            version: Version of the model. If None, gets metadata for the latest version.
            
        Returns:
            Dictionary of metadata.
            
        Raises:
            ModelSerializationError: If the model or metadata is not found.
        """
        return self.serializer.get_metadata(model_name, version)
    
    def delete_model(self, model_name: str, version: Optional[str] = None) -> bool:
        """
        Delete a model from the registry.
        
        Args:
            model_name: Name of the model to delete.
            version: Version of the model to delete. If None, deletes all versions.
            
        Returns:
            True if the model was deleted, False otherwise.
            
        Raises:
            ModelSerializationError: If the model cannot be deleted.
        """
        return self.serializer.delete_model(model_name, version)


def save_model(
    model: Any,
    model_path: str,
    model_format: str = "pickle",
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs
) -> str:
    """
    Save a model to a file.
    
    This is a convenience function that creates a ModelSerializer and calls its save_model method.
    
    Args:
        model: The model to save.
        model_path: Path to save the model to.
        model_format: Format to save the model in.
        metadata: Optional metadata to save with the model.
        **kwargs: Additional arguments for serialization.
        
    Returns:
        Path to the saved model.
        
    Raises:
        ModelSerializationError: If the model cannot be saved.
    """
    try:
        # Extract directory and filename from path
        model_dir = os.path.dirname(model_path)
        model_name = os.path.basename(model_path).split(".")[0]
        
        # Create serializer with the parent directory
        serializer = ModelSerializer(model_dir)
        
        # Save the model
        return serializer.save_model(model, model_name, model_format, metadata, **kwargs)
    
    except Exception as e:
        error_msg = f"Error saving model to {model_path}: {str(e)}"
        logging.error(error_msg)
        raise ModelSerializationError(error_msg)


def load_model(
    model_path: str,
    model_format: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Load a model from a file.
    
    This is a convenience function that creates a ModelSerializer and calls its load_model method.
    
    Args:
        model_path: Path to the model file.
        model_format: Format of the model. If None, determined from file extension.
        **kwargs: Additional arguments for deserialization.
        
    Returns:
        The loaded model.
        
    Raises:
        ModelSerializationError: If the model cannot be loaded.
    """
    try:
        # Determine model format from file extension if not provided
        if model_format is None:
            ext = os.path.splitext(model_path)[1].lower()
            if ext == ".pkl":
                model_format = "pickle"
            elif ext == ".joblib":
                model_format = "joblib"
            elif ext == ".keras" or ext == ".h5":
                model_format = "keras"
            elif ext == ".pt" or ext == ".pth":
                model_format = "pytorch"
            elif ext == ".onnx":
                model_format = "onnx"
            else:
                raise ModelSerializationError(f"Could not determine model format from extension: {ext}")
        
        # Extract directory and filename from path
        model_dir = os.path.dirname(model_path)
        model_name = os.path.basename(model_path).split(".")[0]
        
        # Create serializer with the parent directory
        serializer = ModelSerializer(model_dir)
        
        # Load the model
        model, _ = serializer.load_model(model_name, None, model_format, **kwargs)
        
        return model
    
    except Exception as e:
        error_msg = f"Error loading model from {model_path}: {str(e)}"
        logging.error(error_msg)
        raise ModelSerializationError(error_msg)


def example_model_serialization():
    """
    Example of using model serialization utilities.
    
    Returns:
        Dictionary with example results.
    """
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.datasets import make_regression
    import tempfile
    import os
    
    # Create a temporary directory for models
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a synthetic regression dataset
        X, y = make_regression(n_samples=100, n_features=5, noise=0.1, random_state=42)
        
        # Train a scikit-learn model
        model = LinearRegression().fit(X, y)
        
        # Create a model registry
        registry = ModelRegistry(temp_dir)
        
        # Register the model
        metadata = {
            "description": "Example linear regression model",
            "features": 5,
            "dataset_size": 100,
            "random_state": 42
        }
        
        model_path = registry.register_model(
            model,
            "linear_regression",
            "pickle",
            metadata
        )
        
        # List models in the registry
        models = registry.list_models()
        
        # List versions for the model
        versions = registry.list_versions("linear_regression")
        
        # Get metadata for the model
        model_metadata = registry.get_metadata("linear_regression")
        
        # Get the model from the registry
        loaded_model, _ = registry.get_model("linear_regression")
        
        # Make predictions with the loaded model
        predictions = loaded_model.predict(X[:5])
        
        return {
            "model_type": "LinearRegression",
            "model_path": model_path,
            "models_in_registry": models,
            "model_versions": versions,
            "model_metadata": model_metadata,
            "predictions": predictions.tolist()
        }
"""