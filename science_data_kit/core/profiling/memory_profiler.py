"""
Memory Profiler for Science Data Kit

This module provides tools for profiling memory usage and identifying memory bottlenecks.
"""

import os
import sys
import time
import threading
import tracemalloc
import functools
import gc
from typing import Dict, List, Any, Optional, Callable, Union, Tuple

class MemoryProfiler:
    """
    A memory profiler for tracking memory usage and identifying memory bottlenecks.
    
    This class provides methods for:
    - Tracking memory usage of functions and code blocks
    - Identifying memory leaks
    - Generating memory usage reports
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implement singleton pattern with thread safety."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MemoryProfiler, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the memory profiler."""
        # Skip initialization if already initialized (singleton pattern)
        if self._initialized:
            return
            
        # Memory profiling data storage
        self._profiles = {
            "function_memory": {},  # {function_name: [(memory_before, memory_after, peak_memory, timestamp)]}
            "block_memory": {},     # {block_name: [(memory_before, memory_after, peak_memory, timestamp)]}
            "snapshots": {},        # {snapshot_name: tracemalloc.Snapshot}
            "memory_leaks": [],     # [(name, memory_increase, timestamp, details)]
        }
        
        # Configuration
        self._memory_leak_threshold = 1024 * 1024  # 1 MB
        self._enabled = False
        self._tracemalloc_started = False
        
        # Thread safety
        self._profiles_lock = threading.Lock()
        
        self._initialized = True
    
    def start(self):
        """Start memory profiling."""
        if not self._tracemalloc_started:
            tracemalloc.start()
            self._tracemalloc_started = True
        self._enabled = True
    
    def stop(self):
        """Stop memory profiling."""
        self._enabled = False
        if self._tracemalloc_started:
            tracemalloc.stop()
            self._tracemalloc_started = False
    
    def is_enabled(self) -> bool:
        """
        Check if memory profiling is enabled.
        
        Returns:
            True if memory profiling is enabled, False otherwise
        """
        return self._enabled
    
    def profile_function_memory(self, func: Callable) -> Callable:
        """
        Decorator for profiling function memory usage.
        
        Args:
            func: The function to profile
            
        Returns:
            Decorated function
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self._enabled:
                return func(*args, **kwargs)
                
            # Force garbage collection to get more accurate memory measurements
            gc.collect()
            
            # Record memory before
            memory_before = tracemalloc.get_traced_memory()[0]
            
            # Take snapshot before
            snapshot_before = tracemalloc.take_snapshot()
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Record memory after
            memory_after = tracemalloc.get_traced_memory()[0]
            peak_memory = tracemalloc.get_traced_memory()[1]
            
            # Take snapshot after
            snapshot_after = tracemalloc.take_snapshot()
            
            # Calculate memory difference
            memory_diff = memory_after - memory_before
            
            # Record the profile data
            with self._profiles_lock:
                function_name = f"{func.__module__}.{func.__name__}"
                
                if function_name not in self._profiles["function_memory"]:
                    self._profiles["function_memory"][function_name] = []
                
                self._profiles["function_memory"][function_name].append((
                    memory_before,
                    memory_after,
                    peak_memory,
                    time.time()
                ))
                
                # Check if this might be a memory leak
                if memory_diff > self._memory_leak_threshold:
                    # Compare snapshots to find where memory increased
                    stats = snapshot_after.compare_to(snapshot_before, 'lineno')
                    top_stats = stats[:10]  # Get top 10 differences
                    
                    self._profiles["memory_leaks"].append((
                        function_name,
                        memory_diff,
                        time.time(),
                        {
                            "top_differences": [(str(stat), stat.size_diff) for stat in top_stats]
                        }
                    ))
            
            return result
        
        return wrapper
    
    def start_block_memory_profile(self, name: str) -> Tuple[int, tracemalloc.Snapshot]:
        """
        Start profiling memory usage for a block of code.
        
        Args:
            name: Name of the code block
            
        Returns:
            Tuple of (memory_before, snapshot_before)
        """
        if not self._enabled:
            return (0, None)
            
        # Force garbage collection
        gc.collect()
        
        # Record memory before
        memory_before = tracemalloc.get_traced_memory()[0]
        
        # Take snapshot before
        snapshot_before = tracemalloc.take_snapshot()
        
        return (memory_before, snapshot_before)
    
    def end_block_memory_profile(self, name: str, start_data: Tuple[int, tracemalloc.Snapshot]) -> int:
        """
        End profiling memory usage for a block of code and record the usage.
        
        Args:
            name: Name of the code block
            start_data: Tuple returned from start_block_memory_profile
            
        Returns:
            Memory difference in bytes
        """
        if not self._enabled or not start_data:
            return 0
            
        memory_before, snapshot_before = start_data
        
        # Record memory after
        memory_after = tracemalloc.get_traced_memory()[0]
        peak_memory = tracemalloc.get_traced_memory()[1]
        
        # Take snapshot after
        snapshot_after = tracemalloc.take_snapshot()
        
        # Calculate memory difference
        memory_diff = memory_after - memory_before
        
        # Record the profile data
        with self._profiles_lock:
            if name not in self._profiles["block_memory"]:
                self._profiles["block_memory"][name] = []
            
            self._profiles["block_memory"][name].append((
                memory_before,
                memory_after,
                peak_memory,
                time.time()
            ))
            
            # Check if this might be a memory leak
            if memory_diff > self._memory_leak_threshold:
                # Compare snapshots to find where memory increased
                stats = snapshot_after.compare_to(snapshot_before, 'lineno')
                top_stats = stats[:10]  # Get top 10 differences
                
                self._profiles["memory_leaks"].append((
                    f"Block: {name}",
                    memory_diff,
                    time.time(),
                    {
                        "top_differences": [(str(stat), stat.size_diff) for stat in top_stats]
                    }
                ))
        
        return memory_diff
    
    def take_snapshot(self, name: str) -> None:
        """
        Take a memory snapshot for later comparison.
        
        Args:
            name: Name for the snapshot
        """
        if not self._enabled:
            return
            
        snapshot = tracemalloc.take_snapshot()
        
        with self._profiles_lock:
            self._profiles["snapshots"][name] = snapshot
    
    def compare_snapshots(self, name1: str, name2: str, key_type: str = 'lineno', limit: int = 10) -> List[Tuple[str, int]]:
        """
        Compare two memory snapshots.
        
        Args:
            name1: Name of the first snapshot
            name2: Name of the second snapshot
            key_type: Type of grouping ('lineno', 'filename', 'traceback')
            limit: Maximum number of differences to return
            
        Returns:
            List of (description, size_diff) tuples
        """
        with self._profiles_lock:
            snapshot1 = self._profiles["snapshots"].get(name1)
            snapshot2 = self._profiles["snapshots"].get(name2)
            
            if not snapshot1 or not snapshot2:
                return []
            
            stats = snapshot2.compare_to(snapshot1, key_type)
            top_stats = stats[:limit]
            
            return [(str(stat), stat.size_diff) for stat in top_stats]
    
    def get_memory_leaks(self) -> List[Tuple[str, int, float, Dict[str, Any]]]:
        """
        Get a list of potential memory leaks.
        
        Returns:
            List of (name, memory_increase, timestamp, details) tuples
        """
        with self._profiles_lock:
            return list(self._profiles["memory_leaks"])
    
    def get_function_memory_profiles(self, function_name: Optional[str] = None) -> Dict[str, List[Tuple[int, int, int, float]]]:
        """
        Get memory profiles for functions.
        
        Args:
            function_name: Optional name of function to get profiles for
            
        Returns:
            Dictionary of function memory profiles
        """
        with self._profiles_lock:
            if function_name:
                return {function_name: list(self._profiles["function_memory"].get(function_name, []))}
            else:
                return {name: list(profiles) for name, profiles in self._profiles["function_memory"].items()}
    
    def get_block_memory_profiles(self, block_name: Optional[str] = None) -> Dict[str, List[Tuple[int, int, int, float]]]:
        """
        Get memory profiles for code blocks.
        
        Args:
            block_name: Optional name of block to get profiles for
            
        Returns:
            Dictionary of block memory profiles
        """
        with self._profiles_lock:
            if block_name:
                return {block_name: list(self._profiles["block_memory"].get(block_name, []))}
            else:
                return {name: list(profiles) for name, profiles in self._profiles["block_memory"].items()}
    
    def get_current_memory_usage(self) -> Dict[str, int]:
        """
        Get current memory usage.
        
        Returns:
            Dictionary with current and peak memory usage
        """
        if not self._enabled:
            return {"current": 0, "peak": 0}
            
        current, peak = tracemalloc.get_traced_memory()
        return {"current": current, "peak": peak}
    
    def reset(self) -> None:
        """Reset all memory profiles."""
        with self._profiles_lock:
            self._profiles = {
                "function_memory": {},
                "block_memory": {},
                "snapshots": {},
                "memory_leaks": [],
            }
    
    def set_memory_leak_threshold(self, threshold: int) -> None:
        """
        Set the threshold for identifying memory leaks.
        
        Args:
            threshold: Memory threshold in bytes
        """
        with self._profiles_lock:
            self._memory_leak_threshold = threshold
    
    def get_memory_leak_threshold(self) -> int:
        """
        Get the current memory leak threshold.
        
        Returns:
            Current threshold in bytes
        """
        return self._memory_leak_threshold
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of memory profiling data.
        
        Returns:
            Dictionary containing memory profiling summary
        """
        with self._profiles_lock:
            # Calculate average memory usage for functions
            function_memory_stats = {}
            for name, profiles in self._profiles["function_memory"].items():
                if profiles:
                    memory_diffs = [p[1] - p[0] for p in profiles]
                    peak_memories = [p[2] for p in profiles]
                    function_memory_stats[name] = {
                        "avg_memory_diff": sum(memory_diffs) / len(memory_diffs),
                        "min_memory_diff": min(memory_diffs),
                        "max_memory_diff": max(memory_diffs),
                        "avg_peak_memory": sum(peak_memories) / len(peak_memories),
                        "max_peak_memory": max(peak_memories),
                        "call_count": len(profiles)
                    }
            
            # Calculate average memory usage for code blocks
            block_memory_stats = {}
            for name, profiles in self._profiles["block_memory"].items():
                if profiles:
                    memory_diffs = [p[1] - p[0] for p in profiles]
                    peak_memories = [p[2] for p in profiles]
                    block_memory_stats[name] = {
                        "avg_memory_diff": sum(memory_diffs) / len(memory_diffs),
                        "min_memory_diff": min(memory_diffs),
                        "max_memory_diff": max(memory_diffs),
                        "avg_peak_memory": sum(peak_memories) / len(peak_memories),
                        "max_peak_memory": max(peak_memories),
                        "call_count": len(profiles)
                    }
            
            # Get top memory leaks
            memory_leaks = sorted(self._profiles["memory_leaks"], key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "function_memory_stats": function_memory_stats,
                "block_memory_stats": block_memory_stats,
                "memory_leaks_count": len(self._profiles["memory_leaks"]),
                "top_memory_leaks": memory_leaks,
                "snapshots_count": len(self._profiles["snapshots"]),
                "memory_leak_threshold": self._memory_leak_threshold,
                "current_memory": self.get_current_memory_usage() if self._enabled else {"current": 0, "peak": 0},
                "enabled": self._enabled
            }


# Create a singleton instance
memory_profiler = MemoryProfiler()

# Decorator for profiling function memory usage
def profile_memory(func=None):
    """
    Decorator for profiling function memory usage.
    
    Args:
        func: The function to profile
        
    Returns:
        Decorated function
    """
    if func is None:
        # Called as @profile_memory()
        return lambda f: memory_profiler.profile_function_memory(f)
    
    # Called as @profile_memory
    return memory_profiler.profile_function_memory(func)
"""