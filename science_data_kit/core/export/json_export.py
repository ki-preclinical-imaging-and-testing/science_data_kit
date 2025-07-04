"""
# JSON Export Module for Science Data Kit

This module provides functionality for exporting data from Science Data Kit to JSON format.
It includes functions for converting various data structures to JSON and saving them to files.

## Features
- Convert pandas DataFrames to JSON
- Convert Neo4j query results to JSON
- Convert graph data to JSON
- Save data to JSON files

## Usage
```python
from science_data_kit.core.export.json_export import (
    dataframe_to_json,
    query_results_to_json,
    graph_to_json,
    save_to_json_file
)

# Convert a pandas DataFrame to JSON
json_data = dataframe_to_json(df)

# Convert Neo4j query results to JSON
json_data = query_results_to_json(results)

# Convert graph data to JSON
json_data = graph_to_json(nodes, relationships)

# Save data to a JSON file
save_to_json_file(data, 'data.json')
```
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Union
import logging
import os
from datetime import datetime, date

logger = logging.getLogger(__name__)

class JSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles various data types.
    """
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        return super().default(obj)

def dataframe_to_json(
    df: pd.DataFrame,
    orient: str = 'records',
    date_format: str = 'iso',
    double_precision: int = 10,
    force_ascii: bool = False,
    indent: Optional[int] = None
) -> str:
    """
    Convert a pandas DataFrame to JSON.

    Args:
        df: The pandas DataFrame to convert.
        orient: The format of the JSON string. Options include 'records', 'split', 'index', 'columns', 'values', 'table'.
        date_format: The format for dates. Options include 'epoch', 'iso'.
        double_precision: The number of decimal places to use for floating point values.
        force_ascii: Whether to force ASCII encoding.
        indent: The number of spaces to use for indentation.

    Returns:
        A JSON string representation of the DataFrame.
    """
    try:
        return df.to_json(
            orient=orient,
            date_format=date_format,
            double_precision=double_precision,
            force_ascii=force_ascii,
            indent=indent
        )
    except Exception as e:
        logger.error(f"Error converting DataFrame to JSON: {str(e)}")
        return "{}"

def query_results_to_json(
    results: List[Dict[str, Any]],
    indent: Optional[int] = None
) -> str:
    """
    Convert Neo4j query results to JSON.

    Args:
        results: List of dictionaries containing Neo4j query results.
        indent: The number of spaces to use for indentation.

    Returns:
        A JSON string representation of the query results.
    """
    try:
        return json.dumps(results, cls=JSONEncoder, indent=indent)
    except Exception as e:
        logger.error(f"Error converting query results to JSON: {str(e)}")
        return "{}"

def graph_to_json(
    nodes: List[Dict[str, Any]],
    relationships: List[Dict[str, Any]],
    indent: Optional[int] = None
) -> str:
    """
    Convert graph data to JSON.

    Args:
        nodes: List of dictionaries representing nodes.
        relationships: List of dictionaries representing relationships.
        indent: The number of spaces to use for indentation.

    Returns:
        A JSON string representation of the graph data.
    """
    try:
        graph_data = {
            "nodes": nodes,
            "relationships": relationships
        }
        return json.dumps(graph_data, cls=JSONEncoder, indent=indent)
    except Exception as e:
        logger.error(f"Error converting graph data to JSON: {str(e)}")
        return "{}"

def save_to_json_file(
    data: Any,
    file_path: str,
    indent: Optional[int] = 4,
    ensure_ascii: bool = False
) -> Tuple[bool, str]:
    """
    Save data to a JSON file.

    Args:
        data: The data to save. Can be a dictionary, list, pandas DataFrame, or any JSON-serializable object.
        file_path: The path to save the JSON file.
        indent: The number of spaces to use for indentation.
        ensure_ascii: Whether to ensure ASCII encoding.

    Returns:
        A tuple containing:
        - A boolean indicating success or failure.
        - A message describing the result.
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        # Convert pandas DataFrame to dict
        if isinstance(data, pd.DataFrame):
            data = json.loads(dataframe_to_json(data, indent=indent))

        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, cls=JSONEncoder, indent=indent, ensure_ascii=ensure_ascii)

        return True, f"Data saved to {file_path}"
    except Exception as e:
        logger.error(f"Error saving data to JSON file: {str(e)}")
        return False, f"Error saving data to JSON file: {str(e)}"

def load_from_json_file(file_path: str) -> Tuple[bool, Union[Dict[str, Any], List[Any], str]]:
    """
    Load data from a JSON file.

    Args:
        file_path: The path to the JSON file.

    Returns:
        A tuple containing:
        - A boolean indicating success or failure.
        - The loaded data or an error message.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return True, data
    except Exception as e:
        logger.error(f"Error loading data from JSON file: {str(e)}")
        return False, f"Error loading data from JSON file: {str(e)}"

def get_dataframe_from_json_file(file_path: str) -> Tuple[bool, Union[pd.DataFrame, str]]:
    """
    Load a pandas DataFrame from a JSON file.

    Args:
        file_path: The path to the JSON file.

    Returns:
        A tuple containing:
        - A boolean indicating success or failure.
        - A pandas DataFrame or an error message.
    """
    try:
        df = pd.read_json(file_path)
        return True, df
    except Exception as e:
        logger.error(f"Error loading DataFrame from JSON file: {str(e)}")
        return False, f"Error loading DataFrame from JSON file: {str(e)}"

def get_dataframe_from_json_string(json_string: str) -> Tuple[bool, Union[pd.DataFrame, str]]:
    """
    Load a pandas DataFrame from a JSON string.

    Args:
        json_string: The JSON string.

    Returns:
        A tuple containing:
        - A boolean indicating success or failure.
        - A pandas DataFrame or an error message.
    """
    try:
        df = pd.read_json(json_string)
        return True, df
    except Exception as e:
        logger.error(f"Error loading DataFrame from JSON string: {str(e)}")
        return False, f"Error loading DataFrame from JSON string: {str(e)}"

def convert_to_json_serializable(obj: Any) -> Any:
    """
    Convert an object to a JSON-serializable format.

    Args:
        obj: The object to convert.

    Returns:
        A JSON-serializable representation of the object.
    """
    try:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            return json.loads(dataframe_to_json(obj))
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        elif pd.isna(obj):
            return None
        elif hasattr(obj, '__dict__'):
            return {k: convert_to_json_serializable(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
        elif isinstance(obj, (list, tuple)):
            return [convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: convert_to_json_serializable(v) for k, v in obj.items()}
        return obj
    except Exception as e:
        logger.error(f"Error converting object to JSON-serializable format: {str(e)}")
        return None
