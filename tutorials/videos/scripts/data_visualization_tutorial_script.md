# Data Visualization Tutorial Script

## Introduction (0:00-1:00)

Hello and welcome to the Science Data Kit Data Visualization Tutorial. In this video, we'll explore the various visualization capabilities of the Science Data Kit, from basic static plots to interactive visualizations and specialized graph database visualizations.

The Science Data Kit provides a comprehensive set of tools for visualizing scientific data, allowing researchers to gain insights and communicate their findings effectively. Whether you're working with tabular data, time series, or complex network relationships, the SDK has visualization options to meet your needs.

In this tutorial, we'll cover:
1. Static visualizations with Matplotlib
2. Interactive visualizations with Plotly
3. Web-based visualizations with D3.js
4. Graph database visualizations with Neo4j

Let's get started!

## Setting Up the Environment (1:00-2:30)

Before we begin creating visualizations, let's set up our environment. We'll need to import the necessary libraries and load some sample data.

```python
# Import the Science Data Kit visualization modules
from science_data_kit.visualization import static_plots, interactive_plots, web_plots, graph_plots

# Import supporting libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
```

For this tutorial, we'll use a sample dataset from a preclinical cancer research study. This dataset includes tumor growth measurements over time for different treatment groups.

```python
# Load the sample dataset
from science_data_kit.data.samples.load_preclinical_dataset import load_tumor_growth_data

# Load the data
tumor_growth_df = load_tumor_growth_data()

# Display the first few rows
print(tumor_growth_df.head())
```

The dataset contains the following columns:
- `animal_id`: Unique identifier for each animal
- `treatment_group`: The treatment group (Control, Drug A, Drug B, Combination)
- `day`: Day of measurement
- `tumor_volume`: Tumor volume in mm³
- `weight`: Animal weight in grams

Now that we have our data loaded, let's start creating visualizations.

## Static Visualizations with Matplotlib (2:30-6:00)

Let's begin with static visualizations using Matplotlib, which is excellent for creating publication-quality figures.

### Line Plot for Tumor Growth

First, let's create a line plot showing the average tumor growth over time for each treatment group.

```python
# Calculate the mean tumor volume for each treatment group and day
grouped_data = tumor_growth_df.groupby(['treatment_group', 'day'])['tumor_volume'].mean().reset_index()

# Create a pivot table for easier plotting
pivot_data = grouped_data.pivot(index='day', columns='treatment_group', values='tumor_volume')

# Create the line plot using the Science Data Kit's static_plots module
fig, ax = static_plots.create_line_plot(
    data=pivot_data,
    title='Average Tumor Growth Over Time',
    xlabel='Day',
    ylabel='Tumor Volume (mm³)',
    legend_title='Treatment Group',
    grid=True,
    colors=['blue', 'red', 'green', 'purple']
)

# Display the plot
plt.tight_layout()
plt.show()
```

This plot clearly shows how tumor volume changes over time for each treatment group. We can see that the control group has the fastest tumor growth, while the combination therapy shows the best tumor suppression.

### Bar Plot for Final Tumor Volume

Next, let's create a bar plot comparing the final tumor volumes across treatment groups.

```python
# Get the data for the last day of measurement
last_day = tumor_growth_df['day'].max()
final_day_data = tumor_growth_df[tumor_growth_df['day'] == last_day]

# Calculate the mean and standard error for each treatment group
final_stats = final_day_data.groupby('treatment_group')['tumor_volume'].agg(['mean', 'sem']).reset_index()

# Create the bar plot
fig, ax = static_plots.create_bar_plot(
    data=final_stats,
    x='treatment_group',
    y='mean',
    yerr='sem',
    title='Final Tumor Volume by Treatment Group',
    xlabel='Treatment Group',
    ylabel='Tumor Volume (mm³)',
    color='skyblue',
    edgecolor='black'
)

# Display the plot
plt.tight_layout()
plt.show()
```

This bar plot provides a clear comparison of the final tumor volumes across treatment groups, with error bars representing the standard error of the mean.

### Box Plot for Weight Distribution

Now, let's create a box plot to visualize the distribution of animal weights across treatment groups.

```python
# Create the box plot
fig, ax = static_plots.create_box_plot(
    data=tumor_growth_df,
    x='treatment_group',
    y='weight',
    title='Weight Distribution by Treatment Group',
    xlabel='Treatment Group',
    ylabel='Weight (g)',
    palette='pastel'
)

# Display the plot
plt.tight_layout()
plt.show()
```

The box plot shows the median, quartiles, and potential outliers in the weight data for each treatment group, helping us assess whether the treatments affected animal weight.

### Heatmap for Correlation Matrix

Finally, let's create a heatmap to visualize the correlation between different variables in our dataset.

```python
# Create a correlation matrix
numeric_data = tumor_growth_df[['day', 'tumor_volume', 'weight']]
correlation_matrix = numeric_data.corr()

# Create the heatmap
fig, ax = static_plots.create_heatmap(
    data=correlation_matrix,
    title='Correlation Matrix',
    cmap='coolwarm',
    annot=True,
    fmt='.2f',
    linewidths=0.5
)

# Display the plot
plt.tight_layout()
plt.show()
```

The heatmap visualizes the correlation coefficients between day, tumor volume, and weight, helping us understand how these variables relate to each other.

## Interactive Visualizations with Plotly (6:00-10:00)

Now, let's move on to interactive visualizations using Plotly, which allows users to hover over data points, zoom in/out, and more.

### Interactive Line Plot

First, let's recreate our tumor growth line plot with Plotly for interactivity.

```python
# Calculate the mean tumor volume for each treatment group and day
grouped_data = tumor_growth_df.groupby(['treatment_group', 'day'])['tumor_volume'].mean().reset_index()

# Create the interactive line plot
fig = interactive_plots.create_line_plot(
    data=grouped_data,
    x='day',
    y='tumor_volume',
    color='treatment_group',
    title='Average Tumor Growth Over Time',
    xlabel='Day',
    ylabel='Tumor Volume (mm³)',
    hover_data=['treatment_group', 'tumor_volume']
)

# Display the plot
fig.show()
```

This interactive plot allows users to hover over data points to see exact values, zoom in on specific time periods, and toggle treatment groups on/off in the legend.

### Interactive Scatter Plot

Next, let's create an interactive scatter plot to explore the relationship between tumor volume and animal weight.

```python
# Create the interactive scatter plot
fig = interactive_plots.create_scatter_plot(
    data=tumor_growth_df,
    x='weight',
    y='tumor_volume',
    color='treatment_group',
    size='day',  # Point size increases with day
    title='Tumor Volume vs. Weight',
    xlabel='Weight (g)',
    ylabel='Tumor Volume (mm³)',
    hover_data=['animal_id', 'day']
)

# Display the plot
fig.show()
```

This scatter plot allows us to explore the relationship between tumor volume and weight, with points colored by treatment group and sized by day of measurement.

### Interactive Box Plot

Let's create an interactive box plot for tumor volumes across treatment groups and days.

```python
# Create the interactive box plot
fig = interactive_plots.create_box_plot(
    data=tumor_growth_df,
    x='treatment_group',
    y='tumor_volume',
    color='treatment_group',
    title='Tumor Volume Distribution by Treatment Group',
    xlabel='Treatment Group',
    ylabel='Tumor Volume (mm³)',
    points='all'  # Show all points
)

# Display the plot
fig.show()
```

This interactive box plot allows users to hover over boxes and points to see exact values and toggle treatment groups on/off.

### Interactive 3D Scatter Plot

Finally, let's create a 3D scatter plot to visualize the relationship between day, tumor volume, and weight.

```python
# Create the interactive 3D scatter plot
fig = interactive_plots.create_3d_scatter_plot(
    data=tumor_growth_df,
    x='day',
    y='weight',
    z='tumor_volume',
    color='treatment_group',
    title='3D Visualization of Tumor Growth Data',
    xlabel='Day',
    ylabel='Weight (g)',
    zlabel='Tumor Volume (mm³)',
    hover_data=['animal_id']
)

# Display the plot
fig.show()
```

This 3D scatter plot provides a comprehensive view of the relationships between day, weight, and tumor volume, with points colored by treatment group.

## Web-based Visualizations with D3.js (10:00-13:30)

Now, let's explore web-based visualizations using D3.js, which allows for highly customized interactive visualizations that can be embedded in web applications.

### Setting Up D3.js Visualization

To use D3.js visualizations in the Science Data Kit, we need to prepare our data in a format suitable for web visualization.

```python
# Prepare data for D3.js visualization
from science_data_kit.visualization.web_plots import prepare_data_for_d3

# Prepare the tumor growth data
d3_data = prepare_data_for_d3(
    data=grouped_data,
    id_col='treatment_group',
    x_col='day',
    y_col='tumor_volume'
)

# Display the prepared data structure
print(d3_data)
```

### Creating a D3.js Line Chart

Now, let's create a D3.js line chart for our tumor growth data.

```python
# Create a D3.js line chart
from science_data_kit.visualization.web_plots import create_d3_line_chart

# Create the chart
html_output = create_d3_line_chart(
    data=d3_data,
    title='Tumor Growth Over Time',
    xlabel='Day',
    ylabel='Tumor Volume (mm³)',
    width=800,
    height=500,
    margin={'top': 50, 'right': 150, 'bottom': 80, 'left': 80},
    line_colors=['#4e79a7', '#f28e2c', '#e15759', '#76b7b2']
)

# Save the HTML output to a file
with open('tumor_growth_d3.html', 'w') as f:
    f.write(html_output)

# Display the chart in a Jupyter notebook
from IPython.display import HTML
HTML(html_output)
```

This D3.js line chart provides a highly customizable and interactive visualization that can be embedded in web applications or shared as a standalone HTML file.

### Creating a D3.js Stacked Area Chart

Let's create a stacked area chart to visualize the proportion of animals in each treatment group over time.

```python
# Calculate the count of animals in each treatment group by day
animal_counts = tumor_growth_df.groupby(['day', 'treatment_group']).size().reset_index(name='count')

# Prepare data for D3.js visualization
d3_stacked_data = prepare_data_for_d3(
    data=animal_counts,
    id_col='treatment_group',
    x_col='day',
    y_col='count'
)

# Create a D3.js stacked area chart
from science_data_kit.visualization.web_plots import create_d3_stacked_area_chart

# Create the chart
html_output = create_d3_stacked_area_chart(
    data=d3_stacked_data,
    title='Animal Count by Treatment Group Over Time',
    xlabel='Day',
    ylabel='Number of Animals',
    width=800,
    height=500,
    margin={'top': 50, 'right': 150, 'bottom': 80, 'left': 80},
    area_colors=['#4e79a7', '#f28e2c', '#e15759', '#76b7b2']
)

# Save the HTML output to a file
with open('animal_count_d3.html', 'w') as f:
    f.write(html_output)

# Display the chart in a Jupyter notebook
from IPython.display import HTML
HTML(html_output)
```

This stacked area chart provides a visual representation of the number of animals in each treatment group over time.

## Graph Database Visualizations with Neo4j (13:30-17:00)

Finally, let's explore visualizations for graph databases using Neo4j. The Science Data Kit provides tools for visualizing graph data, which is particularly useful for understanding complex relationships.

### Connecting to Neo4j

First, let's connect to a Neo4j database containing our preclinical research data.

```python
# Connect to Neo4j
from science_data_kit.database import neo4j_connector

# Create a connection to the Neo4j database
connector = neo4j_connector.Neo4jConnector(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# Test the connection
if connector.test_connection():
    print("Successfully connected to Neo4j database")
else:
    print("Failed to connect to Neo4j database")
```

### Visualizing Treatment Groups and Animals

Now, let's visualize the relationship between treatment groups and animals.

```python
# Create a Cypher query to get treatment groups and animals
query = """
MATCH (tg:TreatmentGroup)<-[:BELONGS_TO]-(a:Animal)
RETURN tg, a
LIMIT 100
"""

# Execute the query and visualize the results
from science_data_kit.visualization.graph_plots import visualize_neo4j_query

# Create the visualization
graph_html = visualize_neo4j_query(
    connector=connector,
    query=query,
    title='Treatment Groups and Animals',
    node_labels=True,
    relationship_labels=True,
    physics_enabled=True
)

# Save the HTML output to a file
with open('treatment_groups_graph.html', 'w') as f:
    f.write(graph_html)

# Display the visualization in a Jupyter notebook
from IPython.display import HTML
HTML(graph_html)
```

This visualization shows the relationships between treatment groups and animals, with nodes representing entities and edges representing relationships.

### Visualizing the Complete Experimental Design

Let's create a more complex visualization showing the complete experimental design, including studies, treatment groups, animals, and measurements.

```python
# Create a Cypher query to get the complete experimental design
query = """
MATCH (s:Study)-[:INCLUDES]->(tg:TreatmentGroup)<-[:BELONGS_TO]-(a:Animal)-[:HAS_MEASUREMENT]->(m:Measurement)
RETURN s, tg, a, m
LIMIT 200
"""

# Execute the query and visualize the results
graph_html = visualize_neo4j_query(
    connector=connector,
    query=query,
    title='Complete Experimental Design',
    node_labels=True,
    relationship_labels=True,
    physics_enabled=True,
    node_colors={
        'Study': '#4e79a7',
        'TreatmentGroup': '#f28e2c',
        'Animal': '#e15759',
        'Measurement': '#76b7b2'
    }
)

# Save the HTML output to a file
with open('experimental_design_graph.html', 'w') as f:
    f.write(graph_html)

# Display the visualization in a Jupyter notebook
from IPython.display import HTML
HTML(graph_html)
```

This visualization provides a comprehensive view of the experimental design, showing how studies, treatment groups, animals, and measurements are related.

### Creating a Custom Graph Visualization

Finally, let's create a custom graph visualization that focuses on the relationships between animals and their measurements.

```python
# Create a Cypher query to get animals and their measurements
query = """
MATCH (a:Animal)-[:HAS_MEASUREMENT]->(m:Measurement)
WHERE a.treatment_group IN ['Control', 'Drug A', 'Drug B', 'Combination']
RETURN a, m
LIMIT 300
"""

# Execute the query and get the graph data
from science_data_kit.visualization.graph_plots import get_graph_data_from_query

# Get the graph data
graph_data = get_graph_data_from_query(connector, query)

# Create a custom visualization using the graph_plots module
from science_data_kit.visualization.graph_plots import create_custom_graph_visualization

# Create the visualization
custom_graph_html = create_custom_graph_visualization(
    graph_data=graph_data,
    title='Animals and Measurements',
    node_size_property='weight',  # Size nodes based on weight property
    node_color_property='treatment_group',  # Color nodes based on treatment group
    edge_width_property='day',  # Width of edges based on day property
    layout='force',  # Use force-directed layout
    tooltip_properties=['id', 'weight', 'tumor_volume', 'day']  # Properties to show in tooltips
)

# Save the HTML output to a file
with open('animals_measurements_graph.html', 'w') as f:
    f.write(custom_graph_html)

# Display the visualization in a Jupyter notebook
from IPython.display import HTML
HTML(custom_graph_html)
```

This custom visualization provides a focused view of the relationships between animals and their measurements, with node sizes, colors, and edge widths encoding additional information.

## Conclusion (17:00-18:00)

In this tutorial, we've explored the various visualization capabilities of the Science Data Kit:

1. Static visualizations with Matplotlib for creating publication-quality figures
2. Interactive visualizations with Plotly for exploring data dynamically
3. Web-based visualizations with D3.js for creating highly customized interactive visualizations
4. Graph database visualizations with Neo4j for understanding complex relationships

These visualization tools allow researchers to gain insights from their data and communicate their findings effectively. Whether you're exploring data interactively, creating figures for publications, or visualizing complex relationships, the Science Data Kit provides the tools you need.

To learn more about data visualization with the Science Data Kit, check out the documentation and the Jupyter notebook version of this tutorial, which allows you to run the code and experiment with different visualization options.

Thank you for watching this tutorial. Happy visualizing!