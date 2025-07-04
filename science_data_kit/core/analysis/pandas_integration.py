"""
# Pandas Integration Module for Science Data Kit

This module provides integration between Science Data Kit and pandas for data analysis.
It includes functions for converting between SDK data structures and pandas DataFrames,
as well as utilities for data manipulation and analysis using pandas.

## Features
- Convert Neo4j query results to pandas DataFrames
- Convert pandas DataFrames to Neo4j-compatible format
- Data manipulation utilities using pandas
- Data analysis utilities using pandas
- Data visualization utilities using pandas

## Usage
```python
from science_data_kit.core.analysis.pandas_integration import (
    query_to_dataframe,
    dataframe_to_neo4j,
    analyze_dataframe,
    visualize_dataframe
)

# Convert Neo4j query results to pandas DataFrame
df = query_to_dataframe(results)

# Analyze the DataFrame
analysis = analyze_dataframe(df)

# Visualize the DataFrame
fig = visualize_dataframe(df)

# Convert DataFrame to Neo4j-compatible format
nodes, relationships = dataframe_to_neo4j(df)
```
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Union
import logging
from ..db.db_manager import DBManager

logger = logging.getLogger(__name__)

def query_to_dataframe(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert Neo4j query results to a pandas DataFrame.

    Args:
        results: List of dictionaries containing Neo4j query results.

    Returns:
        A pandas DataFrame containing the query results.
    """
    try:
        return pd.DataFrame(results)
    except Exception as e:
        logger.error(f"Error converting query results to DataFrame: {str(e)}")
        return pd.DataFrame()

def dataframe_to_neo4j(
    df: pd.DataFrame, 
    node_label: str = "Node", 
    id_column: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Convert a pandas DataFrame to Neo4j-compatible format.

    Args:
        df: The pandas DataFrame to convert.
        node_label: The label to use for the nodes.
        id_column: The column to use as the node ID. If None, a UUID will be generated.

    Returns:
        A tuple containing:
        - A list of dictionaries representing nodes.
        - A list of dictionaries representing relationships.
    """
    try:
        import uuid
        
        nodes = []
        relationships = []
        
        # Convert DataFrame to nodes
        for _, row in df.iterrows():
            node_id = str(row[id_column]) if id_column else str(uuid.uuid4())
            node = {
                "id": node_id,
                "labels": [node_label],
                "properties": row.to_dict()
            }
            nodes.append(node)
            
        return nodes, relationships
    except Exception as e:
        logger.error(f"Error converting DataFrame to Neo4j format: {str(e)}")
        return [], []

def analyze_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform basic analysis on a pandas DataFrame.

    Args:
        df: The pandas DataFrame to analyze.

    Returns:
        A dictionary containing analysis results.
    """
    try:
        analysis = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "summary_statistics": df.describe().to_dict(),
            "correlation_matrix": df.corr().to_dict() if df.select_dtypes(include=[np.number]).shape[1] > 1 else {}
        }
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing DataFrame: {str(e)}")
        return {}

def visualize_dataframe(
    df: pd.DataFrame, 
    plot_type: str = "bar", 
    x: Optional[str] = None, 
    y: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Create a visualization of a pandas DataFrame.

    Args:
        df: The pandas DataFrame to visualize.
        plot_type: The type of plot to create (bar, line, scatter, etc.).
        x: The column to use for the x-axis.
        y: The column to use for the y-axis.
        **kwargs: Additional arguments to pass to the plotting function.

    Returns:
        A matplotlib figure or None if an error occurs.
    """
    try:
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if plot_type == "bar":
            if x and y:
                df.plot(kind="bar", x=x, y=y, ax=ax, **kwargs)
            else:
                df.plot(kind="bar", ax=ax, **kwargs)
        elif plot_type == "line":
            if x and y:
                df.plot(kind="line", x=x, y=y, ax=ax, **kwargs)
            else:
                df.plot(kind="line", ax=ax, **kwargs)
        elif plot_type == "scatter":
            if x and y:
                df.plot(kind="scatter", x=x, y=y, ax=ax, **kwargs)
            else:
                logger.error("Scatter plot requires x and y parameters")
                return None
        elif plot_type == "hist":
            if y:
                df[y].plot(kind="hist", ax=ax, **kwargs)
            else:
                df.plot(kind="hist", ax=ax, **kwargs)
        elif plot_type == "box":
            if y:
                df[y].plot(kind="box", ax=ax, **kwargs)
            else:
                df.plot(kind="box", ax=ax, **kwargs)
        else:
            logger.error(f"Unsupported plot type: {plot_type}")
            return None
            
        plt.tight_layout()
        return fig
    except Exception as e:
        logger.error(f"Error visualizing DataFrame: {str(e)}")
        return None

def get_dataframe_from_query(
    query: str, 
    params: Optional[Dict[str, Any]] = None,
    connection_name: Optional[str] = None
) -> pd.DataFrame:
    """
    Execute a Neo4j query and return the results as a pandas DataFrame.

    Args:
        query: The Cypher query to execute.
        params: Parameters for the query.
        connection_name: The name of the Neo4j connection to use.

    Returns:
        A pandas DataFrame containing the query results.
    """
    try:
        db_manager = DBManager()
        success, results = db_manager.query(query, params, connection_name)
        
        if success:
            return query_to_dataframe(results)
        else:
            logger.error(f"Query failed: {results}")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        return pd.DataFrame()

def save_dataframe_to_csv(df: pd.DataFrame, file_path: str) -> Tuple[bool, str]:
    """
    Save a pandas DataFrame to a CSV file.

    Args:
        df: The pandas DataFrame to save.
        file_path: The path to save the CSV file.

    Returns:
        A tuple containing:
        - A boolean indicating success or failure.
        - A message describing the result.
    """
    try:
        df.to_csv(file_path, index=False)
        return True, f"DataFrame saved to {file_path}"
    except Exception as e:
        logger.error(f"Error saving DataFrame to CSV: {str(e)}")
        return False, f"Error saving DataFrame to CSV: {str(e)}"

def save_dataframe_to_excel(df: pd.DataFrame, file_path: str) -> Tuple[bool, str]:
    """
    Save a pandas DataFrame to an Excel file.

    Args:
        df: The pandas DataFrame to save.
        file_path: The path to save the Excel file.

    Returns:
        A tuple containing:
        - A boolean indicating success or failure.
        - A message describing the result.
    """
    try:
        df.to_excel(file_path, index=False)
        return True, f"DataFrame saved to {file_path}"
    except Exception as e:
        logger.error(f"Error saving DataFrame to Excel: {str(e)}")
        return False, f"Error saving DataFrame to Excel: {str(e)}"

def load_dataframe_from_csv(file_path: str) -> Tuple[bool, Union[pd.DataFrame, str]]:
    """
    Load a pandas DataFrame from a CSV file.

    Args:
        file_path: The path to the CSV file.

    Returns:
        A tuple containing:
        - A boolean indicating success or failure.
        - A pandas DataFrame or an error message.
    """
    try:
        df = pd.read_csv(file_path)
        return True, df
    except Exception as e:
        logger.error(f"Error loading DataFrame from CSV: {str(e)}")
        return False, f"Error loading DataFrame from CSV: {str(e)}"

def load_dataframe_from_excel(file_path: str) -> Tuple[bool, Union[pd.DataFrame, str]]:
    """
    Load a pandas DataFrame from an Excel file.

    Args:
        file_path: The path to the Excel file.

    Returns:
        A tuple containing:
        - A boolean indicating success or failure.
        - A pandas DataFrame or an error message.
    """
    try:
        df = pd.read_excel(file_path)
        return True, df
    except Exception as e:
        logger.error(f"Error loading DataFrame from Excel: {str(e)}")
        return False, f"Error loading DataFrame from Excel: {str(e)}"
"""