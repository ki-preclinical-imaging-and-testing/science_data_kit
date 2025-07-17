"""
A simple Hello World plugin for the Science Data Kit.

This module provides a basic example of a Science Data Kit plugin that
simply prints a greeting message when initialized.
"""

import logging
from science_data_kit.core.plugins.base import Plugin

logger = logging.getLogger(__name__)


class HelloWorldPlugin(Plugin):
    """A simple Hello World plugin for the Science Data Kit.
    
    This plugin demonstrates the basic structure of a Science Data Kit plugin.
    It simply prints a greeting message when initialized.
    """
    
    @property
    def name(self) -> str:
        """Return the name of the plugin."""
        return "hello_world"
    
    @property
    def version(self) -> str:
        """Return the version of the plugin."""
        return "1.0.0"
    
    @property
    def description(self) -> str:
        """Return a description of the plugin."""
        return "A simple Hello World plugin for the Science Data Kit."
    
    def initialize(self) -> None:
        """Initialize the plugin.
        
        This method is called when the plugin is activated. It simply prints
        a greeting message.
        """
        logger.info("Hello, World! The Hello World plugin has been initialized.")
        print("Hello, World! The Hello World plugin has been initialized.")
    
    def shutdown(self) -> None:
        """Shut down the plugin.
        
        This method is called when the plugin is deactivated. It simply prints
        a goodbye message.
        """
        logger.info("Goodbye, World! The Hello World plugin has been shut down.")
        print("Goodbye, World! The Hello World plugin has been shut down.")
    
    def greet(self, name: str) -> str:
        """Greet a user by name.
        
        Args:
            name: The name of the user to greet.
            
        Returns:
            A greeting message for the user.
        """
        message = f"Hello, {name}! Welcome to the Science Data Kit."
        logger.info(f"Greeting user: {name}")
        return message