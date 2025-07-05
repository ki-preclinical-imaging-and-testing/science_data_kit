"""
Machine Learning Model Training Utilities for Science Data Kit

This module provides utilities for training machine learning models,
supporting different frameworks and model types. It integrates with
the streaming_processing and schema_validation modules to ensure
efficient and validated data processing during training.
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


class ModelTrainingError(Exception):
    """Exception raised for errors during model training."""
    pass


class ModelTrainer:
    """
    Base class for training machine learning models.
    
    This class provides methods for training models with support for
    different frameworks and model types. It handles data preprocessing,
    model configuration, training, and basic evaluation.
    """
    
    def __init__(
        self,
        model: Any,
        preprocessor: Optional[Callable[[Any], Any]] = None,
        postprocessor: Optional[Callable[[Any], Any]] = None,
        batch_size: int = 32,
        validation_split: float = 0.2,
        random_state: Optional[int] = None
    ):
        """
        Initialize a model trainer.
        
        Args:
            model: The machine learning model to train.
            preprocessor: Optional function to preprocess input data.
            postprocessor: Optional function to postprocess model outputs.
            batch_size: Size of batches for training.
            validation_split: Fraction of data to use for validation.
            random_state: Random seed for reproducibility.
        """
        self.model = model
        self.preprocessor = preprocessor
        self.postprocessor = postprocessor
        self.batch_size = batch_size
        self.validation_split = validation_split
        self.random_state = random_state
        self.logger = logging.getLogger(__name__)
        self.training_history: Dict[str, List[float]] = {}
        
    def preprocess_data(self, X: Any, y: Any) -> Tuple[Any, Any]:
        """
        Preprocess training data.
        
        Args:
            X: Features.
            y: Target values.
            
        Returns:
            Tuple of preprocessed features and target values.
        """
        if self.preprocessor:
            return self.preprocessor(X), y
        return X, y
    
    def postprocess_output(self, output: Any) -> Any:
        """
        Postprocess model output.
        
        Args:
            output: Model output.
            
        Returns:
            Postprocessed output.
        """
        if self.postprocessor:
            return self.postprocessor(output)
        return output
    
    def train(self, X: Any, y: Any, **kwargs) -> Any:
        """
        Train the model.
        
        Args:
            X: Features.
            y: Target values.
            **kwargs: Additional arguments to pass to the model's fit method.
            
        Returns:
            The trained model.
            
        Raises:
            ModelTrainingError: If training fails.
        """
        try:
            # Preprocess data
            X_processed, y_processed = self.preprocess_data(X, y)
            
            # Train the model
            start_time = time.time()
            
            if hasattr(self.model, 'fit'):
                self.model.fit(X_processed, y_processed, **kwargs)
            else:
                raise ModelTrainingError("Model does not have a fit method")
            
            training_time = time.time() - start_time
            self.logger.info(f"Model training completed in {training_time:.2f} seconds")
            
            return self.model
        
        except Exception as e:
            error_msg = f"Error during model training: {str(e)}"
            self.logger.error(error_msg)
            raise ModelTrainingError(error_msg)
    
    def evaluate(self, X: Any, y: Any) -> Dict[str, float]:
        """
        Evaluate the model.
        
        Args:
            X: Features.
            y: Target values.
            
        Returns:
            Dictionary of evaluation metrics.
            
        Raises:
            ModelTrainingError: If evaluation fails.
        """
        try:
            # Preprocess data
            X_processed, y_processed = self.preprocess_data(X, y)
            
            # Evaluate the model
            if hasattr(self.model, 'score'):
                score = self.model.score(X_processed, y_processed)
                return {'score': score}
            elif hasattr(self.model, 'evaluate'):
                metrics = self.model.evaluate(X_processed, y_processed)
                if isinstance(metrics, list) and hasattr(self.model, 'metrics_names'):
                    return {name: value for name, value in zip(self.model.metrics_names, metrics)}
                return {'score': metrics}
            else:
                # Make predictions and calculate basic metrics
                if hasattr(self.model, 'predict'):
                    y_pred = self.model.predict(X_processed)
                elif callable(self.model):
                    y_pred = self.model(X_processed)
                else:
                    raise ModelTrainingError("Model does not have a predict method and is not callable")
                
                # Calculate mean squared error for regression or accuracy for classification
                try:
                    from sklearn.metrics import mean_squared_error, accuracy_score
                    
                    # Try regression metric
                    try:
                        mse = mean_squared_error(y_processed, y_pred)
                        return {'mean_squared_error': mse}
                    except:
                        # Try classification metric
                        try:
                            acc = accuracy_score(y_processed, y_pred)
                            return {'accuracy': acc}
                        except:
                            return {'evaluation_error': 'Could not calculate metrics'}
                except ImportError:
                    return {'evaluation_error': 'scikit-learn not available for metrics calculation'}
        
        except Exception as e:
            error_msg = f"Error during model evaluation: {str(e)}"
            self.logger.error(error_msg)
            raise ModelTrainingError(error_msg)
    
    def train_with_validation(
        self,
        X: Any,
        y: Any,
        validation_data: Optional[Tuple[Any, Any]] = None,
        **kwargs
    ) -> Tuple[Any, Dict[str, float]]:
        """
        Train the model with validation.
        
        Args:
            X: Features.
            y: Target values.
            validation_data: Optional tuple of (X_val, y_val) for validation.
                            If None, uses validation_split to create validation data.
            **kwargs: Additional arguments to pass to the model's fit method.
            
        Returns:
            Tuple of (trained model, validation metrics).
            
        Raises:
            ModelTrainingError: If training fails.
        """
        try:
            # Split data if validation_data is not provided
            if validation_data is None and self.validation_split > 0:
                try:
                    from sklearn.model_selection import train_test_split
                    
                    X_train, X_val, y_train, y_val = train_test_split(
                        X, y, test_size=self.validation_split, random_state=self.random_state
                    )
                    validation_data = (X_val, y_val)
                except ImportError:
                    self.logger.warning("scikit-learn not available for train_test_split, using all data for training")
                    X_train, y_train = X, y
            else:
                X_train, y_train = X, y
            
            # Train the model
            self.train(X_train, y_train, **kwargs)
            
            # Evaluate on validation data if available
            if validation_data is not None:
                X_val, y_val = validation_data
                validation_metrics = self.evaluate(X_val, y_val)
                self.logger.info(f"Validation metrics: {validation_metrics}")
                return self.model, validation_metrics
            
            return self.model, {}
        
        except Exception as e:
            error_msg = f"Error during model training with validation: {str(e)}"
            self.logger.error(error_msg)
            raise ModelTrainingError(error_msg)


class SklearnModelTrainer(ModelTrainer):
    """
    Trainer for scikit-learn models.
    
    This class extends ModelTrainer with scikit-learn specific functionality,
    including support for grid search, cross-validation, and scikit-learn pipelines.
    """
    
    def __init__(
        self,
        model: Any,
        preprocessor: Optional[Callable[[Any], Any]] = None,
        postprocessor: Optional[Callable[[Any], Any]] = None,
        batch_size: int = 32,
        validation_split: float = 0.2,
        random_state: Optional[int] = None
    ):
        """
        Initialize a scikit-learn model trainer.
        
        Args:
            model: The scikit-learn model to train.
            preprocessor: Optional function to preprocess input data.
            postprocessor: Optional function to postprocess model outputs.
            batch_size: Size of batches for training.
            validation_split: Fraction of data to use for validation.
            random_state: Random seed for reproducibility.
        """
        super().__init__(model, preprocessor, postprocessor, batch_size, validation_split, random_state)
    
    def grid_search(
        self,
        X: Any,
        y: Any,
        param_grid: Dict[str, List[Any]],
        cv: int = 5,
        scoring: Optional[str] = None
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Perform grid search for hyperparameter tuning.
        
        Args:
            X: Features.
            y: Target values.
            param_grid: Dictionary with parameters names as keys and lists of parameter values.
            cv: Number of cross-validation folds.
            scoring: Scoring method to use.
            
        Returns:
            Tuple of (best model, grid search results).
            
        Raises:
            ModelTrainingError: If grid search fails.
        """
        try:
            from sklearn.model_selection import GridSearchCV
            
            # Preprocess data
            X_processed, y_processed = self.preprocess_data(X, y)
            
            # Create grid search
            grid_search = GridSearchCV(
                self.model,
                param_grid,
                cv=cv,
                scoring=scoring,
                n_jobs=-1,
                verbose=1
            )
            
            # Perform grid search
            start_time = time.time()
            grid_search.fit(X_processed, y_processed)
            search_time = time.time() - start_time
            
            # Log results
            self.logger.info(f"Grid search completed in {search_time:.2f} seconds")
            self.logger.info(f"Best parameters: {grid_search.best_params_}")
            self.logger.info(f"Best score: {grid_search.best_score_}")
            
            # Update model with best estimator
            self.model = grid_search.best_estimator_
            
            return self.model, {
                'best_params': grid_search.best_params_,
                'best_score': grid_search.best_score_,
                'cv_results': grid_search.cv_results_
            }
        
        except Exception as e:
            error_msg = f"Error during grid search: {str(e)}"
            self.logger.error(error_msg)
            raise ModelTrainingError(error_msg)
    
    def cross_validate(
        self,
        X: Any,
        y: Any,
        cv: int = 5,
        scoring: Optional[Union[str, List[str]]] = None
    ) -> Dict[str, List[float]]:
        """
        Perform cross-validation.
        
        Args:
            X: Features.
            y: Target values.
            cv: Number of cross-validation folds.
            scoring: Scoring method(s) to use.
            
        Returns:
            Dictionary of cross-validation results.
            
        Raises:
            ModelTrainingError: If cross-validation fails.
        """
        try:
            from sklearn.model_selection import cross_validate
            
            # Preprocess data
            X_processed, y_processed = self.preprocess_data(X, y)
            
            # Perform cross-validation
            start_time = time.time()
            cv_results = cross_validate(
                self.model,
                X_processed,
                y_processed,
                cv=cv,
                scoring=scoring,
                n_jobs=-1,
                return_train_score=True
            )
            cv_time = time.time() - start_time
            
            # Log results
            self.logger.info(f"Cross-validation completed in {cv_time:.2f} seconds")
            
            # Format results
            formatted_results = {}
            for key, values in cv_results.items():
                if isinstance(values, np.ndarray):
                    formatted_results[key] = values.tolist()
                else:
                    formatted_results[key] = values
            
            return formatted_results
        
        except Exception as e:
            error_msg = f"Error during cross-validation: {str(e)}"
            self.logger.error(error_msg)
            raise ModelTrainingError(error_msg)


class KerasModelTrainer(ModelTrainer):
    """
    Trainer for Keras models.
    
    This class extends ModelTrainer with Keras specific functionality,
    including support for callbacks, early stopping, and model checkpointing.
    """
    
    def __init__(
        self,
        model: Any,
        preprocessor: Optional[Callable[[Any], Any]] = None,
        postprocessor: Optional[Callable[[Any], Any]] = None,
        batch_size: int = 32,
        validation_split: float = 0.2,
        random_state: Optional[int] = None
    ):
        """
        Initialize a Keras model trainer.
        
        Args:
            model: The Keras model to train.
            preprocessor: Optional function to preprocess input data.
            postprocessor: Optional function to postprocess model outputs.
            batch_size: Size of batches for training.
            validation_split: Fraction of data to use for validation.
            random_state: Random seed for reproducibility.
        """
        super().__init__(model, preprocessor, postprocessor, batch_size, validation_split, random_state)
    
    def train(
        self,
        X: Any,
        y: Any,
        epochs: int = 10,
        callbacks: Optional[List[Any]] = None,
        **kwargs
    ) -> Any:
        """
        Train the Keras model.
        
        Args:
            X: Features.
            y: Target values.
            epochs: Number of epochs to train for.
            callbacks: List of Keras callbacks.
            **kwargs: Additional arguments to pass to the model's fit method.
            
        Returns:
            The trained model.
            
        Raises:
            ModelTrainingError: If training fails.
        """
        try:
            # Preprocess data
            X_processed, y_processed = self.preprocess_data(X, y)
            
            # Set default kwargs
            kwargs.setdefault('batch_size', self.batch_size)
            kwargs.setdefault('epochs', epochs)
            kwargs.setdefault('verbose', 1)
            
            # If validation_split is not in kwargs and validation_data is not provided,
            # use the validation_split from the constructor
            if 'validation_split' not in kwargs and 'validation_data' not in kwargs:
                kwargs['validation_split'] = self.validation_split
            
            # Train the model
            start_time = time.time()
            history = self.model.fit(X_processed, y_processed, callbacks=callbacks, **kwargs)
            training_time = time.time() - start_time
            
            # Store training history
            self.training_history = {key: values for key, values in history.history.items()}
            
            self.logger.info(f"Keras model training completed in {training_time:.2f} seconds")
            
            return self.model
        
        except Exception as e:
            error_msg = f"Error during Keras model training: {str(e)}"
            self.logger.error(error_msg)
            raise ModelTrainingError(error_msg)
    
    def create_callbacks(
        self,
        checkpoint_path: Optional[str] = None,
        early_stopping: bool = True,
        patience: int = 10,
        tensorboard_log_dir: Optional[str] = None
    ) -> List[Any]:
        """
        Create common Keras callbacks.
        
        Args:
            checkpoint_path: Path to save model checkpoints.
            early_stopping: Whether to use early stopping.
            patience: Number of epochs with no improvement after which training will be stopped.
            tensorboard_log_dir: Directory for TensorBoard logs.
            
        Returns:
            List of Keras callbacks.
            
        Raises:
            ModelTrainingError: If callback creation fails.
        """
        try:
            from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard
            
            callbacks = []
            
            # Model checkpoint
            if checkpoint_path:
                os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
                checkpoint = ModelCheckpoint(
                    checkpoint_path,
                    monitor='val_loss',
                    save_best_only=True,
                    save_weights_only=False,
                    verbose=1
                )
                callbacks.append(checkpoint)
            
            # Early stopping
            if early_stopping:
                early_stop = EarlyStopping(
                    monitor='val_loss',
                    patience=patience,
                    verbose=1,
                    restore_best_weights=True
                )
                callbacks.append(early_stop)
            
            # TensorBoard
            if tensorboard_log_dir:
                os.makedirs(tensorboard_log_dir, exist_ok=True)
                tensorboard = TensorBoard(
                    log_dir=tensorboard_log_dir,
                    histogram_freq=1,
                    write_graph=True,
                    write_images=True,
                    update_freq='epoch'
                )
                callbacks.append(tensorboard)
            
            return callbacks
        
        except Exception as e:
            error_msg = f"Error creating Keras callbacks: {str(e)}"
            self.logger.error(error_msg)
            raise ModelTrainingError(error_msg)


class PyTorchModelTrainer(ModelTrainer):
    """
    Trainer for PyTorch models.
    
    This class extends ModelTrainer with PyTorch specific functionality,
    including support for optimizers, loss functions, and training loops.
    """
    
    def __init__(
        self,
        model: Any,
        loss_fn: Any,
        optimizer: Any,
        preprocessor: Optional[Callable[[Any], Any]] = None,
        postprocessor: Optional[Callable[[Any], Any]] = None,
        batch_size: int = 32,
        validation_split: float = 0.2,
        random_state: Optional[int] = None,
        device: Optional[str] = None
    ):
        """
        Initialize a PyTorch model trainer.
        
        Args:
            model: The PyTorch model to train.
            loss_fn: The loss function to use.
            optimizer: The optimizer to use.
            preprocessor: Optional function to preprocess input data.
            postprocessor: Optional function to postprocess model outputs.
            batch_size: Size of batches for training.
            validation_split: Fraction of data to use for validation.
            random_state: Random seed for reproducibility.
            device: Device to use for training ('cpu' or 'cuda').
        """
        super().__init__(model, preprocessor, postprocessor, batch_size, validation_split, random_state)
        self.loss_fn = loss_fn
        self.optimizer = optimizer
        
        # Set device
        try:
            import torch
            self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
            self.model = self.model.to(self.device)
        except ImportError:
            self.logger.warning("PyTorch not available, using CPU")
            self.device = 'cpu'
    
    def train(
        self,
        X: Any,
        y: Any,
        epochs: int = 10,
        **kwargs
    ) -> Any:
        """
        Train the PyTorch model.
        
        Args:
            X: Features.
            y: Target values.
            epochs: Number of epochs to train for.
            **kwargs: Additional arguments (not used).
            
        Returns:
            The trained model.
            
        Raises:
            ModelTrainingError: If training fails.
        """
        try:
            import torch
            from torch.utils.data import TensorDataset, DataLoader
            
            # Preprocess data
            X_processed, y_processed = self.preprocess_data(X, y)
            
            # Convert to PyTorch tensors if needed
            if not isinstance(X_processed, torch.Tensor):
                X_tensor = torch.tensor(X_processed, dtype=torch.float32, device=self.device)
            else:
                X_tensor = X_processed.to(self.device)
            
            if not isinstance(y_processed, torch.Tensor):
                y_tensor = torch.tensor(y_processed, dtype=torch.float32, device=self.device)
            else:
                y_tensor = y_processed.to(self.device)
            
            # Create dataset and dataloader
            dataset = TensorDataset(X_tensor, y_tensor)
            dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
            
            # Training loop
            start_time = time.time()
            self.model.train()
            
            for epoch in range(epochs):
                epoch_loss = 0.0
                for batch_X, batch_y in dataloader:
                    # Zero gradients
                    self.optimizer.zero_grad()
                    
                    # Forward pass
                    outputs = self.model(batch_X)
                    loss = self.loss_fn(outputs, batch_y)
                    
                    # Backward pass and optimize
                    loss.backward()
                    self.optimizer.step()
                    
                    epoch_loss += loss.item()
                
                # Log progress
                avg_loss = epoch_loss / len(dataloader)
                self.logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
                
                # Store in training history
                if 'loss' not in self.training_history:
                    self.training_history['loss'] = []
                self.training_history['loss'].append(avg_loss)
            
            training_time = time.time() - start_time
            self.logger.info(f"PyTorch model training completed in {training_time:.2f} seconds")
            
            return self.model
        
        except Exception as e:
            error_msg = f"Error during PyTorch model training: {str(e)}"
            self.logger.error(error_msg)
            raise ModelTrainingError(error_msg)
    
    def evaluate(self, X: Any, y: Any) -> Dict[str, float]:
        """
        Evaluate the PyTorch model.
        
        Args:
            X: Features.
            y: Target values.
            
        Returns:
            Dictionary of evaluation metrics.
            
        Raises:
            ModelTrainingError: If evaluation fails.
        """
        try:
            import torch
            from torch.utils.data import TensorDataset, DataLoader
            
            # Preprocess data
            X_processed, y_processed = self.preprocess_data(X, y)
            
            # Convert to PyTorch tensors if needed
            if not isinstance(X_processed, torch.Tensor):
                X_tensor = torch.tensor(X_processed, dtype=torch.float32, device=self.device)
            else:
                X_tensor = X_processed.to(self.device)
            
            if not isinstance(y_processed, torch.Tensor):
                y_tensor = torch.tensor(y_processed, dtype=torch.float32, device=self.device)
            else:
                y_tensor = y_processed.to(self.device)
            
            # Create dataset and dataloader
            dataset = TensorDataset(X_tensor, y_tensor)
            dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)
            
            # Evaluation loop
            self.model.eval()
            total_loss = 0.0
            
            with torch.no_grad():
                for batch_X, batch_y in dataloader:
                    outputs = self.model(batch_X)
                    loss = self.loss_fn(outputs, batch_y)
                    total_loss += loss.item()
            
            avg_loss = total_loss / len(dataloader)
            
            return {'loss': avg_loss}
        
        except Exception as e:
            error_msg = f"Error during PyTorch model evaluation: {str(e)}"
            self.logger.error(error_msg)
            raise ModelTrainingError(error_msg)


def train_model(
    model: Any,
    X: Any,
    y: Any,
    model_type: str = 'sklearn',
    **kwargs
) -> Tuple[Any, Dict[str, Any]]:
    """
    Train a machine learning model.
    
    This is a convenience function that creates the appropriate ModelTrainer
    and calls its train method.
    
    Args:
        model: The machine learning model to train.
        X: Features.
        y: Target values.
        model_type: Type of model ('sklearn', 'keras', or 'pytorch').
        **kwargs: Additional arguments to pass to the trainer and train method.
        
    Returns:
        Tuple of (trained model, training results).
        
    Raises:
        ModelTrainingError: If training fails.
    """
    try:
        # Extract trainer kwargs
        trainer_kwargs = {
            'preprocessor': kwargs.pop('preprocessor', None),
            'postprocessor': kwargs.pop('postprocessor', None),
            'batch_size': kwargs.pop('batch_size', 32),
            'validation_split': kwargs.pop('validation_split', 0.2),
            'random_state': kwargs.pop('random_state', None)
        }
        
        # Create appropriate trainer
        if model_type == 'sklearn':
            trainer = SklearnModelTrainer(model, **trainer_kwargs)
            
            # Check for grid search
            if 'param_grid' in kwargs:
                param_grid = kwargs.pop('param_grid')
                cv = kwargs.pop('cv', 5)
                scoring = kwargs.pop('scoring', None)
                
                model, results = trainer.grid_search(X, y, param_grid, cv, scoring)
                return model, results
            
            # Check for cross-validation
            if kwargs.pop('cross_validate', False):
                cv = kwargs.pop('cv', 5)
                scoring = kwargs.pop('scoring', None)
                
                results = trainer.cross_validate(X, y, cv, scoring)
                return model, results
            
        elif model_type == 'keras':
            trainer = KerasModelTrainer(model, **trainer_kwargs)
            
            # Create callbacks if specified
            if kwargs.pop('use_callbacks', False):
                callbacks = trainer.create_callbacks(
                    checkpoint_path=kwargs.pop('checkpoint_path', None),
                    early_stopping=kwargs.pop('early_stopping', True),
                    patience=kwargs.pop('patience', 10),
                    tensorboard_log_dir=kwargs.pop('tensorboard_log_dir', None)
                )
                kwargs['callbacks'] = callbacks
            
        elif model_type == 'pytorch':
            # Extract PyTorch specific kwargs
            loss_fn = kwargs.pop('loss_fn')
            optimizer = kwargs.pop('optimizer')
            device = kwargs.pop('device', None)
            
            trainer = PyTorchModelTrainer(
                model, loss_fn, optimizer, device=device, **trainer_kwargs
            )
            
        else:
            raise ModelTrainingError(f"Unsupported model type: {model_type}")
        
        # Train with validation
        if kwargs.pop('use_validation', True):
            validation_data = kwargs.pop('validation_data', None)
            model, validation_metrics = trainer.train_with_validation(X, y, validation_data, **kwargs)
            
            return model, {
                'validation_metrics': validation_metrics,
                'training_history': trainer.training_history
            }
        
        # Train without validation
        trainer.train(X, y, **kwargs)
        
        return model, {
            'training_history': trainer.training_history
        }
    
    except Exception as e:
        if isinstance(e, ModelTrainingError):
            raise
        
        error_msg = f"Error during model training: {str(e)}"
        logging.error(error_msg)
        raise ModelTrainingError(error_msg)


def example_model_training():
    """
    Example of using model training utilities.
    
    Returns:
        Dictionary with example results.
    """
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.datasets import make_regression
    
    # Create a synthetic regression dataset
    X, y = make_regression(n_samples=100, n_features=5, noise=0.1, random_state=42)
    
    # Split into train and test sets
    X_train, X_test = X[:80], X[80:]
    y_train, y_test = y[:80], y[80:]
    
    # Train a scikit-learn model
    model, results = train_model(
        LinearRegression(),
        X_train,
        y_train,
        model_type='sklearn',
        use_validation=True
    )
    
    # Evaluate on test set
    trainer = SklearnModelTrainer(model)
    test_metrics = trainer.evaluate(X_test, y_test)
    
    return {
        'model_type': 'LinearRegression',
        'training_results': results,
        'test_metrics': test_metrics,
        'model_params': {
            'coef': model.coef_.tolist(),
            'intercept': float(model.intercept_)
        }
    }
"""