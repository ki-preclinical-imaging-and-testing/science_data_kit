# Advanced Data Visualization with Science Data Kit

## Introduction (0:00 - 1:30)

Hello and welcome to this tutorial on advanced data visualization with the Science Data Kit. My name is [Presenter Name], and today I'll be showing you how to create sophisticated visualizations for your scientific data.

In this tutorial, we'll cover:
1. Creating custom plots with matplotlib and plotly
2. Building interactive visualizations
3. Working with 3D visualizations
4. Creating dashboards with multiple visualizations

Before we begin, make sure you have the Science Data Kit installed and have access to a Neo4j database with some sample data. If you need help with setup, please refer to our "Getting Started" tutorial.

## Basic Visualization Review (1:30 - 3:45)

Let's start with a quick review of basic visualization capabilities in the SDK. The SDK provides several built-in visualization functions that make it easy to create common plot types.

```python
from science_data_kit.core.visualization import create_bar_chart, create_line_plot, create_scatter_plot

# Create a simple bar chart
create_bar_chart(data=my_data, x_column='category', y_column='value', title='Sample Bar Chart')

# Create a line plot
create_line_plot(data=time_series_data, x_column='date', y_column='measurement', title='Time Series Data')

# Create a scatter plot
create_scatter_plot(data=correlation_data, x_column='variable_x', y_column='variable_y', 
                   color_column='group', title='Correlation Analysis')
```

These functions provide a convenient wrapper around matplotlib and plotly, with sensible defaults for scientific data visualization.

## Custom Visualizations (3:45 - 8:30)

Now, let's move on to creating custom visualizations. The SDK allows you to access the underlying matplotlib or plotly objects for full customization.

```python
from science_data_kit.core.visualization import create_custom_plot
import matplotlib.pyplot as plt
import numpy as np

# Create a custom plot with matplotlib
fig, ax = create_custom_plot(figsize=(10, 6))

# Generate some data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# Create a custom plot
ax.plot(x, y1, label='sin(x)', linewidth=2)
ax.plot(x, y2, label='cos(x)', linewidth=2, linestyle='--')
ax.fill_between(x, y1, y2, where=(y1 > y2), alpha=0.3, color='green', interpolate=True)
ax.fill_between(x, y1, y2, where=(y1 <= y2), alpha=0.3, color='red', interpolate=True)

# Customize the plot
ax.set_title('Custom Trigonometric Functions Plot', fontsize=16)
ax.set_xlabel('X', fontsize=12)
ax.set_ylabel('Y', fontsize=12)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=12)

# Show the plot
plt.tight_layout()
plt.show()
```

This gives you complete control over the visualization, allowing you to create exactly what you need for your scientific data.

## Interactive Visualizations (8:30 - 14:00)

One of the most powerful features of the SDK is the ability to create interactive visualizations. Let's see how to create an interactive scatter plot with plotly.

```python
from science_data_kit.core.visualization import create_interactive_plot
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Create some sample data
np.random.seed(42)
n_points = 100
data = pd.DataFrame({
    'x': np.random.normal(0, 1, n_points),
    'y': np.random.normal(0, 1, n_points),
    'size': np.random.uniform(5, 15, n_points),
    'group': np.random.choice(['A', 'B', 'C'], n_points),
    'value': np.random.uniform(0, 1, n_points)
})

# Create an interactive plot
fig = create_interactive_plot()

# Add scatter trace
for group, group_data in data.groupby('group'):
    fig.add_trace(go.Scatter(
        x=group_data['x'],
        y=group_data['y'],
        mode='markers',
        marker=dict(
            size=group_data['size'],
            color=group_data['value'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Value')
        ),
        text=group_data.apply(lambda row: f"Group: {row['group']}<br>Value: {row['value']:.2f}", axis=1),
        hoverinfo='text',
        name=f'Group {group}'
    ))

# Customize layout
fig.update_layout(
    title='Interactive Scatter Plot',
    xaxis_title='X Axis',
    yaxis_title='Y Axis',
    legend_title='Group',
    hovermode='closest'
)

# Show the plot
fig.show()
```

This creates an interactive scatter plot where you can hover over points to see details, zoom in and out, and even save the plot as an image.

## 3D Visualizations (14:00 - 20:00)

Now, let's explore 3D visualizations. The SDK provides several functions for creating 3D plots, which are particularly useful for spatial data, molecular structures, and multivariate relationships.

```python
from science_data_kit.core.visualization.visualization_3d import scatter_3d, surface_3d
import numpy as np
import pandas as pd

# Create 3D scatter plot data
np.random.seed(42)
n_points = 200
scatter_data = pd.DataFrame({
    'x': np.random.normal(0, 1, n_points),
    'y': np.random.normal(0, 1, n_points),
    'z': np.random.normal(0, 1, n_points),
    'color': np.random.rand(n_points),
    'size': np.random.rand(n_points) * 2 + 0.5
})

# Create 3D scatter plot
scatter_fig = scatter_3d(
    data=scatter_data,
    x_column='x',
    y_column='y',
    z_column='z',
    color_column='color',
    size_column='size',
    title='3D Scatter Plot',
    library='plotly'
)

# Display the plot
scatter_fig.show()

# Create 3D surface plot
x = np.linspace(-5, 5, 50)
y = np.linspace(-5, 5, 50)

def z_func(x, y):
    return np.sin(np.sqrt(x**2 + y**2))

surface_fig = surface_3d(
    x=x,
    y=y,
    z=z_func,
    title='3D Surface Plot',
    colormap='viridis',
    library='plotly'
)

# Display the plot
surface_fig.show()
```

These 3D visualizations allow you to explore complex relationships in your data that might not be apparent in 2D visualizations.

## Creating Dashboards (20:00 - 25:00)

Finally, let's see how to create dashboards with multiple visualizations. The SDK provides a dashboard framework that allows you to combine multiple plots into a single interactive dashboard.

```python
from science_data_kit.core.visualization import create_dashboard, add_plot_to_dashboard
import plotly.express as px
import pandas as pd
import numpy as np

# Create a dashboard
dashboard = create_dashboard(title='Scientific Data Dashboard', n_rows=2, n_cols=2)

# Create some sample data
np.random.seed(42)
dates = pd.date_range(start='2023-01-01', periods=100)
time_series = pd.DataFrame({
    'date': dates,
    'value1': np.cumsum(np.random.normal(0, 1, 100)),
    'value2': np.cumsum(np.random.normal(0, 1, 100)) + 10,
    'category': np.random.choice(['A', 'B', 'C'], 100)
})

# Add a line plot
line_fig = px.line(time_series, x='date', y=['value1', 'value2'], title='Time Series Data')
add_plot_to_dashboard(dashboard, line_fig, row=1, col=1)

# Add a scatter plot
scatter_fig = px.scatter(time_series, x='value1', y='value2', color='category', title='Correlation Analysis')
add_plot_to_dashboard(dashboard, scatter_fig, row=1, col=2)

# Add a histogram
hist_fig = px.histogram(time_series, x='value1', title='Distribution of Value 1')
add_plot_to_dashboard(dashboard, hist_fig, row=2, col=1)

# Add a box plot
box_fig = px.box(time_series, x='category', y='value2', title='Value 2 by Category')
add_plot_to_dashboard(dashboard, box_fig, row=2, col=2)

# Display the dashboard
dashboard.show()
```

This creates a dashboard with four different visualizations, allowing you to present multiple aspects of your data in a single view.

## Conclusion (25:00 - 26:30)

In this tutorial, we've explored advanced data visualization techniques using the Science Data Kit. We've covered custom plots, interactive visualizations, 3D visualizations, and dashboards.

These tools provide powerful ways to explore and communicate your scientific data. Remember that effective visualization is about more than just making pretty pictures—it's about revealing patterns, relationships, and insights in your data.

For more information, check out the SDK documentation, which includes a comprehensive guide to all visualization functions and many more examples.

Thank you for watching, and happy visualizing!