"""
Visualization Templates for Science Data Kit

This module provides reusable templates for common visualization types.
These templates can be used to quickly create visualizations for different data types
without having to rewrite the visualization code each time.

Templates include:
- Bar charts
- Line charts
- Scatter plots
- Pie charts
- Network graphs
- Heatmaps
- Box plots
- Histograms
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
import seaborn as sns
import networkx as nx
from matplotlib.colors import LinearSegmentedColormap

def create_bar_chart(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str = "Bar Chart",
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    color: str = "skyblue",
    orientation: str = "vertical",
    figsize: Tuple[int, int] = (10, 6),
    show_values: bool = True,
    sort_values: bool = False,
    sort_ascending: bool = False
) -> str:
    """
    Create a bar chart visualization.

    Args:
        data: DataFrame containing the data to visualize.
        x_column: Column name for x-axis categories.
        y_column: Column name for y-axis values.
        title: Chart title.
        x_label: Label for x-axis (defaults to x_column if None).
        y_label: Label for y-axis (defaults to y_column if None).
        color: Color for the bars.
        orientation: 'vertical' or 'horizontal' orientation.
        figsize: Figure size as (width, height) in inches.
        show_values: Whether to show values on top of bars.
        sort_values: Whether to sort the data by values.
        sort_ascending: Sort in ascending order if True, descending if False.

    Returns:
        Base64-encoded image data for the visualization.
    """
    try:
        # Create a copy of the data to avoid modifying the original
        plot_data = data.copy()
        
        # Sort data if requested
        if sort_values:
            plot_data = plot_data.sort_values(by=y_column, ascending=sort_ascending)
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Set default labels if not provided
        if x_label is None:
            x_label = x_column
        if y_label is None:
            y_label = y_column
        
        # Create bar chart
        if orientation == "vertical":
            bars = ax.bar(plot_data[x_column], plot_data[y_column], color=color)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            # Rotate x-axis labels for better readability if there are many categories
            if len(plot_data) > 5:
                plt.xticks(rotation=45, ha='right')
            
            # Add value labels on top of bars
            if show_values:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + (max(plot_data[y_column]) * 0.01),
                            f'{height:.1f}', ha='center', va='bottom')
        else:  # horizontal
            bars = ax.barh(plot_data[x_column], plot_data[y_column], color=color)
            ax.set_xlabel(y_label)
            ax.set_ylabel(x_label)
            
            # Add value labels to the right of bars
            if show_values:
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width + (max(plot_data[y_column]) * 0.01), bar.get_y() + bar.get_height()/2.,
                            f'{width:.1f}', ha='left', va='center')
        
        # Set title
        ax.set_title(title)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save figure to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("utf-8")
        
        return img_data
    except Exception as e:
        st.error(f"Error creating bar chart: {e}")
        return ""

def create_line_chart(
    data: pd.DataFrame,
    x_column: str,
    y_columns: Union[str, List[str]],
    title: str = "Line Chart",
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    colors: Optional[List[str]] = None,
    figsize: Tuple[int, int] = (10, 6),
    show_markers: bool = True,
    show_legend: bool = True,
    grid: bool = True
) -> str:
    """
    Create a line chart visualization.

    Args:
        data: DataFrame containing the data to visualize.
        x_column: Column name for x-axis.
        y_columns: Column name or list of column names for y-axis values.
        title: Chart title.
        x_label: Label for x-axis (defaults to x_column if None).
        y_label: Label for y-axis (defaults to y_columns if None and y_columns is a string).
        colors: List of colors for the lines (defaults to matplotlib defaults if None).
        figsize: Figure size as (width, height) in inches.
        show_markers: Whether to show markers on the lines.
        show_legend: Whether to show the legend.
        grid: Whether to show grid lines.

    Returns:
        Base64-encoded image data for the visualization.
    """
    try:
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Set default labels if not provided
        if x_label is None:
            x_label = x_column
        
        # Convert y_columns to list if it's a string
        if isinstance(y_columns, str):
            y_columns = [y_columns]
            if y_label is None:
                y_label = y_columns[0]
        
        # Set default y_label if not provided and y_columns is a list
        if y_label is None:
            y_label = "Values"
        
        # Set default colors if not provided
        if colors is None:
            colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        
        # Create line chart
        for i, y_column in enumerate(y_columns):
            color = colors[i % len(colors)]
            marker = 'o' if show_markers else None
            ax.plot(data[x_column], data[y_column], label=y_column, color=color, marker=marker)
        
        # Set labels and title
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        
        # Show legend if requested
        if show_legend and len(y_columns) > 1:
            ax.legend()
        
        # Show grid if requested
        if grid:
            ax.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save figure to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("utf-8")
        
        return img_data
    except Exception as e:
        st.error(f"Error creating line chart: {e}")
        return ""

def create_scatter_plot(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str = "Scatter Plot",
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    color_column: Optional[str] = None,
    size_column: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
    alpha: float = 0.7,
    show_trend_line: bool = False,
    grid: bool = True
) -> str:
    """
    Create a scatter plot visualization.

    Args:
        data: DataFrame containing the data to visualize.
        x_column: Column name for x-axis.
        y_column: Column name for y-axis.
        title: Chart title.
        x_label: Label for x-axis (defaults to x_column if None).
        y_label: Label for y-axis (defaults to y_column if None).
        color_column: Column name to use for point colors (optional).
        size_column: Column name to use for point sizes (optional).
        figsize: Figure size as (width, height) in inches.
        alpha: Transparency of the points (0-1).
        show_trend_line: Whether to show a trend line.
        grid: Whether to show grid lines.

    Returns:
        Base64-encoded image data for the visualization.
    """
    try:
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Set default labels if not provided
        if x_label is None:
            x_label = x_column
        if y_label is None:
            y_label = y_column
        
        # Prepare scatter plot parameters
        scatter_params = {
            'alpha': alpha,
            'edgecolors': 'w',
            'linewidth': 0.5
        }
        
        # Add color parameter if color_column is provided
        if color_column is not None:
            scatter_params['c'] = data[color_column]
            scatter = ax.scatter(data[x_column], data[y_column], **scatter_params)
            # Add colorbar
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label(color_column)
        else:
            # Add size parameter if size_column is provided
            if size_column is not None:
                # Scale sizes to be between 20 and 200
                sizes = 20 + (data[size_column] - data[size_column].min()) / (data[size_column].max() - data[size_column].min()) * 180
                scatter_params['s'] = sizes
            
            ax.scatter(data[x_column], data[y_column], **scatter_params)
        
        # Add trend line if requested
        if show_trend_line:
            z = np.polyfit(data[x_column], data[y_column], 1)
            p = np.poly1d(z)
            ax.plot(data[x_column], p(data[x_column]), "r--", alpha=0.8)
        
        # Set labels and title
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        
        # Show grid if requested
        if grid:
            ax.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save figure to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("utf-8")
        
        return img_data
    except Exception as e:
        st.error(f"Error creating scatter plot: {e}")
        return ""

def create_pie_chart(
    data: pd.DataFrame,
    label_column: str,
    value_column: str,
    title: str = "Pie Chart",
    colors: Optional[List[str]] = None,
    figsize: Tuple[int, int] = (10, 6),
    show_percentages: bool = True,
    show_labels: bool = True,
    explode: Optional[List[float]] = None,
    start_angle: float = 90
) -> str:
    """
    Create a pie chart visualization.

    Args:
        data: DataFrame containing the data to visualize.
        label_column: Column name for slice labels.
        value_column: Column name for slice values.
        title: Chart title.
        colors: List of colors for the slices (defaults to matplotlib defaults if None).
        figsize: Figure size as (width, height) in inches.
        show_percentages: Whether to show percentages on the slices.
        show_labels: Whether to show labels on the slices.
        explode: List of values to "explode" slices (pull them out from the pie).
        start_angle: Starting angle for the pie chart in degrees.

    Returns:
        Base64-encoded image data for the visualization.
    """
    try:
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Prepare data
        labels = data[label_column].tolist()
        values = data[value_column].tolist()
        
        # Set default explode if not provided
        if explode is None:
            explode = [0] * len(labels)
        
        # Set autopct format based on show_percentages
        autopct = '%1.1f%%' if show_percentages else None
        
        # Create pie chart
        ax.pie(
            values,
            explode=explode,
            labels=labels if show_labels else None,
            autopct=autopct,
            shadow=True,
            startangle=start_angle,
            colors=colors
        )
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        # Set title
        ax.set_title(title)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save figure to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("utf-8")
        
        return img_data
    except Exception as e:
        st.error(f"Error creating pie chart: {e}")
        return ""

def create_network_graph(
    nodes: pd.DataFrame,
    edges: pd.DataFrame,
    source_column: str = "source",
    target_column: str = "target",
    node_label_column: Optional[str] = None,
    node_size_column: Optional[str] = None,
    node_color_column: Optional[str] = None,
    edge_weight_column: Optional[str] = None,
    title: str = "Network Graph",
    figsize: Tuple[int, int] = (12, 8),
    node_size_default: float = 300,
    edge_width_default: float = 1.0,
    layout: str = "spring"
) -> str:
    """
    Create a network graph visualization.

    Args:
        nodes: DataFrame containing node data.
        edges: DataFrame containing edge data.
        source_column: Column name in edges DataFrame for source nodes.
        target_column: Column name in edges DataFrame for target nodes.
        node_label_column: Column name in nodes DataFrame for node labels.
        node_size_column: Column name in nodes DataFrame for node sizes.
        node_color_column: Column name in nodes DataFrame for node colors.
        edge_weight_column: Column name in edges DataFrame for edge weights.
        title: Chart title.
        figsize: Figure size as (width, height) in inches.
        node_size_default: Default node size if node_size_column is not provided.
        edge_width_default: Default edge width if edge_weight_column is not provided.
        layout: Layout algorithm to use ('spring', 'circular', 'random', 'shell', 'kamada_kawai').

    Returns:
        Base64-encoded image data for the visualization.
    """
    try:
        # Create a NetworkX graph
        G = nx.Graph()
        
        # Add nodes
        for _, row in nodes.iterrows():
            node_id = row.name
            node_attrs = {}
            
            # Add node label if provided
            if node_label_column is not None:
                node_attrs['label'] = row[node_label_column]
            
            # Add node size if provided
            if node_size_column is not None:
                node_attrs['size'] = row[node_size_column]
            
            # Add node color if provided
            if node_color_column is not None:
                node_attrs['color'] = row[node_color_column]
            
            G.add_node(node_id, **node_attrs)
        
        # Add edges
        for _, row in edges.iterrows():
            source = row[source_column]
            target = row[target_column]
            edge_attrs = {}
            
            # Add edge weight if provided
            if edge_weight_column is not None:
                edge_attrs['weight'] = row[edge_weight_column]
            
            G.add_edge(source, target, **edge_attrs)
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Choose layout
        if layout == 'spring':
            pos = nx.spring_layout(G)
        elif layout == 'circular':
            pos = nx.circular_layout(G)
        elif layout == 'random':
            pos = nx.random_layout(G)
        elif layout == 'shell':
            pos = nx.shell_layout(G)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(G)
        else:
            pos = nx.spring_layout(G)
        
        # Prepare node sizes
        if node_size_column is not None:
            node_sizes = [G.nodes[n].get('size', node_size_default) for n in G.nodes()]
        else:
            node_sizes = node_size_default
        
        # Prepare node colors
        if node_color_column is not None:
            node_colors = [G.nodes[n].get('color', 'skyblue') for n in G.nodes()]
        else:
            node_colors = 'skyblue'
        
        # Prepare edge widths
        if edge_weight_column is not None:
            edge_widths = [G.edges[e].get('weight', edge_width_default) for e in G.edges()]
        else:
            edge_widths = edge_width_default
        
        # Draw the graph
        nx.draw_networkx(
            G,
            pos=pos,
            with_labels=True,
            node_size=node_sizes,
            node_color=node_colors,
            width=edge_widths,
            edge_color='gray',
            alpha=0.8,
            font_size=10,
            font_weight='bold',
            ax=ax
        )
        
        # Set title
        ax.set_title(title)
        
        # Remove axis
        ax.axis('off')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save figure to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("utf-8")
        
        return img_data
    except Exception as e:
        st.error(f"Error creating network graph: {e}")
        return ""

def create_heatmap(
    data: pd.DataFrame,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
    value_column: Optional[str] = None,
    title: str = "Heatmap",
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 8),
    cmap: str = "viridis",
    show_values: bool = True,
    value_format: str = ".1f",
    center: Optional[float] = None
) -> str:
    """
    Create a heatmap visualization.

    Args:
        data: DataFrame containing the data to visualize.
            If x_column, y_column, and value_column are provided, data should have these columns.
            If they are not provided, data should be a pivot table or correlation matrix.
        x_column: Column name for x-axis categories (optional).
        y_column: Column name for y-axis categories (optional).
        value_column: Column name for cell values (optional).
        title: Chart title.
        x_label: Label for x-axis (defaults to x_column if None).
        y_label: Label for y-axis (defaults to y_column if None).
        figsize: Figure size as (width, height) in inches.
        cmap: Colormap to use.
        show_values: Whether to show values in the cells.
        value_format: Format string for cell values.
        center: Value to center the colormap at (useful for diverging data).

    Returns:
        Base64-encoded image data for the visualization.
    """
    try:
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Prepare data for heatmap
        if x_column is not None and y_column is not None and value_column is not None:
            # Pivot the data
            pivot_data = data.pivot(index=y_column, columns=x_column, values=value_column)
        else:
            # Use the data as is (assuming it's already in the right format)
            pivot_data = data
        
        # Set default labels if not provided
        if x_label is None and x_column is not None:
            x_label = x_column
        if y_label is None and y_column is not None:
            y_label = y_column
        
        # Create heatmap
        sns.heatmap(
            pivot_data,
            annot=show_values,
            fmt=value_format,
            cmap=cmap,
            center=center,
            ax=ax,
            cbar_kws={'shrink': 0.8}
        )
        
        # Set labels and title
        if x_label is not None:
            ax.set_xlabel(x_label)
        if y_label is not None:
            ax.set_ylabel(y_label)
        ax.set_title(title)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save figure to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("utf-8")
        
        return img_data
    except Exception as e:
        st.error(f"Error creating heatmap: {e}")
        return ""

def create_box_plot(
    data: pd.DataFrame,
    x_column: Optional[str] = None,
    y_column: str = None,
    title: str = "Box Plot",
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
    color: str = "skyblue",
    notch: bool = False,
    grid: bool = True,
    orientation: str = "vertical"
) -> str:
    """
    Create a box plot visualization.

    Args:
        data: DataFrame containing the data to visualize.
        x_column: Column name for categories (optional).
        y_column: Column name for values.
        title: Chart title.
        x_label: Label for x-axis (defaults to x_column if None).
        y_label: Label for y-axis (defaults to y_column if None).
        figsize: Figure size as (width, height) in inches.
        color: Color for the boxes.
        notch: Whether to create notched box plots.
        grid: Whether to show grid lines.
        orientation: 'vertical' or 'horizontal' orientation.

    Returns:
        Base64-encoded image data for the visualization.
    """
    try:
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Set default labels if not provided
        if x_column is not None and x_label is None:
            x_label = x_column
        if y_label is None:
            y_label = y_column
        
        # Create box plot
        if orientation == "vertical":
            if x_column is not None:
                sns.boxplot(x=x_column, y=y_column, data=data, notch=notch, color=color, ax=ax)
            else:
                sns.boxplot(y=y_column, data=data, notch=notch, color=color, ax=ax)
            
            # Set labels
            if x_column is not None and x_label is not None:
                ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
        else:  # horizontal
            if x_column is not None:
                sns.boxplot(y=x_column, x=y_column, data=data, notch=notch, color=color, ax=ax)
            else:
                sns.boxplot(x=y_column, data=data, notch=notch, color=color, ax=ax)
            
            # Set labels
            if x_column is not None and x_label is not None:
                ax.set_ylabel(x_label)
            ax.set_xlabel(y_label)
        
        # Set title
        ax.set_title(title)
        
        # Show grid if requested
        if grid:
            ax.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save figure to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("utf-8")
        
        return img_data
    except Exception as e:
        st.error(f"Error creating box plot: {e}")
        return ""

def create_histogram(
    data: pd.DataFrame,
    column: str,
    title: str = "Histogram",
    x_label: Optional[str] = None,
    y_label: str = "Frequency",
    figsize: Tuple[int, int] = (10, 6),
    bins: int = 10,
    color: str = "skyblue",
    kde: bool = False,
    grid: bool = True,
    show_stats: bool = True
) -> str:
    """
    Create a histogram visualization.

    Args:
        data: DataFrame containing the data to visualize.
        column: Column name for the data to plot.
        title: Chart title.
        x_label: Label for x-axis (defaults to column if None).
        y_label: Label for y-axis.
        figsize: Figure size as (width, height) in inches.
        bins: Number of bins.
        color: Color for the histogram.
        kde: Whether to show a kernel density estimate.
        grid: Whether to show grid lines.
        show_stats: Whether to show statistics (mean, median, std).

    Returns:
        Base64-encoded image data for the visualization.
    """
    try:
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Set default x_label if not provided
        if x_label is None:
            x_label = column
        
        # Create histogram
        sns.histplot(data[column], bins=bins, kde=kde, color=color, ax=ax)
        
        # Set labels and title
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        
        # Show grid if requested
        if grid:
            ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add statistics if requested
        if show_stats:
            mean = data[column].mean()
            median = data[column].median()
            std = data[column].std()
            
            stats_text = f"Mean: {mean:.2f}\nMedian: {median:.2f}\nStd Dev: {std:.2f}"
            ax.text(0.95, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
                    verticalalignment='top', horizontalalignment='right',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Adjust layout
        plt.tight_layout()
        
        # Save figure to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("utf-8")
        
        return img_data
    except Exception as e:
        st.error(f"Error creating histogram: {e}")
        return ""

def render_visualization(img_data: str, caption: Optional[str] = None, use_column_width: bool = True) -> None:
    """
    Render a visualization in Streamlit.

    Args:
        img_data: Base64-encoded image data.
        caption: Optional caption for the image.
        use_column_width: Whether to use the full column width.
    """
    if img_data:
        st.image(f"data:image/png;base64,{img_data}", caption=caption, use_column_width=use_column_width)
    else:
        st.warning("No visualization data available.")