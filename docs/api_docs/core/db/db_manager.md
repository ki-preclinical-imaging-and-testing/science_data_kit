# db_manager.py - Neo4j Database Manager

This module provides a comprehensive manager for Neo4j database operations. It includes classes and functions for connecting to Neo4j databases, executing queries, managing Docker containers, and working with graph data.

## Exception Classes

### DatabaseError

Base exception class for database-related errors.

### ConnectionError

Exception raised when there is a problem connecting to the Neo4j database.

### QueryError

Exception raised when there is a problem executing a query.

### ConfigError

Exception raised when there is a problem with the configuration.

## Functions

### load_db_config

```python
def load_db_config(fn: str = 'db_config.yaml') -> Dict[str, Any]
```

Loads database configuration from a YAML file.

**Parameters:**
- `fn` (str, optional): Path to the configuration file. Defaults to 'db_config.yaml'.

**Returns:**
- A dictionary containing the configuration.

### update_db_config_auto

```python
def update_db_config_auto(hostname: str, port: str, username: Optional[str] = None, password: Optional[str] = None, database: Optional[str] = None) -> None
```

Updates the automatic database configuration file.

**Parameters:**
- `hostname` (str): The hostname of the Neo4j server.
- `port` (str): The port of the Neo4j server.
- `username` (str, optional): The username for authentication.
- `password` (str, optional): The password for authentication.
- `database` (str, optional): The name of the database.

### find_free_port

```python
def find_free_port(start_port: int = 7687) -> int
```

Finds a free port starting from the specified port.

**Parameters:**
- `start_port` (int, optional): The port to start searching from. Defaults to 7687.

**Returns:**
- A free port number.

## Classes

### Neo4jManager

A unified manager for Neo4j database operations.

This class provides methods for:
- Managing Neo4j connections
- Starting and stopping Neo4j containers
- Executing queries and processing results
- Importing and exporting data
- Working with ontologies

The class is implemented as a singleton, so only one instance exists at a time.

#### Constructor

```python
def __init__(config: Optional[Dict[str, Any]] = None, config_file: Optional[str] = None, use_session_state: bool = False)
```

**Parameters:**
- `config` (Dict[str, Any], optional): Dictionary with database connection details.
- `config_file` (str, optional): Path to a YAML file with database connection details.
- `use_session_state` (bool, optional): If True, use the connection from Streamlit session_state if available. Defaults to False.

**Raises:**
- `ConnectionError`: If the connection details are invalid or the connection fails.

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

##### is_connected

```python
def is_connected(self) -> bool
```

Checks if the manager is connected to a Neo4j database.

**Returns:**
- True if connected, False otherwise.

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
- `QueryError`: If the query execution fails.

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

**Raises:**
- `ConnectionError`: If there is no active connection.
- `QueryError`: If the query execution fails.

##### query_to_value

```python
def query_to_value(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Any
```

Executes a Cypher query and returns a single value.

**Parameters:**
- `query` (str): The Cypher query to execute.
- `parameters` (Dict[str, Any], optional): Optional dictionary of parameters.

**Returns:**
- A single value if one result is returned, or a list of values if multiple rows are returned.

**Raises:**
- `ConnectionError`: If there is no active connection.
- `QueryError`: If the query execution fails.

##### get_container_status

```python
def get_container_status(self) -> str
```

Gets the status of the Neo4j container.

**Returns:**
- The status of the container ("running", "stopped", or "not found").

##### get_hostname

```python
def get_hostname(self) -> str
```

Gets the hostname for connecting to the Neo4j container.

**Returns:**
- The hostname (either "localhost" or the container's IP address).

##### start_container

```python
def start_container(self, version: str = "latest") -> bool
```

Starts the Neo4j container.

**Parameters:**
- `version` (str, optional): The Neo4j version to use. Defaults to "latest".

**Returns:**
- True if the container was started successfully, False otherwise.

**Raises:**
- `ConnectionError`: If the container cannot be started.

##### stop_container

```python
def stop_container(self) -> bool
```

Stops the Neo4j container.

**Returns:**
- True if the container was stopped successfully, False otherwise.

##### fetch_labels

```python
def fetch_labels(self) -> List[str]
```

Fetches all labels from the Neo4j database.

**Returns:**
- List of label names.

**Raises:**
- `ConnectionError`: If there is no active connection.
- `QueryError`: If the query execution fails.

##### fetch_node_properties

```python
def fetch_node_properties(self, label: str) -> List[str]
```

Fetches all property keys for nodes with the given label.

**Parameters:**
- `label` (str): The node label to query.

**Returns:**
- List of property keys.

**Raises:**
- `ConnectionError`: If there is no active connection.
- `QueryError`: If the query execution fails.

##### fetch_nodes

```python
def fetch_nodes(self, label: str, properties: Optional[List[str]] = None, limit: int = 100) -> List[Dict[str, Any]]
```

Fetches nodes with the given label and returns selected properties.

**Parameters:**
- `label` (str): The node label to query.
- `properties` (List[str], optional): List of property keys to return. If None, returns all properties.
- `limit` (int, optional): Maximum number of nodes to return. Defaults to 100.

**Returns:**
- List of dictionaries containing node properties.

**Raises:**
- `ConnectionError`: If there is no active connection.
- `QueryError`: If the query execution fails.

##### summarize_ontology_terms

```python
def summarize_ontology_terms(self, label: Optional[str] = None) -> Dict[str, Dict[str, Any]]
```

Summarizes available ontology terms used as properties for node labels.

**Parameters:**
- `label` (str, optional): Optional label to filter the summary. If None, summarizes terms for all labels.

**Returns:**
- A dictionary with label names as keys and dictionaries of property summaries as values.

**Raises:**
- `ConnectionError`: If there is no active connection.
- `QueryError`: If the query execution fails.

##### load_ontology_relationships

```python
def load_ontology_relationships(self, ontology_annotations: List[Any], create_source_nodes: bool = True, relationship_type: str = "HAS_TERM") -> int
```

Loads ontology terms and their relationships into Neo4j.

**Parameters:**
- `ontology_annotations` (List[Any]): List of OntologyAnnotation objects to load.
- `create_source_nodes` (bool, optional): Whether to create nodes for ontology sources. Defaults to True.
- `relationship_type` (str, optional): The type of relationship to create between source and term nodes. Defaults to "HAS_TERM".

**Returns:**
- Number of relationships created.

**Raises:**
- `ConnectionError`: If there is no active connection.
- `QueryError`: If the query execution fails.

##### export_graph

```python
def export_graph(self, file_path: str) -> Tuple[bool, str]
```

Exports the entire graph to a file.

**Parameters:**
- `file_path` (str): Path where the graph will be saved.

**Returns:**
- A tuple containing (success, message).

**Raises:**
- `ConnectionError`: If there is no active connection.

##### import_graph

```python
def import_graph(self, file_path: str) -> Tuple[bool, str]
```

Imports a graph from a file into Neo4j.

**Parameters:**
- `file_path` (str): Path to the file containing the graph.

**Returns:**
- A tuple containing (success, message).

**Raises:**
- `ConnectionError`: If there is no active connection.

## Examples

### Basic Usage

```python
# Get the singleton instance
from science_data_kit.core.db.db_manager import db_manager

# Or create a new instance with custom configuration
from science_data_kit.core.db.db_manager import Neo4jManager
manager = Neo4jManager(
    config={
        "uri": "bolt://localhost:7687",
        "user": "neo4j",
        "password": "password",
        "database": "neo4j"
    }
)

# Execute a query
results = manager.execute_query("MATCH (n) RETURN n LIMIT 10")

# Convert results to a DataFrame
df = manager.query_to_dataframe("MATCH (n) RETURN n.name, n.age LIMIT 10")

# Close the connection when done
manager.close()
```

### Working with Docker Containers

```python
# Start a Neo4j container
success = manager.start_container(version="4.4")
if success:
    print("Container started successfully")

# Check container status
status = manager.get_container_status()
print(f"Container status: {status}")

# Stop the container when done
manager.stop_container()
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
relationships_created = manager.load_ontology_relationships(
    ontology_annotations=terms,
    create_source_nodes=True,
    relationship_type="HAS_TERM"
)
```

### Importing and Exporting Graphs

```python
# Export the graph to a file
success, message = manager.export_graph("graph_backup.pkl")
if success:
    print(message)
else:
    print(f"Export failed: {message}")

# Import the graph from a file
success, message = manager.import_graph("graph_backup.pkl")
if success:
    print(message)
else:
    print(f"Import failed: {message}")
```