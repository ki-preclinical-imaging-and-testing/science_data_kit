"""
Matplotlib Integration for Science Data Kit

This module provides comprehensive integration with matplotlib for data visualization,
including functions for creating various types of plots, customizing plot appearance,
and saving plots to files.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Union, Callable
import logging
import io
import base64
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

# Import matplotlib with error handling
try:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    logger.warning("Matplotlib is not installed. Please install it with 'pip install matplotlib'.")
    MATPLOTLIB_AVAILABLE = False
    
    # Define placeholder classes for type hints
    class Figure:
        pass
    
    class Axes:
        pass


def check_matplotlib():
    """
    Check if matplotlib is available.
    
    Returns:
        bool: True if matplotlib is available, False otherwise.
    
    Raises:
        ImportError: If matplotlib is not available.
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("Matplotlib is not installed. Please install it with 'pip install matplotlib'.")
    return True


def create_figure(figsize: Tuple[float, float] = (10, 6), dpi: int = 100, **kwargs) -> Tuple[Figure, Axes]:
    """
    Create a new matplotlib figure and axes.
    
    Args:
        figsize: Figure size in inches (width, height).
        dpi: Dots per inch.
        **kwargs: Additional keyword arguments to pass to plt.subplots().
    
    Returns:
        A tuple containing the figure and axes objects.
    
    Raises:
        ImportError: If matplotlib is not available.
    """
    check_matplotlib()
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, **kwargs)
    return fig, ax


def plot_line(
    data: Union[pd.DataFrame, pd.Series, np.ndarray, List],
    x: Optional[Union[str, List, np.ndarray]] = None,
    y: Optional[Union[str, List, np.ndarray]] = None,
    ax: Optional[Axes] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    color: Optional[str] = None,
    linestyle: str = '-',
    marker: Optional[str] = None,
    linewidth: float = 1.5,
    grid: bool = True,
    legend: bool = True,
    **kwargs
) -> Tuple[Figure, Axes]:
    """
    Create a line plot.
    
    Args:
        data: The data to plot. Can be a DataFrame, Series, array, or list.
        x: The x-axis data or column name.
        y: The y-axis data or column name.
        ax: An existing axes to plot on. If None, a new figure and axes will be created.
        title: The plot title.
        xlabel: The x-axis label.
        ylabel: The y-axis label.
        color: The line color.
        linestyle: The line style.
        marker: The marker style.
        linewidth: The line width.
        grid: Whether to show grid lines.
        legend: Whether to show a legend.
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A tuple containing the figure and axes objects.
    
    Raises:
        ImportError: If matplotlib is not available.
    """
    check_matplotlib()
    
    # Create figure and axes if not provided
    if ax is None:
        fig, ax = create_figure()
    else:
        fig = ax.figure
    
    # Handle different input types
    if isinstance(data, pd.DataFrame):
        if x is not None and y is not None:
            data.plot(
                kind='line',
                x=x,
                y=y,
                ax=ax,
                color=color,
                linestyle=linestyle,
                marker=marker,
                linewidth=linewidth,
                grid=grid,
                legend=legend,
                **kwargs
            )
        elif y is not None:
            data.plot(
                kind='line',
                y=y,
                ax=ax,
                color=color,
                linestyle=linestyle,
                marker=marker,
                linewidth=linewidth,
                grid=grid,
                legend=legend,
                **kwargs
            )
        else:
            data.plot(
                kind='line',
                ax=ax,
                color=color,
                linestyle=linestyle,
                marker=marker,
                linewidth=linewidth,
                grid=grid,
                legend=legend,
                **kwargs
            )
    elif isinstance(data, pd.Series):
        data.plot(
            kind='line',
            ax=ax,
            color=color,
            linestyle=linestyle,
            marker=marker,
            linewidth=linewidth,
            grid=grid,
            legend=legend,
            **kwargs
        )
    else:
        # For numpy arrays or lists
        if x is None:
            x = range(len(data))
        ax.plot(
            x,
            data,
            color=color,
            linestyle=linestyle,
            marker=marker,
            linewidth=linewidth,
            **kwargs
        )
        if grid:
            ax.grid(True)
    
    # Set title and labels
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    
    plt.tight_layout()
    return fig, ax


def plot_bar(
    data: Union[pd.DataFrame, pd.Series, np.ndarray, List],
    x: Optional[Union[str, List, np.ndarray]] = None,
    y: Optional[Union[str, List, np.ndarray]] = None,
    ax: Optional[Axes] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    color: Optional[Union[str, List[str]]] = None,
    width: float = 0.8,
    grid: bool = True,
    legend: bool = True,
    horizontal: bool = False,
    stacked: bool = False,
    **kwargs
) -> Tuple[Figure, Axes]:
    """
    Create a bar plot.
    
    Args:
        data: The data to plot. Can be a DataFrame, Series, array, or list.
        x: The x-axis data or column name.
        y: The y-axis data or column name.
        ax: An existing axes to plot on. If None, a new figure and axes will be created.
        title: The plot title.
        xlabel: The x-axis label.
        ylabel: The y-axis label.
        color: The bar color(s).
        width: The bar width.
        grid: Whether to show grid lines.
        legend: Whether to show a legend.
        horizontal: Whether to create a horizontal bar plot.
        stacked: Whether to create a stacked bar plot.
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A tuple containing the figure and axes objects.
    
    Raises:
        ImportError: If matplotlib is not available.
    """
    check_matplotlib()
    
    # Create figure and axes if not provided
    if ax is None:
        fig, ax = create_figure()
    else:
        fig = ax.figure
    
    # Handle different input types
    if isinstance(data, pd.DataFrame):
        kind = 'barh' if horizontal else 'bar'
        if x is not None and y is not None:
            data.plot(
                kind=kind,
                x=x,
                y=y,
                ax=ax,
                color=color,
                width=width,
                grid=grid,
                legend=legend,
                stacked=stacked,
                **kwargs
            )
        elif y is not None:
            data.plot(
                kind=kind,
                y=y,
                ax=ax,
                color=color,
                width=width,
                grid=grid,
                legend=legend,
                stacked=stacked,
                **kwargs
            )
        else:
            data.plot(
                kind=kind,
                ax=ax,
                color=color,
                width=width,
                grid=grid,
                legend=legend,
                stacked=stacked,
                **kwargs
            )
    elif isinstance(data, pd.Series):
        kind = 'barh' if horizontal else 'bar'
        data.plot(
            kind=kind,
            ax=ax,
            color=color,
            width=width,
            grid=grid,
            legend=legend,
            **kwargs
        )
    else:
        # For numpy arrays or lists
        if x is None:
            x = range(len(data))
        if horizontal:
            ax.barh(x, data, color=color, height=width, **kwargs)
        else:
            ax.bar(x, data, color=color, width=width, **kwargs)
        if grid:
            ax.grid(True)
    
    # Set title and labels
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    
    plt.tight_layout()
    return fig, ax


def plot_scatter(
    data: Union[pd.DataFrame, np.ndarray, List],
    x: Union[str, List, np.ndarray],
    y: Union[str, List, np.ndarray],
    ax: Optional[Axes] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    color: Optional[Union[str, List[str]]] = None,
    marker: str = 'o',
    s: Union[float, List[float]] = 50,
    alpha: float = 0.7,
    grid: bool = True,
    legend: bool = True,
    **kwargs
) -> Tuple[Figure, Axes]:
    """
    Create a scatter plot.
    
    Args:
        data: The data to plot. Can be a DataFrame, array, or list.
        x: The x-axis data or column name.
        y: The y-axis data or column name.
        ax: An existing axes to plot on. If None, a new figure and axes will be created.
        title: The plot title.
        xlabel: The x-axis label.
        ylabel: The y-axis label.
        color: The marker color(s).
        marker: The marker style.
        s: The marker size(s).
        alpha: The marker transparency.
        grid: Whether to show grid lines.
        legend: Whether to show a legend.
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A tuple containing the figure and axes objects.
    
    Raises:
        ImportError: If matplotlib is not available.
        ValueError: If x or y is not provided.
    """
    check_matplotlib()
    
    if x is None or y is None:
        raise ValueError("Both x and y must be provided for a scatter plot.")
    
    # Create figure and axes if not provided
    if ax is None:
        fig, ax = create_figure()
    else:
        fig = ax.figure
    
    # Handle different input types
    if isinstance(data, pd.DataFrame):
        data.plot(
            kind='scatter',
            x=x,
            y=y,
            ax=ax,
            color=color,
            marker=marker,
            s=s,
            alpha=alpha,
            grid=grid,
            legend=legend,
            **kwargs
        )
    else:
        # For numpy arrays or lists
        ax.scatter(
            x,
            y,
            color=color,
            marker=marker,
            s=s,
            alpha=alpha,
            **kwargs
        )
        if grid:
            ax.grid(True)
    
    # Set title and labels
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    
    plt.tight_layout()
    return fig, ax


def plot_histogram(
    data: Union[pd.DataFrame, pd.Series, np.ndarray, List],
    column: Optional[str] = None,
    ax: Optional[Axes] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    color: Optional[str] = None,
    bins: Union[int, List, np.ndarray] = 10,
    density: bool = False,
    grid: bool = True,
    **kwargs
) -> Tuple[Figure, Axes]:
    """
    Create a histogram.
    
    Args:
        data: The data to plot. Can be a DataFrame, Series, array, or list.
        column: The column name to plot (if data is a DataFrame).
        ax: An existing axes to plot on. If None, a new figure and axes will be created.
        title: The plot title.
        xlabel: The x-axis label.
        ylabel: The y-axis label.
        color: The histogram color.
        bins: The number of bins or bin edges.
        density: Whether to normalize the histogram.
        grid: Whether to show grid lines.
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A tuple containing the figure and axes objects.
    
    Raises:
        ImportError: If matplotlib is not available.
    """
    check_matplotlib()
    
    # Create figure and axes if not provided
    if ax is None:
        fig, ax = create_figure()
    else:
        fig = ax.figure
    
    # Handle different input types
    if isinstance(data, pd.DataFrame):
        if column is not None:
            data[column].plot(
                kind='hist',
                ax=ax,
                color=color,
                bins=bins,
                density=density,
                grid=grid,
                **kwargs
            )
        else:
            data.plot(
                kind='hist',
                ax=ax,
                color=color,
                bins=bins,
                density=density,
                grid=grid,
                **kwargs
            )
    elif isinstance(data, pd.Series):
        data.plot(
            kind='hist',
            ax=ax,
            color=color,
            bins=bins,
            density=density,
            grid=grid,
            **kwargs
        )
    else:
        # For numpy arrays or lists
        ax.hist(
            data,
            bins=bins,
            color=color,
            density=density,
            **kwargs
        )
        if grid:
            ax.grid(True)
    
    # Set title and labels
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    
    plt.tight_layout()
    return fig, ax


def plot_boxplot(
    data: Union[pd.DataFrame, pd.Series, np.ndarray, List],
    column: Optional[Union[str, List[str]]] = None,
    ax: Optional[Axes] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    vert: bool = True,
    grid: bool = True,
    **kwargs
) -> Tuple[Figure, Axes]:
    """
    Create a box plot.
    
    Args:
        data: The data to plot. Can be a DataFrame, Series, array, or list.
        column: The column name(s) to plot (if data is a DataFrame).
        ax: An existing axes to plot on. If None, a new figure and axes will be created.
        title: The plot title.
        xlabel: The x-axis label.
        ylabel: The y-axis label.
        vert: Whether to create a vertical box plot.
        grid: Whether to show grid lines.
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A tuple containing the figure and axes objects.
    
    Raises:
        ImportError: If matplotlib is not available.
    """
    check_matplotlib()
    
    # Create figure and axes if not provided
    if ax is None:
        fig, ax = create_figure()
    else:
        fig = ax.figure
    
    # Handle different input types
    if isinstance(data, pd.DataFrame):
        if column is not None:
            if isinstance(column, list):
                data[column].plot(
                    kind='box',
                    ax=ax,
                    vert=vert,
                    grid=grid,
                    **kwargs
                )
            else:
                data[column].plot(
                    kind='box',
                    ax=ax,
                    vert=vert,
                    grid=grid,
                    **kwargs
                )
        else:
            data.plot(
                kind='box',
                ax=ax,
                vert=vert,
                grid=grid,
                **kwargs
            )
    elif isinstance(data, pd.Series):
        data.plot(
            kind='box',
            ax=ax,
            vert=vert,
            grid=grid,
            **kwargs
        )
    else:
        # For numpy arrays or lists
        ax.boxplot(
            data,
            vert=vert,
            **kwargs
        )
        if grid:
            ax.grid(True)
    
    # Set title and labels
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    
    plt.tight_layout()
    return fig, ax


def plot_heatmap(
    data: Union[pd.DataFrame, np.ndarray],
    ax: Optional[Axes] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    cmap: str = 'viridis',
    annot: bool = True,
    fmt: str = '.2f',
    linewidths: float = 0.5,
    **kwargs
) -> Tuple[Figure, Axes]:
    """
    Create a heatmap.
    
    Args:
        data: The data to plot. Should be a DataFrame or 2D array.
        ax: An existing axes to plot on. If None, a new figure and axes will be created.
        title: The plot title.
        xlabel: The x-axis label.
        ylabel: The y-axis label.
        cmap: The colormap to use.
        annot: Whether to annotate cells with values.
        fmt: String formatting code for annotations.
        linewidths: Width of the lines that divide cells.
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A tuple containing the figure and axes objects.
    
    Raises:
        ImportError: If matplotlib is not available.
        ValueError: If data is not 2D.
    """
    check_matplotlib()
    
    # Convert to DataFrame if necessary
    if not isinstance(data, pd.DataFrame):
        if len(data.shape) != 2:
            raise ValueError("Data must be 2D for a heatmap.")
        data = pd.DataFrame(data)
    
    # Create figure and axes if not provided
    if ax is None:
        fig, ax = create_figure()
    else:
        fig = ax.figure
    
    # Create the heatmap
    im = ax.imshow(data, cmap=cmap, **kwargs)
    
    # Add colorbar
    fig.colorbar(im, ax=ax)
    
    # Add annotations
    if annot:
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                ax.text(j, i, format(data.iloc[i, j], fmt),
                        ha="center", va="center", color="white" if data.iloc[i, j] > data.values.mean() else "black")
    
    # Set ticks and labels
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    ax.set_xticklabels(data.columns)
    ax.set_yticklabels(data.index)
    
    # Rotate x-axis labels if there are many columns
    if data.shape[1] > 10:
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add grid lines
    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=linewidths)
    ax.tick_params(which="minor", bottom=False, left=False)
    
    # Set title and labels
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    
    plt.tight_layout()
    return fig, ax


def plot_pie(
    data: Union[pd.DataFrame, pd.Series, np.ndarray, List],
    column: Optional[str] = None,
    ax: Optional[Axes] = None,
    title: Optional[str] = None,
    labels: Optional[List[str]] = None,
    colors: Optional[List[str]] = None,
    autopct: str = '%1.1f%%',
    startangle: float = 90,
    shadow: bool = False,
    explode: Optional[List[float]] = None,
    **kwargs
) -> Tuple[Figure, Axes]:
    """
    Create a pie chart.
    
    Args:
        data: The data to plot. Can be a DataFrame, Series, array, or list.
        column: The column name to plot (if data is a DataFrame).
        ax: An existing axes to plot on. If None, a new figure and axes will be created.
        title: The plot title.
        labels: The slice labels.
        colors: The slice colors.
        autopct: String format for percentage display.
        startangle: Starting angle for the first slice.
        shadow: Whether to draw a shadow beneath the pie.
        explode: List of floats to "explode" slices away from center.
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A tuple containing the figure and axes objects.
    
    Raises:
        ImportError: If matplotlib is not available.
    """
    check_matplotlib()
    
    # Create figure and axes if not provided
    if ax is None:
        fig, ax = create_figure()
    else:
        fig = ax.figure
    
    # Handle different input types
    if isinstance(data, pd.DataFrame):
        if column is not None:
            data[column].plot(
                kind='pie',
                ax=ax,
                labels=labels,
                colors=colors,
                autopct=autopct,
                startangle=startangle,
                shadow=shadow,
                explode=explode,
                **kwargs
            )
        else:
            data.iloc[:, 0].plot(
                kind='pie',
                ax=ax,
                labels=labels,
                colors=colors,
                autopct=autopct,
                startangle=startangle,
                shadow=shadow,
                explode=explode,
                **kwargs
            )
    elif isinstance(data, pd.Series):
        data.plot(
            kind='pie',
            ax=ax,
            labels=labels,
            colors=colors,
            autopct=autopct,
            startangle=startangle,
            shadow=shadow,
            explode=explode,
            **kwargs
        )
    else:
        # For numpy arrays or lists
        ax.pie(
            data,
            labels=labels,
            colors=colors,
            autopct=autopct,
            startangle=startangle,
            shadow=shadow,
            explode=explode,
            **kwargs
        )
    
    # Set title
    if title:
        ax.set_title(title)
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')
    
    plt.tight_layout()
    return fig, ax


def save_figure(
    fig: Figure,
    filename: Union[str, Path],
    dpi: int = 300,
    bbox_inches: str = 'tight',
    **kwargs
) -> str:
    """
    Save a matplotlib figure to a file.
    
    Args:
        fig: The figure to save.
        filename: The filename to save to.
        dpi: The resolution in dots per inch.
        bbox_inches: Bounding box in inches.
        **kwargs: Additional keyword arguments to pass to fig.savefig().
    
    Returns:
        The path to the saved file.
    
    Raises:
        ImportError: If matplotlib is not available.
    """
    check_matplotlib()
    
    # Convert to Path object
    path = Path(filename)
    
    # Create directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the figure
    fig.savefig(path, dpi=dpi, bbox_inches=bbox_inches, **kwargs)
    
    return str(path)


def figure_to_base64(
    fig: Figure,
    format: str = 'png',
    dpi: int = 100,
    **kwargs
) -> str:
    """
    Convert a matplotlib figure to a base64-encoded string.
    
    Args:
        fig: The figure to convert.
        format: The image format (png, jpg, svg, etc.).
        dpi: The resolution in dots per inch.
        **kwargs: Additional keyword arguments to pass to fig.savefig().
    
    Returns:
        A base64-encoded string representation of the figure.
    
    Raises:
        ImportError: If matplotlib is not available.
    """
    check_matplotlib()
    
    # Save figure to a BytesIO object
    buf = io.BytesIO()
    fig.savefig(buf, format=format, dpi=dpi, **kwargs)
    buf.seek(0)
    
    # Encode as base64
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    
    return f"data:image/{format};base64,{img_str}"


def close_figure(fig: Figure) -> None:
    """
    Close a matplotlib figure to free memory.
    
    Args:
        fig: The figure to close.
    
    Raises:
        ImportError: If matplotlib is not available.
    """
    check_matplotlib()
    plt.close(fig)


def set_style(style: str = 'default') -> None:
    """
    Set the matplotlib style.
    
    Args:
        style: The style to use. Can be 'default', 'classic', 'ggplot', 'seaborn',
               'seaborn-darkgrid', 'seaborn-whitegrid', 'seaborn-notebook',
               'seaborn-paper', 'seaborn-talk', 'seaborn-poster', 'bmh', 'dark_background',
               'fivethirtyeight', 'grayscale', 'seaborn-colorblind', 'seaborn-deep',
               'seaborn-muted', 'seaborn-pastel', 'seaborn-bright', 'tableau-colorblind10'.
    
    Raises:
        ImportError: If matplotlib is not available.
        ValueError: If the style is not valid.
    """
    check_matplotlib()
    
    try:
        plt.style.use(style)
    except Exception as e:
        logger.error(f"Error setting style: {str(e)}")
        raise ValueError(f"Invalid style: {style}. {str(e)}")


def get_available_styles() -> List[str]:
    """
    Get a list of available matplotlib styles.
    
    Returns:
        A list of available style names.
    
    Raises:
        ImportError: If matplotlib is not available.
    """
    check_matplotlib()
    return plt.style.available