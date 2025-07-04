"""
Performance Profiling for Science Data Kit

This package provides tools for profiling and optimizing performance in the Science Data Kit.
"""

from .profiler import Profiler, profile, profiler
from .memory_profiler import MemoryProfiler, profile_memory, memory_profiler
from .code_optimizer import CodeOptimizer, code_optimizer
from .benchmarks import Benchmark, BenchmarkSuite, benchmark
from .recommendations import get_optimization_recommendations

__all__ = [
    'Profiler',
    'profile',
    'profiler',
    'MemoryProfiler',
    'profile_memory',
    'memory_profiler',
    'CodeOptimizer',
    'code_optimizer',
    'Benchmark',
    'BenchmarkSuite',
    'benchmark',
    'get_optimization_recommendations'
]
