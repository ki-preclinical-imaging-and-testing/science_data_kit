"""
MongoDB Provider for Science Data Kit

This module provides a provider for connecting to MongoDB databases, allowing
the Science Data Kit to interact with MongoDB document stores.
"""

import os
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Dict, List, Optional, Any, Union, Tuple

from ...providers.registry import BaseProvider, ProviderType


class MongoDBProvider(BaseProvider):
    """
    Provider for MongoDB database connections.

    This class provides functionality for connecting to MongoDB databases
    and executing queries against them.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the MongoDB database provider.

        Args:
            config: Configuration dictionary containing connection details
                   Required keys:
                   - host: MongoDB host (default: localhost)
                   - port: MongoDB port (default: 27017)
                   - database: Database name
                   - username: Database username (optional)
                   - password: Database password (optional)
                   - connection_string: MongoDB connection string (optional, alternative to individual params)
                   
                   Optional:
                   - auth_source: Authentication database (default: admin)
                   - auth_mechanism: Authentication mechanism
                   - tls: Use TLS/SSL (default: False)
                   - tls_ca_file: Path to CA file for TLS
                   - tls_cert_key_file: Path to client certificate key file
                   - max_pool_size: Connection pool size (default: 100)
                   - timeout_ms: Connection timeout in milliseconds (default: 30000)
        """
        super().__init__(config)
        self.client = None
        self.db = None
        self.connection_string = config.get('connection_string')
        
    async def initialize(self) -> bool:
        """
        Initialize the MongoDB database connection.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # If connection string is provided, use it directly
            if self.connection_string:
                self.client = MongoClient(self.connection_string)
            else:
                # Otherwise, build connection from individual parameters
                host = self.config.get('host', 'localhost')
                port = self.config.get('port', 27017)
                username = self.config.get('username')
                password = self.config.get('password')
                auth_source = self.config.get('auth_source', 'admin')
                auth_mechanism = self.config.get('auth_mechanism')
                tls = self.config.get('tls', False)
                tls_ca_file = self.config.get('tls_ca_file')
                tls_cert_key_file = self.config.get('tls_cert_key_file')
                max_pool_size = self.config.get('max_pool_size', 100)
                timeout_ms = self.config.get('timeout_ms', 30000)
                
                # Build connection parameters
                conn_params = {
                    'host': host,
                    'port': port,
                    'maxPoolSize': max_pool_size,
                    'connectTimeoutMS': timeout_ms,
                }
                
                # Add authentication if provided
                if username and password:
                    conn_params['username'] = username
                    conn_params['password'] = password
                    conn_params['authSource'] = auth_source
                    if auth_mechanism:
                        conn_params['authMechanism'] = auth_mechanism
                
                # Add TLS/SSL if enabled
                if tls:
                    conn_params['tls'] = True
                    if tls_ca_file:
                        conn_params['tlsCAFile'] = tls_ca_file
                    if tls_cert_key_file:
                        conn_params['tlsCertificateKeyFile'] = tls_cert_key_file
                
                self.client = MongoClient(**conn_params)
            
            # Get database
            database_name = self.config.get('database')
            if not database_name:
                print("Database name not provided")
                return False
            
            self.db = self.client[database_name]
            
            # Test connection
            self.client.admin.command('ping')
            
            self.is_initialized = True
            return True
        
        except Exception as e:
            print(f"Error initializing MongoDB provider: {str(e)}")
            self.is_initialized = False
            return False
    
    async def health_check(self) -> bool:
        """
        Check if the database connection is healthy.
        
        Returns:
            True if the connection is healthy, False otherwise
        """
        if not self.is_initialized or not self.client:
            return False
        
        try:
            # Test connection by executing a simple command
            self.client.admin.command('ping')
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
            "name": "mongodb",
            "features": [
                "query",
                "schema_introspection",
                "data_export",
                "document_storage",
                "aggregation_pipeline",
                "geospatial_queries",
                "text_search"
            ],
            "supported_operations": [
                "find",
                "insert",
                "update",
                "delete",
                "aggregate",
                "count",
                "distinct",
                "map_reduce"
            ]
        }
        
        return capabilities
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """
        List collections in the database.
        
        Returns:
            List of collection metadata dictionaries
        """
        if not self.is_initialized or not self.client or not self.db:
            raise Exception("MongoDB provider not initialized")
        
        try:
            collections = []
            
            # Get all collection names
            collection_names = self.db.list_collection_names()
            
            # Get metadata for each collection
            for collection_name in collection_names:
                # Get collection stats
                stats = self.db.command("collStats", collection_name)
                
                # Add collection to the list
                collections.append({
                    "name": collection_name,
                    "count": stats.get("count", 0),
                    "size": stats.get("size", 0),
                    "avg_obj_size": stats.get("avgObjSize", 0),
                    "storage_size": stats.get("storageSize", 0),
                    "is_capped": stats.get("capped", False),
                    "indexes": stats.get("nindexes", 0)
                })
            
            return collections
        
        except Exception as e:
            print(f"Error listing collections: {str(e)}")
            raise
    
    async def execute_query(self, collection: str, query: Dict[str, Any], 
                           projection: Optional[Dict[str, Any]] = None,
                           sort: Optional[List[Tuple[str, int]]] = None,
                           limit: int = 0, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Execute a query on the database.
        
        Args:
            collection: Name of the collection to query
            query: MongoDB query filter
            projection: Optional fields to include or exclude
            sort: Optional sorting criteria
            limit: Maximum number of documents to return (0 for no limit)
            skip: Number of documents to skip
            
        Returns:
            List of dictionaries containing the query results
        """
        if not self.is_initialized or not self.client or not self.db:
            raise Exception("MongoDB provider not initialized")
        
        try:
            # Get collection
            coll = self.db[collection]
            
            # Execute query
            cursor = coll.find(query, projection)
            
            # Apply sort if provided
            if sort:
                cursor = cursor.sort(sort)
            
            # Apply skip and limit
            if skip > 0:
                cursor = cursor.skip(skip)
            if limit > 0:
                cursor = cursor.limit(limit)
            
            # Convert cursor to list
            results = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for doc in results:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            return results
        
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            raise
    
    async def query_to_dataframe(self, collection: str, query: Dict[str, Any],
                                projection: Optional[Dict[str, Any]] = None,
                                sort: Optional[List[Tuple[str, int]]] = None,
                                limit: int = 0, skip: int = 0) -> pd.DataFrame:
        """
        Execute a query and return results as a pandas DataFrame.
        
        Args:
            collection: Name of the collection to query
            query: MongoDB query filter
            projection: Optional fields to include or exclude
            sort: Optional sorting criteria
            limit: Maximum number of documents to return (0 for no limit)
            skip: Number of documents to skip
            
        Returns:
            Pandas DataFrame containing the query results
        """
        if not self.is_initialized or not self.client or not self.db:
            raise Exception("MongoDB provider not initialized")
        
        try:
            # Execute query and get results
            results = await self.execute_query(collection, query, projection, sort, limit, skip)
            
            # Convert to DataFrame
            if results:
                return pd.DataFrame(results)
            else:
                return pd.DataFrame()
        
        except Exception as e:
            print(f"Error executing query to DataFrame: {str(e)}")
            raise
    
    async def insert_documents(self, collection: str, documents: List[Dict[str, Any]]) -> int:
        """
        Insert documents into a collection.
        
        Args:
            collection: Name of the collection
            documents: List of documents to insert
            
        Returns:
            Number of documents inserted
        """
        if not self.is_initialized or not self.client or not self.db:
            raise Exception("MongoDB provider not initialized")
        
        try:
            # Get collection
            coll = self.db[collection]
            
            # Insert documents
            if len(documents) == 1:
                result = coll.insert_one(documents[0])
                return 1 if result.acknowledged else 0
            else:
                result = coll.insert_many(documents)
                return len(result.inserted_ids) if result.acknowledged else 0
        
        except Exception as e:
            print(f"Error inserting documents: {str(e)}")
            raise
    
    async def update_documents(self, collection: str, query: Dict[str, Any], 
                              update: Dict[str, Any], upsert: bool = False,
                              multi: bool = True) -> int:
        """
        Update documents in a collection.
        
        Args:
            collection: Name of the collection
            query: MongoDB query filter
            update: Update operations
            upsert: Whether to insert if document doesn't exist
            multi: Whether to update multiple documents
            
        Returns:
            Number of documents updated
        """
        if not self.is_initialized or not self.client or not self.db:
            raise Exception("MongoDB provider not initialized")
        
        try:
            # Get collection
            coll = self.db[collection]
            
            # Update documents
            if multi:
                result = coll.update_many(query, update, upsert=upsert)
            else:
                result = coll.update_one(query, update, upsert=upsert)
            
            return result.modified_count
        
        except Exception as e:
            print(f"Error updating documents: {str(e)}")
            raise
    
    async def delete_documents(self, collection: str, query: Dict[str, Any], 
                              multi: bool = True) -> int:
        """
        Delete documents from a collection.
        
        Args:
            collection: Name of the collection
            query: MongoDB query filter
            multi: Whether to delete multiple documents
            
        Returns:
            Number of documents deleted
        """
        if not self.is_initialized or not self.client or not self.db:
            raise Exception("MongoDB provider not initialized")
        
        try:
            # Get collection
            coll = self.db[collection]
            
            # Delete documents
            if multi:
                result = coll.delete_many(query)
            else:
                result = coll.delete_one(query)
            
            return result.deleted_count
        
        except Exception as e:
            print(f"Error deleting documents: {str(e)}")
            raise
    
    async def count_documents(self, collection: str, query: Dict[str, Any]) -> int:
        """
        Count documents in a collection.
        
        Args:
            collection: Name of the collection
            query: MongoDB query filter
            
        Returns:
            Number of documents matching the query
        """
        if not self.is_initialized or not self.client or not self.db:
            raise Exception("MongoDB provider not initialized")
        
        try:
            # Get collection
            coll = self.db[collection]
            
            # Count documents
            return coll.count_documents(query)
        
        except Exception as e:
            print(f"Error counting documents: {str(e)}")
            raise
    
    async def aggregate(self, collection: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute an aggregation pipeline.
        
        Args:
            collection: Name of the collection
            pipeline: Aggregation pipeline stages
            
        Returns:
            List of dictionaries containing the aggregation results
        """
        if not self.is_initialized or not self.client or not self.db:
            raise Exception("MongoDB provider not initialized")
        
        try:
            # Get collection
            coll = self.db[collection]
            
            # Execute aggregation
            results = list(coll.aggregate(pipeline))
            
            # Convert ObjectId to string for JSON serialization
            for doc in results:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            return results
        
        except Exception as e:
            print(f"Error executing aggregation: {str(e)}")
            raise
    
    async def aggregate_to_dataframe(self, collection: str, 
                                    pipeline: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Execute an aggregation pipeline and return results as a pandas DataFrame.
        
        Args:
            collection: Name of the collection
            pipeline: Aggregation pipeline stages
            
        Returns:
            Pandas DataFrame containing the aggregation results
        """
        if not self.is_initialized or not self.client or not self.db:
            raise Exception("MongoDB provider not initialized")
        
        try:
            # Execute aggregation and get results
            results = await self.aggregate(collection, pipeline)
            
            # Convert to DataFrame
            if results:
                return pd.DataFrame(results)
            else:
                return pd.DataFrame()
        
        except Exception as e:
            print(f"Error executing aggregation to DataFrame: {str(e)}")
            raise
    
    async def get_collection_schema(self, collection: str, sample_size: int = 100) -> Dict[str, Any]:
        """
        Infer the schema of a collection by sampling documents.
        
        Args:
            collection: Name of the collection
            sample_size: Number of documents to sample
            
        Returns:
            Dictionary containing the inferred schema
        """
        if not self.is_initialized or not self.client or not self.db:
            raise Exception("MongoDB provider not initialized")
        
        try:
            # Get collection
            coll = self.db[collection]
            
            # Sample documents
            sample = list(coll.aggregate([
                {"$sample": {"size": sample_size}},
                {"$limit": sample_size}
            ]))
            
            if not sample:
                return {"fields": {}}
            
            # Infer schema from sample
            schema = {"fields": {}}
            
            for doc in sample:
                for field, value in doc.items():
                    if field not in schema["fields"]:
                        schema["fields"][field] = {"types": set(), "count": 0}
                    
                    schema["fields"][field]["types"].add(type(value).__name__)
                    schema["fields"][field]["count"] += 1
            
            # Convert sets to lists for JSON serialization
            for field in schema["fields"]:
                schema["fields"][field]["types"] = list(schema["fields"][field]["types"])
                schema["fields"][field]["frequency"] = schema["fields"][field]["count"] / len(sample)
                del schema["fields"][field]["count"]
            
            return schema
        
        except Exception as e:
            print(f"Error getting collection schema: {str(e)}")
            raise
    
    async def import_dataframe_to_collection(self, df: pd.DataFrame, collection: str, 
                                           drop_existing: bool = False) -> int:
        """
        Import a pandas DataFrame to a MongoDB collection.
        
        Args:
            df: Pandas DataFrame to import
            collection: Name of the target collection
            drop_existing: Whether to drop the existing collection
            
        Returns:
            Number of documents inserted
        """
        if not self.is_initialized or not self.client or not self.db:
            raise Exception("MongoDB provider not initialized")
        
        try:
            # Get collection
            coll = self.db[collection]
            
            # Drop existing collection if requested
            if drop_existing:
                coll.drop()
            
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            # Insert records
            if records:
                result = coll.insert_many(records)
                return len(result.inserted_ids)
            else:
                return 0
        
        except Exception as e:
            print(f"Error importing DataFrame to collection: {str(e)}")
            raise