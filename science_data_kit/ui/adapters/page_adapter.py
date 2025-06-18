"""
Page Adapter Module for Science Data Kit

This module provides adapters for the page components of the application.
It bridges between the core functionality and the UI pages.
"""

import streamlit as st
from typing import Dict, Any, Optional, Callable, List, Union
import importlib
import sys
from pathlib import Path

class PageAdapter:
    """
    Adapter for page components.
    
    This class provides methods for loading and rendering pages dynamically.
    """
    
    def __init__(self, pages_module: str = "science_data_kit.ui.pages"):
        """
        Initialize the PageAdapter.
        
        Args:
            pages_module: The module path where pages are defined.
        """
        self.pages_module = pages_module
        self.pages = {}
        self._discover_pages()
    
    def _discover_pages(self) -> None:
        """
        Discover available pages in the pages module.
        """
        try:
            # Import the pages module
            module = importlib.import_module(self.pages_module)
            
            # Get all submodules
            for name in dir(module):
                if name.startswith("_"):
                    continue
                
                try:
                    # Import the submodule
                    page_module = importlib.import_module(f"{self.pages_module}.{name}")
                    
                    # Check if the module has a render function
                    if hasattr(page_module, "render"):
                        # Add the page to the pages dictionary
                        self.pages[name] = page_module.render
                except ImportError:
                    continue
        except ImportError:
            st.warning(f"Could not import pages module: {self.pages_module}")
    
    def get_available_pages(self) -> List[str]:
        """
        Get a list of available pages.
        
        Returns:
            A list of page names.
        """
        return list(self.pages.keys())
    
    def render_page(self, page_name: str, **kwargs) -> None:
        """
        Render a page by name.
        
        Args:
            page_name: The name of the page to render.
            **kwargs: Additional arguments to pass to the page's render function.
        """
        if page_name in self.pages:
            self.pages[page_name](**kwargs)
        else:
            st.error(f"Page not found: {page_name}")
    
    def register_page(self, name: str, render_func: Callable) -> None:
        """
        Register a new page.
        
        Args:
            name: The name of the page.
            render_func: The function to call to render the page.
        """
        self.pages[name] = render_func

def load_page_from_file(file_path: Union[str, Path]) -> Optional[Callable]:
    """
    Load a page render function from a file.
    
    Args:
        file_path: The path to the file containing the page definition.
        
    Returns:
        The render function if found, None otherwise.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return None
    
    # Add the parent directory to sys.path temporarily
    parent_dir = str(file_path.parent)
    sys.path.insert(0, parent_dir)
    
    try:
        # Import the module
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check if the module has a render function
        if hasattr(module, "render"):
            return module.render
        
        return None
    except Exception as e:
        st.error(f"Error loading page from file: {e}")
        return None
    finally:
        # Remove the parent directory from sys.path
        if parent_dir in sys.path:
            sys.path.remove(parent_dir)

def create_page_adapter() -> PageAdapter:
    """
    Create a new PageAdapter instance.
    
    Returns:
        A new PageAdapter instance.
    """
    return PageAdapter()