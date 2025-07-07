"""
Visualization Templates for Science Data Kit

This module provides standardized visualization templates for use across the application.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from typing import Optional, List, Union, Dict, Any, Tuple

# Import UI constants
try:
    from science_data_kit.ui.components.ui_constants import *
except ImportError:
    # Default values if constants are not available
    COLOR_PRIMARY = "#4CAF50"
    COLOR_SECONDARY = "#2196F3"

def standard_bar_chart(data: pd.DataFrame, x_column: str, y_column: str, title: str, x_label: Optional[str] = None, y_label: Optional[str] = None, color: Optional[str] = None, figsize: Tuple[int, int] = (8, 5), show_values: bool = False) -> str:
    """
    Create a standardized bar chart.
    
    Args:
        data: The DataFrame containing the data
        x_column: The column to use for the x-axis
        y_column: The column to use for the y-axis
        title: The title of the chart
        x_label: Optional label for the x-axis
        y_label: Optional label for the y-axis
        color: Optional color for the bars
        figsize: Optional figure size as (width, height) in inches
        show_values: Optional flag to show values on the bars
    
    Returns:
        Base64-encoded image data
    """
    # Set default values
    x_label = x_label or x_column
    y_label = y_label or y_column
    color = color or COLOR_PRIMARY
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create the bar chart
    bars = ax.bar(data[x_column], data[y_column], color=color)
    
    # Add values on top of the bars if requested
    if show_values:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, f"{height:.1f}",
                   ha="center", va="bottom")
    
    # Set title and labels
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    
    # Adjust layout
    plt.tight_layout()
    
    # Convert the figure to a base64-encoded image
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    
    return img_str

def standard_line_chart(data: pd.DataFrame, x_column: str, y_columns: List[str], title: str, x_label: Optional[str] = None, y_label: Optional[str] = None, figsize: Tuple[int, int] = (10, 6), show_markers: bool = False, show_legend: bool = True) -> str:
    """
    Create a standardized line chart.
    
    Args:
        data: The DataFrame containing the data
        x_column: The column to use for the x-axis
        y_columns: The columns to use for the y-axis (multiple lines)
        title: The title of the chart
        x_label: Optional label for the x-axis
        y_label: Optional label for the y-axis
        figsize: Optional figure size as (width, height) in inches
        show_markers: Optional flag to show markers on the lines
        show_legend: Optional flag to show the legend
    
    Returns:
        Base64-encoded image data
    """
    # Set default values
    x_label = x_label or x_column
    y_label = y_label or ", ".join(y_columns)
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create the line chart
    for y_column in y_columns:
        ax.plot(data[x_column], data[y_column], marker="o" if show_markers else None, label=y_column)
    
    # Set title and labels
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    
    # Show legend if requested
    if show_legend:
        ax.legend()
    
    # Adjust layout
    plt.tight_layout()
    
    # Convert the figure to a base64-encoded image
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    
    return img_str

def standard_scatter_plot(data: pd.DataFrame, x_column: str, y_column: str, title: str, x_label: Optional[str] = None, y_label: Optional[str] = None, color_column: Optional[str] = None, size_column: Optional[str] = None, figsize: Tuple[int, int] = (8, 8), show_legend: bool = True) -> str:
    """
    Create a standardized scatter plot.
    
    Args:
        data: The DataFrame containing the data
        x_column: The column to use for the x-axis
        y_column: The column to use for the y-axis
        title: The title of the chart
        x_label: Optional label for the x-axis
        y_label: Optional label for the y-axis
        color_column: Optional column to use for point colors
        size_column: Optional column to use for point sizes
        figsize: Optional figure size as (width, height) in inches
        show_legend: Optional flag to show the legend
    
    Returns:
        Base64-encoded image data
    """
    # Set default values
    x_label = x_label or x_column
    y_label = y_label or y_column
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create the scatter plot
    scatter_kwargs = {}
    if color_column:
        scatter_kwargs["c"] = data[color_column]
    if size_column:
        scatter_kwargs["s"] = data[size_column]
    
    scatter = ax.scatter(data[x_column], data[y_column], **scatter_kwargs)
    
    # Set title and labels
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    
    # Show legend if requested and color_column is provided
    if show_legend and color_column:
        if len(data[color_column].unique()) <= 10:  # Only show legend for categorical data
            legend1 = ax.legend(*scatter.legend_elements(), title=color_column)
            ax.add_artist(legend1)
    
    # Adjust layout
    plt.tight_layout()
    
    # Convert the figure to a base64-encoded image
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    
    return img_str