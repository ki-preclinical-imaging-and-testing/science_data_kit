"""
A visualization plugin for the Science Data Kit.

This module provides an example of a Science Data Kit plugin that
creates visualizations of data using matplotlib and seaborn.
"""

import logging
from typing import Dict, List, Optional, Any, Callable, Tuple, Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from science_data_kit.core.plugins.base import Plugin

logger = logging.getLogger(__name__)


class VisualizationPlugin(Plugin):
    """A visualization plugin for the Science Data Kit.
    
    This plugin demonstrates how to create a plugin that generates
    visualizations of data using matplotlib and seaborn. It depends on
    the DataProcessorPlugin for data preprocessing.
    """
    
    @property
    def name(self) -> str:
        """Return the name of the plugin."""
        return "visualization"
    
    @property
    def version(self) -> str:
        """Return the version of the plugin."""
        return "1.0.0"
    
    @property
    def description(self) -> str:
        """Return a description of the plugin."""
        return "A plugin for creating visualizations of data using matplotlib and seaborn."
    
    @property
    def dependencies(self) -> List[str]:
        """Return a list of plugin names that this plugin depends on."""
        return ["data_processor"]
    
    def initialize(self) -> None:
        """Initialize the plugin.
        
        This method is called when the plugin is activated. It initializes
        the plugin's internal state and sets up the visualization styles.
        """
        logger.info("Initializing VisualizationPlugin...")
        
        # Set up default visualization style
        sns.set_style("whitegrid")
        plt.rcParams["figure.figsize"] = (10, 6)
        plt.rcParams["font.size"] = 12
        
        # Initialize plot functions dictionary
        self._plot_functions: Dict[str, Callable] = {}
        
        # Register built-in plot functions
        self.register_plot_function("histogram", self.plot_histogram)
        self.register_plot_function("scatter", self.plot_scatter)
        self.register_plot_function("line", self.plot_line)
        self.register_plot_function("bar", self.plot_bar)
        self.register_plot_function("box", self.plot_box)
        self.register_plot_function("heatmap", self.plot_heatmap)
        self.register_plot_function("pair", self.plot_pair)
        
        logger.info(f"VisualizationPlugin initialized with {len(self._plot_functions)} plot functions.")
    
    def shutdown(self) -> None:
        """Shut down the plugin.
        
        This method is called when the plugin is deactivated. It cleans up
        the plugin's internal state.
        """
        logger.info("Shutting down VisualizationPlugin...")
        self._plot_functions.clear()
        plt.close("all")  # Close all open figures
        logger.info("VisualizationPlugin shut down.")
    
    def register_plot_function(self, name: str, plot_function: Callable) -> None:
        """Register a plot function.
        
        Args:
            name: The name of the plot function.
            plot_function: The plot function to register.
            
        Raises:
            ValueError: If a plot function with the same name is already registered.
        """
        if name in self._plot_functions:
            raise ValueError(f"A plot function with name '{name}' is already registered.")
        
        self._plot_functions[name] = plot_function
        logger.info(f"Registered plot function: {name}")
    
    def get_plot_function(self, name: str) -> Optional[Callable]:
        """Get a registered plot function by name.
        
        Args:
            name: The name of the plot function to get.
            
        Returns:
            The plot function if found, None otherwise.
        """
        return self._plot_functions.get(name)
    
    def get_all_plot_functions(self) -> Dict[str, Callable]:
        """Get all registered plot functions.
        
        Returns:
            A dictionary mapping plot function names to plot functions.
        """
        return self._plot_functions.copy()
    
    def create_plot(self, df: pd.DataFrame, plot_type: str, **kwargs) -> plt.Figure:
        """Create a plot of the specified type.
        
        Args:
            df: The DataFrame to plot.
            plot_type: The type of plot to create.
            **kwargs: Additional arguments to pass to the plot function.
            
        Returns:
            The created matplotlib Figure.
            
        Raises:
            ValueError: If the plot type is not supported.
        """
        plot_function = self.get_plot_function(plot_type)
        if plot_function is None:
            raise ValueError(f"Plot type '{plot_type}' is not supported.")
        
        logger.info(f"Creating {plot_type} plot...")
        fig = plot_function(df, **kwargs)
        logger.info(f"{plot_type.capitalize()} plot created successfully.")
        return fig
    
    def save_plot(self, fig: plt.Figure, filename: str, dpi: int = 300,
                 format: str = "png", **kwargs) -> str:
        """Save a plot to a file.
        
        Args:
            fig: The matplotlib Figure to save.
            filename: The name of the file to save the plot to.
            dpi: The resolution of the saved image in dots per inch.
            format: The format to save the plot in (e.g., "png", "pdf", "svg").
            **kwargs: Additional arguments to pass to savefig.
            
        Returns:
            The path to the saved file.
        """
        logger.info(f"Saving plot to {filename}...")
        fig.savefig(filename, dpi=dpi, format=format, **kwargs)
        logger.info(f"Plot saved to {filename}.")
        return filename
    
    # Built-in plot functions
    
    def plot_histogram(self, df: pd.DataFrame, column: str,
                      bins: int = 30, kde: bool = True,
                      title: Optional[str] = None,
                      xlabel: Optional[str] = None,
                      ylabel: Optional[str] = None,
                      color: str = "blue",
                      **kwargs) -> plt.Figure:
        """Create a histogram plot.
        
        Args:
            df: The DataFrame containing the data to plot.
            column: The name of the column to plot.
            bins: The number of bins in the histogram.
            kde: Whether to overlay a kernel density estimate.
            title: The title of the plot.
            xlabel: The label for the x-axis.
            ylabel: The label for the y-axis.
            color: The color of the histogram.
            **kwargs: Additional arguments to pass to sns.histplot.
            
        Returns:
            The created matplotlib Figure.
        """
        fig, ax = plt.subplots()
        sns.histplot(data=df, x=column, bins=bins, kde=kde, color=color, ax=ax, **kwargs)
        
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f"Histogram of {column}")
        
        if xlabel:
            ax.set_xlabel(xlabel)
        
        if ylabel:
            ax.set_ylabel(ylabel)
        
        fig.tight_layout()
        return fig
    
    def plot_scatter(self, df: pd.DataFrame, x: str, y: str,
                    hue: Optional[str] = None,
                    title: Optional[str] = None,
                    xlabel: Optional[str] = None,
                    ylabel: Optional[str] = None,
                    **kwargs) -> plt.Figure:
        """Create a scatter plot.
        
        Args:
            df: The DataFrame containing the data to plot.
            x: The name of the column to use for the x-axis.
            y: The name of the column to use for the y-axis.
            hue: The name of the column to use for color encoding.
            title: The title of the plot.
            xlabel: The label for the x-axis.
            ylabel: The label for the y-axis.
            **kwargs: Additional arguments to pass to sns.scatterplot.
            
        Returns:
            The created matplotlib Figure.
        """
        fig, ax = plt.subplots()
        sns.scatterplot(data=df, x=x, y=y, hue=hue, ax=ax, **kwargs)
        
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f"Scatter Plot of {y} vs {x}")
        
        if xlabel:
            ax.set_xlabel(xlabel)
        
        if ylabel:
            ax.set_ylabel(ylabel)
        
        fig.tight_layout()
        return fig
    
    def plot_line(self, df: pd.DataFrame, x: str, y: Union[str, List[str]],
                 hue: Optional[str] = None,
                 title: Optional[str] = None,
                 xlabel: Optional[str] = None,
                 ylabel: Optional[str] = None,
                 **kwargs) -> plt.Figure:
        """Create a line plot.
        
        Args:
            df: The DataFrame containing the data to plot.
            x: The name of the column to use for the x-axis.
            y: The name of the column(s) to use for the y-axis.
            hue: The name of the column to use for color encoding.
            title: The title of the plot.
            xlabel: The label for the x-axis.
            ylabel: The label for the y-axis.
            **kwargs: Additional arguments to pass to sns.lineplot.
            
        Returns:
            The created matplotlib Figure.
        """
        fig, ax = plt.subplots()
        
        if isinstance(y, list):
            for col in y:
                sns.lineplot(data=df, x=x, y=col, ax=ax, label=col, **kwargs)
            y_label = "Values"
        else:
            sns.lineplot(data=df, x=x, y=y, hue=hue, ax=ax, **kwargs)
            y_label = y
        
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f"Line Plot of {y_label} vs {x}")
        
        if xlabel:
            ax.set_xlabel(xlabel)
        
        if ylabel:
            ax.set_ylabel(ylabel)
        
        fig.tight_layout()
        return fig
    
    def plot_bar(self, df: pd.DataFrame, x: str, y: str,
                hue: Optional[str] = None,
                title: Optional[str] = None,
                xlabel: Optional[str] = None,
                ylabel: Optional[str] = None,
                **kwargs) -> plt.Figure:
        """Create a bar plot.
        
        Args:
            df: The DataFrame containing the data to plot.
            x: The name of the column to use for the x-axis.
            y: The name of the column to use for the y-axis.
            hue: The name of the column to use for color encoding.
            title: The title of the plot.
            xlabel: The label for the x-axis.
            ylabel: The label for the y-axis.
            **kwargs: Additional arguments to pass to sns.barplot.
            
        Returns:
            The created matplotlib Figure.
        """
        fig, ax = plt.subplots()
        sns.barplot(data=df, x=x, y=y, hue=hue, ax=ax, **kwargs)
        
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f"Bar Plot of {y} vs {x}")
        
        if xlabel:
            ax.set_xlabel(xlabel)
        
        if ylabel:
            ax.set_ylabel(ylabel)
        
        fig.tight_layout()
        return fig
    
    def plot_box(self, df: pd.DataFrame, x: Optional[str] = None, y: str = None,
                hue: Optional[str] = None,
                title: Optional[str] = None,
                xlabel: Optional[str] = None,
                ylabel: Optional[str] = None,
                **kwargs) -> plt.Figure:
        """Create a box plot.
        
        Args:
            df: The DataFrame containing the data to plot.
            x: The name of the column to use for the x-axis.
            y: The name of the column to use for the y-axis.
            hue: The name of the column to use for color encoding.
            title: The title of the plot.
            xlabel: The label for the x-axis.
            ylabel: The label for the y-axis.
            **kwargs: Additional arguments to pass to sns.boxplot.
            
        Returns:
            The created matplotlib Figure.
        """
        fig, ax = plt.subplots()
        sns.boxplot(data=df, x=x, y=y, hue=hue, ax=ax, **kwargs)
        
        if title:
            ax.set_title(title)
        else:
            if x and y:
                ax.set_title(f"Box Plot of {y} vs {x}")
            elif x:
                ax.set_title(f"Box Plot of {x}")
            elif y:
                ax.set_title(f"Box Plot of {y}")
            else:
                ax.set_title("Box Plot")
        
        if xlabel:
            ax.set_xlabel(xlabel)
        
        if ylabel:
            ax.set_ylabel(ylabel)
        
        fig.tight_layout()
        return fig
    
    def plot_heatmap(self, df: pd.DataFrame,
                    title: Optional[str] = None,
                    cmap: str = "viridis",
                    annot: bool = True,
                    **kwargs) -> plt.Figure:
        """Create a heatmap of a correlation matrix.
        
        Args:
            df: The DataFrame containing the data to plot.
            title: The title of the plot.
            cmap: The colormap to use.
            annot: Whether to annotate the heatmap with values.
            **kwargs: Additional arguments to pass to sns.heatmap.
            
        Returns:
            The created matplotlib Figure.
        """
        # Calculate correlation matrix
        corr = df.select_dtypes(include=np.number).corr()
        
        fig, ax = plt.subplots()
        sns.heatmap(corr, cmap=cmap, annot=annot, ax=ax, **kwargs)
        
        if title:
            ax.set_title(title)
        else:
            ax.set_title("Correlation Matrix Heatmap")
        
        fig.tight_layout()
        return fig
    
    def plot_pair(self, df: pd.DataFrame, vars: Optional[List[str]] = None,
                 hue: Optional[str] = None,
                 title: Optional[str] = None,
                 **kwargs) -> plt.Figure:
        """Create a pair plot.
        
        Args:
            df: The DataFrame containing the data to plot.
            vars: The names of the columns to include in the plot.
            hue: The name of the column to use for color encoding.
            title: The title of the plot.
            **kwargs: Additional arguments to pass to sns.pairplot.
            
        Returns:
            The created matplotlib Figure.
        """
        g = sns.pairplot(df, vars=vars, hue=hue, **kwargs)
        
        if title:
            g.fig.suptitle(title, y=1.02)
        
        g.fig.tight_layout()
        return g.fig