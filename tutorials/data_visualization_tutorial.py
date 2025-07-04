"""
Data Visualization Tutorial for Science Data Kit

This tutorial demonstrates how to use the visualization capabilities of the Science Data Kit,
including matplotlib, plotly, and D3.js integration.
"""

import os
import sys
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# Add the project root to the Python path to allow importing from science_data_kit
# when the package is not installed
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import visualization modules
from science_data_kit.core.analysis.matplotlib_integration import (
    create_line_plot, create_scatter_plot, create_bar_plot, create_histogram,
    create_heatmap, create_box_plot, create_violin_plot, create_pie_chart
)
from science_data_kit.core.analysis.plotly_integration import (
    create_interactive_line_plot, create_interactive_scatter_plot,
    create_interactive_bar_plot, create_interactive_histogram,
    create_interactive_heatmap, create_interactive_box_plot,
    create_interactive_3d_scatter, create_interactive_surface_plot
)
from science_data_kit.core.utils.d3js_integration import (
    create_force_directed_graph, create_tree_visualization, create_treemap_visualization
)


def matplotlib_examples():
    """
    Examples of using matplotlib integration.
    """
    print("\n=== Matplotlib Integration Examples ===\n")
    
    # Create sample data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    # Example 1: Line plot
    print("Creating line plot...")
    fig, ax = create_line_plot(
        x=x,
        y=[y1, y2],
        labels=['sin(x)', 'cos(x)'],
        title='Sine and Cosine Functions',
        xlabel='x',
        ylabel='y',
        grid=True,
        figsize=(10, 6)
    )
    plt.savefig('line_plot_example.png')
    plt.close(fig)
    print("Line plot saved as 'line_plot_example.png'")
    
    # Example 2: Scatter plot
    print("\nCreating scatter plot...")
    np.random.seed(42)
    x_scatter = np.random.rand(50)
    y_scatter = np.random.rand(50)
    colors = np.random.rand(50)
    sizes = 1000 * np.random.rand(50)
    
    fig, ax = create_scatter_plot(
        x=x_scatter,
        y=y_scatter,
        colors=colors,
        sizes=sizes,
        title='Random Scatter Plot',
        xlabel='X',
        ylabel='Y',
        colorbar_label='Color Value',
        alpha=0.7,
        figsize=(10, 6)
    )
    plt.savefig('scatter_plot_example.png')
    plt.close(fig)
    print("Scatter plot saved as 'scatter_plot_example.png'")
    
    # Example 3: Bar plot
    print("\nCreating bar plot...")
    categories = ['Category A', 'Category B', 'Category C', 'Category D', 'Category E']
    values = [25, 40, 30, 55, 15]
    
    fig, ax = create_bar_plot(
        categories=categories,
        values=values,
        title='Sample Bar Plot',
        xlabel='Categories',
        ylabel='Values',
        color='skyblue',
        edge_color='navy',
        figsize=(10, 6)
    )
    plt.savefig('bar_plot_example.png')
    plt.close(fig)
    print("Bar plot saved as 'bar_plot_example.png'")
    
    # Example 4: Histogram
    print("\nCreating histogram...")
    data = np.random.normal(0, 1, 1000)
    
    fig, ax = create_histogram(
        data=data,
        bins=30,
        title='Normal Distribution Histogram',
        xlabel='Value',
        ylabel='Frequency',
        color='lightgreen',
        edge_color='darkgreen',
        figsize=(10, 6)
    )
    plt.savefig('histogram_example.png')
    plt.close(fig)
    print("Histogram saved as 'histogram_example.png'")
    
    # Example 5: Heatmap
    print("\nCreating heatmap...")
    data_2d = np.random.rand(10, 12)
    
    fig, ax = create_heatmap(
        data=data_2d,
        title='Sample Heatmap',
        xlabel='X Axis',
        ylabel='Y Axis',
        colorbar_label='Value',
        cmap='viridis',
        figsize=(12, 8)
    )
    plt.savefig('heatmap_example.png')
    plt.close(fig)
    print("Heatmap saved as 'heatmap_example.png'")
    
    print("\nMatplotlib examples completed. Check the output files for results.")


def plotly_examples():
    """
    Examples of using plotly integration.
    """
    print("\n=== Plotly Integration Examples ===\n")
    
    # Create sample data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    # Example 1: Interactive line plot
    print("Creating interactive line plot...")
    fig = create_interactive_line_plot(
        x=x,
        y=[y1, y2],
        labels=['sin(x)', 'cos(x)'],
        title='Interactive Sine and Cosine Functions',
        xlabel='x',
        ylabel='y',
        mode='lines+markers'
    )
    fig.write_html('interactive_line_plot_example.html')
    print("Interactive line plot saved as 'interactive_line_plot_example.html'")
    
    # Example 2: Interactive scatter plot
    print("\nCreating interactive scatter plot...")
    np.random.seed(42)
    df = pd.DataFrame({
        'x': np.random.rand(100),
        'y': np.random.rand(100),
        'size': np.random.rand(100) * 30,
        'color': np.random.rand(100),
        'category': np.random.choice(['A', 'B', 'C', 'D'], 100)
    })
    
    fig = create_interactive_scatter_plot(
        df=df,
        x='x',
        y='y',
        color='color',
        size='size',
        hover_data=['category'],
        title='Interactive Scatter Plot',
        xlabel='X Value',
        ylabel='Y Value',
        color_scale='Viridis'
    )
    fig.write_html('interactive_scatter_plot_example.html')
    print("Interactive scatter plot saved as 'interactive_scatter_plot_example.html'")
    
    # Example 3: Interactive bar plot
    print("\nCreating interactive bar plot...")
    categories = ['Category A', 'Category B', 'Category C', 'Category D', 'Category E']
    values = [25, 40, 30, 55, 15]
    
    fig = create_interactive_bar_plot(
        categories=categories,
        values=values,
        title='Interactive Bar Plot',
        xlabel='Categories',
        ylabel='Values',
        color='category',
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig.write_html('interactive_bar_plot_example.html')
    print("Interactive bar plot saved as 'interactive_bar_plot_example.html'")
    
    # Example 4: Interactive 3D scatter plot
    print("\nCreating interactive 3D scatter plot...")
    np.random.seed(42)
    df_3d = pd.DataFrame({
        'x': np.random.rand(100),
        'y': np.random.rand(100),
        'z': np.random.rand(100),
        'size': np.random.rand(100) * 20,
        'color': np.random.rand(100),
        'category': np.random.choice(['A', 'B', 'C', 'D'], 100)
    })
    
    fig = create_interactive_3d_scatter(
        df=df_3d,
        x='x',
        y='y',
        z='z',
        color='color',
        size='size',
        hover_data=['category'],
        title='Interactive 3D Scatter Plot',
        xlabel='X Value',
        ylabel='Y Value',
        zlabel='Z Value',
        color_scale='Viridis'
    )
    fig.write_html('interactive_3d_scatter_example.html')
    print("Interactive 3D scatter plot saved as 'interactive_3d_scatter_example.html'")
    
    # Example 5: Interactive surface plot
    print("\nCreating interactive surface plot...")
    x = np.outer(np.linspace(-2, 2, 30), np.ones(30))
    y = x.copy().T
    z = np.cos(x ** 2 + y ** 2)
    
    fig = create_interactive_surface_plot(
        x=x,
        y=y,
        z=z,
        title='Interactive Surface Plot',
        xlabel='X',
        ylabel='Y',
        zlabel='Z',
        color_scale='Viridis'
    )
    fig.write_html('interactive_surface_plot_example.html')
    print("Interactive surface plot saved as 'interactive_surface_plot_example.html'")
    
    print("\nPlotly examples completed. Check the output HTML files for results.")


def d3js_examples():
    """
    Examples of using D3.js integration.
    """
    print("\n=== D3.js Integration Examples ===\n")
    
    # Example 1: Force-directed graph
    print("Creating force-directed graph visualization...")
    G = nx.random_geometric_graph(30, 0.3)
    
    # Add some attributes to nodes and edges
    for i, (node, data) in enumerate(G.nodes(data=True)):
        data['name'] = f"Node {i}"
        data['size'] = np.random.randint(5, 15)
        data['group'] = np.random.randint(1, 5)
    
    for u, v, data in G.edges(data=True):
        data['weight'] = np.random.rand()
    
    # Create a force-directed graph visualization
    html = create_force_directed_graph(
        G=G,
        title='Force-Directed Graph Example',
        node_size=lambda d: d.get('size', 10),
        node_color=lambda d: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'][d.get('group', 0) % 5],
        edge_width=lambda d: 1 + 3 * d.get('weight', 0),
        node_label=lambda d: d.get('name', ''),
        charge_strength=-100,
        link_distance=100,
        collision_radius=15,
        save_path='force_directed_graph_example.html'
    )
    print("Force-directed graph saved as 'force_directed_graph_example.html'")
    
    # Example 2: Tree visualization
    print("\nCreating tree visualization...")
    tree_data = {
        "name": "Root",
        "children": [
            {
                "name": "Branch A",
                "children": [
                    {"name": "Leaf A1", "value": 10},
                    {"name": "Leaf A2", "value": 15}
                ]
            },
            {
                "name": "Branch B",
                "children": [
                    {"name": "Leaf B1", "value": 20},
                    {
                        "name": "Sub-branch B2",
                        "children": [
                            {"name": "Leaf B2a", "value": 5},
                            {"name": "Leaf B2b", "value": 8}
                        ]
                    }
                ]
            }
        ]
    }
    
    html = create_tree_visualization(
        data=tree_data,
        title='Tree Visualization Example',
        orientation='horizontal',
        node_size=8,
        node_color=lambda d: '#1f77b4' if 'children' in d else '#2ca02c',
        link_color='#999',
        node_label=lambda d: f"{d['name']} ({d.get('value', '')})" if 'value' in d else d['name'],
        collapsible=True,
        save_path='tree_visualization_example.html'
    )
    print("Tree visualization saved as 'tree_visualization_example.html'")
    
    # Example 3: Treemap visualization
    print("\nCreating treemap visualization...")
    treemap_data = {
        "name": "Root",
        "children": [
            {
                "name": "Category A",
                "children": [
                    {"name": "Item A1", "value": 100},
                    {"name": "Item A2", "value": 150},
                    {"name": "Item A3", "value": 75}
                ]
            },
            {
                "name": "Category B",
                "children": [
                    {"name": "Item B1", "value": 200},
                    {"name": "Item B2", "value": 125},
                    {"name": "Item B3", "value": 175}
                ]
            },
            {
                "name": "Category C",
                "children": [
                    {"name": "Item C1", "value": 50},
                    {"name": "Item C2", "value": 225},
                    {"name": "Item C3", "value": 125}
                ]
            }
        ]
    }
    
    html = create_treemap_visualization(
        data=treemap_data,
        title='Treemap Visualization Example',
        color_scheme='schemeCategory10',
        padding=2,
        value_key='value',
        tooltip=True,
        zoom=True,
        save_path='treemap_visualization_example.html'
    )
    print("Treemap visualization saved as 'treemap_visualization_example.html'")
    
    print("\nD3.js examples completed. Check the output HTML files for results.")


def neo4j_visualization_examples():
    """
    Examples of visualizing Neo4j data.
    
    Note: This requires an active Neo4j connection.
    """
    print("\n=== Neo4j Visualization Examples ===\n")
    
    try:
        from science_data_kit.core.db.db_manager import db_manager
        
        # Check if connected to Neo4j
        if not db_manager.is_connected():
            print("Not connected to Neo4j. Skipping Neo4j visualization examples.")
            return
        
        print("Connected to Neo4j. Running visualization examples...")
        
        # Example 1: Visualize a graph from Neo4j
        print("\nCreating graph visualization from Neo4j data...")
        
        # Run a Cypher query to get a subgraph
        query = """
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT 50
        """
        
        result = db_manager.query(query)
        
        # Convert the result to a NetworkX graph
        G = nx.DiGraph()
        
        # Process nodes
        nodes = set()
        for record in result:
            for node_key in ['n', 'm']:
                if node_key in record and record[node_key] is not None:
                    node = record[node_key]
                    node_id = node.id
                    
                    if node_id not in nodes:
                        nodes.add(node_id)
                        
                        # Add node with properties
                        props = dict(node.items())
                        props['labels'] = list(node.labels)
                        G.add_node(node_id, **props)
            
            # Process relationship
            if 'r' in record and record['r'] is not None:
                rel = record['r']
                start_node = record['n'].id
                end_node = record['m'].id
                
                # Add edge with properties
                props = dict(rel.items())
                props['type'] = rel.type
                G.add_edge(start_node, end_node, **props)
        
        # Create a force-directed graph visualization
        if G.number_of_nodes() > 0:
            html = create_force_directed_graph(
                G=G,
                title='Neo4j Graph Visualization',
                node_size=lambda d: 8 + len(d.get('labels', [])) * 2,
                node_color=lambda d: {
                    'Person': '#1f77b4',
                    'Movie': '#ff7f0e',
                    'Book': '#2ca02c',
                    'Organization': '#d62728'
                }.get(d.get('labels', [''])[0] if d.get('labels', []) else '', '#9467bd'),
                node_label=lambda d: d.get('name', str(d.get('id', ''))),
                edge_width=lambda d: 1 + d.get('weight', 0) * 2 if 'weight' in d else 1.5,
                charge_strength=-120,
                link_distance=150,
                collision_radius=20,
                save_path='neo4j_graph_example.html'
            )
            print("Neo4j graph visualization saved as 'neo4j_graph_example.html'")
        else:
            print("No data returned from Neo4j query. Skipping graph visualization.")
        
    except ImportError:
        print("Could not import Neo4j manager. Skipping Neo4j visualization examples.")
    except Exception as e:
        print(f"Error in Neo4j visualization examples: {str(e)}")


def main():
    """
    Main function to run all examples.
    """
    print("=== Science Data Kit - Data Visualization Tutorial ===")
    print("\nThis tutorial demonstrates how to use the visualization capabilities of the Science Data Kit.")
    
    # Run matplotlib examples
    matplotlib_examples()
    
    # Run plotly examples
    plotly_examples()
    
    # Run D3.js examples
    d3js_examples()
    
    # Run Neo4j visualization examples
    neo4j_visualization_examples()
    
    print("\n=== Tutorial Completed ===")
    print("\nCheck the output files for visualization results.")
    print("For more information, refer to the documentation for each visualization module:")
    print("- science_data_kit.core.analysis.matplotlib_integration")
    print("- science_data_kit.core.analysis.plotly_integration")
    print("- science_data_kit.core.utils.d3js_integration")


if __name__ == "__main__":
    main()