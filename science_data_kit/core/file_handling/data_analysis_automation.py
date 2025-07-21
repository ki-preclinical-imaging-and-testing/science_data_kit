"""
Data analysis automation module for automating analysis of scientific data.

This module provides functionality for automating the analysis of scientific data files,
including statistical analysis, visualization, and report generation. It builds on the
existing file handling infrastructure to extract data from various scientific file formats
and apply appropriate analysis techniques based on the data type and structure.

The module includes:
- Automated data extraction from scientific file formats
- Statistical analysis of numerical data
- Time series analysis for temporal data
- Correlation and regression analysis
- Automated visualization generation
- Report generation with insights and findings
- Customizable analysis workflows
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

from science_data_kit.core.file_handling.text_extraction import (
    TextExtractionOptions,
    extract_text_from_file
)

logger = logging.getLogger(__name__)


class DataType(Enum):
    """Enumeration of data types for analysis."""
    NUMERICAL = "numerical"  # Continuous numerical data
    CATEGORICAL = "categorical"  # Categorical or nominal data
    TIME_SERIES = "time_series"  # Time series data
    GEOSPATIAL = "geospatial"  # Geospatial data
    TEXT = "text"  # Text data
    MIXED = "mixed"  # Mixed data types
    UNKNOWN = "unknown"  # Unknown data type


class AnalysisType(Enum):
    """Enumeration of analysis types."""
    DESCRIPTIVE = "descriptive"  # Descriptive statistics
    EXPLORATORY = "exploratory"  # Exploratory data analysis
    INFERENTIAL = "inferential"  # Inferential statistics
    PREDICTIVE = "predictive"  # Predictive modeling
    PRESCRIPTIVE = "prescriptive"  # Prescriptive analytics
    CUSTOM = "custom"  # Custom analysis


class VisualizationType(Enum):
    """Enumeration of visualization types."""
    HISTOGRAM = "histogram"
    SCATTER = "scatter"
    LINE = "line"
    BAR = "bar"
    BOX = "box"
    HEATMAP = "heatmap"
    PIE = "pie"
    CORRELATION = "correlation"
    PCA = "pca"
    TIME_SERIES = "time_series"
    CUSTOM = "custom"


@dataclass
class AnalysisOptions:
    """Options for data analysis automation."""
    # General options
    analysis_types: List[AnalysisType] = field(default_factory=lambda: [AnalysisType.DESCRIPTIVE, AnalysisType.EXPLORATORY])
    visualization_types: List[VisualizationType] = field(default_factory=lambda: [VisualizationType.HISTOGRAM, VisualizationType.SCATTER, VisualizationType.CORRELATION])
    max_visualizations: int = 5
    generate_report: bool = True
    report_format: str = "html"  # html, markdown, pdf
    
    # Data processing options
    handle_missing_values: bool = True
    remove_outliers: bool = False
    normalize_data: bool = False
    
    # Statistical analysis options
    significance_level: float = 0.05
    correlation_threshold: float = 0.7
    
    # Time series options
    time_column: Optional[str] = None
    seasonal_decompose: bool = True
    forecast_periods: int = 10
    
    # Visualization options
    figure_size: Tuple[int, int] = (10, 6)
    color_palette: str = "viridis"
    
    # File handling options
    output_directory: Optional[str] = None
    
    # Text extraction options
    text_extraction_options: Optional[TextExtractionOptions] = None


@dataclass
class DatasetInfo:
    """Information about a dataset."""
    file_path: str
    data_type: DataType
    num_rows: int
    num_columns: int
    column_types: Dict[str, str]
    missing_values: Dict[str, int]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Result of data analysis."""
    dataset_info: DatasetInfo
    descriptive_stats: Optional[Dict[str, Any]] = None
    correlation_matrix: Optional[pd.DataFrame] = None
    regression_results: Optional[Dict[str, Any]] = None
    clustering_results: Optional[Dict[str, Any]] = None
    time_series_results: Optional[Dict[str, Any]] = None
    visualizations: Dict[str, str] = field(default_factory=dict)  # Path to visualization files
    report_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Return a string representation of the analysis result."""
        return f"Analysis of {os.path.basename(self.dataset_info.file_path)} ({self.dataset_info.data_type.value})"


class DataAnalyzer:
    """Class for automating data analysis."""
    
    def __init__(self, options: Optional[AnalysisOptions] = None):
        """
        Initialize the data analyzer.
        
        Args:
            options: Analysis options
        """
        self.options = options or AnalysisOptions()
        self.data = None
        self.dataset_info = None
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """
        Analyze a data file.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            AnalysisResult object containing the analysis results
        """
        try:
            # Load data from file
            self.data = self._load_data(file_path)
            
            if self.data is None:
                logger.error(f"Failed to load data from {file_path}")
                return self._create_empty_result(file_path, "Failed to load data")
            
            # Create dataset info
            self.dataset_info = self._create_dataset_info(file_path)
            
            # Initialize result
            result = AnalysisResult(dataset_info=self.dataset_info)
            
            # Preprocess data
            self._preprocess_data()
            
            # Perform analyses based on options
            for analysis_type in self.options.analysis_types:
                if analysis_type == AnalysisType.DESCRIPTIVE:
                    result.descriptive_stats = self._perform_descriptive_analysis()
                elif analysis_type == AnalysisType.EXPLORATORY:
                    result.correlation_matrix = self._perform_correlation_analysis()
                    result.visualizations.update(self._generate_visualizations())
                elif analysis_type == AnalysisType.INFERENTIAL:
                    # Add inferential statistics as needed
                    pass
                elif analysis_type == AnalysisType.PREDICTIVE:
                    result.regression_results = self._perform_regression_analysis()
                    result.clustering_results = self._perform_clustering_analysis()
                elif analysis_type == AnalysisType.PRESCRIPTIVE:
                    # Add prescriptive analytics as needed
                    pass
            
            # Handle time series data if applicable
            if self.dataset_info.data_type == DataType.TIME_SERIES:
                result.time_series_results = self._perform_time_series_analysis()
            
            # Generate report if requested
            if self.options.generate_report:
                result.report_path = self._generate_report(result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return self._create_empty_result(file_path, str(e))
    
    def _create_empty_result(self, file_path: str, error_message: str) -> AnalysisResult:
        """
        Create an empty analysis result with error information.
        
        Args:
            file_path: Path to the data file
            error_message: Error message
            
        Returns:
            Empty AnalysisResult object
        """
        dataset_info = DatasetInfo(
            file_path=file_path,
            data_type=DataType.UNKNOWN,
            num_rows=0,
            num_columns=0,
            column_types={},
            missing_values={},
            metadata={"error": error_message}
        )
        
        return AnalysisResult(
            dataset_info=dataset_info,
            metadata={"error": error_message}
        )
    
    def _load_data(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Load data from a file into a pandas DataFrame.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            Pandas DataFrame or None if loading fails
        """
        try:
            # Get file extension
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            
            # Load data based on file type
            if ext == '.csv':
                return pd.read_csv(file_path)
            elif ext == '.xlsx' or ext == '.xls':
                return pd.read_excel(file_path)
            elif ext == '.json':
                return pd.read_json(file_path)
            elif ext == '.parquet':
                return pd.read_parquet(file_path)
            elif ext == '.hdf' or ext == '.h5':
                return pd.read_hdf(file_path)
            elif ext == '.feather':
                return pd.read_feather(file_path)
            elif ext == '.pickle' or ext == '.pkl':
                return pd.read_pickle(file_path)
            elif ext == '.txt' or ext == '.dat':
                # Try to read as CSV with different delimiters
                for delimiter in [',', '\t', ';', '|', ' ']:
                    try:
                        return pd.read_csv(file_path, delimiter=delimiter)
                    except:
                        continue
            
            # For other file types, try to extract data using specialized handlers
            if ext in ['.nc', '.netcdf']:
                return self._load_netcdf(file_path)
            elif ext in ['.fits', '.fit']:
                return self._load_fits(file_path)
            elif ext in ['.tif', '.tiff', '.geotiff']:
                return self._load_geotiff(file_path)
            
            logger.warning(f"Unsupported file type: {ext}")
            return None
        
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            return None
    
    def _load_netcdf(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Load data from a NetCDF file.
        
        Args:
            file_path: Path to the NetCDF file
            
        Returns:
            Pandas DataFrame or None if loading fails
        """
        try:
            import xarray as xr
            
            # Open NetCDF file
            ds = xr.open_dataset(file_path)
            
            # Convert to pandas DataFrame
            df = ds.to_dataframe().reset_index()
            
            return df
        
        except ImportError:
            logger.warning("xarray not available for loading NetCDF files")
            return None
        
        except Exception as e:
            logger.error(f"Error loading NetCDF file {file_path}: {e}")
            return None
    
    def _load_fits(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Load data from a FITS file.
        
        Args:
            file_path: Path to the FITS file
            
        Returns:
            Pandas DataFrame or None if loading fails
        """
        try:
            from astropy.io import fits
            from astropy.table import Table
            
            # Open FITS file
            with fits.open(file_path) as hdul:
                # Try to convert the first HDU with data to a DataFrame
                for hdu in hdul:
                    if isinstance(hdu, fits.BinTableHDU) or isinstance(hdu, fits.TableHDU):
                        table = Table(hdu.data)
                        return table.to_pandas()
                
                # If no table HDUs, try to use the primary HDU data
                if len(hdul) > 0 and hdul[0].data is not None:
                    # Convert 2D array to DataFrame
                    data = hdul[0].data
                    if len(data.shape) == 2:
                        df = pd.DataFrame(data)
                        return df
            
            logger.warning(f"No usable data found in FITS file {file_path}")
            return None
        
        except ImportError:
            logger.warning("astropy not available for loading FITS files")
            return None
        
        except Exception as e:
            logger.error(f"Error loading FITS file {file_path}: {e}")
            return None
    
    def _load_geotiff(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Load data from a GeoTIFF file.
        
        Args:
            file_path: Path to the GeoTIFF file
            
        Returns:
            Pandas DataFrame or None if loading fails
        """
        try:
            import rasterio
            
            # Open GeoTIFF file
            with rasterio.open(file_path) as src:
                # Read data
                data = src.read(1)  # Read first band
                
                # Get coordinates
                height, width = data.shape
                cols, rows = np.meshgrid(np.arange(width), np.arange(height))
                
                # Get actual coordinates
                xs, ys = rasterio.transform.xy(src.transform, rows, cols)
                
                # Create DataFrame
                df = pd.DataFrame({
                    'x': np.array(xs).flatten(),
                    'y': np.array(ys).flatten(),
                    'value': data.flatten()
                })
                
                return df
        
        except ImportError:
            logger.warning("rasterio not available for loading GeoTIFF files")
            return None
        
        except Exception as e:
            logger.error(f"Error loading GeoTIFF file {file_path}: {e}")
            return None
    
    def _create_dataset_info(self, file_path: str) -> DatasetInfo:
        """
        Create dataset information.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            DatasetInfo object
        """
        # Get basic information
        num_rows, num_columns = self.data.shape
        
        # Get column types
        column_types = {col: str(dtype) for col, dtype in self.data.dtypes.items()}
        
        # Count missing values
        missing_values = {col: int(self.data[col].isna().sum()) for col in self.data.columns}
        
        # Determine data type
        data_type = self._determine_data_type()
        
        # Create metadata
        metadata = {
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "file_extension": os.path.splitext(file_path)[1].lower(),
            "memory_usage": self.data.memory_usage(deep=True).sum()
        }
        
        return DatasetInfo(
            file_path=file_path,
            data_type=data_type,
            num_rows=num_rows,
            num_columns=num_columns,
            column_types=column_types,
            missing_values=missing_values,
            metadata=metadata
        )
    
    def _determine_data_type(self) -> DataType:
        """
        Determine the type of data in the dataset.
        
        Returns:
            DataType enum value
        """
        # Check for time series data
        time_columns = []
        for col in self.data.columns:
            if pd.api.types.is_datetime64_any_dtype(self.data[col]):
                time_columns.append(col)
            elif 'date' in col.lower() or 'time' in col.lower():
                try:
                    pd.to_datetime(self.data[col])
                    time_columns.append(col)
                except:
                    pass
        
        if time_columns and self.options.time_column is None:
            self.options.time_column = time_columns[0]
        
        # Check for geospatial data
        geo_columns = []
        for col in self.data.columns:
            if any(term in col.lower() for term in ['lat', 'lon', 'latitude', 'longitude', 'x', 'y', 'coord']):
                geo_columns.append(col)
        
        # Count numerical and categorical columns
        numerical_cols = self.data.select_dtypes(include=['number']).columns
        categorical_cols = self.data.select_dtypes(include=['object', 'category']).columns
        
        # Determine data type based on column composition
        if len(time_columns) >= 1 and len(numerical_cols) >= 1:
            return DataType.TIME_SERIES
        elif len(geo_columns) >= 2:
            return DataType.GEOSPATIAL
        elif len(numerical_cols) >= len(self.data.columns) * 0.7:
            return DataType.NUMERICAL
        elif len(categorical_cols) >= len(self.data.columns) * 0.7:
            return DataType.CATEGORICAL
        else:
            return DataType.MIXED
    
    def _preprocess_data(self):
        """Preprocess the data based on options."""
        # Handle missing values
        if self.options.handle_missing_values:
            # For numerical columns, fill with mean
            num_cols = self.data.select_dtypes(include=['number']).columns
            for col in num_cols:
                self.data[col] = self.data[col].fillna(self.data[col].mean())
            
            # For categorical columns, fill with mode
            cat_cols = self.data.select_dtypes(include=['object', 'category']).columns
            for col in cat_cols:
                if not self.data[col].empty:
                    mode_value = self.data[col].mode()[0] if not self.data[col].mode().empty else "Unknown"
                    self.data[col] = self.data[col].fillna(mode_value)
        
        # Remove outliers if requested
        if self.options.remove_outliers:
            num_cols = self.data.select_dtypes(include=['number']).columns
            for col in num_cols:
                # Calculate IQR
                Q1 = self.data[col].quantile(0.25)
                Q3 = self.data[col].quantile(0.75)
                IQR = Q3 - Q1
                
                # Define bounds
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Filter outliers
                self.data = self.data[(self.data[col] >= lower_bound) & (self.data[col] <= upper_bound)]
        
        # Normalize data if requested
        if self.options.normalize_data:
            num_cols = self.data.select_dtypes(include=['number']).columns
            if not num_cols.empty:
                scaler = StandardScaler()
                self.data[num_cols] = scaler.fit_transform(self.data[num_cols])
    
    def _perform_descriptive_analysis(self) -> Dict[str, Any]:
        """
        Perform descriptive statistical analysis.
        
        Returns:
            Dictionary of descriptive statistics
        """
        result = {}
        
        # Basic statistics for numerical columns
        num_cols = self.data.select_dtypes(include=['number']).columns
        if not num_cols.empty:
            result["numerical_stats"] = self.data[num_cols].describe().to_dict()
        
        # Frequency counts for categorical columns
        cat_cols = self.data.select_dtypes(include=['object', 'category']).columns
        result["categorical_stats"] = {}
        for col in cat_cols:
            value_counts = self.data[col].value_counts().to_dict()
            # Limit to top 10 categories
            if len(value_counts) > 10:
                top_items = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                value_counts = {k: v for k, v in top_items}
                value_counts["other"] = self.data[col].value_counts().sum() - sum(value_counts.values())
            result["categorical_stats"][col] = value_counts
        
        # Additional statistics
        result["data_completeness"] = 1.0 - (self.data.isna().sum().sum() / (self.data.shape[0] * self.data.shape[1]))
        
        return result
    
    def _perform_correlation_analysis(self) -> Optional[pd.DataFrame]:
        """
        Perform correlation analysis on numerical data.
        
        Returns:
            Correlation matrix as a pandas DataFrame
        """
        # Get numerical columns
        num_cols = self.data.select_dtypes(include=['number']).columns
        
        if len(num_cols) < 2:
            logger.warning("Not enough numerical columns for correlation analysis")
            return None
        
        # Calculate correlation matrix
        corr_matrix = self.data[num_cols].corr()
        
        return corr_matrix
    
    def _perform_regression_analysis(self) -> Dict[str, Any]:
        """
        Perform regression analysis on numerical data.
        
        Returns:
            Dictionary of regression results
        """
        # Get numerical columns
        num_cols = self.data.select_dtypes(include=['number']).columns
        
        if len(num_cols) < 2:
            logger.warning("Not enough numerical columns for regression analysis")
            return {}
        
        results = {}
        
        # Try to find a suitable target variable
        target_col = None
        
        # If there's a column named 'target', 'y', or 'dependent', use it
        for col in ['target', 'y', 'dependent', 'output', 'result']:
            if col in num_cols:
                target_col = col
                break
        
        # Otherwise, use the last column
        if target_col is None:
            target_col = num_cols[-1]
        
        # Get feature columns (all numerical columns except target)
        feature_cols = [col for col in num_cols if col != target_col]
        
        if not feature_cols:
            logger.warning("No feature columns available for regression analysis")
            return {}
        
        # Prepare data
        X = self.data[feature_cols]
        y = self.data[target_col]
        
        # Linear regression
        try:
            model = LinearRegression()
            model.fit(X, y)
            
            y_pred = model.predict(X)
            
            # Calculate metrics
            mse = mean_squared_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            # Store results
            results["linear_regression"] = {
                "target_column": target_col,
                "feature_columns": feature_cols,
                "coefficients": {col: float(coef) for col, coef in zip(feature_cols, model.coef_)},
                "intercept": float(model.intercept_),
                "mse": mse,
                "r2": r2
            }
        except Exception as e:
            logger.error(f"Error in linear regression: {e}")
        
        # Random Forest regression
        try:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            y_pred = model.predict(X)
            
            # Calculate metrics
            mse = mean_squared_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            # Store results
            results["random_forest_regression"] = {
                "target_column": target_col,
                "feature_columns": feature_cols,
                "feature_importances": {col: float(imp) for col, imp in zip(feature_cols, model.feature_importances_)},
                "mse": mse,
                "r2": r2
            }
        except Exception as e:
            logger.error(f"Error in Random Forest regression: {e}")
        
        return results
    
    def _perform_clustering_analysis(self) -> Dict[str, Any]:
        """
        Perform clustering analysis on numerical data.
        
        Returns:
            Dictionary of clustering results
        """
        # Get numerical columns
        num_cols = self.data.select_dtypes(include=['number']).columns
        
        if len(num_cols) < 2:
            logger.warning("Not enough numerical columns for clustering analysis")
            return {}
        
        results = {}
        
        try:
            # Prepare data
            X = self.data[num_cols]
            
            # Determine optimal number of clusters (simple method)
            max_clusters = min(10, len(self.data) // 10)  # Limit to 10 clusters or 1/10 of data points
            if max_clusters < 2:
                max_clusters = 2
            
            inertias = []
            for k in range(2, max_clusters + 1):
                kmeans = KMeans(n_clusters=k, random_state=42)
                kmeans.fit(X)
                inertias.append(kmeans.inertia_)
            
            # Find elbow point (simple method)
            optimal_k = 2
            if len(inertias) > 1:
                diffs = np.diff(inertias)
                if len(diffs) > 1:
                    # Find where the rate of improvement slows down
                    rates = np.diff(diffs)
                    optimal_idx = np.argmax(rates) + 2 if rates.size > 0 else 2
                    optimal_k = optimal_idx + 2
                else:
                    optimal_k = 2
            
            # Apply K-means with optimal k
            kmeans = KMeans(n_clusters=optimal_k, random_state=42)
            clusters = kmeans.fit_predict(X)
            
            # Calculate cluster statistics
            cluster_stats = {}
            for i in range(optimal_k):
                cluster_data = X[clusters == i]
                if len(cluster_data) > 0:
                    cluster_stats[f"cluster_{i}"] = {
                        "size": int(len(cluster_data)),
                        "percentage": float(len(cluster_data) / len(X) * 100),
                        "center": {col: float(val) for col, val in zip(num_cols, kmeans.cluster_centers_[i])},
                        "mean": {col: float(cluster_data[col].mean()) for col in num_cols},
                        "std": {col: float(cluster_data[col].std()) for col in num_cols}
                    }
            
            # Store results
            results["kmeans_clustering"] = {
                "num_clusters": optimal_k,
                "inertia": float(kmeans.inertia_),
                "cluster_sizes": {i: int(np.sum(clusters == i)) for i in range(optimal_k)},
                "cluster_stats": cluster_stats
            }
            
            # Add cluster labels to metadata
            self.dataset_info.metadata["cluster_labels"] = clusters.tolist()
        
        except Exception as e:
            logger.error(f"Error in clustering analysis: {e}")
        
        return results
    
    def _perform_time_series_analysis(self) -> Dict[str, Any]:
        """
        Perform time series analysis.
        
        Returns:
            Dictionary of time series analysis results
        """
        if self.dataset_info.data_type != DataType.TIME_SERIES:
            logger.warning("Dataset is not identified as time series data")
            return {}
        
        if not self.options.time_column:
            logger.warning("No time column specified for time series analysis")
            return {}
        
        results = {}
        
        try:
            # Ensure time column is datetime
            if not pd.api.types.is_datetime64_any_dtype(self.data[self.options.time_column]):
                self.data[self.options.time_column] = pd.to_datetime(self.data[self.options.time_column])
            
            # Sort by time
            self.data = self.data.sort_values(by=self.options.time_column)
            
            # Get numerical columns (excluding time column)
            num_cols = [col for col in self.data.select_dtypes(include=['number']).columns 
                      if col != self.options.time_column]
            
            if not num_cols:
                logger.warning("No numerical columns available for time series analysis")
                return {}
            
            # Basic time series statistics
            results["time_range"] = {
                "start": self.data[self.options.time_column].min().isoformat(),
                "end": self.data[self.options.time_column].max().isoformat(),
                "duration": str(self.data[self.options.time_column].max() - self.data[self.options.time_column].min())
            }
            
            # Check for seasonality and trend
            if self.options.seasonal_decompose and len(self.data) >= 10:
                try:
                    from statsmodels.tsa.seasonal import seasonal_decompose
                    
                    # Set the time column as index
                    ts_data = self.data.set_index(self.options.time_column)
                    
                    # Perform seasonal decomposition for each numerical column
                    seasonal_results = {}
                    for col in num_cols[:3]:  # Limit to first 3 columns
                        if ts_data[col].isna().sum() == 0 and len(ts_data) > 2:
                            # Determine frequency (period)
                            # This is a simple heuristic and might need adjustment
                            if len(ts_data) >= 365:
                                period = 365  # Daily data for a year
                            elif len(ts_data) >= 52:
                                period = 52  # Weekly data
                            elif len(ts_data) >= 12:
                                period = 12  # Monthly data
                            else:
                                period = 2  # Minimum period
                            
                            # Perform decomposition
                            decomposition = seasonal_decompose(ts_data[col], model='additive', period=period)
                            
                            # Store results
                            seasonal_results[col] = {
                                "trend": decomposition.trend.dropna().tolist()[-5:],  # Last 5 values
                                "seasonal": decomposition.seasonal.dropna().tolist()[-5:],  # Last 5 values
                                "residual": decomposition.resid.dropna().tolist()[-5:],  # Last 5 values
                                "period": period
                            }
                    
                    results["seasonal_decomposition"] = seasonal_results
                
                except ImportError:
                    logger.warning("statsmodels not available for seasonal decomposition")
                except Exception as e:
                    logger.error(f"Error in seasonal decomposition: {e}")
            
            # Simple forecasting
            if self.options.forecast_periods > 0:
                try:
                    from sklearn.linear_model import LinearRegression
                    
                    forecast_results = {}
                    for col in num_cols[:3]:  # Limit to first 3 columns
                        # Create features (time index)
                        X = np.arange(len(self.data)).reshape(-1, 1)
                        y = self.data[col].values
                        
                        # Fit linear model
                        model = LinearRegression()
                        model.fit(X, y)
                        
                        # Forecast
                        X_future = np.arange(len(self.data), len(self.data) + self.options.forecast_periods).reshape(-1, 1)
                        y_future = model.predict(X_future)
                        
                        # Store results
                        forecast_results[col] = {
                            "forecast": y_future.tolist(),
                            "slope": float(model.coef_[0]),
                            "intercept": float(model.intercept_)
                        }
                    
                    results["forecasting"] = forecast_results
                
                except Exception as e:
                    logger.error(f"Error in forecasting: {e}")
            
            return results
        
        except Exception as e:
            logger.error(f"Error in time series analysis: {e}")
            return {}
    
    def _generate_visualizations(self) -> Dict[str, str]:
        """
        Generate visualizations based on the data and options.
        
        Returns:
            Dictionary mapping visualization names to file paths
        """
        visualizations = {}
        
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Set style
            sns.set(style="whitegrid")
            plt.rcParams["figure.figsize"] = self.options.figure_size
            
            # Create output directory if needed
            output_dir = self.options.output_directory
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(self.dataset_info.file_path), "analysis_output")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Get numerical and categorical columns
            num_cols = self.data.select_dtypes(include=['number']).columns
            cat_cols = self.data.select_dtypes(include=['object', 'category']).columns
            
            # Generate visualizations based on options
            viz_count = 0
            
            for viz_type in self.options.visualization_types:
                if viz_count >= self.options.max_visualizations:
                    break
                
                if viz_type == VisualizationType.HISTOGRAM and len(num_cols) > 0:
                    # Create histograms for numerical columns
                    for col in num_cols[:min(3, len(num_cols))]:  # Limit to 3 columns
                        plt.figure()
                        sns.histplot(self.data[col], kde=True)
                        plt.title(f"Distribution of {col}")
                        plt.tight_layout()
                        
                        # Save figure
                        file_path = os.path.join(output_dir, f"histogram_{col}.png")
                        plt.savefig(file_path)
                        plt.close()
                        
                        visualizations[f"histogram_{col}"] = file_path
                        viz_count += 1
                
                elif viz_type == VisualizationType.SCATTER and len(num_cols) >= 2:
                    # Create scatter plots for pairs of numerical columns
                    for i in range(min(2, len(num_cols))):
                        for j in range(i+1, min(3, len(num_cols))):
                            plt.figure()
                            sns.scatterplot(x=self.data[num_cols[i]], y=self.data[num_cols[j]])
                            plt.title(f"Scatter plot: {num_cols[i]} vs {num_cols[j]}")
                            plt.xlabel(num_cols[i])
                            plt.ylabel(num_cols[j])
                            plt.tight_layout()
                            
                            # Save figure
                            file_path = os.path.join(output_dir, f"scatter_{num_cols[i]}_{num_cols[j]}.png")
                            plt.savefig(file_path)
                            plt.close()
                            
                            visualizations[f"scatter_{num_cols[i]}_{num_cols[j]}"] = file_path
                            viz_count += 1
                
                elif viz_type == VisualizationType.BAR and len(cat_cols) > 0:
                    # Create bar plots for categorical columns
                    for col in cat_cols[:min(2, len(cat_cols))]:  # Limit to 2 columns
                        plt.figure()
                        value_counts = self.data[col].value_counts()
                        # Limit to top 10 categories
                        if len(value_counts) > 10:
                            value_counts = value_counts.nlargest(10)
                        sns.barplot(x=value_counts.index, y=value_counts.values)
                        plt.title(f"Frequency of {col}")
                        plt.xticks(rotation=45)
                        plt.tight_layout()
                        
                        # Save figure
                        file_path = os.path.join(output_dir, f"bar_{col}.png")
                        plt.savefig(file_path)
                        plt.close()
                        
                        visualizations[f"bar_{col}"] = file_path
                        viz_count += 1
                
                elif viz_type == VisualizationType.BOX and len(num_cols) > 0:
                    # Create box plots for numerical columns
                    plt.figure()
                    sns.boxplot(data=self.data[num_cols[:min(5, len(num_cols))]])  # Limit to 5 columns
                    plt.title("Box plots of numerical variables")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    
                    # Save figure
                    file_path = os.path.join(output_dir, "boxplot_numerical.png")
                    plt.savefig(file_path)
                    plt.close()
                    
                    visualizations["boxplot_numerical"] = file_path
                    viz_count += 1
                
                elif viz_type == VisualizationType.HEATMAP and len(num_cols) >= 2:
                    # Create correlation heatmap
                    plt.figure()
                    corr_matrix = self.data[num_cols].corr()
                    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
                    plt.title("Correlation Heatmap")
                    plt.tight_layout()
                    
                    # Save figure
                    file_path = os.path.join(output_dir, "correlation_heatmap.png")
                    plt.savefig(file_path)
                    plt.close()
                    
                    visualizations["correlation_heatmap"] = file_path
                    viz_count += 1
                
                elif viz_type == VisualizationType.PIE and len(cat_cols) > 0:
                    # Create pie charts for categorical columns
                    for col in cat_cols[:min(2, len(cat_cols))]:  # Limit to 2 columns
                        plt.figure()
                        value_counts = self.data[col].value_counts()
                        # Limit to top 5 categories + "Other"
                        if len(value_counts) > 5:
                            top_5 = value_counts.nlargest(5)
                            other_count = value_counts.sum() - top_5.sum()
                            top_5['Other'] = other_count
                            value_counts = top_5
                        plt.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%')
                        plt.title(f"Distribution of {col}")
                        plt.tight_layout()
                        
                        # Save figure
                        file_path = os.path.join(output_dir, f"pie_{col}.png")
                        plt.savefig(file_path)
                        plt.close()
                        
                        visualizations[f"pie_{col}"] = file_path
                        viz_count += 1
                
                elif viz_type == VisualizationType.PCA and len(num_cols) >= 3:
                    # Perform PCA and visualize
                    plt.figure()
                    
                    # Prepare data
                    X = self.data[num_cols].dropna()
                    if len(X) < 2:
                        continue
                    
                    # Standardize data
                    scaler = StandardScaler()
                    X_scaled = scaler.fit_transform(X)
                    
                    # Apply PCA
                    pca = PCA(n_components=2)
                    X_pca = pca.fit_transform(X_scaled)
                    
                    # Create DataFrame for plotting
                    pca_df = pd.DataFrame({
                        'PC1': X_pca[:, 0],
                        'PC2': X_pca[:, 1]
                    })
                    
                    # Add a categorical column for coloring if available
                    if len(cat_cols) > 0:
                        pca_df['category'] = self.data[cat_cols[0]].values[:len(pca_df)]
                        sns.scatterplot(x='PC1', y='PC2', hue='category', data=pca_df)
                    else:
                        sns.scatterplot(x='PC1', y='PC2', data=pca_df)
                    
                    plt.title("PCA: First two principal components")
                    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)")
                    plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)")
                    plt.tight_layout()
                    
                    # Save figure
                    file_path = os.path.join(output_dir, "pca_visualization.png")
                    plt.savefig(file_path)
                    plt.close()
                    
                    visualizations["pca_visualization"] = file_path
                    viz_count += 1
                
                elif viz_type == VisualizationType.TIME_SERIES and self.dataset_info.data_type == DataType.TIME_SERIES:
                    # Create time series plots
                    if self.options.time_column and self.options.time_column in self.data.columns:
                        # Get numerical columns (excluding time column)
                        ts_cols = [col for col in num_cols if col != self.options.time_column]
                        
                        if ts_cols:
                            plt.figure()
                            for col in ts_cols[:min(3, len(ts_cols))]:  # Limit to 3 columns
                                plt.plot(self.data[self.options.time_column], self.data[col], label=col)
                            plt.title("Time Series Plot")
                            plt.xlabel(self.options.time_column)
                            plt.legend()
                            plt.xticks(rotation=45)
                            plt.tight_layout()
                            
                            # Save figure
                            file_path = os.path.join(output_dir, "time_series_plot.png")
                            plt.savefig(file_path)
                            plt.close()
                            
                            visualizations["time_series_plot"] = file_path
                            viz_count += 1
            
            return visualizations
        
        except ImportError:
            logger.warning("matplotlib or seaborn not available for generating visualizations")
            return {}
        
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
            return {}
    
    def _generate_report(self, result: AnalysisResult) -> Optional[str]:
        """
        Generate a report of the analysis results.
        
        Args:
            result: AnalysisResult object
            
        Returns:
            Path to the generated report file
        """
        try:
            # Create output directory if needed
            output_dir = self.options.output_directory
            if output_dir is None:
                output_dir = os.path.join(os.path.dirname(result.dataset_info.file_path), "analysis_output")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate report based on format
            if self.options.report_format == "html":
                return self._generate_html_report(result, output_dir)
            elif self.options.report_format == "markdown":
                return self._generate_markdown_report(result, output_dir)
            elif self.options.report_format == "pdf":
                return self._generate_pdf_report(result, output_dir)
            else:
                logger.warning(f"Unsupported report format: {self.options.report_format}")
                return None
        
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return None
    
    def _generate_html_report(self, result: AnalysisResult, output_dir: str) -> str:
        """
        Generate an HTML report.
        
        Args:
            result: AnalysisResult object
            output_dir: Output directory
            
        Returns:
            Path to the generated HTML file
        """
        # Generate file name
        file_name = os.path.splitext(os.path.basename(result.dataset_info.file_path))[0]
        report_path = os.path.join(output_dir, f"{file_name}_analysis_report.html")
        
        # Generate HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Analysis Report: {file_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .visualization {{ margin: 20px 0; text-align: center; }}
                .visualization img {{ max-width: 100%; height: auto; }}
                .section {{ margin-bottom: 30px; }}
            </style>
        </head>
        <body>
            <h1>Data Analysis Report</h1>
            
            <div class="section">
                <h2>Dataset Information</h2>
                <p><strong>File:</strong> {os.path.basename(result.dataset_info.file_path)}</p>
                <p><strong>Data Type:</strong> {result.dataset_info.data_type.value}</p>
                <p><strong>Rows:</strong> {result.dataset_info.num_rows}</p>
                <p><strong>Columns:</strong> {result.dataset_info.num_columns}</p>
                <p><strong>Data Completeness:</strong> {result.descriptive_stats.get("data_completeness", 0):.2%}</p>
            </div>
        """
        
        # Add descriptive statistics
        if result.descriptive_stats and "numerical_stats" in result.descriptive_stats:
            html_content += """
            <div class="section">
                <h2>Descriptive Statistics</h2>
                <h3>Numerical Variables</h3>
                <table>
                    <tr>
                        <th>Variable</th>
                        <th>Count</th>
                        <th>Mean</th>
                        <th>Std</th>
                        <th>Min</th>
                        <th>25%</th>
                        <th>50%</th>
                        <th>75%</th>
                        <th>Max</th>
                    </tr>
            """
            
            for col, stats in result.descriptive_stats["numerical_stats"].items():
                html_content += f"""
                    <tr>
                        <td>{col}</td>
                        <td>{stats['count']}</td>
                        <td>{stats['mean']:.2f}</td>
                        <td>{stats['std']:.2f}</td>
                        <td>{stats['min']:.2f}</td>
                        <td>{stats['25%']:.2f}</td>
                        <td>{stats['50%']:.2f}</td>
                        <td>{stats['75%']:.2f}</td>
                        <td>{stats['max']:.2f}</td>
                    </tr>
                """
            
            html_content += """
                </table>
            """
        
        # Add categorical statistics
        if result.descriptive_stats and "categorical_stats" in result.descriptive_stats:
            html_content += """
                <h3>Categorical Variables</h3>
            """
            
            for col, counts in result.descriptive_stats["categorical_stats"].items():
                html_content += f"""
                <h4>{col}</h4>
                <table>
                    <tr>
                        <th>Value</th>
                        <th>Count</th>
                    </tr>
                """
                
                for value, count in counts.items():
                    html_content += f"""
                    <tr>
                        <td>{value}</td>
                        <td>{count}</td>
                    </tr>
                    """
                
                html_content += """
                </table>
                """
            
            html_content += """
            </div>
            """
        
        # Add visualizations
        if result.visualizations:
            html_content += """
            <div class="section">
                <h2>Visualizations</h2>
            """
            
            for name, path in result.visualizations.items():
                # Convert to relative path
                rel_path = os.path.relpath(path, output_dir)
                html_content += f"""
                <div class="visualization">
                    <h3>{name.replace('_', ' ').title()}</h3>
                    <img src="{rel_path}" alt="{name}">
                </div>
                """
            
            html_content += """
            </div>
            """
        
        # Add correlation analysis
        if result.correlation_matrix is not None:
            html_content += """
            <div class="section">
                <h2>Correlation Analysis</h2>
                <p>Correlations above {self.options.correlation_threshold} are highlighted.</p>
                <table>
                    <tr>
                        <th>Variable 1</th>
                        <th>Variable 2</th>
                        <th>Correlation</th>
                    </tr>
            """
            
            # Get correlations above threshold
            corr_data = result.correlation_matrix.unstack()
            corr_data = corr_data[corr_data < 1.0]  # Remove self-correlations
            high_corr = corr_data[abs(corr_data) >= self.options.correlation_threshold]
            
            if not high_corr.empty:
                for (var1, var2), corr in high_corr.items():
                    html_content += f"""
                    <tr>
                        <td>{var1}</td>
                        <td>{var2}</td>
                        <td>{corr:.4f}</td>
                    </tr>
                    """
            else:
                html_content += """
                    <tr>
                        <td colspan="3">No significant correlations found</td>
                    </tr>
                """
            
            html_content += """
                </table>
            </div>
            """
        
        # Add regression results
        if result.regression_results:
            html_content += """
            <div class="section">
                <h2>Regression Analysis</h2>
            """
            
            if "linear_regression" in result.regression_results:
                lr_result = result.regression_results["linear_regression"]
                html_content += f"""
                <h3>Linear Regression</h3>
                <p><strong>Target Variable:</strong> {lr_result['target_column']}</p>
                <p><strong>R-squared:</strong> {lr_result['r2']:.4f}</p>
                <p><strong>Mean Squared Error:</strong> {lr_result['mse']:.4f}</p>
                
                <h4>Coefficients</h4>
                <table>
                    <tr>
                        <th>Variable</th>
                        <th>Coefficient</th>
                    </tr>
                    <tr>
                        <td>(Intercept)</td>
                        <td>{lr_result['intercept']:.4f}</td>
                    </tr>
                """
                
                for var, coef in lr_result['coefficients'].items():
                    html_content += f"""
                    <tr>
                        <td>{var}</td>
                        <td>{coef:.4f}</td>
                    </tr>
                    """
                
                html_content += """
                </table>
                """
            
            if "random_forest_regression" in result.regression_results:
                rf_result = result.regression_results["random_forest_regression"]
                html_content += f"""
                <h3>Random Forest Regression</h3>
                <p><strong>Target Variable:</strong> {rf_result['target_column']}</p>
                <p><strong>R-squared:</strong> {rf_result['r2']:.4f}</p>
                <p><strong>Mean Squared Error:</strong> {rf_result['mse']:.4f}</p>
                
                <h4>Feature Importances</h4>
                <table>
                    <tr>
                        <th>Variable</th>
                        <th>Importance</th>
                    </tr>
                """
                
                # Sort by importance
                sorted_importances = sorted(rf_result['feature_importances'].items(), key=lambda x: x[1], reverse=True)
                for var, imp in sorted_importances:
                    html_content += f"""
                    <tr>
                        <td>{var}</td>
                        <td>{imp:.4f}</td>
                    </tr>
                    """
                
                html_content += """
                </table>
                """
            
            html_content += """
            </div>
            """
        
        # Add clustering results
        if result.clustering_results and "kmeans_clustering" in result.clustering_results:
            cluster_result = result.clustering_results["kmeans_clustering"]
            html_content += f"""
            <div class="section">
                <h2>Clustering Analysis</h2>
                <p><strong>Number of Clusters:</strong> {cluster_result['num_clusters']}</p>
                <p><strong>Inertia:</strong> {cluster_result['inertia']:.4f}</p>
                
                <h3>Cluster Sizes</h3>
                <table>
                    <tr>
                        <th>Cluster</th>
                        <th>Size</th>
                        <th>Percentage</th>
                    </tr>
            """
            
            for cluster_id, size in cluster_result['cluster_sizes'].items():
                percentage = size / result.dataset_info.num_rows * 100
                html_content += f"""
                <tr>
                    <td>Cluster {cluster_id}</td>
                    <td>{size}</td>
                    <td>{percentage:.2f}%</td>
                </tr>
                """
            
            html_content += """
                </table>
            </div>
            """
        
        # Add time series results
        if result.time_series_results:
            html_content += """
            <div class="section">
                <h2>Time Series Analysis</h2>
            """
            
            if "time_range" in result.time_series_results:
                time_range = result.time_series_results["time_range"]
                html_content += f"""
                <p><strong>Time Range:</strong> {time_range['start']} to {time_range['end']}</p>
                <p><strong>Duration:</strong> {time_range['duration']}</p>
                """
            
            if "seasonal_decomposition" in result.time_series_results:
                html_content += """
                <h3>Seasonal Decomposition</h3>
                <p>Last 5 values of each component are shown.</p>
                """
                
                for var, decomp in result.time_series_results["seasonal_decomposition"].items():
                    html_content += f"""
                    <h4>{var}</h4>
                    <p><strong>Period:</strong> {decomp['period']}</p>
                    
                    <table>
                        <tr>
                            <th>Component</th>
                            <th>Values (last 5)</th>
                        </tr>
                        <tr>
                            <td>Trend</td>
                            <td>{', '.join([f'{x:.2f}' for x in decomp['trend']])}</td>
                        </tr>
                        <tr>
                            <td>Seasonal</td>
                            <td>{', '.join([f'{x:.2f}' for x in decomp['seasonal']])}</td>
                        </tr>
                        <tr>
                            <td>Residual</td>
                            <td>{', '.join([f'{x:.2f}' for x in decomp['residual']])}</td>
                        </tr>
                    </table>
                    """
            
            if "forecasting" in result.time_series_results:
                html_content += """
                <h3>Forecasting</h3>
                """
                
                for var, forecast in result.time_series_results["forecasting"].items():
                    html_content += f"""
                    <h4>{var}</h4>
                    <p><strong>Trend:</strong> {'Increasing' if forecast['slope'] > 0 else 'Decreasing'} (slope: {forecast['slope']:.4f})</p>
                    <p><strong>Forecast (next {len(forecast['forecast'])} periods):</strong> {', '.join([f'{x:.2f}' for x in forecast['forecast']])}</p>
                    """
            
            html_content += """
            </div>
            """
        
        # Close HTML
        html_content += """
        </body>
        </html>
        """
        
        # Write to file
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        return report_path
    
    def _generate_markdown_report(self, result: AnalysisResult, output_dir: str) -> str:
        """
        Generate a Markdown report.
        
        Args:
            result: AnalysisResult object
            output_dir: Output directory
            
        Returns:
            Path to the generated Markdown file
        """
        # Generate file name
        file_name = os.path.splitext(os.path.basename(result.dataset_info.file_path))[0]
        report_path = os.path.join(output_dir, f"{file_name}_analysis_report.md")
        
        # Generate Markdown content
        md_content = f"""
# Data Analysis Report

## Dataset Information
- **File:** {os.path.basename(result.dataset_info.file_path)}
- **Data Type:** {result.dataset_info.data_type.value}
- **Rows:** {result.dataset_info.num_rows}
- **Columns:** {result.dataset_info.num_columns}
- **Data Completeness:** {result.descriptive_stats.get("data_completeness", 0):.2%}

"""
        
        # Add descriptive statistics
        if result.descriptive_stats and "numerical_stats" in result.descriptive_stats:
            md_content += """
## Descriptive Statistics

### Numerical Variables
| Variable | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|----------|-------|------|-----|-----|-----|-----|-----|-----|
"""
            
            for col, stats in result.descriptive_stats["numerical_stats"].items():
                md_content += f"| {col} | {stats['count']} | {stats['mean']:.2f} | {stats['std']:.2f} | {stats['min']:.2f} | {stats['25%']:.2f} | {stats['50%']:.2f} | {stats['75%']:.2f} | {stats['max']:.2f} |\n"
        
        # Add categorical statistics
        if result.descriptive_stats and "categorical_stats" in result.descriptive_stats:
            md_content += """
### Categorical Variables
"""
            
            for col, counts in result.descriptive_stats["categorical_stats"].items():
                md_content += f"""
#### {col}
| Value | Count |
|-------|-------|
"""
                
                for value, count in counts.items():
                    md_content += f"| {value} | {count} |\n"
        
        # Add visualizations
        if result.visualizations:
            md_content += """
## Visualizations
"""
            
            for name, path in result.visualizations.items():
                # Convert to relative path
                rel_path = os.path.relpath(path, output_dir)
                md_content += f"""
### {name.replace('_', ' ').title()}
![{name}]({rel_path})
"""
        
        # Add correlation analysis
        if result.correlation_matrix is not None:
            md_content += f"""
## Correlation Analysis
Correlations above {self.options.correlation_threshold} are shown.

| Variable 1 | Variable 2 | Correlation |
|------------|------------|-------------|
"""
            
            # Get correlations above threshold
            corr_data = result.correlation_matrix.unstack()
            corr_data = corr_data[corr_data < 1.0]  # Remove self-correlations
            high_corr = corr_data[abs(corr_data) >= self.options.correlation_threshold]
            
            if not high_corr.empty:
                for (var1, var2), corr in high_corr.items():
                    md_content += f"| {var1} | {var2} | {corr:.4f} |\n"
            else:
                md_content += "| - | - | No significant correlations found |\n"
        
        # Add regression results
        if result.regression_results:
            md_content += """
## Regression Analysis
"""
            
            if "linear_regression" in result.regression_results:
                lr_result = result.regression_results["linear_regression"]
                md_content += f"""
### Linear Regression
- **Target Variable:** {lr_result['target_column']}
- **R-squared:** {lr_result['r2']:.4f}
- **Mean Squared Error:** {lr_result['mse']:.4f}

#### Coefficients
| Variable | Coefficient |
|----------|-------------|
| (Intercept) | {lr_result['intercept']:.4f} |
"""
                
                for var, coef in lr_result['coefficients'].items():
                    md_content += f"| {var} | {coef:.4f} |\n"
            
            if "random_forest_regression" in result.regression_results:
                rf_result = result.regression_results["random_forest_regression"]
                md_content += f"""
### Random Forest Regression
- **Target Variable:** {rf_result['target_column']}
- **R-squared:** {rf_result['r2']:.4f}
- **Mean Squared Error:** {rf_result['mse']:.4f}

#### Feature Importances
| Variable | Importance |
|----------|------------|
"""
                
                # Sort by importance
                sorted_importances = sorted(rf_result['feature_importances'].items(), key=lambda x: x[1], reverse=True)
                for var, imp in sorted_importances:
                    md_content += f"| {var} | {imp:.4f} |\n"
        
        # Add clustering results
        if result.clustering_results and "kmeans_clustering" in result.clustering_results:
            cluster_result = result.clustering_results["kmeans_clustering"]
            md_content += f"""
## Clustering Analysis
- **Number of Clusters:** {cluster_result['num_clusters']}
- **Inertia:** {cluster_result['inertia']:.4f}

### Cluster Sizes
| Cluster | Size | Percentage |
|---------|------|------------|
"""
            
            for cluster_id, size in cluster_result['cluster_sizes'].items():
                percentage = size / result.dataset_info.num_rows * 100
                md_content += f"| Cluster {cluster_id} | {size} | {percentage:.2f}% |\n"
        
        # Add time series results
        if result.time_series_results:
            md_content += """
## Time Series Analysis
"""
            
            if "time_range" in result.time_series_results:
                time_range = result.time_series_results["time_range"]
                md_content += f"""
- **Time Range:** {time_range['start']} to {time_range['end']}
- **Duration:** {time_range['duration']}
"""
            
            if "seasonal_decomposition" in result.time_series_results:
                md_content += """
### Seasonal Decomposition
Last 5 values of each component are shown.

"""
                
                for var, decomp in result.time_series_results["seasonal_decomposition"].items():
                    md_content += f"""
#### {var}
- **Period:** {decomp['period']}

| Component | Values (last 5) |
|-----------|----------------|
| Trend | {', '.join([f'{x:.2f}' for x in decomp['trend']])} |
| Seasonal | {', '.join([f'{x:.2f}' for x in decomp['seasonal']])} |
| Residual | {', '.join([f'{x:.2f}' for x in decomp['residual']])} |
"""
            
            if "forecasting" in result.time_series_results:
                md_content += """
### Forecasting
"""
                
                for var, forecast in result.time_series_results["forecasting"].items():
                    trend_direction = 'Increasing' if forecast['slope'] > 0 else 'Decreasing'
                    md_content += f"""
#### {var}
- **Trend:** {trend_direction} (slope: {forecast['slope']:.4f})
- **Forecast (next {len(forecast['forecast'])} periods):** {', '.join([f'{x:.2f}' for x in forecast['forecast']])}
"""
        
        # Write to file
        with open(report_path, 'w') as f:
            f.write(md_content)
        
        return report_path
    
    def _generate_pdf_report(self, result: AnalysisResult, output_dir: str) -> Optional[str]:
        """
        Generate a PDF report.
        
        Args:
            result: AnalysisResult object
            output_dir: Output directory
            
        Returns:
            Path to the generated PDF file
        """
        try:
            # First generate a Markdown report
            md_path = self._generate_markdown_report(result, output_dir)
            
            # Generate file name for PDF
            file_name = os.path.splitext(os.path.basename(md_path))[0]
            pdf_path = os.path.join(output_dir, f"{file_name}.pdf")
            
            # Try to convert Markdown to PDF
            try:
                import pypandoc
                pypandoc.convert_file(md_path, 'pdf', outputfile=pdf_path)
                return pdf_path
            except ImportError:
                logger.warning("pypandoc not available for converting Markdown to PDF")
                return md_path
            except Exception as e:
                logger.error(f"Error converting Markdown to PDF: {e}")
                return md_path
        
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            return None


def analyze_data_file(file_path: str, 
                    analysis_types: List[AnalysisType] = None,
                    visualization_types: List[VisualizationType] = None,
                    **kwargs) -> AnalysisResult:
    """
    Analyze a data file.
    
    Args:
        file_path: Path to the data file
        analysis_types: List of analysis types to perform
        visualization_types: List of visualization types to generate
        **kwargs: Additional options for analysis
        
    Returns:
        AnalysisResult object containing the analysis results
    """
    # Set default analysis types if not provided
    if analysis_types is None:
        analysis_types = [AnalysisType.DESCRIPTIVE, AnalysisType.EXPLORATORY]
    
    # Set default visualization types if not provided
    if visualization_types is None:
        visualization_types = [VisualizationType.HISTOGRAM, VisualizationType.SCATTER, VisualizationType.CORRELATION]
    
    # Create options
    options = AnalysisOptions(
        analysis_types=analysis_types,
        visualization_types=visualization_types,
        **kwargs
    )
    
    # Create analyzer and analyze file
    analyzer = DataAnalyzer(options)
    return analyzer.analyze_file(file_path)


def generate_data_report(file_path: str, output_format: str = "html", 
                       output_directory: Optional[str] = None) -> Optional[str]:
    """
    Generate a data analysis report for a file.
    
    Args:
        file_path: Path to the data file
        output_format: Format of the report (html, markdown, pdf)
        output_directory: Directory to save the report
        
    Returns:
        Path to the generated report file
    """
    # Create options
    options = AnalysisOptions(
        generate_report=True,
        report_format=output_format,
        output_directory=output_directory
    )
    
    # Create analyzer and analyze file
    analyzer = DataAnalyzer(options)
    result = analyzer.analyze_file(file_path)
    
    return result.report_path


def compare_datasets(file_paths: List[str], 
                   analysis_types: List[AnalysisType] = None,
                   **kwargs) -> Dict[str, AnalysisResult]:
    """
    Compare multiple datasets.
    
    Args:
        file_paths: List of paths to data files
        analysis_types: List of analysis types to perform
        **kwargs: Additional options for analysis
        
    Returns:
        Dictionary mapping file paths to AnalysisResult objects
    """
    results = {}
    
    for file_path in file_paths:
        result = analyze_data_file(file_path, analysis_types, **kwargs)
        results[file_path] = result
    
    return results


def detect_anomalies(file_path: str, method: str = "zscore", 
                   threshold: float = 3.0) -> Dict[str, List[int]]:
    """
    Detect anomalies in a dataset.
    
    Args:
        file_path: Path to the data file
        method: Anomaly detection method ('zscore', 'iqr', 'isolation_forest')
        threshold: Threshold for anomaly detection
        
    Returns:
        Dictionary mapping column names to lists of anomalous row indices
    """
    try:
        # Load data
        data = pd.read_csv(file_path)
        
        # Get numerical columns
        num_cols = data.select_dtypes(include=['number']).columns
        
        anomalies = {}
        
        for col in num_cols:
            if method == "zscore":
                # Z-score method
                z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
                anomalies[col] = list(data.index[z_scores > threshold])
            
            elif method == "iqr":
                # IQR method
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                anomalies[col] = list(data.index[(data[col] < lower_bound) | (data[col] > upper_bound)])
            
            elif method == "isolation_forest":
                try:
                    from sklearn.ensemble import IsolationForest
                    
                    # Reshape for isolation forest
                    X = data[col].values.reshape(-1, 1)
                    
                    # Fit model
                    model = IsolationForest(contamination=0.1, random_state=42)
                    preds = model.fit_predict(X)
                    
                    # -1 indicates anomaly
                    anomalies[col] = list(data.index[preds == -1])
                
                except ImportError:
                    logger.warning("sklearn not available for Isolation Forest")
                    # Fall back to Z-score
                    z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
                    anomalies[col] = list(data.index[z_scores > threshold])
        
        return anomalies
    
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        return {}
"""