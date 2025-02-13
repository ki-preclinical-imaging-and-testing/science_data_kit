import yaml
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import Neo4jError
import pandas as pd

def load_db_config(fn='db_config.yaml'):
    """
    Loads the database configuration from a YAML file.

    :param fn: Path to the YAML configuration file.
    :return: Dictionary containing the database configuration.
    """
    try:
        with open(fn, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"ERROR: Could not load {fn} - {e}")
        return None

class Neo4jConnection:
    """
    A robust Neo4j driver for connecting and executing queries with improved error handling and extended functionality.
    """

    def __init__(self, config=None, config_file=None):
        """
        Initialize the Neo4jConnection instance.

        :param config: Dictionary with database connection details (overrides config_file if provided).
        :param config_file: Path to a YAML file with database connection details.
        """
        if config is None:
            if config_file:
                config = load_db_config(config_file)
            else:
                raise ValueError("Either a config dictionary or a config_file path must be provided.")
        
        required_keys = {"uri", "user", "password", "database"}
        if not all(key in config for key in required_keys):
            raise ValueError(f"Missing required keys in config. Expected keys: {required_keys}")

        self.uri = config["uri"]
        self.user = config["user"]
        self.password = config["password"]
        self.database = config.get("database", "aipt")
        self._driver: Driver = None
        self._connect()

    def _connect(self):
        """
        Establishes a connection to the Neo4j database.
        """
        try:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        except Neo4jError as e:
            raise ConnectionError(f"Failed to connect to Neo4j: {e}")

    def close(self):
        """
        Closes the Neo4j driver connection.
        """
        if self._driver:
            self._driver.close()
            self._driver = None

    def execute_query(self, query: str, parameters: dict = None):
        """
        Executes a Cypher query and returns the raw results.

        :param query: The Cypher query to execute.
        :param parameters: Optional dictionary of parameters to include in the query.
        :return: Neo4j result object.
        """
        if not self._driver:
            raise ConnectionError("Cannot run query. No active connection to Neo4j.")
        
        parameters = parameters or {}
        
        try:
            with self._driver.session(database=self.database) as session:
                return list(session.run(query, parameters))
        except Neo4jError as e:
            raise RuntimeError(f"Query execution failed: {e}")

    def query_to_dataframe(self, query: str, parameters: dict = None) -> pd.DataFrame:
        """
        Executes a Cypher query and returns the results as a Pandas DataFrame.

        :param query: The Cypher query to execute.
        :param parameters: Optional dictionary of parameters.
        :return: A Pandas DataFrame containing the query results.
        """
        result = self.execute_query(query, parameters)
        records = [dict(record) for record in result]
        return pd.DataFrame(records)

    def query_to_dict(self, query: str, parameters: dict = None) -> dict:
        """
        Executes a Cypher query and returns the results as a list of dictionaries.

        :param query: The Cypher query to execute.
        :param parameters: Optional dictionary of parameters.
        :return: A list of dictionaries representing the query results.
        """
        result = self.execute_query(query, parameters)
        return [dict(record) for record in result]

    def query_to_value(self, query: str, parameters: dict = None):
        """
        Executes a Cypher query and returns a single value or a set of values.

        :param query: The Cypher query to execute.
        :param parameters: Optional dictionary of parameters.
        :return: A single value if one result is returned, or a list of values if multiple rows are returned.
        """
        result = self.execute_query(query, parameters)
        values = [list(record.values())[0] for record in result]
        return values[0] if len(values) == 1 else values

    def push_dataframe(self, df: pd.DataFrame, label_col: str, property_cols: list, match_cols: list):
        """
        Pushes a DataFrame into Neo4j, using specified columns for labels, properties, and match criteria.

        :param df: The Pandas DataFrame containing data to push.
        :param label_col: The column containing labels for nodes.
        :param property_cols: The columns to be used as properties.
        :param match_cols: The columns to be used for matching existing nodes.
        """
        if label_col not in df.columns:
            raise ValueError(f"Label column '{label_col}' not found in DataFrame.")
        
        for _, row in df.iterrows():
            label = row[label_col]
            properties = {col: row[col] for col in property_cols if col in df.columns}
            match_criteria = {col: row[col] for col in match_cols if col in df.columns}
            
            if not match_criteria:
                raise ValueError("At least one match column must be provided.")
            
            match_string = ", ".join(f"{k}: ${k}" for k in match_criteria.keys())
            properties_string = ", ".join(f"{k}: ${k}" for k in properties.keys())
            
            query = f"""
            MERGE (n:{label} {{ {match_string} }})
            SET n += {{ {properties_string} }}
            """
            
            self.execute_query(query, {**match_criteria, **properties})

    def push_and_link_dataframe(self, df: pd.DataFrame, label_col: str, property_cols: list, match_cols: list, node_match_label: str, node_match_properties: list, node_match_relationship_type: str):
        """
        Pushes a DataFrame into Neo4j and links nodes based on match criteria.
        """
        if label_col not in df.columns:
            raise ValueError(f"Label column '{label_col}' not found in DataFrame.")
        for _, row in df.iterrows():
            label = row[label_col]
            label_match = row[node_match_label]
            properties = {col: row[col] for col in property_cols if col in df.columns}
            match_criteria = {col: row[col] for col in match_cols if col in df.columns}
            node_match_criteria = {col: row[col] for col in node_match_properties if col in df.columns}
            if not match_criteria or not node_match_criteria:
                raise ValueError("Both entity match columns and node match columns must be provided.")
            match_string = ", ".join(f"{k}: ${k}" for k in match_criteria.keys())
            properties_string = ", ".join(f"{k}: ${k}" for k in properties.keys())
            node_match_string = ", ".join(f"{k}: ${k}" for k in node_match_criteria.keys())
            query = f"""
            MERGE (n:{label} {{ {match_string} }})
            SET n += {{ {properties_string} }}
            WITH n
            MATCH (m:{label_match} {{ {node_match_string} }})
            MERGE (n)-[:{node_match_relationship_type}]->(m)
            """
            self.execute_query(query, {**match_criteria, **properties, **node_match_criteria})

    def test_connection(self, quiet: bool = False) -> bool:
        """
        Tests the Neo4j connection by running a simple query.

        :param quiet: If True, suppresses success message output.
        :return: True if the connection is successful, raises an exception otherwise.
        """
        try:
            self.execute_query("RETURN 1")
            if not quiet:
                print("Connection successful!")
            return True
        except Exception as e:
            raise ConnectionError(f"Connection failed: {e}")


# Example usage:
# conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
# conn.test_connection()
# df = conn.query_to_dataframe("MATCH (n) RETURN n LIMIT 10")
# print(df)
# results = conn.query_to_dict("MATCH (n) RETURN n LIMIT 10")
# print(results)
# count = conn.query_to_value("MATCH (n) RETURN COUNT(n)")
# print(count)
# conn.close()
