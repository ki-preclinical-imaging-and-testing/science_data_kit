"""
Database Operations Workflow Diagram Generator

This script generates a diagram illustrating the database operations workflow
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

def create_database_workflow_diagram():
    """
    Create a diagram illustrating the database operations workflow.
    """
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes for each step in the workflow
    nodes = [
        ("connect", "Connect to Database"),
        ("query", "Execute Query"),
        ("cache", "Query Cache"),
        ("results", "Process Results"),
        ("transform", "Transform Data"),
        ("visualize", "Visualize Data")
    ]
    
    for node_id, node_label in nodes:
        G.add_node(node_id, label=node_label)
    
    # Add edges to show the workflow
    edges = [
        ("connect", "query"),
        ("query", "cache"),
        ("cache", "results"),
        ("results", "transform"),
        ("transform", "visualize"),
        # Add some additional connections
        ("cache", "query"),  # Cache can affect future queries
        ("results", "query")  # Results can lead to new queries
    ]
    
    for source, target in edges:
        G.add_edge(source, target)
    
    # Create the figure
    plt.figure(figsize=(10, 6))
    
    # Define node positions
    pos = {
        "connect": (0, 0),
        "query": (1, 0),
        "cache": (2, 0),
        "results": (3, 0),
        "transform": (4, 0),
        "visualize": (5, 0)
    }
    
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="skyblue", alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.7, edge_color="gray", 
                          connectionstyle='arc3,rad=0.1', arrowsize=20)
    
    # Add labels
    labels = {node_id: data["label"] for node_id, data in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight="bold")
    
    # Remove axis
    plt.axis("off")
    
    # Add title
    plt.title("Database Operations Workflow", fontsize=16, fontweight="bold", pad=20)
    
    # Save the figure
    output_path = os.path.join(os.path.dirname(__file__), "database_operations_workflow.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    
    print(f"Diagram saved to {output_path}")
    return output_path

if __name__ == "__main__":
    create_database_workflow_diagram()