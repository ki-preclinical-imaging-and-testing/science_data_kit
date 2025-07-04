"""
# Scikit-learn Integration Module for Science Data Kit

This module provides integration between Science Data Kit and scikit-learn for machine learning.
It includes functions for data preparation, model training, model evaluation, and model persistence.

## Features
- Data preparation utilities for scikit-learn
- Model training utilities
- Model evaluation utilities
- Model persistence utilities
- Integration with Neo4j for storing model metadata

## Usage
```python
from science_data_kit.core.analysis.sklearn_integration import (
    prepare_data,
    train_model,
    evaluate_model,
    save_model,
    load_model
)

# Prepare data for machine learning
X_train, X_test, y_train, y_test = prepare_data(df, target_column='target', test_size=0.2)

# Train a model
model = train_model(X_train, y_train, model_type='random_forest')

# Evaluate the model
metrics = evaluate_model(model, X_test, y_test)

# Save the model
save_model(model, 'model.pkl')

# Load the model
model = load_model('model.pkl')
```
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Union, Callable
import logging
import joblib
import os
from ..db.db_manager import DBManager

logger = logging.getLogger(__name__)

def prepare_data(
    df: pd.DataFrame,
    target_column: str,
    feature_columns: Optional[List[str]] = None,
    test_size: float = 0.2,
    random_state: int = 42,
    stratify: bool = False
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Prepare data for machine learning by splitting it into training and testing sets.

    Args:
        df: The pandas DataFrame containing the data.
        target_column: The name of the column containing the target variable.
        feature_columns: The names of the columns containing the features. If None, all columns except the target column will be used.
        test_size: The proportion of the data to include in the test split.
        random_state: Random state for reproducibility.
        stratify: Whether to stratify the split based on the target variable.

    Returns:
        A tuple containing:
        - X_train: Training features.
        - X_test: Testing features.
        - y_train: Training target.
        - y_test: Testing target.
    """
    try:
        from sklearn.model_selection import train_test_split

        # Determine feature columns
        if feature_columns is None:
            feature_columns = [col for col in df.columns if col != target_column]

        # Extract features and target
        X = df[feature_columns].values
        y = df[target_column].values

        # Split the data
        if stratify and len(np.unique(y)) > 1:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )

        return X_train, X_test, y_train, y_test
    except Exception as e:
        logger.error(f"Error preparing data: {str(e)}")
        raise

def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    model_type: str = 'random_forest',
    model_params: Optional[Dict[str, Any]] = None,
    custom_model: Optional[Any] = None
) -> Any:
    """
    Train a machine learning model.

    Args:
        X_train: Training features.
        y_train: Training target.
        model_type: The type of model to train (random_forest, svm, logistic_regression, etc.).
        model_params: Parameters for the model.
        custom_model: A custom model to use instead of the built-in models.

    Returns:
        The trained model.
    """
    try:
        if custom_model is not None:
            model = custom_model
        else:
            if model_params is None:
                model_params = {}

            if model_type == 'random_forest':
                from sklearn.ensemble import RandomForestClassifier
                model = RandomForestClassifier(**model_params)
            elif model_type == 'svm':
                from sklearn.svm import SVC
                model = SVC(**model_params)
            elif model_type == 'logistic_regression':
                from sklearn.linear_model import LogisticRegression
                model = LogisticRegression(**model_params)
            elif model_type == 'decision_tree':
                from sklearn.tree import DecisionTreeClassifier
                model = DecisionTreeClassifier(**model_params)
            elif model_type == 'gradient_boosting':
                from sklearn.ensemble import GradientBoostingClassifier
                model = GradientBoostingClassifier(**model_params)
            elif model_type == 'knn':
                from sklearn.neighbors import KNeighborsClassifier
                model = KNeighborsClassifier(**model_params)
            elif model_type == 'linear_regression':
                from sklearn.linear_model import LinearRegression
                model = LinearRegression(**model_params)
            elif model_type == 'ridge_regression':
                from sklearn.linear_model import Ridge
                model = Ridge(**model_params)
            elif model_type == 'lasso_regression':
                from sklearn.linear_model import Lasso
                model = Lasso(**model_params)
            elif model_type == 'elastic_net':
                from sklearn.linear_model import ElasticNet
                model = ElasticNet(**model_params)
            elif model_type == 'random_forest_regressor':
                from sklearn.ensemble import RandomForestRegressor
                model = RandomForestRegressor(**model_params)
            elif model_type == 'gradient_boosting_regressor':
                from sklearn.ensemble import GradientBoostingRegressor
                model = GradientBoostingRegressor(**model_params)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")

        # Train the model
        model.fit(X_train, y_train)

        return model
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise

def evaluate_model(
    model: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
    metrics: Optional[List[str]] = None,
    is_classifier: Optional[bool] = None
) -> Dict[str, float]:
    """
    Evaluate a machine learning model.

    Args:
        model: The trained model to evaluate.
        X_test: Testing features.
        y_test: Testing target.
        metrics: The metrics to use for evaluation. If None, default metrics will be used.
        is_classifier: Whether the model is a classifier. If None, it will be inferred.

    Returns:
        A dictionary containing the evaluation metrics.
    """
    try:
        from sklearn import metrics as sk_metrics

        # Determine if the model is a classifier
        if is_classifier is None:
            try:
                is_classifier = hasattr(model, 'predict_proba')
            except:
                is_classifier = False

        # Make predictions
        y_pred = model.predict(X_test)

        # Calculate metrics
        results = {}

        if is_classifier:
            if metrics is None:
                metrics = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']

            for metric in metrics:
                if metric == 'accuracy':
                    results['accuracy'] = sk_metrics.accuracy_score(y_test, y_pred)
                elif metric == 'precision':
                    results['precision'] = sk_metrics.precision_score(y_test, y_pred, average='weighted')
                elif metric == 'recall':
                    results['recall'] = sk_metrics.recall_score(y_test, y_pred, average='weighted')
                elif metric == 'f1':
                    results['f1'] = sk_metrics.f1_score(y_test, y_pred, average='weighted')
                elif metric == 'roc_auc':
                    try:
                        y_prob = model.predict_proba(X_test)
                        if len(np.unique(y_test)) == 2:  # Binary classification
                            results['roc_auc'] = sk_metrics.roc_auc_score(y_test, y_prob[:, 1])
                        else:  # Multi-class classification
                            results['roc_auc'] = sk_metrics.roc_auc_score(y_test, y_prob, multi_class='ovr')
                    except:
                        logger.warning("ROC AUC could not be calculated")
                elif metric == 'confusion_matrix':
                    results['confusion_matrix'] = sk_metrics.confusion_matrix(y_test, y_pred).tolist()
                elif metric == 'classification_report':
                    results['classification_report'] = sk_metrics.classification_report(y_test, y_pred)
        else:
            if metrics is None:
                metrics = ['mse', 'rmse', 'mae', 'r2']

            for metric in metrics:
                if metric == 'mse':
                    results['mse'] = sk_metrics.mean_squared_error(y_test, y_pred)
                elif metric == 'rmse':
                    results['rmse'] = np.sqrt(sk_metrics.mean_squared_error(y_test, y_pred))
                elif metric == 'mae':
                    results['mae'] = sk_metrics.mean_absolute_error(y_test, y_pred)
                elif metric == 'r2':
                    results['r2'] = sk_metrics.r2_score(y_test, y_pred)

        return results
    except Exception as e:
        logger.error(f"Error evaluating model: {str(e)}")
        return {}

def save_model(
    model: Any,
    file_path: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str]:
    """
    Save a machine learning model to a file.

    Args:
        model: The trained model to save.
        file_path: The path to save the model.
        metadata: Additional metadata to save with the model.

    Returns:
        A tuple containing:
        - A boolean indicating success or failure.
        - A message describing the result.
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        # Save the model
        joblib.dump(model, file_path)

        # Save metadata if provided
        if metadata is not None:
            metadata_path = f"{os.path.splitext(file_path)[0]}_metadata.json"
            import json
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)

        return True, f"Model saved to {file_path}"
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        return False, f"Error saving model: {str(e)}"

def load_model(file_path: str) -> Tuple[bool, Union[Any, str]]:
    """
    Load a machine learning model from a file.

    Args:
        file_path: The path to the model file.

    Returns:
        A tuple containing:
        - A boolean indicating success or failure.
        - The loaded model or an error message.
    """
    try:
        model = joblib.load(file_path)
        return True, model
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False, f"Error loading model: {str(e)}"

def get_model_metadata(file_path: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
    """
    Get metadata for a saved model.

    Args:
        file_path: The path to the model file.

    Returns:
        A tuple containing:
        - A boolean indicating success or failure.
        - The model metadata or an error message.
    """
    try:
        metadata_path = f"{os.path.splitext(file_path)[0]}_metadata.json"

        if os.path.exists(metadata_path):
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            return True, metadata
        else:
            return False, "Metadata file not found"
    except Exception as e:
        logger.error(f"Error loading model metadata: {str(e)}")
        return False, f"Error loading model metadata: {str(e)}"

def store_model_metadata_in_neo4j(
    model_name: str,
    metadata: Dict[str, Any],
    connection_name: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Store model metadata in Neo4j.

    Args:
        model_name: The name of the model.
        metadata: The model metadata.
        connection_name: The name of the Neo4j connection to use.

    Returns:
        A tuple containing:
        - A boolean indicating success or failure.
        - A message describing the result.
    """
    try:
        db_manager = DBManager()

        # Create a node for the model
        query = """
        CREATE (m:Model {name: $name, created_at: datetime()})
        SET m += $metadata
        RETURN m
        """

        params = {
            "name": model_name,
            "metadata": metadata
        }

        success, result = db_manager.query(query, params, connection_name)

        if success:
            return True, f"Model metadata stored in Neo4j"
        else:
            return False, f"Error storing model metadata in Neo4j: {result}"
    except Exception as e:
        logger.error(f"Error storing model metadata in Neo4j: {str(e)}")
        return False, f"Error storing model metadata in Neo4j: {str(e)}"

def get_model_metadata_from_neo4j(
    model_name: str,
    connection_name: Optional[str] = None
) -> Tuple[bool, Union[Dict[str, Any], str]]:
    """
    Get model metadata from Neo4j.

    Args:
        model_name: The name of the model.
        connection_name: The name of the Neo4j connection to use.

    Returns:
        A tuple containing:
        - A boolean indicating success or failure.
        - The model metadata or an error message.
    """
    try:
        db_manager = DBManager()

        # Get the model node
        query = """
        MATCH (m:Model {name: $name})
        RETURN m
        """

        params = {
            "name": model_name
        }

        success, result = db_manager.query(query, params, connection_name)

        if success and len(result) > 0:
            return True, result[0]['m']
        elif success:
            return False, "Model not found"
        else:
            return False, f"Error retrieving model metadata from Neo4j: {result}"
    except Exception as e:
        logger.error(f"Error retrieving model metadata from Neo4j: {str(e)}")
        return False, f"Error retrieving model metadata from Neo4j: {str(e)}"

def cross_validate(
    X: np.ndarray,
    y: np.ndarray,
    model_type: str = 'random_forest',
    model_params: Optional[Dict[str, Any]] = None,
    cv: int = 5,
    metrics: Optional[List[str]] = None,
    is_classifier: Optional[bool] = None
) -> Dict[str, List[float]]:
    """
    Perform cross-validation on a model.

    Args:
        X: Features.
        y: Target.
        model_type: The type of model to train.
        model_params: Parameters for the model.
        cv: Number of cross-validation folds.
        metrics: The metrics to use for evaluation.
        is_classifier: Whether the model is a classifier.

    Returns:
        A dictionary containing the cross-validation results.
    """
    try:
        from sklearn.model_selection import cross_validate

        # Create the model
        if model_params is None:
            model_params = {}

        model = train_model(None, None, model_type, model_params)

        # Determine if the model is a classifier
        if is_classifier is None:
            try:
                is_classifier = hasattr(model, 'predict_proba')
            except:
                is_classifier = False

        # Determine scoring metrics
        scoring = []
        if is_classifier:
            if metrics is None:
                metrics = ['accuracy', 'precision', 'recall', 'f1']

            for metric in metrics:
                if metric == 'accuracy':
                    scoring.append('accuracy')
                elif metric == 'precision':
                    scoring.append('precision_weighted')
                elif metric == 'recall':
                    scoring.append('recall_weighted')
                elif metric == 'f1':
                    scoring.append('f1_weighted')
                elif metric == 'roc_auc':
                    scoring.append('roc_auc_ovr')
        else:
            if metrics is None:
                metrics = ['mse', 'mae', 'r2']

            for metric in metrics:
                if metric == 'mse':
                    scoring.append('neg_mean_squared_error')
                elif metric == 'mae':
                    scoring.append('neg_mean_absolute_error')
                elif metric == 'r2':
                    scoring.append('r2')

        # Perform cross-validation
        cv_results = cross_validate(model, X, y, cv=cv, scoring=scoring)

        # Process results
        results = {}
        for metric in scoring:
            key = f"test_{metric}"
            if key in cv_results:
                results[metric] = cv_results[key].tolist()

        return results
    except Exception as e:
        logger.error(f"Error performing cross-validation: {str(e)}")
        return {}
