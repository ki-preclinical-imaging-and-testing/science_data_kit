"""
Preclinical Challenge Workflow Diagram Generator

This script generates a diagram illustrating the preclinical challenge workflow
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

def create_preclinical_challenge_workflow_diagram():
    """
    Create a diagram illustrating the preclinical challenge workflow.
    """
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes for each step in the workflow
    nodes = [
        ("data", "Preclinical Dataset"),
        ("explore", "Exploratory Data Analysis"),
        ("design", "Experimental Design Analysis"),
        ("groups", "Animal Group Analysis"),
        ("tumor", "Tumor Growth Analysis"),
        ("survival", "Survival Analysis"),
        ("stats", "Statistical Testing"),
        ("report", "Results Reporting")
    ]
    
    for node_id, node_label in nodes:
        G.add_node(node_id, label=node_label)
    
    # Add edges to show the workflow
    edges = [
        ("data", "explore"),
        ("explore", "design"),
        ("design", "groups"),
        ("groups", "tumor"),
        ("tumor", "survival"),
        ("survival", "stats"),
        ("stats", "report"),
        # Add some additional connections
        ("explore", "tumor"),  # Exploratory analysis can lead directly to tumor growth analysis
        ("explore", "survival"),  # Exploratory analysis can lead directly to survival analysis
        ("tumor", "stats"),  # Tumor growth analysis leads to statistical testing
        ("groups", "stats")  # Animal group analysis leads to statistical testing
    ]
    
    for source, target in edges:
        G.add_edge(source, target)
    
    # Create the figure
    plt.figure(figsize=(12, 8))
    
    # Define node positions in a hierarchical layout
    pos = {
        "data": (0, 3),
        "explore": (2, 3),
        "design": (4, 3),
        "groups": (6, 3),
        "tumor": (2, 1),
        "survival": (4, 1),
        "stats": (6, 1),
        "report": (8, 2)
    }
    
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_size=2500, node_color="salmon", alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.7, edge_color="gray", 
                          connectionstyle='arc3,rad=0.1', arrowsize=20)
    
    # Add labels
    labels = {node_id: data["label"] for node_id, data in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight="bold")
    
    # Remove axis
    plt.axis("off")
    
    # Add title
    plt.title("Preclinical Challenge Workflow", fontsize=16, fontweight="bold", pad=20)
    
    # Save the figure
    output_path = os.path.join(os.path.dirname(__file__), "preclinical_challenge_workflow.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    
    print(f"Diagram saved to {output_path}")
    return output_path

if __name__ == "__main__":
    create_preclinical_challenge_workflow_diagram()