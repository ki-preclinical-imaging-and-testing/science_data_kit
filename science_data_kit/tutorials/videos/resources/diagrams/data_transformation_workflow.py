"""
Data Transformation Workflow Diagram Generator

This script generates a diagram illustrating the data transformation workflow
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

def create_data_transformation_workflow_diagram():
    """
    Create a diagram illustrating the data transformation workflow.
    """
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes for each step in the workflow
    nodes = [
        ("input", "Input Data"),
        ("validate", "Validate Data"),
        ("clean", "Clean Data"),
        ("transform", "Transform Data"),
        ("map", "Map to Target Schema"),
        ("validate_output", "Validate Output"),
        ("export", "Export Data")
    ]
    
    for node_id, node_label in nodes:
        G.add_node(node_id, label=node_label)
    
    # Add edges to show the workflow
    edges = [
        ("input", "validate"),
        ("validate", "clean"),
        ("clean", "transform"),
        ("transform", "map"),
        ("map", "validate_output"),
        ("validate_output", "export"),
        # Add some additional connections
        ("validate", "input"),  # Validation can require going back to input
        ("validate_output", "transform")  # Output validation can require retransformation
    ]
    
    for source, target in edges:
        G.add_edge(source, target)
    
    # Create the figure
    plt.figure(figsize=(12, 6))
    
    # Define node positions in a more complex layout
    pos = {
        "input": (0, 0),
        "validate": (1, 0),
        "clean": (2, 0),
        "transform": (3, 0),
        "map": (4, 0),
        "validate_output": (5, 0),
        "export": (6, 0)
    }
    
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="lightgreen", alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.7, edge_color="gray", 
                          connectionstyle='arc3,rad=0.1', arrowsize=20)
    
    # Add labels
    labels = {node_id: data["label"] for node_id, data in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight="bold")
    
    # Remove axis
    plt.axis("off")
    
    # Add title
    plt.title("Data Transformation Workflow", fontsize=16, fontweight="bold", pad=20)
    
    # Save the figure
    output_path = os.path.join(os.path.dirname(__file__), "data_transformation_workflow.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    
    print(f"Diagram saved to {output_path}")
    return output_path

if __name__ == "__main__":
    create_data_transformation_workflow_diagram()