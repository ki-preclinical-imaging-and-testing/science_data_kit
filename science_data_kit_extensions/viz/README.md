# Science Data Kit - Visualization Extension

This extension provides enhanced visualization capabilities for the Science Data Kit. It includes advanced plotting, interactive visualizations, and specialized scientific visualization tools.

## Installation

```bash
pip install science_data_kit_viz
```

## Requirements

- Science Data Kit (core package)
- Matplotlib
- Pillow
- Plotly
- Seaborn
- Bokeh

## Features

- **Advanced Plotting**: Enhanced plotting capabilities beyond the core package
- **Interactive Visualizations**: Interactive charts and graphs for data exploration
- **Scientific Visualizations**: Specialized visualizations for scientific data
- **3D Visualizations**: Three-dimensional plots and surfaces
- **Network Visualizations**: Enhanced network and graph visualizations
- **Geospatial Visualizations**: Maps and geospatial data visualization
- **Statistical Visualizations**: Advanced statistical plots and charts
- **Custom Themes**: Customizable themes for consistent visualization styling
- **Publication-Ready Figures**: Tools for creating publication-quality figures

## Usage

```python
from science_data_kit.core.database import DatabaseManager
from science_data_kit_viz import (
    AdvancedPlotter,
    InteractivePlotter,
    NetworkVisualizer,
    GeoVisualizer,
    StatisticalVisualizer
)

# Initialize database manager
db_manager = DatabaseManager()
db_manager.connect_to_neo4j(uri="bolt://localhost:7687", username="neo4j", password="password")

# Create advanced plotter
plotter = AdvancedPlotter(theme="scientific")

# Query data from Neo4j
query = """
MATCH (e:Experiment)-[:HAS_MEASUREMENT]->(m:Measurement)
WHERE e.type = 'temperature_study'
RETURN e.id, e.condition, m.time, m.value
ORDER BY e.id, m.time
"""
results = db_manager.query(query)

# Create multi-panel figure
fig = plotter.create_multi_panel_figure(
    rows=2,
    cols=2,
    figsize=(12, 10),
    shared_x=True
)

# Plot time series data with error bands
plotter.plot_time_series_with_error_bands(
    data=results,
    x_column="m.time",
    y_column="m.value",
    group_column="e.condition",
    panel=(0, 0),
    title="Temperature Measurements",
    xlabel="Time (min)",
    ylabel="Temperature (°C)"
)

# Create box plots
plotter.plot_box_plot(
    data=results,
    x_column="e.condition",
    y_column="m.value",
    panel=(0, 1),
    title="Distribution by Condition",
    xlabel="Condition",
    ylabel="Temperature (°C)"
)

# Create violin plots
plotter.plot_violin_plot(
    data=results,
    x_column="e.condition",
    y_column="m.value",
    panel=(1, 0),
    title="Distribution by Condition (Violin)",
    xlabel="Condition",
    ylabel="Temperature (°C)"
)

# Create heatmap
plotter.plot_heatmap(
    data=results,
    x_column="m.time",
    y_column="e.id",
    value_column="m.value",
    panel=(1, 1),
    title="Heatmap of Measurements",
    xlabel="Time (min)",
    ylabel="Experiment ID",
    colormap="viridis"
)

# Adjust layout and save
plotter.adjust_layout(
    tight_layout=True,
    suptitle="Temperature Study Analysis"
)
plotter.save_figure("temperature_analysis.png", dpi=300)

# Create interactive visualization
interactive_plotter = InteractivePlotter()

# Create interactive scatter plot
scatter_plot = interactive_plotter.create_interactive_scatter(
    data=results,
    x_column="m.time",
    y_column="m.value",
    color_column="e.condition",
    size_column="m.value",
    hover_data=["e.id", "e.condition"],
    title="Interactive Temperature Measurements"
)
scatter_plot.show()

# Create network visualization
network_viz = NetworkVisualizer()

# Query network data
network_query = """
MATCH (s:Sample)-[r:RELATED_TO]->(o:Sample)
RETURN s.id, s.type, o.id, o.type, r.strength
LIMIT 100
"""
network_data = db_manager.query(network_query)

# Create network visualization
network = network_viz.create_network(
    data=network_data,
    source_column="s.id",
    target_column="o.id",
    source_attr_columns={"type": "s.type"},
    target_attr_columns={"type": "o.type"},
    edge_attr_columns={"weight": "r.strength"},
    title="Sample Relationships"
)
network.show()

# Create geospatial visualization
geo_viz = GeoVisualizer()

# Query geospatial data
geo_query = """
MATCH (l:Location)
RETURN l.id, l.name, l.latitude, l.longitude, l.value
"""
geo_data = db_manager.query(geo_query)

# Create map
map_viz = geo_viz.create_choropleth_map(
    data=geo_data,
    lat_column="l.latitude",
    lon_column="l.longitude",
    value_column="l.value",
    hover_name_column="l.name",
    title="Measurement Locations",
    colorscale="Viridis"
)
map_viz.show()
```

## Visualization Types

### Statistical Visualizations
- Box plots
- Violin plots
- Swarm plots
- Strip plots
- Bar plots with error bars
- Histograms with KDE
- Q-Q plots
- Correlation heatmaps

### Time Series Visualizations
- Line plots with confidence intervals
- Area plots
- Stacked area plots
- Seasonal decomposition plots
- Autocorrelation plots
- Rolling statistics plots

### Network Visualizations
- Force-directed graphs
- Hierarchical layouts
- Circular layouts
- Arc diagrams
- Matrix plots
- Community detection visualizations

### Geospatial Visualizations
- Choropleth maps
- Bubble maps
- Heatmaps
- Flow maps
- Cartograms
- Hexbin maps

### 3D Visualizations
- 3D scatter plots
- 3D surface plots
- 3D wireframes
- 3D bar charts
- 3D network graphs

## Customization Options

The extension provides extensive customization options:

- Color palettes and colormaps
- Marker styles and sizes
- Line styles and widths
- Font styles and sizes
- Grid styles
- Legend positioning and styling
- Axis scaling (linear, log, symlog)
- Figure sizes and DPI
- Output formats (PNG, PDF, SVG, HTML)

## License

This extension is released under the MIT License.