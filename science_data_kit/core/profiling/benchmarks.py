"""
Performance Benchmarks for Science Data Kit

This module provides tools for measuring and comparing performance of code.
"""

import time
import statistics
import functools
import json
import os
import datetime
import logging
from typing import Dict, List, Any, Optional, Callable, Union, Tuple, Set

from .profiler import profiler
from .memory_profiler import memory_profiler


class Benchmark:
    """
    A benchmark for measuring and comparing performance of code.
    
    This class provides methods for:
    - Running benchmarks on functions
    - Comparing benchmark results
    - Generating benchmark reports
    """
    
    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize a benchmark.
        
        Args:
            name: Name of the benchmark
            description: Optional description of the benchmark
        """
        self.name = name
        self.description = description or f"Benchmark for {name}"
        self.logger = logging.getLogger(__name__)
        self.results = {}
        
    def run(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Run a benchmark on a function.
        
        Args:
            func: Function to benchmark
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Dictionary containing benchmark results
        """
        # Get function name
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Initialize results
        result = {
            "name": self.name,
            "function": func_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "execution_times": [],
            "memory_usage": None,
            "stats": {}
        }
        
        # Run the function once to warm up
        func(*args, **kwargs)
        
        # Measure memory usage if memory profiler is enabled
        if memory_profiler.is_enabled():
            # Force garbage collection
            import gc
            gc.collect()
            
            # Record memory before
            memory_before = memory_profiler.get_current_memory_usage()["current"]
            
            # Execute the function
            func(*args, **kwargs)
            
            # Record memory after
            memory_after = memory_profiler.get_current_memory_usage()["current"]
            
            # Calculate memory difference
            memory_diff = memory_after - memory_before
            
            result["memory_usage"] = {
                "before": memory_before,
                "after": memory_after,
                "diff": memory_diff
            }
        
        # Run the benchmark multiple times
        num_runs = 10
        for _ in range(num_runs):
            start_time = time.time()
            func(*args, **kwargs)
            execution_time = time.time() - start_time
            result["execution_times"].append(execution_time)
        
        # Calculate statistics
        execution_times = result["execution_times"]
        result["stats"] = {
            "min": min(execution_times),
            "max": max(execution_times),
            "mean": statistics.mean(execution_times),
            "median": statistics.median(execution_times),
            "stdev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        }
        
        # Store the result
        self.results[func_name] = result
        
        return result
    
    def compare(self, func1: Callable, func2: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Compare performance of two functions.
        
        Args:
            func1: First function to benchmark
            func2: Second function to benchmark
            *args: Arguments to pass to the functions
            **kwargs: Keyword arguments to pass to the functions
            
        Returns:
            Dictionary containing comparison results
        """
        # Run benchmarks
        result1 = self.run(func1, *args, **kwargs)
        result2 = self.run(func2, *args, **kwargs)
        
        # Calculate comparison
        comparison = {
            "name": self.name,
            "function1": result1["function"],
            "function2": result2["function"],
            "timestamp": datetime.datetime.now().isoformat(),
            "execution_time_diff": result1["stats"]["mean"] - result2["stats"]["mean"],
            "execution_time_ratio": result1["stats"]["mean"] / result2["stats"]["mean"] if result2["stats"]["mean"] > 0 else float('inf'),
            "memory_usage_diff": None,
            "memory_usage_ratio": None
        }
        
        # Compare memory usage if available
        if result1["memory_usage"] and result2["memory_usage"]:
            comparison["memory_usage_diff"] = result1["memory_usage"]["diff"] - result2["memory_usage"]["diff"]
            comparison["memory_usage_ratio"] = result1["memory_usage"]["diff"] / result2["memory_usage"]["diff"] if result2["memory_usage"]["diff"] > 0 else float('inf')
        
        return comparison
    
    def save_results(self, filename: str) -> None:
        """
        Save benchmark results to a file.
        
        Args:
            filename: Name of the file to save results to
        """
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def load_results(self, filename: str) -> Dict[str, Any]:
        """
        Load benchmark results from a file.
        
        Args:
            filename: Name of the file to load results from
            
        Returns:
            Dictionary containing benchmark results
        """
        with open(filename, 'r') as f:
            self.results = json.load(f)
        return self.results
    
    def generate_report(self) -> str:
        """
        Generate a report of benchmark results.
        
        Returns:
            String containing the report
        """
        report = []
        report.append(f"# Benchmark Report: {self.name}")
        report.append(f"## Description: {self.description}")
        report.append(f"## Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for func_name, result in self.results.items():
            report.append(f"### Function: {func_name}")
            report.append(f"- Timestamp: {result['timestamp']}")
            report.append(f"- Execution Time (mean): {result['stats']['mean']:.6f} seconds")
            report.append(f"- Execution Time (median): {result['stats']['median']:.6f} seconds")
            report.append(f"- Execution Time (min): {result['stats']['min']:.6f} seconds")
            report.append(f"- Execution Time (max): {result['stats']['max']:.6f} seconds")
            report.append(f"- Execution Time (stdev): {result['stats']['stdev']:.6f} seconds")
            
            if result["memory_usage"]:
                report.append(f"- Memory Usage (before): {result['memory_usage']['before'] / (1024 * 1024):.2f} MB")
                report.append(f"- Memory Usage (after): {result['memory_usage']['after'] / (1024 * 1024):.2f} MB")
                report.append(f"- Memory Usage (diff): {result['memory_usage']['diff'] / (1024 * 1024):.2f} MB")
            
            report.append("")
        
        return "\n".join(report)


class BenchmarkSuite:
    """
    A suite of benchmarks for measuring and comparing performance of code.
    
    This class provides methods for:
    - Running multiple benchmarks
    - Comparing benchmark results
    - Generating benchmark reports
    """
    
    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize a benchmark suite.
        
        Args:
            name: Name of the benchmark suite
            description: Optional description of the benchmark suite
        """
        self.name = name
        self.description = description or f"Benchmark suite for {name}"
        self.logger = logging.getLogger(__name__)
        self.benchmarks = {}
    
    def add_benchmark(self, benchmark: Benchmark) -> None:
        """
        Add a benchmark to the suite.
        
        Args:
            benchmark: Benchmark to add
        """
        self.benchmarks[benchmark.name] = benchmark
    
    def create_benchmark(self, name: str, description: Optional[str] = None) -> Benchmark:
        """
        Create a new benchmark and add it to the suite.
        
        Args:
            name: Name of the benchmark
            description: Optional description of the benchmark
            
        Returns:
            The created benchmark
        """
        benchmark = Benchmark(name, description)
        self.add_benchmark(benchmark)
        return benchmark
    
    def run_all(self, functions: Dict[str, Callable], *args, **kwargs) -> Dict[str, Dict[str, Any]]:
        """
        Run all benchmarks on all functions.
        
        Args:
            functions: Dictionary mapping function names to functions
            *args: Arguments to pass to the functions
            **kwargs: Keyword arguments to pass to the functions
            
        Returns:
            Dictionary mapping benchmark names to dictionaries mapping function names to results
        """
        results = {}
        
        for benchmark_name, benchmark in self.benchmarks.items():
            results[benchmark_name] = {}
            
            for func_name, func in functions.items():
                result = benchmark.run(func, *args, **kwargs)
                results[benchmark_name][func_name] = result
        
        return results
    
    def generate_report(self) -> str:
        """
        Generate a report of all benchmark results.
        
        Returns:
            String containing the report
        """
        report = []
        report.append(f"# Benchmark Suite Report: {self.name}")
        report.append(f"## Description: {self.description}")
        report.append(f"## Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for benchmark_name, benchmark in self.benchmarks.items():
            report.append(f"## Benchmark: {benchmark_name}")
            report.append(f"### Description: {benchmark.description}")
            report.append("")
            
            for func_name, result in benchmark.results.items():
                report.append(f"#### Function: {func_name}")
                report.append(f"- Timestamp: {result['timestamp']}")
                report.append(f"- Execution Time (mean): {result['stats']['mean']:.6f} seconds")
                report.append(f"- Execution Time (median): {result['stats']['median']:.6f} seconds")
                report.append(f"- Execution Time (min): {result['stats']['min']:.6f} seconds")
                report.append(f"- Execution Time (max): {result['stats']['max']:.6f} seconds")
                report.append(f"- Execution Time (stdev): {result['stats']['stdev']:.6f} seconds")
                
                if result["memory_usage"]:
                    report.append(f"- Memory Usage (before): {result['memory_usage']['before'] / (1024 * 1024):.2f} MB")
                    report.append(f"- Memory Usage (after): {result['memory_usage']['after'] / (1024 * 1024):.2f} MB")
                    report.append(f"- Memory Usage (diff): {result['memory_usage']['diff'] / (1024 * 1024):.2f} MB")
                
                report.append("")
        
        return "\n".join(report)
    
    def save_results(self, directory: str) -> None:
        """
        Save all benchmark results to files in a directory.
        
        Args:
            directory: Directory to save results to
        """
        os.makedirs(directory, exist_ok=True)
        
        for benchmark_name, benchmark in self.benchmarks.items():
            filename = os.path.join(directory, f"{benchmark_name}.json")
            benchmark.save_results(filename)
    
    def load_results(self, directory: str) -> Dict[str, Dict[str, Any]]:
        """
        Load all benchmark results from files in a directory.
        
        Args:
            directory: Directory to load results from
            
        Returns:
            Dictionary mapping benchmark names to dictionaries containing benchmark results
        """
        results = {}
        
        for benchmark_name, benchmark in self.benchmarks.items():
            filename = os.path.join(directory, f"{benchmark_name}.json")
            if os.path.exists(filename):
                results[benchmark_name] = benchmark.load_results(filename)
        
        return results


# Decorator for benchmarking functions
def benchmark(name: Optional[str] = None, description: Optional[str] = None):
    """
    Decorator for benchmarking functions.
    
    Args:
        name: Optional name for the benchmark
        description: Optional description for the benchmark
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a benchmark
            benchmark_name = name or f"{func.__module__}.{func.__name__}"
            benchmark_description = description or f"Benchmark for {func.__module__}.{func.__name__}"
            benchmark = Benchmark(benchmark_name, benchmark_description)
            
            # Run the benchmark
            result = benchmark.run(func, *args, **kwargs)
            
            # Log the result
            logger = logging.getLogger(__name__)
            logger.info(f"Benchmark {benchmark_name}: {result['stats']['mean']:.6f} seconds (mean)")
            
            # Execute the function and return its result
            return func(*args, **kwargs)
        
        return wrapper
    
    # Handle case where decorator is used without arguments
    if callable(name):
        func = name
        name = None
        return decorator(func)
    
    return decorator
"""