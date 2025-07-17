"""
Example plugins for the Science Data Kit.

This package contains example plugins that demonstrate how to use the
Science Data Kit plugin system.
"""

from science_data_kit.core.plugins.examples.hello_world import HelloWorldPlugin
from science_data_kit.core.plugins.examples.data_processor import DataProcessorPlugin
from science_data_kit.core.plugins.examples.visualization import VisualizationPlugin

__all__ = ['HelloWorldPlugin', 'DataProcessorPlugin', 'VisualizationPlugin']