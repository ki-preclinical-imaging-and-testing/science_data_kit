"""
Test script for the Science Data Kit plugin system.

This script demonstrates how to use the Science Data Kit plugin system
by loading and activating the example plugins.
"""

import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from science_data_kit.core.plugins.base import PluginManager
from science_data_kit.core.plugins.discovery import discover_plugins
from science_data_kit.core.plugins.examples.hello_world import HelloWorldPlugin
from science_data_kit.core.plugins.examples.data_processor import DataProcessorPlugin
from science_data_kit.core.plugins.examples.visualization import VisualizationPlugin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_sample_data() -> pd.DataFrame:
    """Create a sample DataFrame for testing."""
    np.random.seed(42)
    n = 100
    
    data = {
        "id": range(1, n + 1),
        "category": np.random.choice(["A", "B", "C"], size=n),
        "value1": np.random.normal(0, 1, n),
        "value2": np.random.normal(5, 2, n),
        "value3": np.random.exponential(2, n),
    }
    
    # Add some missing values
    data["value1"][np.random.choice(n, 10, replace=False)] = np.nan
    data["value2"][np.random.choice(n, 5, replace=False)] = np.nan
    
    return pd.DataFrame(data)


def test_hello_world_plugin():
    """Test the HelloWorldPlugin."""
    logger.info("Testing HelloWorldPlugin...")
    
    # Create a plugin manager
    manager = PluginManager()
    
    # Create and register the plugin
    plugin = HelloWorldPlugin()
    manager.register_plugin(plugin)
    
    # Activate the plugin
    success = manager.activate_plugin(plugin.name)
    assert success, f"Failed to activate plugin: {plugin.name}"
    
    # Use the plugin
    greeting = plugin.greet("User")
    logger.info(f"Greeting: {greeting}")
    
    # Deactivate the plugin
    success = manager.deactivate_plugin(plugin.name)
    assert success, f"Failed to deactivate plugin: {plugin.name}"
    
    logger.info("HelloWorldPlugin test completed successfully.")


def test_data_processor_plugin():
    """Test the DataProcessorPlugin."""
    logger.info("Testing DataProcessorPlugin...")
    
    # Create a plugin manager
    manager = PluginManager()
    
    # Create and register the plugin
    plugin = DataProcessorPlugin()
    manager.register_plugin(plugin)
    
    # Activate the plugin
    success = manager.activate_plugin(plugin.name)
    assert success, f"Failed to activate plugin: {plugin.name}"
    
    # Create sample data
    df = create_sample_data()
    logger.info(f"Sample data shape: {df.shape}")
    
    # Use the plugin to transform data
    transformers = plugin.get_all_transformers()
    logger.info(f"Available transformers: {list(transformers.keys())}")
    
    # Normalize the data
    df_normalized = plugin.apply_transformer(df, "normalize")
    logger.info(f"Normalized data shape: {df_normalized.shape}")
    
    # Standardize the data
    df_standardized = plugin.apply_transformer(df, "standardize")
    logger.info(f"Standardized data shape: {df_standardized.shape}")
    
    # Fill missing values
    df_filled = plugin.apply_transformer(df, "fill_missing", strategy="mean")
    logger.info(f"Data with filled missing values shape: {df_filled.shape}")
    
    # Remove outliers
    df_no_outliers = plugin.apply_transformer(df, "remove_outliers", method="zscore", threshold=2.0)
    logger.info(f"Data with outliers removed shape: {df_no_outliers.shape}")
    
    # Deactivate the plugin
    success = manager.deactivate_plugin(plugin.name)
    assert success, f"Failed to deactivate plugin: {plugin.name}"
    
    logger.info("DataProcessorPlugin test completed successfully.")


def test_visualization_plugin():
    """Test the VisualizationPlugin."""
    logger.info("Testing VisualizationPlugin...")
    
    # Create a plugin manager
    manager = PluginManager()
    
    # Create and register the plugins
    data_processor = DataProcessorPlugin()
    visualization = VisualizationPlugin()
    
    manager.register_plugin(data_processor)
    manager.register_plugin(visualization)
    
    # Activate the visualization plugin (which will also activate the data_processor plugin)
    success = manager.activate_plugin(visualization.name)
    assert success, f"Failed to activate plugin: {visualization.name}"
    
    # Create sample data
    df = create_sample_data()
    logger.info(f"Sample data shape: {df.shape}")
    
    # Fill missing values using the data processor plugin
    data_processor_plugin = manager.get_plugin("data_processor")
    df_filled = data_processor_plugin.apply_transformer(df, "fill_missing", strategy="mean")
    
    # Use the visualization plugin to create plots
    plot_functions = visualization.get_all_plot_functions()
    logger.info(f"Available plot functions: {list(plot_functions.keys())}")
    
    # Create a histogram
    fig_hist = visualization.create_plot(df_filled, "histogram", column="value1")
    plt.close(fig_hist)
    
    # Create a scatter plot
    fig_scatter = visualization.create_plot(df_filled, "scatter", x="value1", y="value2", hue="category")
    plt.close(fig_scatter)
    
    # Create a line plot
    fig_line = visualization.create_plot(df_filled, "line", x="id", y=["value1", "value2"])
    plt.close(fig_line)
    
    # Create a heatmap
    fig_heatmap = visualization.create_plot(df_filled, "heatmap")
    plt.close(fig_heatmap)
    
    # Deactivate the plugins
    success = manager.deactivate_all_plugins()
    assert all(success.values()), f"Failed to deactivate plugins: {[name for name, status in success.items() if not status]}"
    
    logger.info("VisualizationPlugin test completed successfully.")


def test_plugin_discovery():
    """Test plugin discovery."""
    logger.info("Testing plugin discovery...")
    
    # Create a plugin manager
    manager = PluginManager()
    
    # Discover plugins from the examples module
    results = discover_plugins(manager, plugin_modules=["science_data_kit.core.plugins.examples"])
    logger.info(f"Discovered plugins: {list(results.keys())}")
    
    # Activate all plugins
    activation_results = manager.activate_all_plugins()
    logger.info(f"Activation results: {activation_results}")
    
    # Get all active plugins
    active_plugins = manager.get_active_plugins()
    logger.info(f"Active plugins: {list(active_plugins.keys())}")
    
    # Deactivate all plugins
    deactivation_results = manager.deactivate_all_plugins()
    logger.info(f"Deactivation results: {deactivation_results}")
    
    logger.info("Plugin discovery test completed successfully.")


def main():
    """Run all tests."""
    logger.info("Starting plugin system tests...")
    
    test_hello_world_plugin()
    test_data_processor_plugin()
    test_visualization_plugin()
    test_plugin_discovery()
    
    logger.info("All plugin system tests completed successfully.")


if __name__ == "__main__":
    main()