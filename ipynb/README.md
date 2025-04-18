# Science Data Kit - Jupyter Notebooks

This directory contains Jupyter notebooks for tutorials, examples, and demonstrations of the Science Data Kit.

## Overview

The Jupyter notebooks in this directory provide interactive examples and tutorials for using the Science Data Kit programmatically. These notebooks complement the Streamlit web application by showing how to use the toolkit's functionality directly in Python.

## Tutorials

### Entity Resolution

- [**Tutorial_ResolveEntities.ipynb**](Tutorial_ResolveEntities.ipynb) - Learn how to resolve and identify entities in your data.

### Data Enrichment

- [**Tutorial_Enrich_1.ipynb**](Tutorial_Enrich_1.ipynb) - Basic data enrichment techniques.
- [**Tutorial_Enrich_2.ipynb**](Tutorial_Enrich_2.ipynb) - Advanced data enrichment techniques.

## Examples

- [**Example_Enrich_2.ipynb**](Example_Enrich_2.ipynb) - Example of enriching data with additional information.
- [**Example_RandomFiles.ipynb**](Example_RandomFiles.ipynb) - Example of working with random file collections.
- [**LauraM_USGI_uCT_Entities-Copy1.ipynb**](LauraM_USGI_uCT_Entities-Copy1.ipynb) - Example of working with medical imaging entities.

## Using the Notebooks

### Prerequisites

- Python 3.10+
- Jupyter Lab or Jupyter Notebook
- Science Data Kit dependencies installed

### Running the Notebooks

1. Start Jupyter Lab from the repository root:
   ```bash
   jupyter lab
   ```

2. Navigate to the `ipynb/` directory and open the desired notebook.

3. Run the cells in sequence to follow the tutorial or example.

### Integration with the Web Application

These notebooks can be used in conjunction with the Streamlit web application. You can:

1. Use the web application to scan and organize your data
2. Export the data to a format usable in the notebooks
3. Perform advanced analysis or custom operations in the notebooks
4. Import the results back into the web application if needed

## Creating Your Own Notebooks

Feel free to create your own notebooks based on these examples. You can:

1. Copy an existing notebook as a starting point
2. Import the necessary modules from the Science Data Kit
3. Customize the code to fit your specific use case

## Database Integration

Some notebooks may require a connection to a Neo4j database. You can:

1. Use the `utils.database` module to connect to your Neo4j instance
2. Load and save graph data using the provided functions
3. Visualize the graph structure using built-in visualization tools

The `neo4j_db.pickle` file in this directory contains a serialized Neo4j database that can be used for testing and examples.