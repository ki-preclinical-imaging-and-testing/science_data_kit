"""
Elasticsearch Provider for Science Data Kit

This module provides a provider for connecting to Elasticsearch databases, allowing
the Science Data Kit to interact with Elasticsearch document stores.
"""

import os
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ElasticsearchException

from ...providers.registry import BaseProvider, ProviderType


class ElasticsearchProvider(BaseProvider):
    """
    Provider for Elasticsearch database connections.

    This class provides functionality for connecting to Elasticsearch databases
    and executing queries against them.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Elasticsearch database provider.

        Args:
            config: Configuration dictionary containing connection details
                   Required keys:
                   - hosts: List of Elasticsearch hosts or single host string
                   
                   Optional:
                   - port: Elasticsearch port (default: 9200)
                   - username: Username for authentication (optional)
                   - password: Password for authentication (optional)
                   - api_key: API key for authentication (optional, alternative to username/password)
                   - cloud_id: Cloud ID for Elastic Cloud (optional)
                   - use_ssl: Use SSL/TLS (default: False)
                   - verify_certs: Verify SSL certificates (default: True)
                   - ca_certs: Path to CA certificate bundle
                   - client_cert: Path to client certificate
                   - client_key: Path to client key
                   - timeout: Connection timeout in seconds (default: 30)
                   - max_retries: Maximum number of retries (default: 3)
                   - retry_on_timeout: Retry on timeout (default: False)
        """
        super().__init__(config)
        self.client = None
        
    async def initialize(self) -> bool:
        """
        Initialize the Elasticsearch database connection.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Get connection parameters
            hosts = self.config.get('hosts')
            if not hosts:
                print("Elasticsearch hosts not provided")
                return False
            
            # Convert single host string to list if necessary
            if isinstance(hosts, str):
                hosts = [hosts]
            
            # Get optional parameters
            port = self.config.get('port', 9200)
            username = self.config.get('username')
            password = self.config.get('password')
            api_key = self.config.get('api_key')
            cloud_id = self.config.get('cloud_id')
            use_ssl = self.config.get('use_ssl', False)
            verify_certs = self.config.get('verify_certs', True)
            ca_certs = self.config.get('ca_certs')
            client_cert = self.config.get('client_cert')
            client_key = self.config.get('client_key')
            timeout = self.config.get('timeout', 30)
            max_retries = self.config.get('max_retries', 3)
            retry_on_timeout = self.config.get('retry_on_timeout', False)
            
            # Build connection parameters
            conn_params = {
                'hosts': hosts,
                'timeout': timeout,
                'max_retries': max_retries,
                'retry_on_timeout': retry_on_timeout
            }
            
            # Add authentication if provided
            if username and password:
                conn_params['http_auth'] = (username, password)
            elif api_key:
                conn_params['api_key'] = api_key
            
            # Add cloud ID if provided
            if cloud_id:
                conn_params['cloud_id'] = cloud_id
            
            # Add SSL/TLS if enabled
            if use_ssl:
                conn_params['use_ssl'] = True
                conn_params['verify_certs'] = verify_certs
                if ca_certs:
                    conn_params['ca_certs'] = ca_certs
                if client_cert:
                    conn_params['client_cert'] = client_cert
                if client_key:
                    conn_params['client_key'] = client_key
            
            # Initialize Elasticsearch client
            self.client = Elasticsearch(**conn_params)
            
            # Test connection
            info = self.client.info()
            
            self.is_initialized = True
            return True
        
        except Exception as e:
            print(f"Error initializing Elasticsearch provider: {str(e)}")
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
            # Test connection by getting cluster health
            health = self.client.cluster.health()
            return health['status'] in ['green', 'yellow']
        except Exception as e:
            print(f"Elasticsearch health check failed: {str(e)}")
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the provider.
        
        Returns:
            Dictionary of provider capabilities
        """
        capabilities = {
            "type": ProviderType.DATABASE.value,
            "name": "elasticsearch",
            "features": [
                "query",
                "schema_introspection",
                "data_export",
                "document_storage",
                "full_text_search",
                "aggregations",
                "geospatial_queries",
                "analytics"
            ],
            "supported_operations": [
                "search",
                "index",
                "update",
                "delete",
                "bulk",
                "aggregations",
                "count",
                "scroll"
            ]
        }
        
        return capabilities
    
    async def list_indices(self) -> List[Dict[str, Any]]:
        """
        List indices in the Elasticsearch cluster.
        
        Returns:
            List of index metadata dictionaries
        """
        if not self.is_initialized or not self.client:
            raise Exception("Elasticsearch provider not initialized")
        
        try:
            # Get all indices
            indices_info = self.client.indices.get('*')
            
            # Format the response
            indices = []
            for index_name, index_info in indices_info.items():
                # Get index stats
                stats = self.client.indices.stats(index=index_name)
                index_stats = stats['indices'].get(index_name, {})
                
                # Add index to the list
                indices.append({
                    "name": index_name,
                    "docs_count": index_stats.get('total', {}).get('docs', {}).get('count', 0),
                    "size_in_bytes": index_stats.get('total', {}).get('store', {}).get('size_in_bytes', 0),
                    "health": self.client.cluster.health(index=index_name).get('status', 'unknown'),
                    "settings": index_info.get('settings', {}),
                    "mappings": index_info.get('mappings', {})
                })
            
            return indices
        
        except Exception as e:
            print(f"Error listing indices: {str(e)}")
            raise
    
    async def search(self, index: str, query: Dict[str, Any], 
                    size: int = 10, from_: int = 0) -> Dict[str, Any]:
        """
        Execute a search query on an index.
        
        Args:
            index: Name of the index to query
            query: Elasticsearch query DSL
            size: Maximum number of documents to return
            from_: Starting offset for results
            
        Returns:
            Dictionary containing the search results
        """
        if not self.is_initialized or not self.client:
            raise Exception("Elasticsearch provider not initialized")
        
        try:
            # Execute search
            results = self.client.search(
                index=index,
                body=query,
                size=size,
                from_=from_
            )
            
            return results
        
        except Exception as e:
            print(f"Error executing search: {str(e)}")
            raise
    
    async def search_to_dataframe(self, index: str, query: Dict[str, Any],
                                 size: int = 10, from_: int = 0) -> pd.DataFrame:
        """
        Execute a search query and return results as a pandas DataFrame.
        
        Args:
            index: Name of the index to query
            query: Elasticsearch query DSL
            size: Maximum number of documents to return
            from_: Starting offset for results
            
        Returns:
            Pandas DataFrame containing the search results
        """
        if not self.is_initialized or not self.client:
            raise Exception("Elasticsearch provider not initialized")
        
        try:
            # Execute search
            results = await self.search(index, query, size, from_)
            
            # Extract hits
            hits = results.get('hits', {}).get('hits', [])
            
            # Convert to DataFrame
            if hits:
                # Extract _source from each hit
                docs = []
                for hit in hits:
                    doc = hit.get('_source', {})
                    # Add metadata fields
                    doc['_id'] = hit.get('_id')
                    doc['_score'] = hit.get('_score')
                    doc['_index'] = hit.get('_index')
                    docs.append(doc)
                
                return pd.DataFrame(docs)
            else:
                return pd.DataFrame()
        
        except Exception as e:
            print(f"Error executing search to DataFrame: {str(e)}")
            raise
    
    async def index_document(self, index: str, document: Dict[str, Any], 
                           doc_id: Optional[str] = None, refresh: bool = False) -> Dict[str, Any]:
        """
        Index a document in Elasticsearch.
        
        Args:
            index: Name of the index
            document: Document to index
            doc_id: Optional document ID
            refresh: Whether to refresh the index immediately
            
        Returns:
            Dictionary containing the indexing result
        """
        if not self.is_initialized or not self.client:
            raise Exception("Elasticsearch provider not initialized")
        
        try:
            # Index document
            if doc_id:
                result = self.client.index(
                    index=index,
                    id=doc_id,
                    body=document,
                    refresh=refresh
                )
            else:
                result = self.client.index(
                    index=index,
                    body=document,
                    refresh=refresh
                )
            
            return result
        
        except Exception as e:
            print(f"Error indexing document: {str(e)}")
            raise
    
    async def bulk_index(self, index: str, documents: List[Dict[str, Any]], 
                        id_field: Optional[str] = None, refresh: bool = False) -> Dict[str, Any]:
        """
        Bulk index documents into Elasticsearch.
        
        Args:
            index: Name of the index
            documents: List of documents to index
            id_field: Optional field to use as document ID
            refresh: Whether to refresh the index immediately
            
        Returns:
            Dictionary containing bulk indexing results
        """
        if not self.is_initialized or not self.client:
            raise Exception("Elasticsearch provider not initialized")
        
        try:
            # Prepare bulk actions
            actions = []
            for doc in documents:
                action = {
                    "_index": index,
                    "_source": doc
                }
                
                # Add ID if specified
                if id_field and id_field in doc:
                    action["_id"] = doc[id_field]
                
                actions.append(action)
            
            # Execute bulk operation
            result = helpers.bulk(self.client, actions, refresh=refresh)
            
            return {
                "took": 0,  # Not provided by helpers.bulk
                "errors": False,  # helpers.bulk raises an exception on error
                "items": [],  # Not provided by helpers.bulk
                "success": result[0],  # Number of successful operations
                "failed": result[1]  # Number of failed operations
            }
        
        except Exception as e:
            print(f"Error bulk indexing documents: {str(e)}")
            raise
    
    async def delete_document(self, index: str, doc_id: str, refresh: bool = False) -> Dict[str, Any]:
        """
        Delete a document from Elasticsearch.
        
        Args:
            index: Name of the index
            doc_id: Document ID to delete
            refresh: Whether to refresh the index immediately
            
        Returns:
            Dictionary containing the deletion result
        """
        if not self.is_initialized or not self.client:
            raise Exception("Elasticsearch provider not initialized")
        
        try:
            # Delete document
            result = self.client.delete(
                index=index,
                id=doc_id,
                refresh=refresh
            )
            
            return result
        
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            raise
    
    async def delete_by_query(self, index: str, query: Dict[str, Any], 
                            refresh: bool = False) -> Dict[str, Any]:
        """
        Delete documents matching a query.
        
        Args:
            index: Name of the index
            query: Elasticsearch query DSL
            refresh: Whether to refresh the index immediately
            
        Returns:
            Dictionary containing the deletion result
        """
        if not self.is_initialized or not self.client:
            raise Exception("Elasticsearch provider not initialized")
        
        try:
            # Delete by query
            result = self.client.delete_by_query(
                index=index,
                body=query,
                refresh=refresh
            )
            
            return result
        
        except Exception as e:
            print(f"Error deleting by query: {str(e)}")
            raise
    
    async def count_documents(self, index: str, query: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents in an index.
        
        Args:
            index: Name of the index
            query: Optional Elasticsearch query DSL
            
        Returns:
            Number of documents matching the query
        """
        if not self.is_initialized or not self.client:
            raise Exception("Elasticsearch provider not initialized")
        
        try:
            # Count documents
            if query:
                result = self.client.count(
                    index=index,
                    body=query
                )
            else:
                result = self.client.count(
                    index=index
                )
            
            return result.get('count', 0)
        
        except Exception as e:
            print(f"Error counting documents: {str(e)}")
            raise
    
    async def create_index(self, index: str, mappings: Dict[str, Any], 
                         settings: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create an index in Elasticsearch.
        
        Args:
            index: Name of the index
            mappings: Index mappings
            settings: Optional index settings
            
        Returns:
            True if index was created successfully, False otherwise
        """
        if not self.is_initialized or not self.client:
            raise Exception("Elasticsearch provider not initialized")
        
        try:
            # Prepare index creation body
            body = {
                "mappings": mappings
            }
            
            if settings:
                body["settings"] = settings
            
            # Create index
            result = self.client.indices.create(
                index=index,
                body=body
            )
            
            return result.get('acknowledged', False)
        
        except Exception as e:
            print(f"Error creating index: {str(e)}")
            raise
    
    async def delete_index(self, index: str) -> bool:
        """
        Delete an index from Elasticsearch.
        
        Args:
            index: Name of the index
            
        Returns:
            True if index was deleted successfully, False otherwise
        """
        if not self.is_initialized or not self.client:
            raise Exception("Elasticsearch provider not initialized")
        
        try:
            # Delete index
            result = self.client.indices.delete(
                index=index
            )
            
            return result.get('acknowledged', False)
        
        except Exception as e:
            print(f"Error deleting index: {str(e)}")
            raise
    
    async def get_index_mapping(self, index: str) -> Dict[str, Any]:
        """
        Get the mapping for an index.
        
        Args:
            index: Name of the index
            
        Returns:
            Dictionary containing the index mapping
        """
        if not self.is_initialized or not self.client:
            raise Exception("Elasticsearch provider not initialized")
        
        try:
            # Get mapping
            result = self.client.indices.get_mapping(
                index=index
            )
            
            return result
        
        except Exception as e:
            print(f"Error getting index mapping: {str(e)}")
            raise
    
    async def get_cluster_health(self) -> Dict[str, Any]:
        """
        Get Elasticsearch cluster health.
        
        Returns:
            Dictionary containing cluster health information
        """
        if not self.is_initialized or not self.client:
            raise Exception("Elasticsearch provider not initialized")
        
        try:
            # Get cluster health
            result = self.client.cluster.health()
            
            return result
        
        except Exception as e:
            print(f"Error getting cluster health: {str(e)}")
            raise
    
    async def import_dataframe_to_index(self, df: pd.DataFrame, index: str, 
                                      id_field: Optional[str] = None,
                                      drop_existing: bool = False,
                                      refresh: bool = False) -> Dict[str, Any]:
        """
        Import a pandas DataFrame to an Elasticsearch index.
        
        Args:
            df: Pandas DataFrame to import
            index: Name of the target index
            id_field: Optional field to use as document ID
            drop_existing: Whether to drop the existing index
            refresh: Whether to refresh the index immediately
            
        Returns:
            Dictionary containing bulk indexing results
        """
        if not self.is_initialized or not self.client:
            raise Exception("Elasticsearch provider not initialized")
        
        try:
            # Drop existing index if requested
            if drop_existing:
                try:
                    self.client.indices.delete(index=index)
                except Exception:
                    # Ignore if index doesn't exist
                    pass
            
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            # Bulk index records
            return await self.bulk_index(index, records, id_field, refresh)
        
        except Exception as e:
            print(f"Error importing DataFrame to index: {str(e)}")
            raise