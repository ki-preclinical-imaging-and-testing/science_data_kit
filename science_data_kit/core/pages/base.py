"""
Base Page Module for Science Data Kit Core

This module provides the base class for all pages in the Science Data Kit application.
It defines the framework-independent core functionality for pages.
"""

from abc import ABC, abstractmethod
from science_data_kit.core.models.page import PageData

class BasePage(ABC):
    """
    Base class for all pages in the Science Data Kit application.
    
    This class defines the common structure and functionality for all pages
    in a framework-independent way. Subclasses should implement the get_page_data
    method to provide the data needed to render the page.
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize the page with an optional database connection.
        
        Args:
            db_connection: Optional database connection to use for data retrieval.
        """
        self.db_connection = db_connection
    
    @abstractmethod
    def get_page_data(self) -> PageData:
        """
        Return data needed to render this page.
        
        This method must be implemented by subclasses to provide the data
        needed to render the page. The returned data should be an instance
        of a subclass of PageData.
        
        Returns:
            An instance of PageData or a subclass containing the data needed
            to render the page.
        """
        pass