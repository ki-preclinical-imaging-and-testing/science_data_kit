# graph_utils.py - Neo4j Graph Utilities

This module provides utilities for working with Neo4j graphs. It includes functions for executing queries, converting results to different formats, and working with ontology terms and relationships.

## Classes

### Neo4jConnection

A robust Neo4j driver for connecting and executing queries with improved error handling and extended functionality.

This class provides methods for:
- Managing Neo4j connections
- Executing queries and processing results
- Working with DataFrames
- Working with ontology terms and relationships

**Note:** This class is provided for backward compatibility. For new code, use the Neo4jManager class instead.

#### Constructor

```python
def __init__(uri: str, user: str, password: str, database: str = "neo4j")
```

**Parameters:**
- `uri` (str): The URI of the Neo4j server.
- `user` (str): The username for authentication.
- `password` (str): The password for authentication.
- `database` (str, optional): The name of the database to connect to. Defaults to "neo4j".

#### Methods

##### _connect

```python
def _connect(self) -> None
```

Establishes a connection to the Neo4j database.

**Raises:**
- `ConnectionError`: If the connection fails.

##### close

```python
def close(self) -> None
```

Closes the Neo4j driver connection.

##### execute_query

```python
def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]
```

Executes a Cypher query and returns the results.

**Parameters:**
- `query` (str): The Cypher query to execute.
- `parameters` (Dict[str, Any], optional): Optional dictionary of parameters to include in the query.

**Returns:**
- List of dictionaries containing the query results.

**Raises:**
- `ConnectionError`: If there is no active connection.
- `RuntimeError`: If the query execution fails.

##### query_to_dataframe

```python
def query_to_dataframe(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame
```

Executes a Cypher query and returns the results as a Pandas DataFrame.

**Parameters:**
- `query` (str): The Cypher query to execute.
- `parameters` (Dict[str, Any], optional): Optional dictionary of parameters.

**Returns:**
- A Pandas DataFrame containing the query results.

##### query_to_dict

```python
def query_to_dict(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]
```

Executes a Cypher query and returns the results as a list of dictionaries.

**Parameters:**
- `query` (str): The Cypher query to execute.
- `parameters` (Dict[str, Any], optional): Optional dictionary of parameters.

**Returns:**
- A list of dictionaries representing the query results.

##### query_to_value

```python
def query_to_value(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Any
```

Executes a Cypher query and returns a single value or a set of values.

**Parameters:**
- `query` (str): The Cypher query to execute.
- `parameters` (Dict[str, Any], optional): Optional dictionary of parameters.

**Returns:**
- A single value if one result is returned, or a list of values if multiple rows are returned.

##### push_dataframe

```python
def push_dataframe(self, df: pd.DataFrame, label_col: str, property_cols: List[str], match_cols: List[str]) -> None
```

Pushes a DataFrame into Neo4j, using specified columns for labels, properties, and match criteria.

**Parameters:**
- `df` (pd.DataFrame): The Pandas DataFrame containing data to push.
- `label_col` (str): The column containing labels for nodes.
- `property_cols` (List[str]): The columns to be used as properties.
- `match_cols` (List[str]): The columns to be used for matching existing nodes.

**Raises:**
- `ValueError`: If the label column is not found or no match columns are provided.

##### push_and_link_dataframe

```python
def push_and_link_dataframe(
    self, 
    df: pd.DataFrame, 
    label_col: str, 
    property_cols: List[str], 
    match_cols: List[str], 
    node_match_label: str, 
    node_match_properties: List[str], 
    node_match_relationship_type: str
) -> None
```

Pushes a DataFrame into Neo4j and links nodes based on match criteria.

**Parameters:**
- `df` (pd.DataFrame): The Pandas DataFrame containing data to push.
- `label_col` (str): The column containing labels for nodes.
- `property_cols` (List[str]): The columns to be used as properties.
- `match_cols` (List[str]): The columns to be used for matching existing nodes.
- `node_match_label` (str): The label of the nodes to match against.
- `node_match_properties` (List[str]): The properties to use for matching target nodes.
- `node_match_relationship_type` (str): The type of relationship to create.

**Raises:**
- `ValueError`: If the label column is not found or no match columns are provided.

##### test_connection

```python
def test_connection(self, quiet: bool = False) -> bool
```

Tests the Neo4j connection by running a simple query.

**Parameters:**
- `quiet` (bool, optional): If True, suppresses success message output. Defaults to False.

**Returns:**
- True if the connection is successful, raises an exception otherwise.

**Raises:**
- `ConnectionError`: If the connection fails.

##### summarize_ontology_terms_for_labels

```python
def summarize_ontology_terms_for_labels(self, label: Optional[str] = None) -> Dict[str, Dict[str, Any]]
```

Summarizes available ontology terms used as properties for node labels in Neo4j.

This function queries the Neo4j database to find properties that contain ontology terms (identified by having both a value and a URI) and summarizes them by label and property name.

**Parameters:**
- `label` (str, optional): Optional label to filter the summary. If None, summarizes terms for all labels.

**Returns:**
- A dictionary with label names as keys and dictionaries of property summaries as values.

##### load_ontology_relationships

```python
def load_ontology_relationships(
    self, 
    ontology_annotations: List[Any], 
    create_source_nodes: bool = True,
    relationship_type: str = "HAS_TERM"
) -> int
```

Loads ontology terms and their relationships into Neo4j.

This function creates nodes for ontology terms and optionally for their sources, and establishes relationships between them.

**Parameters:**
- `ontology_annotations` (List[Any]): List of OntologyAnnotation objects to load.
- `create_source_nodes` (bool, optional): Whether to create nodes for ontology sources. Defaults to True.
- `relationship_type` (str, optional): The type of relationship to create between source and term nodes. Defaults to "HAS_TERM".

**Returns:**
- Number of relationships created.

## Functions

### create_connection_from_manager

```python
def create_connection_from_manager(manager) -> Neo4jConnection
```

Creates a Neo4jConnection instance from a Neo4jManager instance.

This function is provided for backward compatibility with code that expects a Neo4jConnection.

**Parameters:**
- `manager`: A Neo4jManager instance.

**Returns:**
- A Neo4jConnection instance with the same connection details.

## Examples

### Basic Usage

```python
# Create a connection to Neo4j
connection = Neo4jConnection(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="neo4j"
)

# Execute a query
results = connection.execute_query("MATCH (n) RETURN n LIMIT 10")

# Convert results to a DataFrame
df = connection.query_to_dataframe("MATCH (n) RETURN n.name, n.age LIMIT 10")

# Close the connection when done
connection.close()
```

### Working with DataFrames

```python
import pandas as pd

# Create a DataFrame
data = {
    "label": ["Person", "Person", "Movie"],
    "name": ["Alice", "Bob", "The Matrix"],
    "age": [30, 25, None],
    "year": [None, None, 1999]
}
df = pd.DataFrame(data)

# Push the DataFrame to Neo4j
connection.push_dataframe(
    df=df,
    label_col="label",
    property_cols=["name", "age", "year"],
    match_cols=["name"]
)
```

### Working with Ontology Terms

```python
from science_data_kit.core.utils.isa_compatibility import OntologyAnnotation, OntologySource

# Create ontology terms
source = OntologySource(name="NCBI", file="", version="1.0", description="NCBI Taxonomy")
terms = [
    OntologyAnnotation(term="Homo sapiens", term_accession="http://purl.bioontology.org/ontology/NCBITAXON/9606", term_source=source),
    OntologyAnnotation(term="Mus musculus", term_accession="http://purl.bioontology.org/ontology/NCBITAXON/10090", term_source=source)
]

# Load terms into Neo4j
relationships_created = connection.load_ontology_relationships(
    ontology_annotations=terms,
    create_source_nodes=True,
    relationship_type="HAS_TERM"
)
```