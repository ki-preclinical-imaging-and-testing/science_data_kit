"""
Plotly Integration for Science Data Kit

This module provides comprehensive integration with plotly for interactive data visualization,
including functions for creating various types of plots, customizing plot appearance,
and exporting plots to HTML or as images.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Union, Callable
import logging
import io
import base64
from pathlib import Path
import json

# Configure logging
logger = logging.getLogger(__name__)

# Import plotly with error handling
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    logger.warning("Plotly is not installed. Please install it with 'pip install plotly'.")
    PLOTLY_AVAILABLE = False
    
    # Define placeholder classes for type hints
    class Figure:
        pass


def check_plotly():
    """
    Check if plotly is available.
    
    Returns:
        bool: True if plotly is available, False otherwise.
    
    Raises:
        ImportError: If plotly is not available.
    """
    if not PLOTLY_AVAILABLE:
        raise ImportError("Plotly is not installed. Please install it with 'pip install plotly'.")
    return True


def create_figure(rows: int = 1, cols: int = 1, subplot_titles: Optional[List[str]] = None, **kwargs) -> go.Figure:
    """
    Create a new plotly figure.
    
    Args:
        rows: Number of rows in the subplot grid.
        cols: Number of columns in the subplot grid.
        subplot_titles: Titles for each subplot.
        **kwargs: Additional keyword arguments to pass to make_subplots().
    
    Returns:
        A plotly Figure object.
    
    Raises:
        ImportError: If plotly is not available.
    """
    check_plotly()
    
    if rows > 1 or cols > 1:
        fig = make_subplots(rows=rows, cols=cols, subplot_titles=subplot_titles, **kwargs)
    else:
        fig = go.Figure(**kwargs)
    
    return fig


def plot_line(
    data: Union[pd.DataFrame, pd.Series, np.ndarray, List],
    x: Optional[Union[str, List, np.ndarray]] = None,
    y: Optional[Union[str, List, np.ndarray]] = None,
    fig: Optional[go.Figure] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    color: Optional[str] = None,
    line_dash: Optional[str] = None,
    mode: str = 'lines',
    name: Optional[str] = None,
    row: Optional[int] = None,
    col: Optional[int] = None,
    **kwargs
) -> go.Figure:
    """
    Create a line plot.
    
    Args:
        data: The data to plot. Can be a DataFrame, Series, array, or list.
        x: The x-axis data or column name.
        y: The y-axis data or column name.
        fig: An existing figure to add the plot to. If None, a new figure will be created.
        title: The plot title.
        xlabel: The x-axis label.
        ylabel: The y-axis label.
        color: The line color.
        line_dash: The line dash style ('solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot').
        mode: The plotting mode ('lines', 'markers', 'lines+markers').
        name: The trace name for the legend.
        row: The row index for subplot (if using subplots).
        col: The column index for subplot (if using subplots).
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A plotly Figure object.
    
    Raises:
        ImportError: If plotly is not available.
    """
    check_plotly()
    
    # Create figure if not provided
    if fig is None:
        fig = create_figure()
    
    # Handle different input types
    if isinstance(data, pd.DataFrame):
        if x is not None and y is not None:
            # If both x and y are provided, use them
            x_data = data[x]
            y_data = data[y]
            trace_name = name if name is not None else y
        elif y is not None:
            # If only y is provided, use index as x
            x_data = data.index
            y_data = data[y]
            trace_name = name if name is not None else y
        else:
            # If neither x nor y is provided, plot all columns
            for col_name in data.columns:
                fig = plot_line(
                    data=data,
                    y=col_name,
                    fig=fig,
                    title=title,
                    xlabel=xlabel,
                    ylabel=ylabel,
                    color=None,  # Use default color cycle
                    line_dash=line_dash,
                    mode=mode,
                    name=col_name,
                    row=row,
                    col=col,
                    **kwargs
                )
            return fig
    elif isinstance(data, pd.Series):
        x_data = data.index
        y_data = data.values
        trace_name = name if name is not None else data.name
    else:
        # For numpy arrays or lists
        if x is None:
            x_data = list(range(len(data)))
        else:
            x_data = x
        y_data = data
        trace_name = name
    
    # Create the trace
    trace = go.Scatter(
        x=x_data,
        y=y_data,
        mode=mode,
        name=trace_name,
        line=dict(color=color, dash=line_dash),
        **kwargs
    )
    
    # Add the trace to the figure
    if row is not None and col is not None:
        fig.add_trace(trace, row=row, col=col)
    else:
        fig.add_trace(trace)
    
    # Update layout
    layout_args = {}
    if title:
        layout_args['title'] = title
    if xlabel:
        layout_args['xaxis_title'] = xlabel
    if ylabel:
        layout_args['yaxis_title'] = ylabel
    
    fig.update_layout(**layout_args)
    
    return fig


def plot_bar(
    data: Union[pd.DataFrame, pd.Series, np.ndarray, List],
    x: Optional[Union[str, List, np.ndarray]] = None,
    y: Optional[Union[str, List, np.ndarray]] = None,
    fig: Optional[go.Figure] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    color: Optional[str] = None,
    name: Optional[str] = None,
    orientation: str = 'v',
    barmode: str = 'group',
    row: Optional[int] = None,
    col: Optional[int] = None,
    **kwargs
) -> go.Figure:
    """
    Create a bar plot.
    
    Args:
        data: The data to plot. Can be a DataFrame, Series, array, or list.
        x: The x-axis data or column name.
        y: The y-axis data or column name.
        fig: An existing figure to add the plot to. If None, a new figure will be created.
        title: The plot title.
        xlabel: The x-axis label.
        ylabel: The y-axis label.
        color: The bar color.
        name: The trace name for the legend.
        orientation: The orientation of the bars ('v' for vertical, 'h' for horizontal).
        barmode: The bar mode ('group', 'stack', 'overlay', 'relative').
        row: The row index for subplot (if using subplots).
        col: The column index for subplot (if using subplots).
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A plotly Figure object.
    
    Raises:
        ImportError: If plotly is not available.
    """
    check_plotly()
    
    # Create figure if not provided
    if fig is None:
        fig = create_figure()
    
    # Handle different input types
    if isinstance(data, pd.DataFrame):
        if x is not None and y is not None:
            # If both x and y are provided, use them
            x_data = data[x]
            y_data = data[y]
            trace_name = name if name is not None else y
        elif y is not None:
            # If only y is provided, use index as x
            x_data = data.index
            y_data = data[y]
            trace_name = name if name is not None else y
        else:
            # If neither x nor y is provided, plot all columns
            for col_name in data.columns:
                fig = plot_bar(
                    data=data,
                    y=col_name,
                    fig=fig,
                    title=title,
                    xlabel=xlabel,
                    ylabel=ylabel,
                    color=None,  # Use default color cycle
                    name=col_name,
                    orientation=orientation,
                    barmode=barmode,
                    row=row,
                    col=col,
                    **kwargs
                )
            return fig
    elif isinstance(data, pd.Series):
        x_data = data.index
        y_data = data.values
        trace_name = name if name is not None else data.name
    else:
        # For numpy arrays or lists
        if x is None:
            x_data = list(range(len(data)))
        else:
            x_data = x
        y_data = data
        trace_name = name
    
    # Create the trace
    if orientation == 'h':
        trace = go.Bar(
            y=x_data,
            x=y_data,
            orientation=orientation,
            name=trace_name,
            marker_color=color,
            **kwargs
        )
    else:
        trace = go.Bar(
            x=x_data,
            y=y_data,
            orientation=orientation,
            name=trace_name,
            marker_color=color,
            **kwargs
        )
    
    # Add the trace to the figure
    if row is not None and col is not None:
        fig.add_trace(trace, row=row, col=col)
    else:
        fig.add_trace(trace)
    
    # Update layout
    layout_args = {'barmode': barmode}
    if title:
        layout_args['title'] = title
    if xlabel:
        layout_args['xaxis_title'] = xlabel
    if ylabel:
        layout_args['yaxis_title'] = ylabel
    
    fig.update_layout(**layout_args)
    
    return fig


def plot_scatter(
    data: Union[pd.DataFrame, np.ndarray, List],
    x: Union[str, List, np.ndarray],
    y: Union[str, List, np.ndarray],
    fig: Optional[go.Figure] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    color: Optional[Union[str, List, np.ndarray]] = None,
    color_discrete_map: Optional[Dict[Any, str]] = None,
    size: Optional[Union[int, List, np.ndarray]] = None,
    symbol: Optional[Union[str, List, np.ndarray]] = None,
    hover_name: Optional[Union[str, List, np.ndarray]] = None,
    name: Optional[str] = None,
    row: Optional[int] = None,
    col: Optional[int] = None,
    **kwargs
) -> go.Figure:
    """
    Create a scatter plot.
    
    Args:
        data: The data to plot. Can be a DataFrame, array, or list.
        x: The x-axis data or column name.
        y: The y-axis data or column name.
        fig: An existing figure to add the plot to. If None, a new figure will be created.
        title: The plot title.
        xlabel: The x-axis label.
        ylabel: The y-axis label.
        color: The marker color or column name for color mapping.
        color_discrete_map: A dictionary mapping categories to colors.
        size: The marker size or column name for size mapping.
        symbol: The marker symbol or column name for symbol mapping.
        hover_name: The column name to use for hover labels.
        name: The trace name for the legend.
        row: The row index for subplot (if using subplots).
        col: The column index for subplot (if using subplots).
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A plotly Figure object.
    
    Raises:
        ImportError: If plotly is not available.
        ValueError: If x or y is not provided.
    """
    check_plotly()
    
    if x is None or y is None:
        raise ValueError("Both x and y must be provided for a scatter plot.")
    
    # Create figure if not provided
    if fig is None:
        fig = create_figure()
    
    # Handle different input types
    if isinstance(data, pd.DataFrame):
        # If using plotly express for advanced features
        if (isinstance(color, str) and color in data.columns) or \
           (isinstance(size, str) and size in data.columns) or \
           (isinstance(symbol, str) and symbol in data.columns) or \
           (isinstance(hover_name, str) and hover_name in data.columns):
            
            scatter_fig = px.scatter(
                data,
                x=x,
                y=y,
                color=color,
                color_discrete_map=color_discrete_map,
                size=size,
                symbol=symbol,
                hover_name=hover_name,
                title=title,
                labels={x: xlabel or x, y: ylabel or y},
                **kwargs
            )
            
            # Add traces from scatter_fig to the main figure
            for trace in scatter_fig.data:
                if row is not None and col is not None:
                    fig.add_trace(trace, row=row, col=col)
                else:
                    fig.add_trace(trace)
            
            # Update layout
            layout_args = {}
            if title:
                layout_args['title'] = title
            if xlabel:
                layout_args['xaxis_title'] = xlabel
            if ylabel:
                layout_args['yaxis_title'] = ylabel
            
            fig.update_layout(**layout_args)
            
            return fig
        else:
            # Simple case: just x and y columns
            x_data = data[x]
            y_data = data[y]
    else:
        # For numpy arrays or lists
        x_data = x
        y_data = y
    
    # Create the trace
    trace = go.Scatter(
        x=x_data,
        y=y_data,
        mode='markers',
        name=name,
        marker=dict(
            color=color,
            size=size,
            symbol=symbol
        ),
        **kwargs
    )
    
    # Add the trace to the figure
    if row is not None and col is not None:
        fig.add_trace(trace, row=row, col=col)
    else:
        fig.add_trace(trace)
    
    # Update layout
    layout_args = {}
    if title:
        layout_args['title'] = title
    if xlabel:
        layout_args['xaxis_title'] = xlabel
    if ylabel:
        layout_args['yaxis_title'] = ylabel
    
    fig.update_layout(**layout_args)
    
    return fig


def plot_histogram(
    data: Union[pd.DataFrame, pd.Series, np.ndarray, List],
    column: Optional[str] = None,
    fig: Optional[go.Figure] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    color: Optional[str] = None,
    nbins: Optional[int] = None,
    histnorm: Optional[str] = None,
    name: Optional[str] = None,
    row: Optional[int] = None,
    col: Optional[int] = None,
    **kwargs
) -> go.Figure:
    """
    Create a histogram.
    
    Args:
        data: The data to plot. Can be a DataFrame, Series, array, or list.
        column: The column name to plot (if data is a DataFrame).
        fig: An existing figure to add the plot to. If None, a new figure will be created.
        title: The plot title.
        xlabel: The x-axis label.
        ylabel: The y-axis label.
        color: The histogram color.
        nbins: The number of bins.
        histnorm: The normalization method ('', 'percent', 'probability', 'density', 'probability density').
        name: The trace name for the legend.
        row: The row index for subplot (if using subplots).
        col: The column index for subplot (if using subplots).
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A plotly Figure object.
    
    Raises:
        ImportError: If plotly is not available.
    """
    check_plotly()
    
    # Create figure if not provided
    if fig is None:
        fig = create_figure()
    
    # Handle different input types
    if isinstance(data, pd.DataFrame):
        if column is not None:
            # If column is provided, use it
            x_data = data[column]
            trace_name = name if name is not None else column
        else:
            # If column is not provided, plot histograms for all numeric columns
            for col_name in data.select_dtypes(include=[np.number]).columns:
                fig = plot_histogram(
                    data=data,
                    column=col_name,
                    fig=fig,
                    title=title,
                    xlabel=xlabel,
                    ylabel=ylabel,
                    color=None,  # Use default color cycle
                    nbins=nbins,
                    histnorm=histnorm,
                    name=col_name,
                    row=row,
                    col=col,
                    **kwargs
                )
            return fig
    elif isinstance(data, pd.Series):
        x_data = data.values
        trace_name = name if name is not None else data.name
    else:
        # For numpy arrays or lists
        x_data = data
        trace_name = name
    
    # Create the trace
    trace = go.Histogram(
        x=x_data,
        nbinsx=nbins,
        histnorm=histnorm,
        name=trace_name,
        marker_color=color,
        **kwargs
    )
    
    # Add the trace to the figure
    if row is not None and col is not None:
        fig.add_trace(trace, row=row, col=col)
    else:
        fig.add_trace(trace)
    
    # Update layout
    layout_args = {}
    if title:
        layout_args['title'] = title
    if xlabel:
        layout_args['xaxis_title'] = xlabel
    if ylabel:
        layout_args['yaxis_title'] = ylabel
    
    fig.update_layout(**layout_args)
    
    return fig


def plot_boxplot(
    data: Union[pd.DataFrame, pd.Series, np.ndarray, List],
    column: Optional[Union[str, List[str]]] = None,
    fig: Optional[go.Figure] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    color: Optional[str] = None,
    name: Optional[str] = None,
    orientation: str = 'v',
    points: str = 'outliers',
    row: Optional[int] = None,
    col: Optional[int] = None,
    **kwargs
) -> go.Figure:
    """
    Create a box plot.
    
    Args:
        data: The data to plot. Can be a DataFrame, Series, array, or list.
        column: The column name(s) to plot (if data is a DataFrame).
        fig: An existing figure to add the plot to. If None, a new figure will be created.
        title: The plot title.
        xlabel: The x-axis label.
        ylabel: The y-axis label.
        color: The box color.
        name: The trace name for the legend.
        orientation: The orientation of the boxes ('v' for vertical, 'h' for horizontal).
        points: How to display points ('all', 'outliers', 'suspectedoutliers', False).
        row: The row index for subplot (if using subplots).
        col: The column index for subplot (if using subplots).
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A plotly Figure object.
    
    Raises:
        ImportError: If plotly is not available.
    """
    check_plotly()
    
    # Create figure if not provided
    if fig is None:
        fig = create_figure()
    
    # Handle different input types
    if isinstance(data, pd.DataFrame):
        if column is not None:
            if isinstance(column, list):
                # If multiple columns are provided, plot each one
                for col_name in column:
                    fig = plot_boxplot(
                        data=data,
                        column=col_name,
                        fig=fig,
                        title=title,
                        xlabel=xlabel,
                        ylabel=ylabel,
                        color=None,  # Use default color cycle
                        name=col_name,
                        orientation=orientation,
                        points=points,
                        row=row,
                        col=col,
                        **kwargs
                    )
                return fig
            else:
                # If a single column is provided, use it
                y_data = data[column]
                trace_name = name if name is not None else column
        else:
            # If column is not provided, plot boxplots for all numeric columns
            for col_name in data.select_dtypes(include=[np.number]).columns:
                fig = plot_boxplot(
                    data=data,
                    column=col_name,
                    fig=fig,
                    title=title,
                    xlabel=xlabel,
                    ylabel=ylabel,
                    color=None,  # Use default color cycle
                    name=col_name,
                    orientation=orientation,
                    points=points,
                    row=row,
                    col=col,
                    **kwargs
                )
            return fig
    elif isinstance(data, pd.Series):
        y_data = data.values
        trace_name = name if name is not None else data.name
    else:
        # For numpy arrays or lists
        y_data = data
        trace_name = name
    
    # Create the trace
    if orientation == 'h':
        trace = go.Box(
            x=y_data,
            name=trace_name,
            marker_color=color,
            orientation=orientation,
            boxpoints=points,
            **kwargs
        )
    else:
        trace = go.Box(
            y=y_data,
            name=trace_name,
            marker_color=color,
            orientation=orientation,
            boxpoints=points,
            **kwargs
        )
    
    # Add the trace to the figure
    if row is not None and col is not None:
        fig.add_trace(trace, row=row, col=col)
    else:
        fig.add_trace(trace)
    
    # Update layout
    layout_args = {}
    if title:
        layout_args['title'] = title
    if xlabel:
        layout_args['xaxis_title'] = xlabel
    if ylabel:
        layout_args['yaxis_title'] = ylabel
    
    fig.update_layout(**layout_args)
    
    return fig


def plot_heatmap(
    data: Union[pd.DataFrame, np.ndarray],
    fig: Optional[go.Figure] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    colorscale: str = 'Viridis',
    showscale: bool = True,
    text_auto: Union[bool, str] = False,
    row: Optional[int] = None,
    col: Optional[int] = None,
    **kwargs
) -> go.Figure:
    """
    Create a heatmap.
    
    Args:
        data: The data to plot. Should be a DataFrame or 2D array.
        fig: An existing figure to add the plot to. If None, a new figure will be created.
        title: The plot title.
        xlabel: The x-axis label.
        ylabel: The y-axis label.
        colorscale: The colorscale to use.
        showscale: Whether to show the colorscale.
        text_auto: Whether to show text annotations and how to format them.
        row: The row index for subplot (if using subplots).
        col: The column index for subplot (if using subplots).
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A plotly Figure object.
    
    Raises:
        ImportError: If plotly is not available.
        ValueError: If data is not 2D.
    """
    check_plotly()
    
    # Convert to DataFrame if necessary
    if not isinstance(data, pd.DataFrame):
        if len(data.shape) != 2:
            raise ValueError("Data must be 2D for a heatmap.")
        data = pd.DataFrame(data)
    
    # Create figure if not provided
    if fig is None:
        fig = create_figure()
    
    # Create the trace
    trace = go.Heatmap(
        z=data.values,
        x=data.columns,
        y=data.index,
        colorscale=colorscale,
        showscale=showscale,
        text_auto=text_auto,
        **kwargs
    )
    
    # Add the trace to the figure
    if row is not None and col is not None:
        fig.add_trace(trace, row=row, col=col)
    else:
        fig.add_trace(trace)
    
    # Update layout
    layout_args = {}
    if title:
        layout_args['title'] = title
    if xlabel:
        layout_args['xaxis_title'] = xlabel
    if ylabel:
        layout_args['yaxis_title'] = ylabel
    
    fig.update_layout(**layout_args)
    
    return fig


def plot_pie(
    data: Union[pd.DataFrame, pd.Series, np.ndarray, List],
    column: Optional[str] = None,
    names: Optional[Union[str, List]] = None,
    fig: Optional[go.Figure] = None,
    title: Optional[str] = None,
    color_discrete_map: Optional[Dict[Any, str]] = None,
    hole: float = 0,
    textinfo: str = 'percent+label',
    row: Optional[int] = None,
    col: Optional[int] = None,
    **kwargs
) -> go.Figure:
    """
    Create a pie chart.
    
    Args:
        data: The data to plot. Can be a DataFrame, Series, array, or list.
        column: The column name to plot (if data is a DataFrame).
        names: The labels for the pie chart slices.
        fig: An existing figure to add the plot to. If None, a new figure will be created.
        title: The plot title.
        color_discrete_map: A dictionary mapping categories to colors.
        hole: The fraction of the radius to cut out of the center (0-1).
        textinfo: The information to show on the pie chart ('label', 'percent', 'value', 'label+percent', etc.).
        row: The row index for subplot (if using subplots).
        col: The column index for subplot (if using subplots).
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A plotly Figure object.
    
    Raises:
        ImportError: If plotly is not available.
    """
    check_plotly()
    
    # Create figure if not provided
    if fig is None:
        fig = create_figure()
    
    # Handle different input types
    if isinstance(data, pd.DataFrame):
        if column is not None:
            # If column is provided, use it
            values = data[column]
            if names is None and isinstance(data.index, pd.Index):
                names = data.index
        else:
            # If column is not provided, use the first column
            values = data.iloc[:, 0]
            if names is None and isinstance(data.index, pd.Index):
                names = data.index
    elif isinstance(data, pd.Series):
        values = data.values
        if names is None and isinstance(data.index, pd.Index):
            names = data.index
    else:
        # For numpy arrays or lists
        values = data
    
    # Create the trace
    trace = go.Pie(
        values=values,
        labels=names,
        hole=hole,
        textinfo=textinfo,
        marker_colors=[color_discrete_map.get(name) if color_discrete_map else None for name in names] if names else None,
        **kwargs
    )
    
    # Add the trace to the figure
    if row is not None and col is not None:
        fig.add_trace(trace, row=row, col=col)
    else:
        fig.add_trace(trace)
    
    # Update layout
    layout_args = {}
    if title:
        layout_args['title'] = title
    
    fig.update_layout(**layout_args)
    
    return fig


def plot_3d_scatter(
    data: Union[pd.DataFrame, np.ndarray, List],
    x: Union[str, List, np.ndarray],
    y: Union[str, List, np.ndarray],
    z: Union[str, List, np.ndarray],
    fig: Optional[go.Figure] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    zlabel: Optional[str] = None,
    color: Optional[Union[str, List, np.ndarray]] = None,
    size: Optional[Union[int, List, np.ndarray]] = None,
    symbol: Optional[Union[str, List, np.ndarray]] = None,
    hover_name: Optional[Union[str, List, np.ndarray]] = None,
    name: Optional[str] = None,
    **kwargs
) -> go.Figure:
    """
    Create a 3D scatter plot.
    
    Args:
        data: The data to plot. Can be a DataFrame, array, or list.
        x: The x-axis data or column name.
        y: The y-axis data or column name.
        z: The z-axis data or column name.
        fig: An existing figure to add the plot to. If None, a new figure will be created.
        title: The plot title.
        xlabel: The x-axis label.
        ylabel: The y-axis label.
        zlabel: The z-axis label.
        color: The marker color or column name for color mapping.
        size: The marker size or column name for size mapping.
        symbol: The marker symbol or column name for symbol mapping.
        hover_name: The column name to use for hover labels.
        name: The trace name for the legend.
        **kwargs: Additional keyword arguments to pass to the plotting function.
    
    Returns:
        A plotly Figure object.
    
    Raises:
        ImportError: If plotly is not available.
        ValueError: If x, y, or z is not provided.
    """
    check_plotly()
    
    if x is None or y is None or z is None:
        raise ValueError("x, y, and z must be provided for a 3D scatter plot.")
    
    # Create figure if not provided
    if fig is None:
        fig = create_figure()
    
    # Handle different input types
    if isinstance(data, pd.DataFrame):
        # If using plotly express for advanced features
        if (isinstance(color, str) and color in data.columns) or \
           (isinstance(size, str) and size in data.columns) or \
           (isinstance(symbol, str) and symbol in data.columns) or \
           (isinstance(hover_name, str) and hover_name in data.columns):
            
            scatter_fig = px.scatter_3d(
                data,
                x=x,
                y=y,
                z=z,
                color=color,
                size=size,
                symbol=symbol,
                hover_name=hover_name,
                title=title,
                labels={x: xlabel or x, y: ylabel or y, z: zlabel or z},
                **kwargs
            )
            
            # Add traces from scatter_fig to the main figure
            for trace in scatter_fig.data:
                fig.add_trace(trace)
            
            # Update layout
            layout_args = {'scene': {}}
            if title:
                layout_args['title'] = title
            if xlabel:
                layout_args['scene']['xaxis_title'] = xlabel
            if ylabel:
                layout_args['scene']['yaxis_title'] = ylabel
            if zlabel:
                layout_args['scene']['zaxis_title'] = zlabel
            
            fig.update_layout(**layout_args)
            
            return fig
        else:
            # Simple case: just x, y, and z columns
            x_data = data[x]
            y_data = data[y]
            z_data = data[z]
    else:
        # For numpy arrays or lists
        x_data = x
        y_data = y
        z_data = z
    
    # Create the trace
    trace = go.Scatter3d(
        x=x_data,
        y=y_data,
        z=z_data,
        mode='markers',
        name=name,
        marker=dict(
            color=color,
            size=size,
            symbol=symbol
        ),
        **kwargs
    )
    
    # Add the trace to the figure
    fig.add_trace(trace)
    
    # Update layout
    layout_args = {'scene': {}}
    if title:
        layout_args['title'] = title
    if xlabel:
        layout_args['scene']['xaxis_title'] = xlabel
    if ylabel:
        layout_args['scene']['yaxis_title'] = ylabel
    if zlabel:
        layout_args['scene']['zaxis_title'] = zlabel
    
    fig.update_layout(**layout_args)
    
    return fig


def save_figure(
    fig: go.Figure,
    filename: Union[str, Path],
    format: str = 'html',
    include_plotlyjs: Union[bool, str] = 'cdn',
    **kwargs
) -> str:
    """
    Save a plotly figure to a file.
    
    Args:
        fig: The figure to save.
        filename: The filename to save to.
        format: The format to save as ('html', 'png', 'jpeg', 'svg', 'pdf', 'json').
        include_plotlyjs: Whether to include plotly.js in the output ('cdn', True, False, 'directory').
        **kwargs: Additional keyword arguments to pass to the saving function.
    
    Returns:
        The path to the saved file.
    
    Raises:
        ImportError: If plotly is not available.
    """
    check_plotly()
    
    # Convert to Path object
    path = Path(filename)
    
    # Create directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the figure
    if format == 'html':
        pio.write_html(fig, file=path, include_plotlyjs=include_plotlyjs, **kwargs)
    elif format in ['png', 'jpeg', 'svg', 'pdf']:
        pio.write_image(fig, file=path, format=format, **kwargs)
    elif format == 'json':
        with open(path, 'w') as f:
            f.write(fig.to_json())
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    return str(path)


def figure_to_html(
    fig: go.Figure,
    include_plotlyjs: Union[bool, str] = 'cdn',
    full_html: bool = True,
    **kwargs
) -> str:
    """
    Convert a plotly figure to an HTML string.
    
    Args:
        fig: The figure to convert.
        include_plotlyjs: Whether to include plotly.js in the output ('cdn', True, False, 'directory').
        full_html: Whether to include the full HTML document.
        **kwargs: Additional keyword arguments to pass to the conversion function.
    
    Returns:
        An HTML string representation of the figure.
    
    Raises:
        ImportError: If plotly is not available.
    """
    check_plotly()
    
    return pio.to_html(fig, include_plotlyjs=include_plotlyjs, full_html=full_html, **kwargs)


def figure_to_json(
    fig: go.Figure,
    pretty: bool = False,
    **kwargs
) -> str:
    """
    Convert a plotly figure to a JSON string.
    
    Args:
        fig: The figure to convert.
        pretty: Whether to format the JSON with indentation.
        **kwargs: Additional keyword arguments to pass to the conversion function.
    
    Returns:
        A JSON string representation of the figure.
    
    Raises:
        ImportError: If plotly is not available.
    """
    check_plotly()
    
    if pretty:
        return json.dumps(fig.to_dict(), indent=2, **kwargs)
    else:
        return fig.to_json(**kwargs)


def set_template(template: str = 'plotly') -> None:
    """
    Set the plotly template.
    
    Args:
        template: The template to use. Can be 'plotly', 'plotly_white', 'plotly_dark',
                 'ggplot2', 'seaborn', 'simple_white', 'none'.
    
    Raises:
        ImportError: If plotly is not available.
        ValueError: If the template is not valid.
    """
    check_plotly()
    
    try:
        pio.templates.default = template
    except Exception as e:
        logger.error(f"Error setting template: {str(e)}")
        raise ValueError(f"Invalid template: {template}. {str(e)}")


def get_available_templates() -> List[str]:
    """
    Get a list of available plotly templates.
    
    Returns:
        A list of available template names.
    
    Raises:
        ImportError: If plotly is not available.
    """
    check_plotly()
    
    return list(pio.templates)