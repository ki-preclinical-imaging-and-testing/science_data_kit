"""
Dashboard Widgets Module for Science Data Kit

This module provides reusable dashboard widgets that can be used to build
customizable dashboards. These widgets can display various types of data
and visualizations in a consistent and responsive manner.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
import seaborn as sns
import time
from datetime import datetime, timedelta

from science_data_kit.ui.components.visualization_templates import (
    create_bar_chart,
    create_line_chart,
    create_scatter_plot,
    create_pie_chart,
    create_network_graph,
    create_heatmap,
    create_box_plot,
    create_histogram,
    render_visualization
)

class DashboardWidget:
    """Base class for dashboard widgets."""

    def __init__(self, title: str, description: Optional[str] = None):
        """
        Initialize a dashboard widget.

        Args:
            title: The title of the widget
            description: An optional description of the widget
        """
        self.title = title
        self.description = description
        self.last_updated = datetime.now()
        self.refresh_interval = 60  # Default refresh interval in seconds

    def render(self):
        """Render the widget. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement render()")

    def should_refresh(self) -> bool:
        """
        Check if the widget should be refreshed based on the refresh interval.

        Returns:
            bool: True if the widget should be refreshed, False otherwise
        """
        return (datetime.now() - self.last_updated).total_seconds() >= self.refresh_interval

    def refresh(self):
        """Refresh the widget data."""
        self.last_updated = datetime.now()

    def render_widget_container(self):
        """Render the widget in a container with title and description."""
        with st.container():
            st.subheader(self.title)
            if self.description:
                st.caption(self.description)

            # Add a refresh button
            col1, col2 = st.columns([0.85, 0.15])
            with col2:
                if st.button("🔄", key=f"refresh_{self.title}"):
                    self.refresh()

            # Render the widget content
            self.render()

            # Show last updated time
            st.caption(f"Last updated: {self.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")


class MetricWidget(DashboardWidget):
    """Widget for displaying a single metric with optional trend indicator."""

    def __init__(self, title: str, value_func: Callable[[], Any], 
                 description: Optional[str] = None, 
                 prefix: str = "", suffix: str = "",
                 trend_func: Optional[Callable[[], float]] = None,
                 trend_is_good_func: Optional[Callable[[float], bool]] = None):
        """
        Initialize a metric widget.

        Args:
            title: The title of the widget
            value_func: A function that returns the metric value
            description: An optional description of the widget
            prefix: A prefix to display before the value (e.g., "$")
            suffix: A suffix to display after the value (e.g., "%")
            trend_func: A function that returns the trend value (percentage change)
            trend_is_good_func: A function that determines if a trend is good (True) or bad (False)
        """
        super().__init__(title, description)
        self.value_func = value_func
        self.prefix = prefix
        self.suffix = suffix
        self.trend_func = trend_func
        self.trend_is_good_func = trend_is_good_func
        self.value = None
        self.trend = None
        self.refresh()

    def refresh(self):
        """Refresh the metric data."""
        self.value = self.value_func()
        if self.trend_func:
            self.trend = self.trend_func()
        super().refresh()

    def render(self):
        """Render the metric widget."""
        if self.value is None:
            st.warning("No data available")
            return

        # Format the value
        formatted_value = f"{self.prefix}{self.value}{self.suffix}"

        # Display the metric
        if self.trend is not None and self.trend_is_good_func is not None:
            # Determine if the trend is good or bad
            is_good = self.trend_is_good_func(self.trend)

            # Format the trend
            trend_sign = "+" if self.trend > 0 else ""
            trend_text = f"{trend_sign}{self.trend:.1f}%"

            # Display the metric with trend
            if is_good:
                st.metric(label=self.title, value=formatted_value, delta=trend_text, label_visibility="collapsed")
            else:
                st.metric(label=self.title, value=formatted_value, delta=trend_text, delta_color="inverse", label_visibility="collapsed")
        else:
            # Display the metric without trend
            st.metric(label=self.title, value=formatted_value, label_visibility="collapsed")


class ChartWidget(DashboardWidget):
    """Widget for displaying a chart visualization."""

    def __init__(self, title: str, data_func: Callable[[], pd.DataFrame], 
                 chart_type: str, chart_params: Dict[str, Any],
                 description: Optional[str] = None):
        """
        Initialize a chart widget.

        Args:
            title: The title of the widget
            data_func: A function that returns the data for the chart
            chart_type: The type of chart to display (bar_chart, line_chart, etc.)
            chart_params: Parameters for the chart (excluding data)
            description: An optional description of the widget
        """
        super().__init__(title, description)
        self.data_func = data_func
        self.chart_type = chart_type
        self.chart_params = chart_params
        self.data = None
        self.chart_image = None
        self.refresh()

    def refresh(self):
        """Refresh the chart data and image."""
        self.data = self.data_func()

        # Get the chart function based on the chart type
        chart_functions = {
            "bar_chart": create_bar_chart,
            "line_chart": create_line_chart,
            "scatter_plot": create_scatter_plot,
            "pie_chart": create_pie_chart,
            "network_graph": create_network_graph,
            "heatmap": create_heatmap,
            "box_plot": create_box_plot,
            "histogram": create_histogram
        }

        chart_func = chart_functions.get(self.chart_type)
        if chart_func and self.data is not None:
            # Create a copy of the chart parameters and add the data
            params = self.chart_params.copy()
            params["data"] = self.data

            # Generate the chart image
            try:
                self.chart_image = chart_func(**params)
            except Exception as e:
                st.error(f"Error creating chart: {str(e)}")
                self.chart_image = None

        super().refresh()

    def render(self):
        """Render the chart widget."""
        if self.data is None:
            st.warning("No data available")
            return

        if self.chart_image:
            render_visualization(self.chart_image)
        else:
            st.warning("Failed to generate chart")


class TableWidget(DashboardWidget):
    """Widget for displaying tabular data."""

    def __init__(self, title: str, data_func: Callable[[], pd.DataFrame], 
                 description: Optional[str] = None,
                 use_container_width: bool = True,
                 height: Optional[int] = None):
        """
        Initialize a table widget.

        Args:
            title: The title of the widget
            data_func: A function that returns the data for the table
            description: An optional description of the widget
            use_container_width: Whether to use the full container width
            height: Optional height for the table
        """
        super().__init__(title, description)
        self.data_func = data_func
        self.use_container_width = use_container_width
        self.height = height
        self.data = None
        self.refresh()

    def refresh(self):
        """Refresh the table data."""
        self.data = self.data_func()
        super().refresh()

    def render(self):
        """Render the table widget."""
        if self.data is None:
            st.warning("No data available")
            return

        st.dataframe(
            self.data, 
            use_container_width=self.use_container_width,
            height=self.height
        )


class StatusWidget(DashboardWidget):
    """Widget for displaying status information with colored indicators."""

    def __init__(self, title: str, items_func: Callable[[], List[Dict[str, Any]]], 
                 description: Optional[str] = None):
        """
        Initialize a status widget.

        Args:
            title: The title of the widget
            items_func: A function that returns a list of status items
                Each item should be a dict with keys:
                - name: The name of the item
                - status: The status (e.g., "ok", "warning", "error")
                - message: Optional message to display
            description: An optional description of the widget
        """
        super().__init__(title, description)
        self.items_func = items_func
        self.items = None
        self.refresh()

    def refresh(self):
        """Refresh the status data."""
        self.items = self.items_func()
        super().refresh()

    def render(self):
        """Render the status widget."""
        if not self.items:
            st.warning("No status items available")
            return

        # Define status colors
        status_colors = {
            "ok": "green",
            "warning": "orange",
            "error": "red",
            "unknown": "gray"
        }

        # Create a table for the status items
        for item in self.items:
            name = item.get("name", "Unknown")
            status = item.get("status", "unknown").lower()
            message = item.get("message", "")

            # Get the color for the status
            color = status_colors.get(status, "gray")

            # Create a row with colored status indicator
            col1, col2, col3 = st.columns([0.3, 0.2, 0.5])
            with col1:
                st.write(name)
            with col2:
                st.markdown(f"<span style='color:{color};'>●</span> {status.upper()}", unsafe_allow_html=True)
            with col3:
                st.write(message)


class InfoWidget(DashboardWidget):
    """Widget for displaying informational content."""

    def __init__(self, title: str, content_func: Callable[[], str], 
                 description: Optional[str] = None,
                 content_type: str = "markdown"):
        """
        Initialize an info widget.

        Args:
            title: The title of the widget
            content_func: A function that returns the content to display
            description: An optional description of the widget
            content_type: The type of content (markdown, code, etc.)
        """
        super().__init__(title, description)
        self.content_func = content_func
        self.content_type = content_type
        self.content = None
        self.refresh()

    def refresh(self):
        """Refresh the info content."""
        self.content = self.content_func()
        super().refresh()

    def render(self):
        """Render the info widget."""
        if not self.content:
            st.warning("No content available")
            return

        if self.content_type == "markdown":
            st.markdown(self.content)
        elif self.content_type == "code":
            st.code(self.content)
        elif self.content_type == "json":
            st.json(self.content)
        else:
            st.write(self.content)


def create_dashboard_layout(widgets: List[DashboardWidget], layout: List[List[int]]):
    """
    Create a dashboard layout with the given widgets and layout specification.

    Args:
        widgets: A list of DashboardWidget instances
        layout: A list of lists specifying the layout
            Each inner list represents a row, and each integer represents
            the number of widgets in that position of the row.
            For example, [[1, 1], [2]] creates a layout with two widgets
            in the first row and one widget spanning the full width in the second row.
    """
    widget_index = 0

    for row in layout:
        cols = st.columns(row)

        for i, col_width in enumerate(row):
            if widget_index < len(widgets):
                with cols[i]:
                    widgets[widget_index].render_widget_container()
                    widget_index += 1

    # Render any remaining widgets in full-width containers
    while widget_index < len(widgets):
        widgets[widget_index].render_widget_container()
        widget_index += 1


# Example usage:
def example_dashboard():
    """Create an example dashboard with various widgets."""

    # Create some example data functions
    def get_total_users():
        return 1250

    def get_user_trend():
        return 5.2  # 5.2% increase

    def is_user_trend_good(trend):
        return trend > 0

    def get_sales_data():
        dates = pd.date_range(start="2023-01-01", periods=10, freq="D")
        data = {
            "Date": dates,
            "Sales": np.random.randint(100, 1000, size=10)
        }
        return pd.DataFrame(data)

    def get_status_items():
        return [
            {"name": "Database", "status": "ok", "message": "Connected"},
            {"name": "API", "status": "warning", "message": "High latency"},
            {"name": "Storage", "status": "error", "message": "Disk space low"}
        ]

    def get_info_content():
        return """
        ## Dashboard Information

        This is an example dashboard showing various widgets:

        - Metric widgets for displaying KPIs
        - Chart widgets for visualizations
        - Table widgets for tabular data
        - Status widgets for system status
        - Info widgets for documentation

        Widgets can be arranged in a flexible layout and automatically refresh.
        """

    # Create widgets
    widgets = [
        MetricWidget(
            title="Total Users",
            value_func=get_total_users,
            description="Number of registered users",
            trend_func=get_user_trend,
            trend_is_good_func=is_user_trend_good
        ),
        ChartWidget(
            title="Sales Trend",
            data_func=get_sales_data,
            chart_type="line_chart",
            chart_params={
                "x_column": "Date",
                "y_columns": "Sales",
                "title": "Daily Sales",
                "show_markers": True
            },
            description="Daily sales over time"
        ),
        TableWidget(
            title="Sales Data",
            data_func=get_sales_data,
            description="Raw sales data"
        ),
        StatusWidget(
            title="System Status",
            items_func=get_status_items,
            description="Current status of system components"
        ),
        InfoWidget(
            title="Dashboard Info",
            content_func=get_info_content,
            description="Information about this dashboard"
        )
    ]

    # Create a layout with 2 rows
    # First row: 2 widgets side by side
    # Second row: 3 widgets side by side
    layout = [[1, 1], [1, 1, 1]]

    # Render the dashboard
    st.title("Example Dashboard")
    create_dashboard_layout(widgets, layout)


if __name__ == "__main__":
    example_dashboard()
