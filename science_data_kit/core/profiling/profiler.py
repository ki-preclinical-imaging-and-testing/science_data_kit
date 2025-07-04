"""
Performance Profiler for Science Data Kit

This module provides tools for profiling code execution and identifying performance bottlenecks.
"""

import time
import cProfile
import pstats
import io
import logging
import threading
import functools
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from collections import defaultdict

class Profiler:
    """
    A performance profiler for tracking execution times and identifying bottlenecks.
    
    This class provides methods for:
    - Profiling function execution times
    - Tracking memory usage
    - Identifying slow operations
    - Generating performance reports
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implement singleton pattern with thread safety."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Profiler, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the profiler."""
        # Skip initialization if already initialized (singleton pattern)
        if self._initialized:
            return
            
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Profiling data storage
        self._profiles = {
            "function_calls": defaultdict(list),  # {function_name: [(execution_time, args_summary, timestamp)]}
            "code_blocks": defaultdict(list),     # {block_name: [(execution_time, timestamp)]}
            "slow_operations": [],                # [(name, execution_time, timestamp, details)]
            "detailed_profiles": {},              # {name: pstats object}
        }
        
        # Configuration
        self._slow_threshold = 1.0  # seconds
        self._max_profiles_per_function = 100
        self._enabled = True
        
        # Thread safety
        self._profiles_lock = threading.Lock()
        
        self._initialized = True
    
    def profile_function(self, func: Callable) -> Callable:
        """
        Decorator for profiling function execution time.
        
        Args:
            func: The function to profile
            
        Returns:
            Decorated function
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self._enabled:
                return func(*args, **kwargs)
                
            # Record start time
            start_time = time.time()
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Generate a summary of arguments (limited to avoid excessive memory usage)
            args_summary = str(args)[:100] + ('...' if len(str(args)) > 100 else '')
            if kwargs:
                kwargs_summary = str(kwargs)[:100] + ('...' if len(str(kwargs)) > 100 else '')
                args_summary += f", {kwargs_summary}"
            
            # Record the profile data
            with self._profiles_lock:
                function_name = f"{func.__module__}.{func.__name__}"
                self._profiles["function_calls"][function_name].append((
                    execution_time,
                    args_summary,
                    time.time()
                ))
                
                # Limit the number of profiles stored per function
                if len(self._profiles["function_calls"][function_name]) > self._max_profiles_per_function:
                    self._profiles["function_calls"][function_name].pop(0)
                
                # Check if this is a slow operation
                if execution_time > self._slow_threshold:
                    self._profiles["slow_operations"].append((
                        function_name,
                        execution_time,
                        time.time(),
                        {"args_summary": args_summary}
                    ))
                    
                    # Log slow operation
                    self.logger.warning(
                        f"Slow function detected: {function_name} ({execution_time:.2f}s)"
                    )
            
            return result
        
        return wrapper
    
    def start_block_profile(self, name: str) -> int:
        """
        Start profiling a block of code.
        
        Args:
            name: Name of the code block
            
        Returns:
            Start timestamp (can be used with end_block_profile)
        """
        if not self._enabled:
            return 0
            
        return int(time.time() * 1000)  # milliseconds
    
    def end_block_profile(self, name: str, start_time: int) -> float:
        """
        End profiling a block of code and record the execution time.
        
        Args:
            name: Name of the code block
            start_time: Start timestamp from start_block_profile
            
        Returns:
            Execution time in seconds
        """
        if not self._enabled or not start_time:
            return 0.0
            
        # Calculate execution time
        end_time = int(time.time() * 1000)  # milliseconds
        execution_time = (end_time - start_time) / 1000.0  # seconds
        
        # Record the profile data
        with self._profiles_lock:
            self._profiles["code_blocks"][name].append((
                execution_time,
                time.time()
            ))
            
            # Check if this is a slow operation
            if execution_time > self._slow_threshold:
                self._profiles["slow_operations"].append((
                    f"Block: {name}",
                    execution_time,
                    time.time(),
                    {}
                ))
                
                # Log slow operation
                self.logger.warning(
                    f"Slow code block detected: {name} ({execution_time:.2f}s)"
                )
        
        return execution_time
    
    def detailed_profile(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """
        Run a detailed profile on a function using cProfile.
        
        Args:
            name: Name for this profile
            func: Function to profile
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Result of the function call
        """
        if not self._enabled:
            return func(*args, **kwargs)
            
        # Create a cProfile.Profile instance
        profiler = cProfile.Profile()
        
        # Start profiling
        profiler.enable()
        
        # Call the function
        result = func(*args, **kwargs)
        
        # Stop profiling
        profiler.disable()
        
        # Create a StringIO object to capture the stats output
        s = io.StringIO()
        
        # Create a pstats object and sort by cumulative time
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        
        # Store the pstats object
        with self._profiles_lock:
            self._profiles["detailed_profiles"][name] = ps
        
        return result
    
    def get_function_profiles(self, function_name: Optional[str] = None) -> Dict[str, List[Tuple[float, str, float]]]:
        """
        Get profiles for functions.
        
        Args:
            function_name: Optional name of function to get profiles for
            
        Returns:
            Dictionary of function profiles
        """
        with self._profiles_lock:
            if function_name:
                return {function_name: list(self._profiles["function_calls"].get(function_name, []))}
            else:
                return {name: list(profiles) for name, profiles in self._profiles["function_calls"].items()}
    
    def get_block_profiles(self, block_name: Optional[str] = None) -> Dict[str, List[Tuple[float, float]]]:
        """
        Get profiles for code blocks.
        
        Args:
            block_name: Optional name of block to get profiles for
            
        Returns:
            Dictionary of block profiles
        """
        with self._profiles_lock:
            if block_name:
                return {block_name: list(self._profiles["code_blocks"].get(block_name, []))}
            else:
                return {name: list(profiles) for name, profiles in self._profiles["code_blocks"].items()}
    
    def get_slow_operations(self) -> List[Tuple[str, float, float, Dict[str, Any]]]:
        """
        Get a list of slow operations.
        
        Returns:
            List of slow operations
        """
        with self._profiles_lock:
            return list(self._profiles["slow_operations"])
    
    def get_detailed_profile(self, name: str) -> Optional[pstats.Stats]:
        """
        Get a detailed profile.
        
        Args:
            name: Name of the profile
            
        Returns:
            pstats.Stats object or None if not found
        """
        with self._profiles_lock:
            return self._profiles["detailed_profiles"].get(name)
    
    def print_detailed_profile(self, name: str, top_n: int = 20) -> str:
        """
        Print a detailed profile.
        
        Args:
            name: Name of the profile
            top_n: Number of functions to print
            
        Returns:
            String representation of the profile
        """
        ps = self.get_detailed_profile(name)
        if not ps:
            return f"No detailed profile found for '{name}'"
            
        # Create a StringIO object to capture the stats output
        s = io.StringIO()
        
        # Print stats to the StringIO object
        ps.stream = s
        ps.print_stats(top_n)
        
        # Get the string from the StringIO object
        return s.getvalue()
    
    def reset(self) -> None:
        """Reset all profiles."""
        with self._profiles_lock:
            self._profiles = {
                "function_calls": defaultdict(list),
                "code_blocks": defaultdict(list),
                "slow_operations": [],
                "detailed_profiles": {},
            }
    
    def set_slow_threshold(self, threshold: float) -> None:
        """
        Set the threshold for identifying slow operations.
        
        Args:
            threshold: Time threshold in seconds
        """
        with self._profiles_lock:
            self._slow_threshold = threshold
    
    def get_slow_threshold(self) -> float:
        """
        Get the current slow operation threshold.
        
        Returns:
            Current threshold in seconds
        """
        return self._slow_threshold
    
    def enable(self) -> None:
        """Enable profiling."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable profiling."""
        self._enabled = False
    
    def is_enabled(self) -> bool:
        """
        Check if profiling is enabled.
        
        Returns:
            True if profiling is enabled, False otherwise
        """
        return self._enabled
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of profiling data.
        
        Returns:
            Dictionary containing profiling summary
        """
        with self._profiles_lock:
            # Calculate average execution times for functions
            function_avg_times = {}
            for name, profiles in self._profiles["function_calls"].items():
                if profiles:
                    execution_times = [p[0] for p in profiles]
                    function_avg_times[name] = {
                        "avg_time": sum(execution_times) / len(execution_times),
                        "min_time": min(execution_times),
                        "max_time": max(execution_times),
                        "call_count": len(profiles),
                        "total_time": sum(execution_times)
                    }
            
            # Calculate average execution times for code blocks
            block_avg_times = {}
            for name, profiles in self._profiles["code_blocks"].items():
                if profiles:
                    execution_times = [p[0] for p in profiles]
                    block_avg_times[name] = {
                        "avg_time": sum(execution_times) / len(execution_times),
                        "min_time": min(execution_times),
                        "max_time": max(execution_times),
                        "call_count": len(profiles),
                        "total_time": sum(execution_times)
                    }
            
            # Get top slow operations
            slow_ops = sorted(self._profiles["slow_operations"], key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "function_profiles": function_avg_times,
                "block_profiles": block_avg_times,
                "slow_operations_count": len(self._profiles["slow_operations"]),
                "top_slow_operations": slow_ops,
                "detailed_profiles_count": len(self._profiles["detailed_profiles"]),
                "slow_threshold": self._slow_threshold,
                "enabled": self._enabled
            }


# Create a singleton instance
profiler = Profiler()

# Decorator for profiling functions
def profile(func=None, *, name=None):
    """
    Decorator for profiling function execution time.
    
    Can be used as @profile or @profile(name="custom_name")
    
    Args:
        func: The function to profile
        name: Optional custom name for the profile
        
    Returns:
        Decorated function
    """
    if func is None:
        # Called as @profile(name="custom_name")
        return lambda f: profiler.profile_function(f)
    
    # Called as @profile
    return profiler.profile_function(func)