"""
Cassandra Provider for Science Data Kit

This module provides a provider for connecting to Cassandra databases, allowing
the Science Data Kit to interact with Cassandra distributed databases.
"""

import os
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from cassandra.cluster import Cluster, Session
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import DCAwareRoundRobinPolicy, TokenAwarePolicy
from cassandra.query import SimpleStatement, BatchStatement, ConsistencyLevel

from ...providers.registry import BaseProvider, ProviderType


class CassandraProvider(BaseProvider):
    """
    Provider for Cassandra database connections.

    This class provides functionality for connecting to Cassandra databases
    and executing queries against them.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Cassandra database provider.

        Args:
            config: Configuration dictionary containing connection details
                   Required keys:
                   - contact_points: List of Cassandra contact points or single host string
                   - keyspace: Keyspace name
                   
                   Optional:
                   - port: Cassandra port (default: 9042)
                   - username: Username for authentication (optional)
                   - password: Password for authentication (optional)
                   - ssl_options: SSL options for secure connection (optional)
                   - load_balancing_policy: Load balancing policy (default: TokenAwarePolicy with DCAwareRoundRobinPolicy)
                   - protocol_version: Protocol version (default: 4)
                   - compression: Compression type (default: None)
                   - consistency_level: Default consistency level (default: LOCAL_QUORUM)
                   - fetch_size: Default fetch size for queries (default: 5000)
                   - connect_timeout: Connection timeout in seconds (default: 10)
                   - request_timeout: Request timeout in seconds (default: 30)
        """
        super().__init__(config)
        self.cluster = None
        self.session = None
        self.keyspace = config.get('keyspace')
        
    async def initialize(self) -> bool:
        """
        Initialize the Cassandra database connection.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Get connection parameters
            contact_points = self.config.get('contact_points')
            if not contact_points:
                print("Cassandra contact points not provided")
                return False
            
            # Convert single host string to list if necessary
            if isinstance(contact_points, str):
                contact_points = [contact_points]
            
            # Get optional parameters
            port = self.config.get('port', 9042)
            username = self.config.get('username')
            password = self.config.get('password')
            ssl_options = self.config.get('ssl_options')
            protocol_version = self.config.get('protocol_version', 4)
            compression = self.config.get('compression')
            connect_timeout = self.config.get('connect_timeout', 10)
            request_timeout = self.config.get('request_timeout', 30)
            
            # Build connection parameters
            conn_params = {
                'contact_points': contact_points,
                'port': port,
                'protocol_version': protocol_version,
                'connect_timeout': connect_timeout,
                'control_connection_timeout': connect_timeout
            }
            
            # Add authentication if provided
            if username and password:
                auth_provider = PlainTextAuthProvider(username=username, password=password)
                conn_params['auth_provider'] = auth_provider
            
            # Add SSL if provided
            if ssl_options:
                conn_params['ssl_options'] = ssl_options
            
            # Add compression if provided
            if compression:
                conn_params['compression'] = compression
            
            # Add load balancing policy
            dc_policy = DCAwareRoundRobinPolicy()
            conn_params['load_balancing_policy'] = TokenAwarePolicy(dc_policy)
            
            # Initialize Cassandra cluster
            self.cluster = Cluster(**conn_params)
            
            # Connect to keyspace
            if self.keyspace:
                self.session = self.cluster.connect(self.keyspace)
            else:
                self.session = self.cluster.connect()
            
            # Set default request timeout
            self.session.default_timeout = request_timeout
            
            # Test connection
            row = self.session.execute("SELECT release_version FROM system.local").one()
            if row:
                print(f"Connected to Cassandra cluster with version: {row.release_version}")
            
            self.is_initialized = True
            return True
        
        except Exception as e:
            print(f"Error initializing Cassandra provider: {str(e)}")
            self.is_initialized = False
            return False
    
    async def health_check(self) -> bool:
        """
        Check if the database connection is healthy.
        
        Returns:
            True if the connection is healthy, False otherwise
        """
        if not self.is_initialized or not self.cluster or not self.session:
            return False
        
        try:
            # Test connection by executing a simple query
            self.session.execute("SELECT release_version FROM system.local")
            return True
        except Exception as e:
            print(f"Database health check failed: {str(e)}")
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the provider.
        
        Returns:
            Dictionary of provider capabilities
        """
        capabilities = {
            "type": ProviderType.DATABASE.value,
            "name": "cassandra",
            "features": [
                "query",
                "schema_introspection",
                "data_export",
                "wide_column_storage",
                "distributed_database",
                "high_availability",
                "linear_scalability",
                "tunable_consistency"
            ],
            "supported_operations": [
                "select",
                "insert",
                "update",
                "delete",
                "batch",
                "count",
                "create_table",
                "alter_table",
                "drop_table"
            ]
        }
        
        return capabilities
    
    async def list_keyspaces(self) -> List[Dict[str, Any]]:
        """
        List keyspaces in the Cassandra cluster.
        
        Returns:
            List of keyspace metadata dictionaries
        """
        if not self.is_initialized or not self.cluster or not self.session:
            raise Exception("Cassandra provider not initialized")
        
        try:
            # Get all keyspaces
            query = "SELECT keyspace_name, durable_writes, replication FROM system_schema.keyspaces"
            rows = self.session.execute(query)
            
            # Format the response
            keyspaces = []
            for row in rows:
                keyspaces.append({
                    "name": row.keyspace_name,
                    "durable_writes": row.durable_writes,
                    "replication": row.replication
                })
            
            return keyspaces
        
        except Exception as e:
            print(f"Error listing keyspaces: {str(e)}")
            raise
    
    async def list_tables(self, keyspace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List tables in a keyspace.
        
        Args:
            keyspace: Optional keyspace name (uses current keyspace if not provided)
            
        Returns:
            List of table metadata dictionaries
        """
        if not self.is_initialized or not self.cluster or not self.session:
            raise Exception("Cassandra provider not initialized")
        
        try:
            # Use provided keyspace or current keyspace
            ks = keyspace or self.keyspace
            if not ks:
                raise ValueError("Keyspace not specified and no current keyspace")
            
            # Get all tables in the keyspace
            query = f"SELECT table_name FROM system_schema.tables WHERE keyspace_name = '{ks}'"
            rows = self.session.execute(query)
            
            # Format the response
            tables = []
            for row in rows:
                # Get table columns
                columns_query = f"SELECT column_name, type FROM system_schema.columns WHERE keyspace_name = '{ks}' AND table_name = '{row.table_name}'"
                columns = self.session.execute(columns_query)
                
                # Add table to the list
                tables.append({
                    "name": row.table_name,
                    "columns": [{"name": col.column_name, "type": col.type} for col in columns]
                })
            
            return tables
        
        except Exception as e:
            print(f"Error listing tables: {str(e)}")
            raise
    
    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                           consistency_level: Optional[str] = None, fetch_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Execute a query on the database.
        
        Args:
            query: CQL query string
            parameters: Optional parameters for the query
            consistency_level: Optional consistency level for the query
            fetch_size: Optional fetch size for the query
            
        Returns:
            List of dictionaries containing the query results
        """
        if not self.is_initialized or not self.cluster or not self.session:
            raise Exception("Cassandra provider not initialized")
        
        try:
            # Create statement with options
            statement = SimpleStatement(query)
            
            # Set consistency level if provided
            if consistency_level:
                statement.consistency_level = getattr(ConsistencyLevel, consistency_level)
            
            # Set fetch size if provided
            if fetch_size:
                statement.fetch_size = fetch_size
            
            # Execute query
            if parameters:
                rows = self.session.execute(statement, parameters)
            else:
                rows = self.session.execute(statement)
            
            # Convert rows to dictionaries
            results = []
            for row in rows:
                if hasattr(row, "_fields"):
                    # Named tuple
                    results.append({field: getattr(row, field) for field in row._fields})
                else:
                    # Regular row
                    results.append(dict(row.items()))
            
            return results
        
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            raise
    
    async def query_to_dataframe(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                                consistency_level: Optional[str] = None, fetch_size: Optional[int] = None) -> pd.DataFrame:
        """
        Execute a query and return results as a pandas DataFrame.
        
        Args:
            query: CQL query string
            parameters: Optional parameters for the query
            consistency_level: Optional consistency level for the query
            fetch_size: Optional fetch size for the query
            
        Returns:
            Pandas DataFrame containing the query results
        """
        if not self.is_initialized or not self.cluster or not self.session:
            raise Exception("Cassandra provider not initialized")
        
        try:
            # Execute query and get results
            results = await self.execute_query(query, parameters, consistency_level, fetch_size)
            
            # Convert to DataFrame
            if results:
                return pd.DataFrame(results)
            else:
                return pd.DataFrame()
        
        except Exception as e:
            print(f"Error executing query to DataFrame: {str(e)}")
            raise
    
    async def insert_data(self, table: str, data: Dict[str, Any], 
                         consistency_level: Optional[str] = None) -> bool:
        """
        Insert data into a table.
        
        Args:
            table: Name of the table
            data: Dictionary of column-value pairs to insert
            consistency_level: Optional consistency level for the operation
            
        Returns:
            True if insertion was successful, False otherwise
        """
        if not self.is_initialized or not self.cluster or not self.session:
            raise Exception("Cassandra provider not initialized")
        
        try:
            # Build column and value lists
            columns = list(data.keys())
            placeholders = ["%s"] * len(columns)
            values = list(data.values())
            
            # Build query
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            
            # Create statement with options
            statement = SimpleStatement(query)
            
            # Set consistency level if provided
            if consistency_level:
                statement.consistency_level = getattr(ConsistencyLevel, consistency_level)
            
            # Execute query
            self.session.execute(statement, values)
            
            return True
        
        except Exception as e:
            print(f"Error inserting data: {str(e)}")
            raise
    
    async def batch_insert(self, table: str, data_list: List[Dict[str, Any]], 
                          consistency_level: Optional[str] = None) -> bool:
        """
        Insert multiple rows of data into a table using a batch statement.
        
        Args:
            table: Name of the table
            data_list: List of dictionaries containing column-value pairs to insert
            consistency_level: Optional consistency level for the operation
            
        Returns:
            True if batch insertion was successful, False otherwise
        """
        if not self.is_initialized or not self.cluster or not self.session:
            raise Exception("Cassandra provider not initialized")
        
        try:
            # Create batch statement
            batch = BatchStatement()
            
            # Set consistency level if provided
            if consistency_level:
                batch.consistency_level = getattr(ConsistencyLevel, consistency_level)
            
            # Add statements to batch
            for data in data_list:
                # Build column and value lists
                columns = list(data.keys())
                placeholders = ["%s"] * len(columns)
                values = list(data.values())
                
                # Build query
                query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                
                # Add to batch
                batch.add(SimpleStatement(query), values)
            
            # Execute batch
            self.session.execute(batch)
            
            return True
        
        except Exception as e:
            print(f"Error batch inserting data: {str(e)}")
            raise
    
    async def update_data(self, table: str, data: Dict[str, Any], where: Dict[str, Any],
                         consistency_level: Optional[str] = None) -> bool:
        """
        Update data in a table.
        
        Args:
            table: Name of the table
            data: Dictionary of column-value pairs to update
            where: Dictionary of column-value pairs for WHERE clause
            consistency_level: Optional consistency level for the operation
            
        Returns:
            True if update was successful, False otherwise
        """
        if not self.is_initialized or not self.cluster or not self.session:
            raise Exception("Cassandra provider not initialized")
        
        try:
            # Build SET clause
            set_clause = ", ".join([f"{col} = %s" for col in data.keys()])
            set_values = list(data.values())
            
            # Build WHERE clause
            where_clause = " AND ".join([f"{col} = %s" for col in where.keys()])
            where_values = list(where.values())
            
            # Build query
            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            
            # Create statement with options
            statement = SimpleStatement(query)
            
            # Set consistency level if provided
            if consistency_level:
                statement.consistency_level = getattr(ConsistencyLevel, consistency_level)
            
            # Execute query
            self.session.execute(statement, set_values + where_values)
            
            return True
        
        except Exception as e:
            print(f"Error updating data: {str(e)}")
            raise
    
    async def delete_data(self, table: str, where: Dict[str, Any],
                         consistency_level: Optional[str] = None) -> bool:
        """
        Delete data from a table.
        
        Args:
            table: Name of the table
            where: Dictionary of column-value pairs for WHERE clause
            consistency_level: Optional consistency level for the operation
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if not self.is_initialized or not self.cluster or not self.session:
            raise Exception("Cassandra provider not initialized")
        
        try:
            # Build WHERE clause
            where_clause = " AND ".join([f"{col} = %s" for col in where.keys()])
            where_values = list(where.values())
            
            # Build query
            query = f"DELETE FROM {table} WHERE {where_clause}"
            
            # Create statement with options
            statement = SimpleStatement(query)
            
            # Set consistency level if provided
            if consistency_level:
                statement.consistency_level = getattr(ConsistencyLevel, consistency_level)
            
            # Execute query
            self.session.execute(statement, where_values)
            
            return True
        
        except Exception as e:
            print(f"Error deleting data: {str(e)}")
            raise
    
    async def count_rows(self, table: str, where: Optional[Dict[str, Any]] = None,
                        consistency_level: Optional[str] = None) -> int:
        """
        Count rows in a table.
        
        Args:
            table: Name of the table
            where: Optional dictionary of column-value pairs for WHERE clause
            consistency_level: Optional consistency level for the operation
            
        Returns:
            Number of rows matching the criteria
        """
        if not self.is_initialized or not self.cluster or not self.session:
            raise Exception("Cassandra provider not initialized")
        
        try:
            # Build query
            query = f"SELECT COUNT(*) FROM {table}"
            values = []
            
            # Add WHERE clause if provided
            if where:
                where_clause = " AND ".join([f"{col} = %s" for col in where.keys()])
                values = list(where.values())
                query += f" WHERE {where_clause}"
            
            # Create statement with options
            statement = SimpleStatement(query)
            
            # Set consistency level if provided
            if consistency_level:
                statement.consistency_level = getattr(ConsistencyLevel, consistency_level)
            
            # Execute query
            row = self.session.execute(statement, values).one()
            
            # Extract count value
            count = row[0] if row else 0
            
            return count
        
        except Exception as e:
            print(f"Error counting rows: {str(e)}")
            raise
    
    async def get_table_schema(self, table: str, keyspace: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the schema of a table.
        
        Args:
            table: Name of the table
            keyspace: Optional keyspace name (uses current keyspace if not provided)
            
        Returns:
            Dictionary containing the table schema
        """
        if not self.is_initialized or not self.cluster or not self.session:
            raise Exception("Cassandra provider not initialized")
        
        try:
            # Use provided keyspace or current keyspace
            ks = keyspace or self.keyspace
            if not ks:
                raise ValueError("Keyspace not specified and no current keyspace")
            
            # Get table columns
            columns_query = f"SELECT column_name, type, kind FROM system_schema.columns WHERE keyspace_name = '{ks}' AND table_name = '{table}'"
            columns = self.session.execute(columns_query)
            
            # Get table indexes
            indexes_query = f"SELECT index_name, options FROM system_schema.indexes WHERE keyspace_name = '{ks}' AND table_name = '{table}'"
            indexes = self.session.execute(indexes_query)
            
            # Format the response
            schema = {
                "name": table,
                "keyspace": ks,
                "columns": [],
                "indexes": []
            }
            
            # Add columns
            for col in columns:
                column_info = {
                    "name": col.column_name,
                    "type": col.type,
                    "kind": col.kind
                }
                schema["columns"].append(column_info)
            
            # Add indexes
            for idx in indexes:
                index_info = {
                    "name": idx.index_name,
                    "options": idx.options
                }
                schema["indexes"].append(index_info)
            
            return schema
        
        except Exception as e:
            print(f"Error getting table schema: {str(e)}")
            raise
    
    async def import_dataframe_to_table(self, df: pd.DataFrame, table: str, 
                                      create_table: bool = False, 
                                      primary_key: Optional[List[str]] = None,
                                      batch_size: int = 100,
                                      consistency_level: Optional[str] = None) -> int:
        """
        Import a pandas DataFrame to a Cassandra table.
        
        Args:
            df: Pandas DataFrame to import
            table: Name of the target table
            create_table: Whether to create the table if it doesn't exist
            primary_key: List of column names to use as primary key (required if create_table is True)
            batch_size: Number of rows to insert in each batch
            consistency_level: Optional consistency level for the operation
            
        Returns:
            Number of rows imported
        """
        if not self.is_initialized or not self.cluster or not self.session:
            raise Exception("Cassandra provider not initialized")
        
        try:
            # Create table if requested
            if create_table:
                if not primary_key:
                    raise ValueError("Primary key must be specified when creating a table")
                
                # Map pandas dtypes to Cassandra types
                type_mapping = {
                    'int64': 'bigint',
                    'int32': 'int',
                    'float64': 'double',
                    'float32': 'float',
                    'bool': 'boolean',
                    'datetime64[ns]': 'timestamp',
                    'object': 'text',
                    'category': 'text'
                }
                
                # Build column definitions
                columns = []
                for col_name, dtype in df.dtypes.items():
                    cass_type = type_mapping.get(str(dtype), 'text')
                    columns.append(f"{col_name} {cass_type}")
                
                # Build primary key clause
                pk_clause = ", ".join(primary_key)
                if len(primary_key) > 1:
                    pk_clause = f"({pk_clause})"
                
                # Build CREATE TABLE query
                create_query = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns)}, PRIMARY KEY ({pk_clause}))"
                
                # Execute CREATE TABLE query
                self.session.execute(create_query)
            
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            # Insert records in batches
            total_inserted = 0
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                await self.batch_insert(table, batch, consistency_level)
                total_inserted += len(batch)
            
            return total_inserted
        
        except Exception as e:
            print(f"Error importing DataFrame to table: {str(e)}")
            raise