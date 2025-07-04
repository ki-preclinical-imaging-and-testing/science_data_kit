"""
Code Optimizer for Science Data Kit

This module provides tools for automatically optimizing critical code paths based on profiling data.
"""

import ast
import inspect
import textwrap
import functools
import logging
from typing import Dict, List, Any, Optional, Callable, Union, Tuple, Set

from .profiler import profiler
from .memory_profiler import memory_profiler


class CodeOptimizer:
    """
    A code optimizer for automatically optimizing critical code paths.
    
    This class provides methods for:
    - Identifying critical code paths based on profiling data
    - Suggesting optimizations for critical code paths
    - Automatically applying optimizations to code
    """
    
    def __init__(self):
        """Initialize the code optimizer."""
        self.logger = logging.getLogger(__name__)
        self.optimization_patterns = self._load_optimization_patterns()
    
    def _load_optimization_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Load optimization patterns.
        
        Returns:
            Dictionary of optimization patterns
        """
        return {
            # Pattern for replacing list comprehensions with generator expressions
            "list_comprehension_to_generator": {
                "pattern": ast.ListComp,
                "condition": lambda node: True,  # Apply to all list comprehensions
                "transformation": self._transform_list_comp_to_generator,
                "description": "Replace list comprehension with generator expression"
            },
            
            # Pattern for replacing range(len(x)) with enumerate(x)
            "range_len_to_enumerate": {
                "pattern": ast.Call,
                "condition": self._is_range_len_pattern,
                "transformation": self._transform_range_len_to_enumerate,
                "description": "Replace range(len(x)) with enumerate(x)"
            },
            
            # Pattern for replacing multiple append calls with extend
            "multiple_appends_to_extend": {
                "pattern": ast.For,
                "condition": self._is_multiple_append_pattern,
                "transformation": self._transform_multiple_appends_to_extend,
                "description": "Replace multiple append calls with a single extend call"
            },
            
            # Pattern for replacing repeated string concatenation with join
            "string_concat_to_join": {
                "pattern": ast.For,
                "condition": self._is_string_concat_pattern,
                "transformation": self._transform_string_concat_to_join,
                "description": "Replace repeated string concatenation with join"
            }
        }
    
    def _is_range_len_pattern(self, node: ast.Call) -> bool:
        """
        Check if a node matches the range(len(x)) pattern.
        
        Args:
            node: AST node to check
            
        Returns:
            True if the node matches the pattern, False otherwise
        """
        if not isinstance(node, ast.Call):
            return False
            
        # Check if it's a call to range
        if not isinstance(node.func, ast.Name) or node.func.id != 'range':
            return False
            
        # Check if it has one argument
        if len(node.args) != 1:
            return False
            
        # Check if the argument is a call to len
        arg = node.args[0]
        if not isinstance(arg, ast.Call):
            return False
            
        if not isinstance(arg.func, ast.Name) or arg.func.id != 'len':
            return False
            
        return True
    
    def _transform_range_len_to_enumerate(self, node: ast.Call) -> ast.Call:
        """
        Transform range(len(x)) to enumerate(x).
        
        Args:
            node: AST node to transform
            
        Returns:
            Transformed AST node
        """
        # Extract the argument to len
        len_arg = node.args[0].args[0]
        
        # Create a new call to enumerate with the extracted argument
        return ast.Call(
            func=ast.Name(id='enumerate', ctx=ast.Load()),
            args=[len_arg],
            keywords=[]
        )
    
    def _is_multiple_append_pattern(self, node: ast.For) -> bool:
        """
        Check if a node matches the multiple append pattern.
        
        Args:
            node: AST node to check
            
        Returns:
            True if the node matches the pattern, False otherwise
        """
        if not isinstance(node, ast.For):
            return False
            
        # Check if the body consists of a single append call
        if len(node.body) != 1:
            return False
            
        stmt = node.body[0]
        if not isinstance(stmt, ast.Expr):
            return False
            
        call = stmt.value
        if not isinstance(call, ast.Call):
            return False
            
        # Check if it's a call to append
        if not isinstance(call.func, ast.Attribute) or call.func.attr != 'append':
            return False
            
        # Check if the append is called on a name
        if not isinstance(call.func.value, ast.Name):
            return False
            
        # Check if the argument to append is the loop variable or a simple transformation of it
        if len(call.args) != 1:
            return False
            
        arg = call.args[0]
        if isinstance(arg, ast.Name) and arg.id == node.target.id:
            return True
            
        # Check for simple transformations like x.append(item.strip())
        if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and isinstance(arg.func.value, ast.Name):
            if arg.func.value.id == node.target.id:
                return True
                
        return False
    
    def _transform_multiple_appends_to_extend(self, node: ast.For) -> ast.Expr:
        """
        Transform multiple append calls to a single extend call.
        
        Args:
            node: AST node to transform
            
        Returns:
            Transformed AST node
        """
        # Extract the list being appended to
        append_call = node.body[0].value
        list_name = append_call.func.value
        
        # Create a new call to extend with a list comprehension
        return ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=list_name,
                    attr='extend',
                    ctx=ast.Load()
                ),
                args=[
                    ast.ListComp(
                        elt=append_call.args[0],
                        generators=[node.iter]
                    )
                ],
                keywords=[]
            )
        )
    
    def _is_string_concat_pattern(self, node: ast.For) -> bool:
        """
        Check if a node matches the string concatenation pattern.
        
        Args:
            node: AST node to check
            
        Returns:
            True if the node matches the pattern, False otherwise
        """
        if not isinstance(node, ast.For):
            return False
            
        # Check if the body consists of a single assignment
        if len(node.body) != 1:
            return False
            
        stmt = node.body[0]
        if not isinstance(stmt, ast.Assign):
            return False
            
        # Check if the right side is a binary operation
        if not isinstance(stmt.value, ast.BinOp):
            return False
            
        # Check if the operation is addition
        if not isinstance(stmt.value.op, ast.Add):
            return False
            
        # Check if the left side of the addition is the same as the target of the assignment
        if not isinstance(stmt.value.left, ast.Name):
            return False
            
        if not isinstance(stmt.targets[0], ast.Name):
            return False
            
        if stmt.value.left.id != stmt.targets[0].id:
            return False
            
        return True
    
    def _transform_string_concat_to_join(self, node: ast.For) -> ast.Assign:
        """
        Transform repeated string concatenation to join.
        
        Args:
            node: AST node to transform
            
        Returns:
            Transformed AST node
        """
        # Extract the string being concatenated
        assign = node.body[0]
        target = assign.targets[0]
        right = assign.value.right
        
        # Create a new assignment with a join call
        return ast.Assign(
            targets=[target],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Str(s=''),
                    attr='join',
                    ctx=ast.Load()
                ),
                args=[
                    ast.ListComp(
                        elt=right,
                        generators=[
                            ast.comprehension(
                                target=node.target,
                                iter=node.iter,
                                ifs=[],
                                is_async=0
                            )
                        ]
                    )
                ],
                keywords=[]
            )
        )
    
    def _transform_list_comp_to_generator(self, node: ast.ListComp) -> ast.GeneratorExp:
        """
        Transform a list comprehension to a generator expression.
        
        Args:
            node: AST node to transform
            
        Returns:
            Transformed AST node
        """
        return ast.GeneratorExp(
            elt=node.elt,
            generators=node.generators
        )
    
    def identify_critical_functions(self, min_time: float = 1.0, min_calls: int = 5) -> List[str]:
        """
        Identify critical functions based on profiling data.
        
        Args:
            min_time: Minimum average execution time in seconds
            min_calls: Minimum number of calls
            
        Returns:
            List of critical function names
        """
        critical_functions = []
        
        # Get profiling data
        profile_summary = profiler.get_summary()
        function_profiles = profile_summary.get("function_profiles", {})
        
        # Identify critical functions
        for func_name, stats in function_profiles.items():
            if stats.get("avg_time", 0) >= min_time and stats.get("call_count", 0) >= min_calls:
                critical_functions.append(func_name)
        
        return critical_functions
    
    def optimize_function(self, func: Callable) -> Tuple[Callable, List[str]]:
        """
        Optimize a function by applying optimization patterns.
        
        Args:
            func: Function to optimize
            
        Returns:
            Tuple of (optimized function, list of applied optimizations)
        """
        # Get the source code of the function
        source = inspect.getsource(func)
        
        # Parse the source code into an AST
        tree = ast.parse(textwrap.dedent(source))
        
        # Find the function definition node
        func_def = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func.__name__:
                func_def = node
                break
        
        if not func_def:
            self.logger.warning(f"Could not find function definition for {func.__name__}")
            return func, []
        
        # Apply optimizations
        applied_optimizations = []
        transformer = CodeTransformer(self.optimization_patterns)
        optimized_tree = transformer.visit(tree)
        
        # Get the list of applied optimizations
        applied_optimizations = transformer.applied_optimizations
        
        if not applied_optimizations:
            self.logger.info(f"No optimizations applied to {func.__name__}")
            return func, []
        
        # Compile the optimized AST
        ast.fix_missing_locations(optimized_tree)
        compiled = compile(optimized_tree, "<string>", "exec")
        
        # Create a new namespace and execute the compiled code
        namespace = {}
        exec(compiled, func.__globals__, namespace)
        
        # Get the optimized function from the namespace
        optimized_func = namespace[func.__name__]
        
        # Copy the original function's metadata
        functools.update_wrapper(optimized_func, func)
        
        self.logger.info(f"Applied {len(applied_optimizations)} optimizations to {func.__name__}")
        
        return optimized_func, applied_optimizations
    
    def optimize_critical_functions(self, min_time: float = 1.0, min_calls: int = 5) -> Dict[str, List[str]]:
        """
        Optimize critical functions based on profiling data.
        
        Args:
            min_time: Minimum average execution time in seconds
            min_calls: Minimum number of calls
            
        Returns:
            Dictionary mapping function names to lists of applied optimizations
        """
        optimizations = {}
        
        # Identify critical functions
        critical_functions = self.identify_critical_functions(min_time, min_calls)
        
        # Optimize each critical function
        for func_name in critical_functions:
            # Try to get the function object
            module_name, func_name_short = func_name.rsplit('.', 1)
            try:
                module = __import__(module_name, fromlist=[func_name_short])
                func = getattr(module, func_name_short)
            except (ImportError, AttributeError):
                self.logger.warning(f"Could not import function {func_name}")
                continue
            
            # Optimize the function
            try:
                optimized_func, applied_optimizations = self.optimize_function(func)
                
                # Replace the original function with the optimized one
                if applied_optimizations:
                    setattr(module, func_name_short, optimized_func)
                    optimizations[func_name] = applied_optimizations
            except Exception as e:
                self.logger.warning(f"Error optimizing function {func_name}: {e}")
        
        return optimizations


class CodeTransformer(ast.NodeTransformer):
    """
    AST transformer for applying code optimizations.
    """
    
    def __init__(self, optimization_patterns):
        """
        Initialize the transformer.
        
        Args:
            optimization_patterns: Dictionary of optimization patterns
        """
        self.optimization_patterns = optimization_patterns
        self.applied_optimizations = []
    
    def generic_visit(self, node):
        """
        Visit a node and apply optimizations if applicable.
        
        Args:
            node: AST node to visit
            
        Returns:
            Transformed AST node
        """
        # Check if the node matches any optimization pattern
        for pattern_name, pattern in self.optimization_patterns.items():
            if isinstance(node, pattern["pattern"]) and pattern["condition"](node):
                # Apply the transformation
                transformed_node = pattern["transformation"](node)
                
                # Record the applied optimization
                self.applied_optimizations.append(pattern["description"])
                
                # Continue visiting the transformed node
                return ast.NodeTransformer.generic_visit(self, transformed_node)
        
        # If no optimization was applied, continue with normal visiting
        return ast.NodeTransformer.generic_visit(self, node)


# Create a singleton instance
code_optimizer = CodeOptimizer()
"""