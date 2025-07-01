"""
Visualization Utilities for Science Data Kit

This module provides utilities for visualizing data, such as creating network graphs,
charts, and other visualizations. It is designed to be used by the UI components
and other modules that need to visualize data.
"""

import pandas as pd
import networkx as nx
try:
    import matplotlib.pyplot as plt
except ImportError:
    # Define a placeholder for plt that will raise an error when used
    class PlaceholderPlt:
        def __getattr__(self, name):
            raise ImportError("matplotlib is not installed. Please install it with 'pip install matplotlib'.")
    plt = PlaceholderPlt()
import io
import base64
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import json

def create_network_graph(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    directed: bool = True
) -> nx.Graph:
    """
    Create a NetworkX graph from nodes and edges.

    Args:
        nodes: List of node dictionaries with 'id' and other attributes.
        edges: List of edge dictionaries with 'source', 'target', and other attributes.
        directed: Whether to create a directed graph.

    Returns:
        A NetworkX graph.
    """
    # Create a directed or undirected graph
    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()

    # Add nodes with attributes
    for node in nodes:
        node_id = node.pop('id')
        G.add_node(node_id, **node)

    # Add edges with attributes
    for edge in edges:
        source = edge.pop('source')
        target = edge.pop('target')
        G.add_edge(source, target, **edge)

    return G

def plot_network_graph(
    G: nx.Graph,
    figsize: Tuple[int, int] = (10, 8),
    node_size: int = 300,
    node_color: str = '#1f78b4',
    edge_color: str = '#888888',
    font_size: int = 10,
    with_labels: bool = True,
    layout: str = 'spring',
    title: Optional[str] = None,
    save_path: Optional[Union[str, Path]] = None
) -> Optional[plt.Figure]:
    """
    Plot a NetworkX graph using matplotlib.

    Args:
        G: NetworkX graph to plot.
        figsize: Figure size as (width, height) in inches.
        node_size: Size of nodes.
        node_color: Color of nodes.
        edge_color: Color of edges.
        font_size: Font size for node labels.
        with_labels: Whether to show node labels.
        layout: Layout algorithm to use ('spring', 'circular', 'random', 'shell', 'kamada_kawai').
        title: Optional title for the plot.
        save_path: Optional path to save the plot.

    Returns:
        The matplotlib Figure object if save_path is None, otherwise None.
    """
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

    # Draw the graph
    nx.draw(
        G, pos,
        ax=ax,
        with_labels=with_labels,
        node_size=node_size,
        node_color=node_color,
        edge_color=edge_color,
        font_size=font_size
    )

    # Add title if provided
    if title:
        ax.set_title(title)

    # Save the plot if a path is provided
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
        plt.close(fig)
        return None

    return fig

def fig_to_base64(fig: plt.Figure) -> str:
    """
    Convert a matplotlib figure to a base64-encoded string.

    Args:
        fig: Matplotlib figure to convert.

    Returns:
        Base64-encoded string of the figure.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return img_str

def create_html_graph(
    G: nx.Graph,
    width: str = '100%',
    height: str = '600px',
    directed: Optional[bool] = None,
    node_size: int = 10,
    node_color: str = '#1f78b4',
    edge_color: str = '#888888',
    title: Optional[str] = None
) -> str:
    """
    Create an HTML representation of a NetworkX graph using D3.js.

    Args:
        G: NetworkX graph to visualize.
        width: Width of the visualization.
        height: Height of the visualization.
        directed: Whether the graph is directed. If None, inferred from G.
        node_size: Size of nodes.
        node_color: Color of nodes.
        edge_color: Color of edges.
        title: Optional title for the visualization.

    Returns:
        HTML string containing the visualization.
    """
    # Determine if the graph is directed
    if directed is None:
        directed = isinstance(G, nx.DiGraph)

    # Convert the graph to a JSON-serializable format
    nodes = []
    for node, attrs in G.nodes(data=True):
        node_data = {'id': node}
        node_data.update(attrs)
        nodes.append(node_data)

    edges = []
    for source, target, attrs in G.edges(data=True):
        edge_data = {'source': source, 'target': target}
        edge_data.update(attrs)
        edges.append(edge_data)

    # Create the graph data
    graph_data = {
        'nodes': nodes,
        'links': edges,
        'directed': directed
    }

    # Convert to JSON
    graph_json = json.dumps(graph_data)

    # Create the HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title or 'Network Graph'}</title>
        <script src="https://d3js.org/d3.v5.min.js"></script>
        <style>
            body {{ margin: 0; padding: 0; }}
            #graph {{ width: {width}; height: {height}; }}
            .node {{ stroke: #fff; stroke-width: 1.5px; }}
            .link {{ stroke: {edge_color}; stroke-opacity: 0.6; }}
            .node text {{ pointer-events: none; font: 10px sans-serif; }}
        </style>
    </head>
    <body>
        <div id="graph"></div>
        <script>
            const graph = {graph_json};

            const width = document.getElementById('graph').clientWidth;
            const height = document.getElementById('graph').clientHeight;

            const svg = d3.select('#graph')
                .append('svg')
                .attr('width', width)
                .attr('height', height);

            const simulation = d3.forceSimulation()
                .force('link', d3.forceLink().id(d => d.id))
                .force('charge', d3.forceManyBody())
                .force('center', d3.forceCenter(width / 2, height / 2));

            const link = svg.append('g')
                .attr('class', 'links')
                .selectAll('line')
                .data(graph.links)
                .enter().append('line')
                .attr('class', 'link');

            const node = svg.append('g')
                .attr('class', 'nodes')
                .selectAll('circle')
                .data(graph.nodes)
                .enter().append('circle')
                .attr('class', 'node')
                .attr('r', {node_size})
                .attr('fill', '{node_color}')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));

            node.append('title')
                .text(d => d.id);

            simulation
                .nodes(graph.nodes)
                .on('tick', ticked);

            simulation.force('link')
                .links(graph.links);

            function ticked() {{
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);

                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);
            }}

            function dragstarted(d) {{
                if (!d3.event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}

            function dragged(d) {{
                d.fx = d3.event.x;
                d.fy = d3.event.y;
            }}

            function dragended(d) {{
                if (!d3.event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}
        </script>
    </body>
    </html>
    """

    return html

def create_sankey_diagram(
    nodes: List[Dict[str, Any]],
    links: List[Dict[str, Any]],
    width: int = 800,
    height: int = 600,
    title: Optional[str] = None
) -> str:
    """
    Create a Sankey diagram using Plotly.

    Args:
        nodes: List of node dictionaries with 'name' and optional 'color'.
        links: List of link dictionaries with 'source', 'target', and 'value'.
        width: Width of the diagram.
        height: Height of the diagram.
        title: Optional title for the diagram.

    Returns:
        HTML string containing the Sankey diagram.
    """
    # Convert nodes and links to JSON
    nodes_json = json.dumps(nodes)
    links_json = json.dumps(links)

    # Create the HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title or 'Sankey Diagram'}</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <div id="sankey" style="width: {width}px; height: {height}px;"></div>
        <script>
            const nodes = {nodes_json};
            const links = {links_json};

            const data = {{
                type: 'sankey',
                orientation: 'h',
                node: {{
                    pad: 15,
                    thickness: 20,
                    line: {{
                        color: 'black',
                        width: 0.5
                    }},
                    label: nodes.map(n => n.name),
                    color: nodes.map(n => n.color || '#1f78b4')
                }},
                link: {{
                    source: links.map(l => l.source),
                    target: links.map(l => l.target),
                    value: links.map(l => l.value),
                    color: links.map(l => l.color || 'rgba(0, 0, 0, 0.2)')
                }}
            }};

            const layout = {{
                title: '{title or "Sankey Diagram"}',
                font: {{
                    size: 10
                }},
                width: {width},
                height: {height}
            }};

            Plotly.newPlot('sankey', [data], layout);
        </script>
    </body>
    </html>
    """

    return html

def create_heatmap(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    value_column: str,
    width: int = 800,
    height: int = 600,
    colorscale: str = 'Viridis',
    title: Optional[str] = None
) -> str:
    """
    Create a heatmap using Plotly.

    Args:
        data: DataFrame containing the data.
        x_column: Column to use for the x-axis.
        y_column: Column to use for the y-axis.
        value_column: Column to use for the values.
        width: Width of the heatmap.
        height: Height of the heatmap.
        colorscale: Colorscale to use.
        title: Optional title for the heatmap.

    Returns:
        HTML string containing the heatmap.
    """
    # Pivot the data
    pivot_data = data.pivot(index=y_column, columns=x_column, values=value_column)

    # Convert to JSON
    z_values = pivot_data.values.tolist()
    x_values = pivot_data.columns.tolist()
    y_values = pivot_data.index.tolist()

    # Create the HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title or 'Heatmap'}</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <div id="heatmap" style="width: {width}px; height: {height}px;"></div>
        <script>
            const data = [{{
                z: {json.dumps(z_values)},
                x: {json.dumps(x_values)},
                y: {json.dumps(y_values)},
                type: 'heatmap',
                colorscale: '{colorscale}'
            }}];

            const layout = {{
                title: '{title or "Heatmap"}',
                width: {width},
                height: {height},
                xaxis: {{
                    title: '{x_column}'
                }},
                yaxis: {{
                    title: '{y_column}'
                }}
            }};

            Plotly.newPlot('heatmap', data, layout);
        </script>
    </body>
    </html>
    """

    return html

def dataframe_to_network(
    df: pd.DataFrame,
    source_column: str,
    target_column: str,
    edge_attr_columns: Optional[List[str]] = None,
    node_attr_columns: Optional[Dict[str, str]] = None,
    directed: bool = True
) -> nx.Graph:
    """
    Convert a DataFrame to a NetworkX graph.

    Args:
        df: DataFrame containing the data.
        source_column: Column to use as the source node.
        target_column: Column to use as the target node.
        edge_attr_columns: Optional list of columns to use as edge attributes.
        node_attr_columns: Optional dictionary mapping node attribute names to column names.
        directed: Whether to create a directed graph.

    Returns:
        A NetworkX graph.
    """
    # Create a directed or undirected graph
    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()

    # Add edges with attributes
    for _, row in df.iterrows():
        source = row[source_column]
        target = row[target_column]

        # Add edge attributes if specified
        edge_attrs = {}
        if edge_attr_columns:
            for col in edge_attr_columns:
                if col in row:
                    edge_attrs[col] = row[col]

        G.add_edge(source, target, **edge_attrs)

    # Add node attributes if specified
    if node_attr_columns:
        for node in G.nodes():
            # Find rows where this node appears as source or target
            source_rows = df[df[source_column] == node]
            target_rows = df[df[target_column] == node]

            # Use the first row where this node appears
            if not source_rows.empty:
                row = source_rows.iloc[0]
            elif not target_rows.empty:
                row = target_rows.iloc[0]
            else:
                continue

            # Add node attributes
            for attr_name, col_name in node_attr_columns.items():
                if col_name in row:
                    G.nodes[node][attr_name] = row[col_name]

    return G
