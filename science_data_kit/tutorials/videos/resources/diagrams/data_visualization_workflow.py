"""
Data Visualization Workflow Diagram Generator

This script generates a diagram illustrating the data visualization workflow
for the Science Data Kit video tutorials.
"""

import os
import sys
import matplotlib.pyplot as plt
import networkx as nx
import io
import base64

# Add parent directories to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

def create_data_visualization_workflow_diagram():
    """
    Create a diagram illustrating the data visualization workflow.
    """
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes for each step in the workflow
    nodes = [
        ("data", "Input Data"),
        ("explore", "Exploratory Analysis"),
        ("prepare", "Data Preparation"),
        ("select", "Select Visualization Type"),
        ("create", "Create Visualization"),
        ("customize", "Customize Visualization"),
        ("interpret", "Interpret Results"),
        ("share", "Share/Export Visualization")
    ]
    
    for node_id, node_label in nodes:
        G.add_node(node_id, label=node_label)
    
    # Add edges to show the workflow
    edges = [
        ("data", "explore"),
        ("explore", "prepare"),
        ("prepare", "select"),
        ("select", "create"),
        ("create", "customize"),
        ("customize", "interpret"),
        ("interpret", "share"),
        # Add some additional connections
        ("interpret", "prepare"),  # Interpretation can lead to further data preparation
        ("customize", "select"),   # Customization might require changing visualization type
        ("interpret", "select")    # Interpretation might require different visualization
    ]
    
    for source, target in edges:
        G.add_edge(source, target)
    
    # Create the figure
    plt.figure(figsize=(12, 8))
    
    # Define node positions in a circular layout
    pos = nx.circular_layout(G)
    
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_size=2500, node_color="lightblue", alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.7, edge_color="gray", 
                          connectionstyle='arc3,rad=0.1', arrowsize=20)
    
    # Add labels
    labels = {node_id: data["label"] for node_id, data in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight="bold")
    
    # Remove axis
    plt.axis("off")
    
    # Add title
    plt.title("Data Visualization Workflow", fontsize=16, fontweight="bold", pad=20)
    
    # Save the figure
    output_path = os.path.join(os.path.dirname(__file__), "data_visualization_workflow.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    
    print(f"Diagram saved to {output_path}")
    return output_path

if __name__ == "__main__":
    create_data_visualization_workflow_diagram()