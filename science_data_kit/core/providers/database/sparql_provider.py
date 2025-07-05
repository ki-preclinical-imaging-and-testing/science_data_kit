"""
SPARQL Provider for Science Data Kit

This module provides a provider for connecting to SPARQL endpoints, allowing
the Science Data Kit to interact with RDF data stores.
"""

import os
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET

from ...providers.registry import BaseProvider, ProviderType


class SPARQLProvider(BaseProvider):
    """
    Provider for SPARQL endpoint connections.

    This class provides functionality for connecting to SPARQL endpoints
    and executing queries against them.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the SPARQL endpoint provider.

        Args:
            config: Configuration dictionary containing connection details
                   Required keys:
                   - endpoint_url: URL of the SPARQL endpoint
                   
                   Optional:
                   - default_graph: Default graph URI
                   - username: Username for authentication (optional)
                   - password: Password for authentication (optional)
                   - timeout: Query timeout in seconds (default: 60)
                   - user_agent: User agent string (default: "Science Data Kit SPARQL Client")
                   - method: HTTP method to use (GET or POST, default: POST)
                   - return_format: Return format (default: JSON)
        """
        super().__init__(config)
        self.sparql = None
        self.endpoint_url = config.get('endpoint_url')
        
    async def initialize(self) -> bool:
        """
        Initialize the SPARQL endpoint connection.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Check if endpoint URL is provided
            if not self.endpoint_url:
                print("SPARQL endpoint URL not provided")
                return False
            
            # Initialize SPARQLWrapper
            self.sparql = SPARQLWrapper(self.endpoint_url)
            
            # Set default graph if provided
            default_graph = self.config.get('default_graph')
            if default_graph:
                self.sparql.addDefaultGraph(default_graph)
            
            # Set authentication if provided
            username = self.config.get('username')
            password = self.config.get('password')
            if username and password:
                self.sparql.setCredentials(username, password)
            
            # Set timeout
            timeout = self.config.get('timeout', 60)
            self.sparql.setTimeout(timeout)
            
            # Set user agent
            user_agent = self.config.get('user_agent', "Science Data Kit SPARQL Client")
            self.sparql.addCustomHttpHeader("User-Agent", user_agent)
            
            # Set method
            method = self.config.get('method', 'POST')
            if method.upper() == 'GET':
                self.sparql.setMethod(GET)
            else:
                self.sparql.setMethod(POST)
            
            # Set return format
            self.sparql.setReturnFormat(JSON)
            
            # Test connection with a simple query
            self.sparql.setQuery("SELECT * WHERE { ?s ?p ?o } LIMIT 1")
            results = self.sparql.query().convert()
            
            self.is_initialized = True
            return True
        
        except Exception as e:
            print(f"Error initializing SPARQL provider: {str(e)}")
            self.is_initialized = False
            return False
    
    async def health_check(self) -> bool:
        """
        Check if the SPARQL endpoint connection is healthy.
        
        Returns:
            True if the connection is healthy, False otherwise
        """
        if not self.is_initialized or not self.sparql:
            return False
        
        try:
            # Test connection with a simple query
            self.sparql.setQuery("SELECT * WHERE { ?s ?p ?o } LIMIT 1")
            self.sparql.query().convert()
            return True
        except Exception as e:
            print(f"SPARQL endpoint health check failed: {str(e)}")
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the provider.
        
        Returns:
            Dictionary of provider capabilities
        """
        capabilities = {
            "type": ProviderType.DATABASE.value,
            "name": "sparql",
            "features": [
                "query",
                "schema_introspection",
                "data_export",
                "rdf_data",
                "semantic_web",
                "inference",
                "ontology_support"
            ],
            "supported_operations": [
                "select",
                "construct",
                "ask",
                "describe",
                "update"
            ]
        }
        
        return capabilities
    
    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SPARQL query on the endpoint.
        
        Args:
            query: SPARQL query to execute
            parameters: Optional parameters for the query
            
        Returns:
            List of dictionaries containing the query results
        """
        if not self.is_initialized or not self.sparql:
            raise Exception("SPARQL provider not initialized")
        
        try:
            # Apply parameters if provided
            if parameters:
                for key, value in parameters.items():
                    # Simple string replacement for parameters
                    # In a production environment, this should be more sophisticated
                    query = query.replace(f"${key}", f'"{value}"')
            
            # Set query
            self.sparql.setQuery(query)
            
            # Determine query type
            query_type = query.strip().upper().split(maxsplit=1)[0]
            
            # Execute query
            if query_type in ['SELECT', 'ASK']:
                self.sparql.setReturnFormat(JSON)
                results = self.sparql.query().convert()
                
                if query_type == 'ASK':
                    # ASK queries return a boolean
                    return [{"result": results["boolean"]}]
                else:
                    # SELECT queries return a list of bindings
                    bindings = results["results"]["bindings"]
                    
                    # Convert to a list of dictionaries
                    processed_results = []
                    for binding in bindings:
                        processed_binding = {}
                        for var, value in binding.items():
                            processed_binding[var] = value["value"]
                        processed_results.append(processed_binding)
                    
                    return processed_results
            else:
                # For CONSTRUCT and DESCRIBE queries, return the raw results
                # In a production environment, this should be more sophisticated
                results = self.sparql.query().convert()
                return [{"result": results}]
        
        except Exception as e:
            print(f"Error executing SPARQL query: {str(e)}")
            raise
    
    async def query_to_dataframe(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a SPARQL query and return results as a pandas DataFrame.
        
        Args:
            query: SPARQL query to execute
            parameters: Optional parameters for the query
            
        Returns:
            Pandas DataFrame containing the query results
        """
        if not self.is_initialized or not self.sparql:
            raise Exception("SPARQL provider not initialized")
        
        try:
            # Execute query and get results
            results = await self.execute_query(query, parameters)
            
            # Convert to DataFrame
            if results:
                return pd.DataFrame(results)
            else:
                return pd.DataFrame()
        
        except Exception as e:
            print(f"Error executing SPARQL query to DataFrame: {str(e)}")
            raise
    
    async def get_endpoint_info(self) -> Dict[str, Any]:
        """
        Get information about the SPARQL endpoint.
        
        Returns:
            Dictionary containing endpoint information
        """
        if not self.is_initialized or not self.sparql:
            raise Exception("SPARQL provider not initialized")
        
        try:
            # Query for endpoint information
            query = """
            SELECT ?property ?value
            WHERE {
                ?s ?property ?value .
                FILTER(STRSTARTS(STR(?property), "http://www.w3.org/ns/sparql-service-description#"))
            }
            LIMIT 100
            """
            
            results = await self.execute_query(query)
            
            # Process results
            info = {
                "endpoint_url": self.endpoint_url,
                "properties": {}
            }
            
            for result in results:
                property_uri = result.get("property", "")
                property_name = property_uri.split("#")[-1] if "#" in property_uri else property_uri
                info["properties"][property_name] = result.get("value", "")
            
            return info
        
        except Exception as e:
            print(f"Error getting endpoint info: {str(e)}")
            # Return basic info if detailed info is not available
            return {
                "endpoint_url": self.endpoint_url,
                "properties": {}
            }
    
    async def list_graphs(self) -> List[str]:
        """
        List all named graphs in the SPARQL endpoint.
        
        Returns:
            List of graph URIs
        """
        if not self.is_initialized or not self.sparql:
            raise Exception("SPARQL provider not initialized")
        
        try:
            # Query for named graphs
            query = """
            SELECT DISTINCT ?g
            WHERE {
                GRAPH ?g { ?s ?p ?o }
            }
            ORDER BY ?g
            """
            
            results = await self.execute_query(query)
            
            # Extract graph URIs
            graphs = [result.get("g", "") for result in results if "g" in result]
            return graphs
        
        except Exception as e:
            print(f"Error listing graphs: {str(e)}")
            raise
    
    async def count_triples(self, graph_uri: Optional[str] = None) -> int:
        """
        Count triples in the SPARQL endpoint.
        
        Args:
            graph_uri: Optional URI of the named graph to count triples in
            
        Returns:
            Number of triples
        """
        if not self.is_initialized or not self.sparql:
            raise Exception("SPARQL provider not initialized")
        
        try:
            # Construct query based on whether a graph URI is provided
            if graph_uri:
                query = f"""
                SELECT (COUNT(*) AS ?count)
                WHERE {{
                    GRAPH <{graph_uri}> {{ ?s ?p ?o }}
                }}
                """
            else:
                query = """
                SELECT (COUNT(*) AS ?count)
                WHERE {
                    ?s ?p ?o
                }
                """
            
            results = await self.execute_query(query)
            
            # Extract count
            if results and "count" in results[0]:
                return int(results[0]["count"])
            else:
                return 0
        
        except Exception as e:
            print(f"Error counting triples: {str(e)}")
            raise
    
    async def list_classes(self, graph_uri: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all classes in the SPARQL endpoint.
        
        Args:
            graph_uri: Optional URI of the named graph to list classes from
            
        Returns:
            List of dictionaries containing class information
        """
        if not self.is_initialized or not self.sparql:
            raise Exception("SPARQL provider not initialized")
        
        try:
            # Construct query based on whether a graph URI is provided
            if graph_uri:
                query = f"""
                SELECT DISTINCT ?class ?label ?comment (COUNT(?instance) AS ?instanceCount)
                WHERE {{
                    GRAPH <{graph_uri}> {{
                        ?class a <http://www.w3.org/2000/01/rdf-schema#Class> .
                        OPTIONAL {{ ?class <http://www.w3.org/2000/01/rdf-schema#label> ?label }}
                        OPTIONAL {{ ?class <http://www.w3.org/2000/01/rdf-schema#comment> ?comment }}
                        OPTIONAL {{ ?instance a ?class }}
                    }}
                }}
                GROUP BY ?class ?label ?comment
                ORDER BY ?class
                """
            else:
                query = """
                SELECT DISTINCT ?class ?label ?comment (COUNT(?instance) AS ?instanceCount)
                WHERE {
                    ?class a <http://www.w3.org/2000/01/rdf-schema#Class> .
                    OPTIONAL { ?class <http://www.w3.org/2000/01/rdf-schema#label> ?label }
                    OPTIONAL { ?class <http://www.w3.org/2000/01/rdf-schema#comment> ?comment }
                    OPTIONAL { ?instance a ?class }
                }
                GROUP BY ?class ?label ?comment
                ORDER BY ?class
                """
            
            results = await self.execute_query(query)
            return results
        
        except Exception as e:
            print(f"Error listing classes: {str(e)}")
            raise
    
    async def list_properties(self, class_uri: Optional[str] = None, graph_uri: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all properties in the SPARQL endpoint.
        
        Args:
            class_uri: Optional URI of the class to list properties for
            graph_uri: Optional URI of the named graph to list properties from
            
        Returns:
            List of dictionaries containing property information
        """
        if not self.is_initialized or not self.sparql:
            raise Exception("SPARQL provider not initialized")
        
        try:
            # Construct query based on parameters
            if class_uri and graph_uri:
                query = f"""
                SELECT DISTINCT ?property ?label ?comment ?domain ?range
                WHERE {{
                    GRAPH <{graph_uri}> {{
                        ?property a <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> .
                        ?property <http://www.w3.org/2000/01/rdf-schema#domain> <{class_uri}> .
                        OPTIONAL {{ ?property <http://www.w3.org/2000/01/rdf-schema#label> ?label }}
                        OPTIONAL {{ ?property <http://www.w3.org/2000/01/rdf-schema#comment> ?comment }}
                        OPTIONAL {{ ?property <http://www.w3.org/2000/01/rdf-schema#domain> ?domain }}
                        OPTIONAL {{ ?property <http://www.w3.org/2000/01/rdf-schema#range> ?range }}
                    }}
                }}
                ORDER BY ?property
                """
            elif class_uri:
                query = f"""
                SELECT DISTINCT ?property ?label ?comment ?domain ?range
                WHERE {{
                    ?property a <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> .
                    ?property <http://www.w3.org/2000/01/rdf-schema#domain> <{class_uri}> .
                    OPTIONAL {{ ?property <http://www.w3.org/2000/01/rdf-schema#label> ?label }}
                    OPTIONAL {{ ?property <http://www.w3.org/2000/01/rdf-schema#comment> ?comment }}
                    OPTIONAL {{ ?property <http://www.w3.org/2000/01/rdf-schema#domain> ?domain }}
                    OPTIONAL {{ ?property <http://www.w3.org/2000/01/rdf-schema#range> ?range }}
                }}
                ORDER BY ?property
                """
            elif graph_uri:
                query = f"""
                SELECT DISTINCT ?property ?label ?comment ?domain ?range
                WHERE {{
                    GRAPH <{graph_uri}> {{
                        ?property a <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> .
                        OPTIONAL {{ ?property <http://www.w3.org/2000/01/rdf-schema#label> ?label }}
                        OPTIONAL {{ ?property <http://www.w3.org/2000/01/rdf-schema#comment> ?comment }}
                        OPTIONAL {{ ?property <http://www.w3.org/2000/01/rdf-schema#domain> ?domain }}
                        OPTIONAL {{ ?property <http://www.w3.org/2000/01/rdf-schema#range> ?range }}
                    }}
                }}
                ORDER BY ?property
                """
            else:
                query = """
                SELECT DISTINCT ?property ?label ?comment ?domain ?range
                WHERE {
                    ?property a <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> .
                    OPTIONAL { ?property <http://www.w3.org/2000/01/rdf-schema#label> ?label }
                    OPTIONAL { ?property <http://www.w3.org/2000/01/rdf-schema#comment> ?comment }
                    OPTIONAL { ?property <http://www.w3.org/2000/01/rdf-schema#domain> ?domain }
                    OPTIONAL { ?property <http://www.w3.org/2000/01/rdf-schema#range> ?range }
                }
                ORDER BY ?property
                """
            
            results = await self.execute_query(query)
            return results
        
        except Exception as e:
            print(f"Error listing properties: {str(e)}")
            raise