"""
SciPy Integration for Science Data Kit

This module provides comprehensive integration with SciPy for scientific computing,
including functions for optimization, interpolation, signal processing, statistics,
and more.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Union, Callable
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

# Import scipy with error handling
try:
    import scipy
    import scipy.optimize
    import scipy.interpolate
    import scipy.signal
    import scipy.stats
    import scipy.integrate
    import scipy.linalg
    import scipy.sparse
    import scipy.spatial
    import scipy.cluster
    SCIPY_AVAILABLE = True
except ImportError:
    logger.warning("SciPy is not installed. Please install it with 'pip install scipy'.")
    SCIPY_AVAILABLE = False


def check_scipy():
    """
    Check if SciPy is available.
    
    Returns:
        bool: True if SciPy is available, False otherwise.
    
    Raises:
        ImportError: If SciPy is not available.
    """
    if not SCIPY_AVAILABLE:
        raise ImportError("SciPy is not installed. Please install it with 'pip install scipy'.")
    return True


def optimize_function(
    func: Callable,
    x0: Union[float, List[float], np.ndarray],
    method: str = 'BFGS',
    bounds: Optional[List[Tuple[float, float]]] = None,
    constraints: Optional[List[Dict[str, Any]]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Optimize a function using SciPy's optimization routines.
    
    Args:
        func: The function to optimize.
        x0: Initial guess for the parameters.
        method: The optimization method to use.
        bounds: Bounds for the parameters.
        constraints: Constraints for the parameters.
        **kwargs: Additional keyword arguments to pass to the optimization function.
    
    Returns:
        A dictionary containing the optimization results.
    
    Raises:
        ImportError: If SciPy is not available.
    """
    check_scipy()
    
    try:
        if isinstance(x0, (int, float)):
            x0 = [x0]
        
        if method.lower() in ['bfgs', 'l-bfgs-b', 'cg', 'newton-cg', 'nelder-mead', 'powell']:
            result = scipy.optimize.minimize(func, x0, method=method, bounds=bounds, constraints=constraints, **kwargs)
        elif method.lower() == 'differential_evolution':
            if bounds is None:
                raise ValueError("Bounds must be provided for differential_evolution method")
            result = scipy.optimize.differential_evolution(func, bounds, **kwargs)
        elif method.lower() == 'basinhopping':
            result = scipy.optimize.basinhopping(func, x0, **kwargs)
        elif method.lower() == 'dual_annealing':
            if bounds is None:
                raise ValueError("Bounds must be provided for dual_annealing method")
            result = scipy.optimize.dual_annealing(func, bounds, **kwargs)
        else:
            raise ValueError(f"Unsupported optimization method: {method}")
        
        return {
            'x': result.x.tolist() if hasattr(result, 'x') else None,
            'fun': float(result.fun) if hasattr(result, 'fun') else None,
            'success': bool(result.success) if hasattr(result, 'success') else None,
            'message': str(result.message) if hasattr(result, 'message') else None,
            'nfev': int(result.nfev) if hasattr(result, 'nfev') else None,
            'nit': int(result.nit) if hasattr(result, 'nit') else None
        }
    except Exception as e:
        logger.error(f"Error optimizing function: {str(e)}")
        raise


def curve_fit(
    func: Callable,
    x: Union[List[float], np.ndarray],
    y: Union[List[float], np.ndarray],
    p0: Optional[Union[List[float], np.ndarray]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Fit a curve to data using SciPy's curve_fit function.
    
    Args:
        func: The function to fit.
        x: The x data.
        y: The y data.
        p0: Initial guess for the parameters.
        **kwargs: Additional keyword arguments to pass to curve_fit.
    
    Returns:
        A dictionary containing the fit results.
    
    Raises:
        ImportError: If SciPy is not available.
    """
    check_scipy()
    
    try:
        popt, pcov = scipy.optimize.curve_fit(func, x, y, p0=p0, **kwargs)
        perr = np.sqrt(np.diag(pcov))
        
        return {
            'parameters': popt.tolist(),
            'covariance': pcov.tolist(),
            'errors': perr.tolist()
        }
    except Exception as e:
        logger.error(f"Error fitting curve: {str(e)}")
        raise


def interpolate_data(
    x: Union[List[float], np.ndarray],
    y: Union[List[float], np.ndarray],
    kind: str = 'linear',
    x_new: Optional[Union[List[float], np.ndarray]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Interpolate data using SciPy's interpolation routines.
    
    Args:
        x: The x data.
        y: The y data.
        kind: The kind of interpolation to use.
        x_new: The x values to interpolate at. If None, returns the interpolation function.
        **kwargs: Additional keyword arguments to pass to the interpolation function.
    
    Returns:
        A dictionary containing the interpolation results.
    
    Raises:
        ImportError: If SciPy is not available.
    """
    check_scipy()
    
    try:
        if kind in ['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous', 'next']:
            f = scipy.interpolate.interp1d(x, y, kind=kind, **kwargs)
        elif kind == 'spline':
            f = scipy.interpolate.splrep(x, y, **kwargs)
        elif kind == 'rbf':
            f = scipy.interpolate.Rbf(x, y, **kwargs)
        else:
            raise ValueError(f"Unsupported interpolation kind: {kind}")
        
        if x_new is not None:
            if kind == 'spline':
                y_new = scipy.interpolate.splev(x_new, f)
            elif kind == 'rbf':
                y_new = f(x_new)
            else:
                y_new = f(x_new)
            
            return {
                'x_new': x_new.tolist() if isinstance(x_new, np.ndarray) else x_new,
                'y_new': y_new.tolist() if isinstance(y_new, np.ndarray) else y_new
            }
        else:
            return {
                'interpolation_function': f
            }
    except Exception as e:
        logger.error(f"Error interpolating data: {str(e)}")
        raise


def filter_signal(
    signal: Union[List[float], np.ndarray],
    filter_type: str = 'lowpass',
    cutoff_freq: Union[float, List[float], Tuple[float, float]] = 0.1,
    order: int = 4,
    fs: float = 1.0,
    **kwargs
) -> np.ndarray:
    """
    Filter a signal using SciPy's signal processing routines.
    
    Args:
        signal: The signal to filter.
        filter_type: The type of filter to use ('lowpass', 'highpass', 'bandpass', 'bandstop').
        cutoff_freq: The cutoff frequency or frequencies.
        order: The order of the filter.
        fs: The sampling frequency.
        **kwargs: Additional keyword arguments to pass to the filter function.
    
    Returns:
        The filtered signal.
    
    Raises:
        ImportError: If SciPy is not available.
        ValueError: If the filter type is not supported.
    """
    check_scipy()
    
    try:
        nyquist = 0.5 * fs
        
        if filter_type == 'lowpass':
            b, a = scipy.signal.butter(order, cutoff_freq / nyquist, btype='low', **kwargs)
        elif filter_type == 'highpass':
            b, a = scipy.signal.butter(order, cutoff_freq / nyquist, btype='high', **kwargs)
        elif filter_type == 'bandpass':
            if not isinstance(cutoff_freq, (list, tuple)) or len(cutoff_freq) != 2:
                raise ValueError("cutoff_freq must be a list or tuple of length 2 for bandpass filter")
            b, a = scipy.signal.butter(order, [f / nyquist for f in cutoff_freq], btype='band', **kwargs)
        elif filter_type == 'bandstop':
            if not isinstance(cutoff_freq, (list, tuple)) or len(cutoff_freq) != 2:
                raise ValueError("cutoff_freq must be a list or tuple of length 2 for bandstop filter")
            b, a = scipy.signal.butter(order, [f / nyquist for f in cutoff_freq], btype='bandstop', **kwargs)
        else:
            raise ValueError(f"Unsupported filter type: {filter_type}")
        
        filtered_signal = scipy.signal.filtfilt(b, a, signal)
        return filtered_signal
    except Exception as e:
        logger.error(f"Error filtering signal: {str(e)}")
        raise


def compute_fft(
    signal: Union[List[float], np.ndarray],
    fs: float = 1.0,
    **kwargs
) -> Dict[str, np.ndarray]:
    """
    Compute the Fast Fourier Transform of a signal.
    
    Args:
        signal: The signal to transform.
        fs: The sampling frequency.
        **kwargs: Additional keyword arguments to pass to the FFT function.
    
    Returns:
        A dictionary containing the frequencies and FFT values.
    
    Raises:
        ImportError: If SciPy is not available.
    """
    check_scipy()
    
    try:
        n = len(signal)
        fft_values = scipy.fft.fft(signal, **kwargs)
        freqs = scipy.fft.fftfreq(n, 1/fs)
        
        # Only return the positive frequencies
        pos_mask = freqs >= 0
        freqs = freqs[pos_mask]
        fft_values = fft_values[pos_mask]
        
        # Compute magnitude
        magnitude = np.abs(fft_values)
        
        # Compute phase
        phase = np.angle(fft_values)
        
        return {
            'frequencies': freqs,
            'fft_values': fft_values,
            'magnitude': magnitude,
            'phase': phase
        }
    except Exception as e:
        logger.error(f"Error computing FFT: {str(e)}")
        raise


def compute_statistics(
    data: Union[List[float], np.ndarray],
    **kwargs
) -> Dict[str, float]:
    """
    Compute statistical measures using SciPy's stats module.
    
    Args:
        data: The data to analyze.
        **kwargs: Additional keyword arguments to pass to the statistics functions.
    
    Returns:
        A dictionary containing the computed statistics.
    
    Raises:
        ImportError: If SciPy is not available.
    """
    check_scipy()
    
    try:
        stats = {
            'mean': float(scipy.stats.tmean(data, **kwargs)),
            'median': float(scipy.stats.median_abs_deviation(data, **kwargs)),
            'std': float(scipy.stats.tstd(data, **kwargs)),
            'skewness': float(scipy.stats.skew(data, **kwargs)),
            'kurtosis': float(scipy.stats.kurtosis(data, **kwargs)),
            'min': float(np.min(data)),
            'max': float(np.max(data)),
            'range': float(np.max(data) - np.min(data)),
            'iqr': float(scipy.stats.iqr(data, **kwargs)),
            'sem': float(scipy.stats.sem(data, **kwargs))
        }
        return stats
    except Exception as e:
        logger.error(f"Error computing statistics: {str(e)}")
        raise


def perform_hypothesis_test(
    test_type: str,
    sample1: Union[List[float], np.ndarray],
    sample2: Optional[Union[List[float], np.ndarray]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Perform a hypothesis test using SciPy's stats module.
    
    Args:
        test_type: The type of test to perform ('ttest_ind', 'ttest_rel', 'ttest_1samp', 'mannwhitneyu', 'wilcoxon', 'ks_2samp', 'f_oneway', 'kruskal').
        sample1: The first sample.
        sample2: The second sample (if needed for the test).
        **kwargs: Additional keyword arguments to pass to the test function.
    
    Returns:
        A dictionary containing the test results.
    
    Raises:
        ImportError: If SciPy is not available.
        ValueError: If the test type is not supported.
    """
    check_scipy()
    
    try:
        if test_type == 'ttest_ind':
            if sample2 is None:
                raise ValueError("sample2 must be provided for ttest_ind")
            stat, pvalue = scipy.stats.ttest_ind(sample1, sample2, **kwargs)
        elif test_type == 'ttest_rel':
            if sample2 is None:
                raise ValueError("sample2 must be provided for ttest_rel")
            stat, pvalue = scipy.stats.ttest_rel(sample1, sample2, **kwargs)
        elif test_type == 'ttest_1samp':
            if 'popmean' not in kwargs:
                raise ValueError("popmean must be provided for ttest_1samp")
            stat, pvalue = scipy.stats.ttest_1samp(sample1, kwargs.pop('popmean'), **kwargs)
        elif test_type == 'mannwhitneyu':
            if sample2 is None:
                raise ValueError("sample2 must be provided for mannwhitneyu")
            stat, pvalue = scipy.stats.mannwhitneyu(sample1, sample2, **kwargs)
        elif test_type == 'wilcoxon':
            if sample2 is None:
                stat, pvalue = scipy.stats.wilcoxon(sample1, **kwargs)
            else:
                stat, pvalue = scipy.stats.wilcoxon(sample1, sample2, **kwargs)
        elif test_type == 'ks_2samp':
            if sample2 is None:
                raise ValueError("sample2 must be provided for ks_2samp")
            stat, pvalue = scipy.stats.ks_2samp(sample1, sample2, **kwargs)
        elif test_type == 'f_oneway':
            if sample2 is None:
                raise ValueError("At least two samples must be provided for f_oneway")
            samples = [sample1]
            if isinstance(sample2, list) and all(isinstance(s, (list, np.ndarray)) for s in sample2):
                samples.extend(sample2)
            else:
                samples.append(sample2)
            stat, pvalue = scipy.stats.f_oneway(*samples, **kwargs)
        elif test_type == 'kruskal':
            if sample2 is None:
                raise ValueError("At least two samples must be provided for kruskal")
            samples = [sample1]
            if isinstance(sample2, list) and all(isinstance(s, (list, np.ndarray)) for s in sample2):
                samples.extend(sample2)
            else:
                samples.append(sample2)
            stat, pvalue = scipy.stats.kruskal(*samples, **kwargs)
        else:
            raise ValueError(f"Unsupported test type: {test_type}")
        
        return {
            'statistic': float(stat),
            'p_value': float(pvalue),
            'significant': bool(pvalue < 0.05)
        }
    except Exception as e:
        logger.error(f"Error performing hypothesis test: {str(e)}")
        raise


def fit_distribution(
    data: Union[List[float], np.ndarray],
    dist_name: str = 'norm',
    **kwargs
) -> Dict[str, Any]:
    """
    Fit a probability distribution to data using SciPy's stats module.
    
    Args:
        data: The data to fit.
        dist_name: The name of the distribution to fit.
        **kwargs: Additional keyword arguments to pass to the fit function.
    
    Returns:
        A dictionary containing the fit results.
    
    Raises:
        ImportError: If SciPy is not available.
        ValueError: If the distribution is not supported.
    """
    check_scipy()
    
    try:
        # Get the distribution
        if hasattr(scipy.stats, dist_name):
            dist = getattr(scipy.stats, dist_name)
        else:
            raise ValueError(f"Unsupported distribution: {dist_name}")
        
        # Fit the distribution
        params = dist.fit(data, **kwargs)
        
        # Get parameter names
        if hasattr(dist, 'shapes'):
            shape_names = dist.shapes.split(',') if dist.shapes else []
            param_names = shape_names + ['loc', 'scale']
        else:
            param_names = ['loc', 'scale']
        
        # Create a dictionary of parameters
        param_dict = dict(zip(param_names, params))
        
        # Calculate goodness of fit
        ks_stat, ks_pvalue = scipy.stats.kstest(data, dist_name, params)
        
        return {
            'distribution': dist_name,
            'parameters': param_dict,
            'ks_statistic': float(ks_stat),
            'ks_p_value': float(ks_pvalue),
            'good_fit': bool(ks_pvalue > 0.05)
        }
    except Exception as e:
        logger.error(f"Error fitting distribution: {str(e)}")
        raise


def integrate_function(
    func: Callable,
    a: float,
    b: float,
    method: str = 'quad',
    **kwargs
) -> Dict[str, float]:
    """
    Integrate a function using SciPy's integration routines.
    
    Args:
        func: The function to integrate.
        a: The lower limit of integration.
        b: The upper limit of integration.
        method: The integration method to use ('quad', 'romberg', 'simpson', 'trapz').
        **kwargs: Additional keyword arguments to pass to the integration function.
    
    Returns:
        A dictionary containing the integration results.
    
    Raises:
        ImportError: If SciPy is not available.
        ValueError: If the method is not supported.
    """
    check_scipy()
    
    try:
        if method == 'quad':
            result, error = scipy.integrate.quad(func, a, b, **kwargs)
            return {'result': float(result), 'error': float(error)}
        elif method == 'romberg':
            result = scipy.integrate.romberg(func, a, b, **kwargs)
            return {'result': float(result)}
        elif method == 'simpson':
            # For simpson, we need to evaluate the function at points
            n = kwargs.pop('n', 100)
            x = np.linspace(a, b, n)
            y = np.array([func(xi) for xi in x])
            result = scipy.integrate.simpson(y, x, **kwargs)
            return {'result': float(result)}
        elif method == 'trapz':
            # For trapz, we need to evaluate the function at points
            n = kwargs.pop('n', 100)
            x = np.linspace(a, b, n)
            y = np.array([func(xi) for xi in x])
            result = scipy.integrate.trapz(y, x, **kwargs)
            return {'result': float(result)}
        else:
            raise ValueError(f"Unsupported integration method: {method}")
    except Exception as e:
        logger.error(f"Error integrating function: {str(e)}")
        raise


def solve_ode(
    func: Callable,
    y0: Union[float, List[float], np.ndarray],
    t_span: Tuple[float, float],
    t_eval: Optional[Union[List[float], np.ndarray]] = None,
    method: str = 'RK45',
    **kwargs
) -> Dict[str, np.ndarray]:
    """
    Solve an ordinary differential equation using SciPy's ODE solvers.
    
    Args:
        func: The function defining the ODE system (dy/dt = func(t, y)).
        y0: The initial conditions.
        t_span: The time span to solve over (t0, tf).
        t_eval: The times at which to evaluate the solution. If None, the solver's internal steps are used.
        method: The integration method to use.
        **kwargs: Additional keyword arguments to pass to the ODE solver.
    
    Returns:
        A dictionary containing the solution.
    
    Raises:
        ImportError: If SciPy is not available.
    """
    check_scipy()
    
    try:
        sol = scipy.integrate.solve_ivp(func, t_span, y0, method=method, t_eval=t_eval, **kwargs)
        
        return {
            't': sol.t,
            'y': sol.y,
            'success': bool(sol.success),
            'message': str(sol.message),
            'nfev': int(sol.nfev),
            'njev': int(sol.njev) if hasattr(sol, 'njev') else None,
            'nlu': int(sol.nlu) if hasattr(sol, 'nlu') else None
        }
    except Exception as e:
        logger.error(f"Error solving ODE: {str(e)}")
        raise


def perform_clustering(
    data: Union[List[List[float]], np.ndarray],
    method: str = 'kmeans',
    n_clusters: int = 2,
    **kwargs
) -> Dict[str, Any]:
    """
    Perform clustering on data using SciPy's clustering routines.
    
    Args:
        data: The data to cluster.
        method: The clustering method to use ('kmeans', 'hierarchical', 'dbscan').
        n_clusters: The number of clusters to find.
        **kwargs: Additional keyword arguments to pass to the clustering function.
    
    Returns:
        A dictionary containing the clustering results.
    
    Raises:
        ImportError: If SciPy is not available.
        ValueError: If the method is not supported.
    """
    check_scipy()
    
    try:
        if method == 'kmeans':
            centroids, labels = scipy.cluster.vq.kmeans2(data, n_clusters, **kwargs)
            return {
                'centroids': centroids.tolist(),
                'labels': labels.tolist()
            }
        elif method == 'hierarchical':
            Z = scipy.cluster.hierarchy.linkage(data, **kwargs)
            labels = scipy.cluster.hierarchy.fcluster(Z, n_clusters, criterion='maxclust')
            return {
                'linkage_matrix': Z.tolist(),
                'labels': labels.tolist()
            }
        elif method == 'dbscan':
            # For DBSCAN, we need to use scikit-learn
            try:
                from sklearn.cluster import DBSCAN
                dbscan = DBSCAN(n_clusters=n_clusters, **kwargs)
                labels = dbscan.fit_predict(data)
                return {
                    'labels': labels.tolist()
                }
            except ImportError:
                raise ImportError("scikit-learn is not installed. Please install it with 'pip install scikit-learn'.")
        else:
            raise ValueError(f"Unsupported clustering method: {method}")
    except Exception as e:
        logger.error(f"Error performing clustering: {str(e)}")
        raise


def compute_distance_matrix(
    data: Union[List[List[float]], np.ndarray],
    metric: str = 'euclidean',
    **kwargs
) -> np.ndarray:
    """
    Compute a distance matrix using SciPy's spatial distance functions.
    
    Args:
        data: The data points.
        metric: The distance metric to use.
        **kwargs: Additional keyword arguments to pass to the distance function.
    
    Returns:
        The distance matrix.
    
    Raises:
        ImportError: If SciPy is not available.
    """
    check_scipy()
    
    try:
        return scipy.spatial.distance.pdist(data, metric=metric, **kwargs)
    except Exception as e:
        logger.error(f"Error computing distance matrix: {str(e)}")
        raise