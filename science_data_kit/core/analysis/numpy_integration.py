"""
NumPy Integration for Science Data Kit

This module provides comprehensive integration with NumPy for numerical computing,
including functions for array creation, manipulation, mathematical operations,
and statistical analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Union, Callable
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

# Import numpy with error handling
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    logger.warning("NumPy is not installed. Please install it with 'pip install numpy'.")
    NUMPY_AVAILABLE = False


def check_numpy():
    """
    Check if NumPy is available.
    
    Returns:
        bool: True if NumPy is available, False otherwise.
    
    Raises:
        ImportError: If NumPy is not available.
    """
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is not installed. Please install it with 'pip install numpy'.")
    return True


def create_array(
    data: Union[List, Tuple, pd.DataFrame, pd.Series, np.ndarray],
    dtype: Optional[np.dtype] = None
) -> np.ndarray:
    """
    Create a NumPy array from various data types.
    
    Args:
        data: The data to convert to a NumPy array.
        dtype: The desired data type for the array.
    
    Returns:
        A NumPy array.
    
    Raises:
        ImportError: If NumPy is not available.
    """
    check_numpy()
    
    try:
        if isinstance(data, pd.DataFrame):
            return data.values
        elif isinstance(data, pd.Series):
            return data.values
        else:
            return np.array(data, dtype=dtype)
    except Exception as e:
        logger.error(f"Error creating NumPy array: {str(e)}")
        raise


def array_info(arr: np.ndarray) -> Dict[str, Any]:
    """
    Get information about a NumPy array.
    
    Args:
        arr: The NumPy array to get information about.
    
    Returns:
        A dictionary containing information about the array.
    
    Raises:
        ImportError: If NumPy is not available.
    """
    check_numpy()
    
    try:
        info = {
            'shape': arr.shape,
            'size': arr.size,
            'ndim': arr.ndim,
            'dtype': str(arr.dtype),
            'itemsize': arr.itemsize,
            'nbytes': arr.nbytes,
            'min': arr.min() if arr.size > 0 else None,
            'max': arr.max() if arr.size > 0 else None,
            'mean': arr.mean() if arr.size > 0 else None,
            'std': arr.std() if arr.size > 0 else None
        }
        return info
    except Exception as e:
        logger.error(f"Error getting array information: {str(e)}")
        return {}


def reshape_array(
    arr: np.ndarray,
    shape: Tuple[int, ...],
    order: str = 'C'
) -> np.ndarray:
    """
    Reshape a NumPy array.
    
    Args:
        arr: The NumPy array to reshape.
        shape: The new shape.
        order: The order of the elements ('C' for row-major, 'F' for column-major).
    
    Returns:
        The reshaped array.
    
    Raises:
        ImportError: If NumPy is not available.
    """
    check_numpy()
    
    try:
        return arr.reshape(shape, order=order)
    except Exception as e:
        logger.error(f"Error reshaping array: {str(e)}")
        raise


def concatenate_arrays(
    arrays: List[np.ndarray],
    axis: int = 0
) -> np.ndarray:
    """
    Concatenate NumPy arrays.
    
    Args:
        arrays: The arrays to concatenate.
        axis: The axis along which to concatenate.
    
    Returns:
        The concatenated array.
    
    Raises:
        ImportError: If NumPy is not available.
    """
    check_numpy()
    
    try:
        return np.concatenate(arrays, axis=axis)
    except Exception as e:
        logger.error(f"Error concatenating arrays: {str(e)}")
        raise


def split_array(
    arr: np.ndarray,
    indices_or_sections: Union[int, List[int]],
    axis: int = 0
) -> List[np.ndarray]:
    """
    Split a NumPy array into multiple sub-arrays.
    
    Args:
        arr: The array to split.
        indices_or_sections: If an integer, the number of equal-sized sub-arrays to create.
                            If a list of integers, the indices where the array should be split.
        axis: The axis along which to split.
    
    Returns:
        A list of sub-arrays.
    
    Raises:
        ImportError: If NumPy is not available.
    """
    check_numpy()
    
    try:
        return np.split(arr, indices_or_sections, axis=axis)
    except Exception as e:
        logger.error(f"Error splitting array: {str(e)}")
        raise


def apply_function(
    arr: np.ndarray,
    func: Callable,
    axis: Optional[int] = None,
    **kwargs
) -> np.ndarray:
    """
    Apply a function to a NumPy array.
    
    Args:
        arr: The array to apply the function to.
        func: The function to apply.
        axis: The axis along which to apply the function.
        **kwargs: Additional keyword arguments to pass to the function.
    
    Returns:
        The result of applying the function.
    
    Raises:
        ImportError: If NumPy is not available.
    """
    check_numpy()
    
    try:
        if axis is None:
            return func(arr, **kwargs)
        else:
            return np.apply_along_axis(func, axis, arr, **kwargs)
    except Exception as e:
        logger.error(f"Error applying function: {str(e)}")
        raise


def calculate_statistics(
    arr: np.ndarray,
    axis: Optional[int] = None
) -> Dict[str, Union[float, np.ndarray]]:
    """
    Calculate basic statistics for a NumPy array.
    
    Args:
        arr: The array to calculate statistics for.
        axis: The axis along which to calculate statistics.
    
    Returns:
        A dictionary containing the calculated statistics.
    
    Raises:
        ImportError: If NumPy is not available.
    """
    check_numpy()
    
    try:
        stats = {
            'min': np.min(arr, axis=axis),
            'max': np.max(arr, axis=axis),
            'mean': np.mean(arr, axis=axis),
            'median': np.median(arr, axis=axis),
            'std': np.std(arr, axis=axis),
            'var': np.var(arr, axis=axis),
            'sum': np.sum(arr, axis=axis),
            'prod': np.prod(arr, axis=axis)
        }
        return stats
    except Exception as e:
        logger.error(f"Error calculating statistics: {str(e)}")
        return {}


def perform_linear_algebra(
    operation: str,
    a: np.ndarray,
    b: Optional[np.ndarray] = None,
    **kwargs
) -> np.ndarray:
    """
    Perform linear algebra operations on NumPy arrays.
    
    Args:
        operation: The operation to perform ('dot', 'matmul', 'inv', 'det', 'eig', 'svd', 'solve', 'lstsq').
        a: The first array.
        b: The second array (if needed for the operation).
        **kwargs: Additional keyword arguments to pass to the operation.
    
    Returns:
        The result of the operation.
    
    Raises:
        ImportError: If NumPy is not available.
        ValueError: If the operation is not supported.
    """
    check_numpy()
    
    try:
        if operation == 'dot':
            return np.dot(a, b, **kwargs)
        elif operation == 'matmul':
            return np.matmul(a, b, **kwargs)
        elif operation == 'inv':
            return np.linalg.inv(a, **kwargs)
        elif operation == 'det':
            return np.linalg.det(a, **kwargs)
        elif operation == 'eig':
            return np.linalg.eig(a, **kwargs)
        elif operation == 'svd':
            return np.linalg.svd(a, **kwargs)
        elif operation == 'solve':
            return np.linalg.solve(a, b, **kwargs)
        elif operation == 'lstsq':
            return np.linalg.lstsq(a, b, **kwargs)[0]
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    except Exception as e:
        logger.error(f"Error performing linear algebra operation: {str(e)}")
        raise


def generate_random_data(
    distribution: str,
    size: Tuple[int, ...],
    **kwargs
) -> np.ndarray:
    """
    Generate random data using NumPy's random module.
    
    Args:
        distribution: The distribution to use ('uniform', 'normal', 'poisson', 'binomial', 'exponential', 'beta', 'gamma').
        size: The shape of the output array.
        **kwargs: Additional keyword arguments to pass to the distribution function.
    
    Returns:
        An array of random values.
    
    Raises:
        ImportError: If NumPy is not available.
        ValueError: If the distribution is not supported.
    """
    check_numpy()
    
    try:
        if distribution == 'uniform':
            return np.random.uniform(size=size, **kwargs)
        elif distribution == 'normal':
            return np.random.normal(size=size, **kwargs)
        elif distribution == 'poisson':
            return np.random.poisson(size=size, **kwargs)
        elif distribution == 'binomial':
            return np.random.binomial(size=size, **kwargs)
        elif distribution == 'exponential':
            return np.random.exponential(size=size, **kwargs)
        elif distribution == 'beta':
            return np.random.beta(size=size, **kwargs)
        elif distribution == 'gamma':
            return np.random.gamma(size=size, **kwargs)
        else:
            raise ValueError(f"Unsupported distribution: {distribution}")
    except Exception as e:
        logger.error(f"Error generating random data: {str(e)}")
        raise


def save_array(
    arr: np.ndarray,
    file_path: Union[str, Path],
    format: str = 'npy',
    **kwargs
) -> str:
    """
    Save a NumPy array to a file.
    
    Args:
        arr: The array to save.
        file_path: The path to save the array to.
        format: The format to save the array in ('npy', 'npz', 'txt', 'csv').
        **kwargs: Additional keyword arguments to pass to the saving function.
    
    Returns:
        The path to the saved file.
    
    Raises:
        ImportError: If NumPy is not available.
        ValueError: If the format is not supported.
    """
    check_numpy()
    
    try:
        # Convert to Path object
        path = Path(file_path)
        
        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'npy':
            np.save(path, arr, **kwargs)
        elif format == 'npz':
            np.savez(path, arr, **kwargs)
        elif format == 'txt':
            np.savetxt(path, arr, **kwargs)
        elif format == 'csv':
            np.savetxt(path, arr, delimiter=',', **kwargs)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return str(path)
    except Exception as e:
        logger.error(f"Error saving array: {str(e)}")
        raise


def load_array(
    file_path: Union[str, Path],
    format: str = 'npy',
    **kwargs
) -> np.ndarray:
    """
    Load a NumPy array from a file.
    
    Args:
        file_path: The path to the file to load.
        format: The format of the file ('npy', 'npz', 'txt', 'csv').
        **kwargs: Additional keyword arguments to pass to the loading function.
    
    Returns:
        The loaded array.
    
    Raises:
        ImportError: If NumPy is not available.
        ValueError: If the format is not supported.
    """
    check_numpy()
    
    try:
        # Convert to Path object
        path = Path(file_path)
        
        if format == 'npy':
            return np.load(path, **kwargs)
        elif format == 'npz':
            return np.load(path, **kwargs)['arr_0']
        elif format == 'txt':
            return np.loadtxt(path, **kwargs)
        elif format == 'csv':
            return np.loadtxt(path, delimiter=',', **kwargs)
        else:
            raise ValueError(f"Unsupported format: {format}")
    except Exception as e:
        logger.error(f"Error loading array: {str(e)}")
        raise


def convert_to_dataframe(
    arr: np.ndarray,
    columns: Optional[List[str]] = None,
    index: Optional[Union[List, np.ndarray]] = None
) -> pd.DataFrame:
    """
    Convert a NumPy array to a pandas DataFrame.
    
    Args:
        arr: The array to convert.
        columns: Column names for the DataFrame.
        index: Index for the DataFrame.
    
    Returns:
        A pandas DataFrame.
    
    Raises:
        ImportError: If NumPy is not available.
    """
    check_numpy()
    
    try:
        return pd.DataFrame(arr, columns=columns, index=index)
    except Exception as e:
        logger.error(f"Error converting to DataFrame: {str(e)}")
        raise


def convert_from_dataframe(
    df: pd.DataFrame,
    include_index: bool = False,
    include_columns: bool = False
) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    Convert a pandas DataFrame to a NumPy array.
    
    Args:
        df: The DataFrame to convert.
        include_index: Whether to include the index as a separate array.
        include_columns: Whether to include the column names as a separate array.
    
    Returns:
        If include_index and include_columns are False, returns a NumPy array of the DataFrame values.
        If either include_index or include_columns is True, returns a tuple of arrays.
    
    Raises:
        ImportError: If NumPy is not available.
    """
    check_numpy()
    
    try:
        values = df.values
        
        if include_index and include_columns:
            return values, np.array(df.index), np.array(df.columns)
        elif include_index:
            return values, np.array(df.index)
        elif include_columns:
            return values, np.array(df.columns)
        else:
            return values
    except Exception as e:
        logger.error(f"Error converting from DataFrame: {str(e)}")
        raise