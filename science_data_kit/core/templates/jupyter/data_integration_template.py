"""
Data Integration Template

This script provides a template for integrating data from external sources into Neo4j
using the Science Data Kit. It can be used as a starting point for Jupyter notebooks.
"""

#%% md
# Data Integration Template
#
# This notebook provides a template for integrating data from external sources (NExtSEEK, FAIRDOM-Hub) into Neo4j using the Science Data Kit.

#%% md
# ## Setup
#
# First, let's import the necessary libraries and set up the connections.

#%%
# Import required libraries
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import json
from typing import Dict, List, Any

# Add the Science Data Kit to the path if needed
# Adjust the path as necessary for your environment
sdk_path = os.path.abspath('../../..')
if sdk_path not in sys.path:
    sys.path.append(sdk_path)

# Import Science Data Kit modules
from science_data_kit.core.db import Neo4jManager
from science_data_kit.core.integrations import get_provider, list_providers

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
# ## List Available Integration Providers
#
# Let's see what integration providers are available in the Science Data Kit.

#%%
# List available providers
providers = list_providers()
print("Available integration providers:")
for provider in providers:
    print(f"- {provider}")

#%% md
# ## NExtSEEK Integration
#
# Let's demonstrate how to integrate data from NExtSEEK into Neo4j.

#%%
# Initialize the NExtSEEK provider
nextsee_provider = get_provider("nextsee")(
    base_url="https://nextsee.org/api/v1",
    api_key=None  # Replace with your API key if available
)

# Authenticate with NExtSEEK
# Replace with your actual credentials
username = "your_username"
password = "your_password"

# Comment out the authentication if you don't have credentials
# success, message = nextsee_provider.authenticate(username, password)
# print(f"Authentication result: {success}, {message}")

# For demonstration purposes, let's create some sample data
sample_data = {
    "projects": [
        {
            "id": "project1",
            "name": "Sample Project 1",
            "description": "A sample project for demonstration",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z"
        },
        {
            "id": "project2",
            "name": "Sample Project 2",
            "description": "Another sample project",
            "created_at": "2023-02-01T00:00:00Z",
            "updated_at": "2023-02-02T00:00:00Z"
        }
    ],
    "experiments": [
        {
            "id": "experiment1",
            "name": "Sample Experiment 1",
            "description": "A sample experiment",
            "project_id": "project1",
            "created_at": "2023-01-03T00:00:00Z",
            "updated_at": "2023-01-04T00:00:00Z"
        },
        {
            "id": "experiment2",
            "name": "Sample Experiment 2",
            "description": "Another sample experiment",
            "project_id": "project2",
            "created_at": "2023-02-03T00:00:00Z",
            "updated_at": "2023-02-04T00:00:00Z"
        }
    ],
    "samples": [
        {
            "id": "sample1",
            "name": "Sample 1",
            "description": "A sample",
            "experiment_id": "experiment1",
            "created_at": "2023-01-05T00:00:00Z",
            "updated_at": "2023-01-06T00:00:00Z"
        },
        {
            "id": "sample2",
            "name": "Sample 2",
            "description": "Another sample",
            "experiment_id": "experiment2",
            "created_at": "2023-02-05T00:00:00Z",
            "updated_at": "2023-02-06T00:00:00Z"
        }
    ]
}

# Import the sample data into Neo4j
# Comment out if you don't want to import the sample data
success, message = nextsee_provider.import_to_neo4j(sample_data, db_manager)
print(f"Import result: {success}, {message}")

#%% md
# ## FAIRDOM-Hub Integration
#
# Let's demonstrate how to integrate data from FAIRDOM-Hub into Neo4j.

#%%
# Initialize the FAIRDOM-Hub provider
fairdom_provider = get_provider("fairdom")(
    base_url="https://fairdomhub.org/api",
    api_key=None  # Replace with your API key if available
)

# Authenticate with FAIRDOM-Hub
# Replace with your actual credentials
username = "your_username"
password = "your_password"

# Comment out the authentication if you don't have credentials
# success, message = fairdom_provider.authenticate(username, password)
# print(f"Authentication result: {success}, {message}")

# For demonstration purposes, let's create some sample data
sample_data = {
    "investigations": [
        {
            "id": "investigation1",
            "attributes": {
                "title": "Sample Investigation 1",
                "description": "A sample investigation for demonstration",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z"
            }
        },
        {
            "id": "investigation2",
            "attributes": {
                "title": "Sample Investigation 2",
                "description": "Another sample investigation",
                "created_at": "2023-02-01T00:00:00Z",
                "updated_at": "2023-02-02T00:00:00Z"
            }
        }
    ],
    "studies": [
        {
            "id": "study1",
            "attributes": {
                "title": "Sample Study 1",
                "description": "A sample study",
                "created_at": "2023-01-03T00:00:00Z",
                "updated_at": "2023-01-04T00:00:00Z"
            },
            "relationships": {
                "investigation": {
                    "data": {
                        "id": "investigation1"
                    }
                }
            }
        },
        {
            "id": "study2",
            "attributes": {
                "title": "Sample Study 2",
                "description": "Another sample study",
                "created_at": "2023-02-03T00:00:00Z",
                "updated_at": "2023-02-04T00:00:00Z"
            },
            "relationships": {
                "investigation": {
                    "data": {
                        "id": "investigation2"
                    }
                }
            }
        }
    ],
    "assays": [
        {
            "id": "assay1",
            "attributes": {
                "title": "Sample Assay 1",
                "description": "A sample assay",
                "assay_type": "experimental assay",
                "technology_type": "sequencing",
                "created_at": "2023-01-05T00:00:00Z",
                "updated_at": "2023-01-06T00:00:00Z"
            },
            "relationships": {
                "study": {
                    "data": {
                        "id": "study1"
                    }
                }
            }
        },
        {
            "id": "assay2",
            "attributes": {
                "title": "Sample Assay 2",
                "description": "Another sample assay",
                "assay_type": "experimental assay",
                "technology_type": "mass spectrometry",
                "created_at": "2023-02-05T00:00:00Z",
                "updated_at": "2023-02-06T00:00:00Z"
            },
            "relationships": {
                "study": {
                    "data": {
                        "id": "study2"
                    }
                }
            }
        }
    ],
    "data_files": [
        {
            "id": "data_file1",
            "attributes": {
                "title": "Sample Data File 1",
                "description": "A sample data file",
                "content_type": "text/csv",
                "file_size": 1024,
                "created_at": "2023-01-07T00:00:00Z",
                "updated_at": "2023-01-08T00:00:00Z"
            },
            "relationships": {
                "assay": {
                    "data": {
                        "id": "assay1"
                    }
                }
            }
        },
        {
            "id": "data_file2",
            "attributes": {
                "title": "Sample Data File 2",
                "description": "Another sample data file",
                "content_type": "application/vnd.ms-excel",
                "file_size": 2048,
                "created_at": "2023-02-07T00:00:00Z",
                "updated_at": "2023-02-08T00:00:00Z"
            },
            "relationships": {
                "assay": {
                    "data": {
                        "id": "assay2"
                    }
                }
            }
        }
    ]
}

# Import the sample data into Neo4j
# Comment out if you don't want to import the sample data
success, message = fairdom_provider.import_to_neo4j(sample_data, db_manager)
print(f"Import result: {success}, {message}")

#%% md
# ## Query Integrated Data
#
# Now, let's query the integrated data from Neo4j to see what we've imported.

#%%
# Query NExtSEEK data
query = """
MATCH (p:Project:NExtSEEK)-[:CONTAINS]->(e:Experiment:NExtSEEK)-[:CONTAINS]->(s:Sample:NExtSEEK)
RETURN p.name AS project, e.name AS experiment, s.name AS sample
"""
result = db_manager.execute_query(query)
print("NExtSEEK Data:")
if result:
    df = pd.DataFrame([dict(record) for record in result])
    print(df)
else:
    print("No NExtSEEK data found.")

#%%
# Query FAIRDOM-Hub data
query = """
MATCH (i:Investigation:FAIRDOM)-[:CONTAINS]->(s:Study:FAIRDOM)-[:CONTAINS]->(a:Assay:FAIRDOM)-[:CONTAINS]->(d:DataFile:FAIRDOM)
RETURN i.title AS investigation, s.title AS study, a.title AS assay, d.title AS data_file
"""
result = db_manager.execute_query(query)
print("FAIRDOM-Hub Data:")
if result:
    df = pd.DataFrame([dict(record) for record in result])
    print(df)
else:
    print("No FAIRDOM-Hub data found.")

#%% md
# ## Visualize Integrated Data
#
# Let's create a simple visualization of the integrated data.

#%%
# Count nodes by label
query = """
MATCH (n)
WHERE n:NExtSEEK OR n:FAIRDOM
RETURN labels(n) AS labels, count(n) AS count
"""
result = db_manager.execute_query(query)
if result:
    # Process the results to get counts by label
    label_counts = {}
    for record in result:
        labels = record["labels"]
        count = record["count"]
        for label in labels:
            if label in ["NExtSEEK", "FAIRDOM"]:
                continue
            key = f"{label} ({[l for l in labels if l in ['NExtSEEK', 'FAIRDOM']][0]})"
            label_counts[key] = count
    
    # Create a bar chart
    plt.figure(figsize=(12, 6))
    plt.bar(label_counts.keys(), label_counts.values())
    plt.title("Node Counts by Label and Source")
    plt.xlabel("Node Label (Source)")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()
else:
    print("No data found for visualization.")

#%% md
# ## Conclusion
#
# This notebook has demonstrated how to integrate data from external sources (NExtSEEK, FAIRDOM-Hub) into Neo4j using the Science Data Kit. You can use this template as a starting point for your own data integration projects.