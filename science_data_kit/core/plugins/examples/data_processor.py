"""
A data processing plugin for the Science Data Kit.

This module provides an example of a Science Data Kit plugin that
performs data processing operations on pandas DataFrames.
"""

import logging
from typing import Dict, List, Optional, Any, Callable

import numpy as np
import pandas as pd

from science_data_kit.core.plugins.base import Plugin

logger = logging.getLogger(__name__)


class DataProcessorPlugin(Plugin):
    """A data processing plugin for the Science Data Kit.
    
    This plugin demonstrates how to create a plugin that performs data
    processing operations on pandas DataFrames. It provides methods for
    common data transformations and statistical operations.
    """
    
    @property
    def name(self) -> str:
        """Return the name of the plugin."""
        return "data_processor"
    
    @property
    def version(self) -> str:
        """Return the version of the plugin."""
        return "1.0.0"
    
    @property
    def description(self) -> str:
        """Return a description of the plugin."""
        return "A plugin for processing and transforming data in pandas DataFrames."
    
    def initialize(self) -> None:
        """Initialize the plugin.
        
        This method is called when the plugin is activated. It initializes
        the plugin's internal state and registers its data processing functions.
        """
        logger.info("Initializing DataProcessorPlugin...")
        self._transformers: Dict[str, Callable] = {}
        
        # Register built-in transformers
        self.register_transformer("normalize", self.normalize)
        self.register_transformer("standardize", self.standardize)
        self.register_transformer("log_transform", self.log_transform)
        self.register_transformer("fill_missing", self.fill_missing)
        self.register_transformer("remove_outliers", self.remove_outliers)
        
        logger.info(f"DataProcessorPlugin initialized with {len(self._transformers)} transformers.")
    
    def shutdown(self) -> None:
        """Shut down the plugin.
        
        This method is called when the plugin is deactivated. It cleans up
        the plugin's internal state.
        """
        logger.info("Shutting down DataProcessorPlugin...")
        self._transformers.clear()
        logger.info("DataProcessorPlugin shut down.")
    
    def register_transformer(self, name: str, transformer: Callable) -> None:
        """Register a data transformer function.
        
        Args:
            name: The name of the transformer.
            transformer: The transformer function.
            
        Raises:
            ValueError: If a transformer with the same name is already registered.
        """
        if name in self._transformers:
            raise ValueError(f"A transformer with name '{name}' is already registered.")
        
        self._transformers[name] = transformer
        logger.info(f"Registered transformer: {name}")
    
    def get_transformer(self, name: str) -> Optional[Callable]:
        """Get a registered transformer by name.
        
        Args:
            name: The name of the transformer to get.
            
        Returns:
            The transformer function if found, None otherwise.
        """
        return self._transformers.get(name)
    
    def get_all_transformers(self) -> Dict[str, Callable]:
        """Get all registered transformers.
        
        Returns:
            A dictionary mapping transformer names to transformer functions.
        """
        return self._transformers.copy()
    
    def apply_transformer(self, df: pd.DataFrame, transformer_name: str, **kwargs) -> pd.DataFrame:
        """Apply a registered transformer to a DataFrame.
        
        Args:
            df: The DataFrame to transform.
            transformer_name: The name of the transformer to apply.
            **kwargs: Additional arguments to pass to the transformer.
            
        Returns:
            The transformed DataFrame.
            
        Raises:
            ValueError: If the transformer is not registered.
        """
        transformer = self.get_transformer(transformer_name)
        if transformer is None:
            raise ValueError(f"Transformer '{transformer_name}' is not registered.")
        
        logger.info(f"Applying transformer '{transformer_name}' to DataFrame...")
        result = transformer(df, **kwargs)
        logger.info(f"Transformer '{transformer_name}' applied successfully.")
        return result
    
    # Built-in transformers
    
    def normalize(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Normalize numeric columns to the range [0, 1].
        
        Args:
            df: The DataFrame to normalize.
            columns: The columns to normalize. If None, all numeric columns are normalized.
            
        Returns:
            The normalized DataFrame.
        """
        logger.info("Normalizing DataFrame...")
        result = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=np.number).columns.tolist()
        
        for col in columns:
            if col in result.columns and pd.api.types.is_numeric_dtype(result[col]):
                min_val = result[col].min()
                max_val = result[col].max()
                if max_val > min_val:
                    result[col] = (result[col] - min_val) / (max_val - min_val)
        
        logger.info(f"Normalized {len(columns)} columns.")
        return result
    
    def standardize(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Standardize numeric columns to have mean 0 and standard deviation 1.
        
        Args:
            df: The DataFrame to standardize.
            columns: The columns to standardize. If None, all numeric columns are standardized.
            
        Returns:
            The standardized DataFrame.
        """
        logger.info("Standardizing DataFrame...")
        result = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=np.number).columns.tolist()
        
        for col in columns:
            if col in result.columns and pd.api.types.is_numeric_dtype(result[col]):
                mean = result[col].mean()
                std = result[col].std()
                if std > 0:
                    result[col] = (result[col] - mean) / std
        
        logger.info(f"Standardized {len(columns)} columns.")
        return result
    
    def log_transform(self, df: pd.DataFrame, columns: Optional[List[str]] = None,
                     base: float = np.e, offset: float = 1.0) -> pd.DataFrame:
        """Apply a logarithmic transformation to numeric columns.
        
        Args:
            df: The DataFrame to transform.
            columns: The columns to transform. If None, all numeric columns are transformed.
            base: The logarithm base to use.
            offset: A value to add to each element before taking the logarithm (to handle zeros).
            
        Returns:
            The transformed DataFrame.
        """
        logger.info(f"Applying log transformation (base={base}, offset={offset})...")
        result = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=np.number).columns.tolist()
        
        for col in columns:
            if col in result.columns and pd.api.types.is_numeric_dtype(result[col]):
                if base == np.e:
                    result[col] = np.log(result[col] + offset)
                else:
                    result[col] = np.log(result[col] + offset) / np.log(base)
        
        logger.info(f"Applied log transformation to {len(columns)} columns.")
        return result
    
    def fill_missing(self, df: pd.DataFrame, strategy: str = "mean",
                    columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Fill missing values in the DataFrame.
        
        Args:
            df: The DataFrame to process.
            strategy: The strategy to use for filling missing values.
                      Options: "mean", "median", "mode", "zero", "forward", "backward".
            columns: The columns to process. If None, all columns are processed.
            
        Returns:
            The processed DataFrame.
            
        Raises:
            ValueError: If the strategy is not supported.
        """
        logger.info(f"Filling missing values using strategy '{strategy}'...")
        result = df.copy()
        
        if columns is None:
            columns = result.columns.tolist()
        
        for col in columns:
            if col in result.columns:
                if strategy == "mean" and pd.api.types.is_numeric_dtype(result[col]):
                    result[col] = result[col].fillna(result[col].mean())
                elif strategy == "median" and pd.api.types.is_numeric_dtype(result[col]):
                    result[col] = result[col].fillna(result[col].median())
                elif strategy == "mode":
                    result[col] = result[col].fillna(result[col].mode()[0] if not result[col].mode().empty else None)
                elif strategy == "zero" and pd.api.types.is_numeric_dtype(result[col]):
                    result[col] = result[col].fillna(0)
                elif strategy == "forward":
                    result[col] = result[col].fillna(method="ffill")
                elif strategy == "backward":
                    result[col] = result[col].fillna(method="bfill")
                else:
                    raise ValueError(f"Unsupported fill strategy: {strategy}")
        
        logger.info(f"Filled missing values in {len(columns)} columns.")
        return result
    
    def remove_outliers(self, df: pd.DataFrame, method: str = "iqr",
                       columns: Optional[List[str]] = None,
                       threshold: float = 1.5) -> pd.DataFrame:
        """Remove outliers from the DataFrame.
        
        Args:
            df: The DataFrame to process.
            method: The method to use for identifying outliers.
                   Options: "iqr" (Interquartile Range), "zscore".
            columns: The columns to process. If None, all numeric columns are processed.
            threshold: The threshold for identifying outliers.
                      For "iqr", values outside Q1 - threshold*IQR and Q3 + threshold*IQR are outliers.
                      For "zscore", values with absolute z-score greater than threshold are outliers.
            
        Returns:
            The processed DataFrame with outliers removed.
            
        Raises:
            ValueError: If the method is not supported.
        """
        logger.info(f"Removing outliers using method '{method}' with threshold {threshold}...")
        result = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=np.number).columns.tolist()
        
        mask = pd.Series(True, index=df.index)
        
        for col in columns:
            if col in result.columns and pd.api.types.is_numeric_dtype(result[col]):
                if method == "iqr":
                    Q1 = result[col].quantile(0.25)
                    Q3 = result[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR
                    col_mask = (result[col] >= lower_bound) & (result[col] <= upper_bound)
                    mask = mask & col_mask
                elif method == "zscore":
                    mean = result[col].mean()
                    std = result[col].std()
                    if std > 0:
                        z_scores = (result[col] - mean) / std
                        col_mask = z_scores.abs() <= threshold
                        mask = mask & col_mask
                else:
                    raise ValueError(f"Unsupported outlier removal method: {method}")
        
        result = result[mask]
        logger.info(f"Removed {len(df) - len(result)} outliers from {len(columns)} columns.")
        return result