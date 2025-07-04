"""
Neo4j Basic Analysis Template

This script provides a template for connecting to Neo4j and performing basic graph analysis
using the Science Data Kit. It can be used as a starting point for Jupyter notebooks.
"""

#%% md
# Neo4j Basic Analysis Template
#
# This notebook provides a template for connecting to Neo4j and performing basic graph analysis using the Science Data Kit.

#%% md
# ## Setup
#
# First, let's import the necessary libraries and set up the connection to Neo4j.

#%%
# Import required libraries
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from py2neo import Graph, Node, Relationship

# Add the Science Data Kit to the path if needed
# Adjust the path as necessary for your environment
sdk_path = os.path.abspath('../../..')
if sdk_path not in sys.path:
    sys.path.append(sdk_path)

# Import Science Data Kit modules
from science_data_kit.core.db import Neo4jManager
from science_data_kit.core.models import BaseEntity

#%% md
# ## Connect to Neo4j
#
# Now, let's connect to the Neo4j database. You can adjust the connection parameters as needed.

#%%
# Neo4j connection parameters
neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "password"
neo4j_database = "neo4j"

# Connect to Neo4j using the Neo4jManager
db_manager = Neo4jManager(
    uri=neo4j_uri,
    user=neo4j_user,
    password=neo4j_password,
    database=neo4j_database
)

# Test the connection
try:
    result = db_manager.execute_query("MATCH (n) RETURN count(n) AS node_count")
    node_count = result[0]["node_count"]
    print(f"Successfully connected to Neo4j. Database contains {node_count} nodes.")
except Exception as e:
    print(f"Error connecting to Neo4j: {e}")

#%% md
# ## Basic Queries
#
# Let's run some basic queries to explore the data in the Neo4j database.

#%%
# Get all node labels in the database
query = """
CALL db.labels() YIELD label
RETURN label
ORDER BY label
"""
result = db_manager.execute_query(query)
labels = [record["label"] for record in result]
print("Node labels in the database:")
for label in labels:
    print(f"- {label}")

#%%
# Get all relationship types in the database
query = """
CALL db.relationshipTypes() YIELD relationshipType
RETURN relationshipType
ORDER BY relationshipType
"""
result = db_manager.execute_query(query)
rel_types = [record["relationshipType"] for record in result]
print("Relationship types in the database:")
for rel_type in rel_types:
    print(f"- {rel_type}")

#%% md
# ## Data Analysis
#
# Now, let's perform some basic data analysis on the graph data.

#%%
# Choose a node label to analyze (replace 'Person' with an actual label from your database)
node_label = "Person"  # Change this to a label that exists in your database

# Count nodes by label
query = f"""
MATCH (n:{node_label})
RETURN count(n) AS count
"""
result = db_manager.execute_query(query)
count = result[0]["count"]
print(f"Number of {node_label} nodes: {count}")

#%%
# Get properties for the selected node label
query = f"""
MATCH (n:{node_label})
RETURN n LIMIT 1
"""
result = db_manager.execute_query(query)
if result:
    node = result[0]["n"]
    properties = list(node.keys())
    print(f"Properties for {node_label} nodes:")
    for prop in properties:
        print(f"- {prop}")
else:
    print(f"No {node_label} nodes found in the database.")

#%% md
# ## Visualization
#
# Let's visualize some of the graph data using NetworkX and Matplotlib.

#%%
# Extract a small subgraph for visualization
# Adjust the query to match your data model
query = f"""
MATCH (n:{node_label})-[r]-(m)
RETURN n, r, m
LIMIT 20
"""
result = db_manager.execute_query(query)

# Create a NetworkX graph
G = nx.Graph()

# Add nodes and edges from the query result
for record in result:
    source_node = record["n"]
    target_node = record["m"]
    relationship = record["r"]
    
    # Add nodes with properties
    source_id = source_node.get("id", str(source_node.identity))
    target_id = target_node.get("id", str(target_node.identity))
    
    G.add_node(source_id, label=list(source_node.labels)[0], **dict(source_node))
    G.add_node(target_id, label=list(target_node.labels)[0], **dict(target_node))
    
    # Add edge with relationship type
    G.add_edge(source_id, target_id, type=type(relationship).__name__, **dict(relationship))

# Visualize the graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, seed=42)  # Position nodes using a spring layout

# Draw nodes with different colors based on labels
node_labels = nx.get_node_attributes(G, 'label')
unique_labels = set(node_labels.values())
colors = plt.cm.tab10(range(len(unique_labels)))
color_map = dict(zip(unique_labels, colors))

for label, color in color_map.items():
    nodes = [node for node, node_label in node_labels.items() if node_label == label]
    nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=[color], label=label)

# Draw edges
nx.draw_networkx_edges(G, pos)

# Draw node labels
node_labels = {node: G.nodes[node].get('name', str(node)) for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)

plt.title(f"Graph Visualization of {node_label} Nodes and Their Relationships")
plt.legend()
plt.axis('off')
plt.tight_layout()
plt.show()

#%% md
# ## Advanced Analysis
#
# Now, let's perform some more advanced analysis on the graph data.

#%%
# Calculate basic graph metrics
print("Graph Metrics:")
print(f"Number of nodes: {G.number_of_nodes()}")
print(f"Number of edges: {G.number_of_edges()}")
print(f"Average degree: {sum(dict(G.degree()).values()) / G.number_of_nodes():.2f}")

# Calculate connected components
connected_components = list(nx.connected_components(G))
print(f"Number of connected components: {len(connected_components)}")
print(f"Size of largest component: {len(max(connected_components, key=len))}")

# Calculate degree distribution
degrees = [d for n, d in G.degree()]
plt.figure(figsize=(10, 6))
plt.hist(degrees, bins=range(max(degrees) + 2), alpha=0.7)
plt.title('Degree Distribution')
plt.xlabel('Degree')
plt.ylabel('Frequency')
plt.grid(True, alpha=0.3)
plt.show()

#%% md
# ## Working with Science Data Kit Entities
#
# Let's demonstrate how to work with Science Data Kit entities.

#%%
# Define a simple entity class
class Person(BaseEntity):
    def __init__(self, name, age=None, email=None):
        super().__init__()
        self.name = name
        self.age = age
        self.email = email
        
    @classmethod
    def get_schema(cls):
        return {
            "name": {"type": "string", "required": True},
            "age": {"type": "integer", "required": False},
            "email": {"type": "string", "required": False}
        }
    
    @classmethod
    def get_labels(cls):
        return ["Person"]

# Create a new person entity
person = Person(name="John Doe", age=30, email="john.doe@example.com")

# Validate the entity
is_valid, errors = person.validate()
print(f"Is valid: {is_valid}")
if not is_valid:
    print(f"Validation errors: {errors}")

# Save the entity to Neo4j
try:
    person.save(db_manager)
    print(f"Saved person with ID: {person.id}")
except Exception as e:
    print(f"Error saving person: {e}")

# Retrieve the entity from Neo4j
try:
    retrieved_person = Person.get_by_id(db_manager, person.id)
    print(f"Retrieved person: {retrieved_person.name}, {retrieved_person.age}, {retrieved_person.email}")
except Exception as e:
    print(f"Error retrieving person: {e}")

#%% md
# ## Conclusion
#
# This notebook has demonstrated how to connect to Neo4j using the Science Data Kit, perform basic and advanced graph analysis, and work with SDK entities. You can use this template as a starting point for your own graph analysis projects.