"""
ISA Tools Plugin for Science Data Kit

This module provides a plugin implementation for the ISA Tools platform,
adapting the existing ISAToolsProvider to use the new plugin architecture.

This serves as an example of how to convert an existing integration provider
to use the plugin architecture.
"""

import rdflib
from typing import Dict, List, Optional, Any, Tuple, Union

from science_data_kit.core.integrations.plugin_architecture import (
    PlatformPlugin, PluginMetadata, PluginCategory, register_plugin
)
from science_data_kit.core.integrations.isa_tools_provider import ISAToolsProvider


@register_plugin
class ISAToolsPlugin(PlatformPlugin):
    """
    Plugin for integrating with the ISA Tools platform.
    
    This plugin adapts the existing ISAToolsProvider to use the new plugin architecture,
    serving as an example of how to convert existing providers to plugins.
    """
    
    def __init__(self):
        """Initialize the ISA Tools plugin."""
        self._provider = None
        self._authenticated = False
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get the plugin metadata."""
        return PluginMetadata(
            name="isa_tools",
            version="1.0.0",
            description="Integration with the ISA Tools platform for experimental metadata",
            author="Science Data Kit Team",
            category=PluginCategory.PLATFORM,
            dependencies=["requests", "rdflib"],
            tags=["isa", "metadata", "ontology"]
        )
    
    def initialize(self) -> bool:
        """
        Initialize the plugin.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        try:
            # Create the provider instance
            self._provider = ISAToolsProvider()
            return True
        except Exception as e:
            print(f"Failed to initialize ISA Tools plugin: {str(e)}")
            return False
    
    def shutdown(self) -> bool:
        """
        Shut down the plugin and release any resources.
        
        Returns:
            True if shutdown was successful, False otherwise.
        """
        self._provider = None
        self._authenticated = False
        return True
    
    def authenticate(self, base_url: Optional[str] = None, api_key: Optional[str] = None, **kwargs) -> bool:
        """
        Authenticate with the ISA Tools platform.
        
        Args:
            base_url: The base URL of the ISA Tools API.
            api_key: The API key for authenticating with ISA Tools API.
            **kwargs: Additional authentication parameters.
            
        Returns:
            True if authentication was successful, False otherwise.
        """
        try:
            # Re-initialize the provider with authentication parameters
            self._provider = ISAToolsProvider(base_url=base_url, api_key=api_key)
            self._authenticated = True
            return True
        except Exception as e:
            print(f"Failed to authenticate with ISA Tools: {str(e)}")
            self._authenticated = False
            return False
    
    def is_authenticated(self) -> bool:
        """
        Check if the plugin is currently authenticated with the platform.
        
        Returns:
            True if authenticated, False otherwise.
        """
        return self._authenticated
    
    def get_resources(self, resource_type: str, **kwargs) -> Any:
        """
        Get resources from the ISA Tools platform.
        
        Args:
            resource_type: The type of resources to get.
            **kwargs: Additional parameters for the request.
            
        Returns:
            The retrieved resources.
            
        Raises:
            ValueError: If the resource type is not supported.
        """
        if not self._provider:
            raise RuntimeError("ISA Tools plugin is not initialized")
        
        if resource_type == "ontology":
            url = kwargs.get("url")
            destination_path = kwargs.get("destination_path")
            if not url:
                raise ValueError("URL is required for ontology resources")
            
            success, result = self._provider.import_ontology(url, destination_path)
            if not success:
                raise ValueError(f"Failed to import ontology: {result}")
            
            return result
        
        elif resource_type == "isa_json":
            file_path = kwargs.get("file_path")
            if not file_path:
                raise ValueError("File path is required for ISA JSON resources")
            
            success, result = self._provider.import_isa_json(file_path)
            if not success:
                raise ValueError(f"Failed to import ISA JSON: {result}")
            
            return result
        
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
    
    # Additional methods that provide access to the underlying provider functionality
    
    def import_ontology(self, url: str, destination_path: Optional[str] = None) -> Tuple[bool, Union[rdflib.Graph, str]]:
        """
        Import an RDF/OWL ontology from a URL.
        
        Args:
            url: The URL of the ontology to import.
            destination_path: Optional path to save the ontology file.
            
        Returns:
            A tuple containing (success, result).
            - success: True if the import was successful, False otherwise.
            - result: The imported ontology graph if successful, or an error message if not.
        """
        if not self._provider:
            return False, "ISA Tools plugin is not initialized"
        
        return self._provider.import_ontology(url, destination_path)
    
    def select_ontology_subset(self, graph: rdflib.Graph, root_nodes: List[str], max_depth: int = 3) -> Tuple[bool, Union[rdflib.Graph, str]]:
        """
        Select a subset of an ontology based on root nodes and maximum depth.
        
        Args:
            graph: The ontology graph.
            root_nodes: List of root node URIs to include in the subset.
            max_depth: Maximum depth of relationships to include.
            
        Returns:
            A tuple containing (success, result).
            - success: True if the selection was successful, False otherwise.
            - result: The selected ontology subset if successful, or an error message if not.
        """
        if not self._provider:
            return False, "ISA Tools plugin is not initialized"
        
        return self._provider.select_ontology_subset(graph, root_nodes, max_depth)
    
    def export_ontology(self, graph: rdflib.Graph, destination_path: str, format: str = "xml") -> Tuple[bool, str]:
        """
        Export an ontology graph to a file.
        
        Args:
            graph: The ontology graph to export.
            destination_path: Path to save the ontology file.
            format: Format to use for the export (xml, turtle, n3, etc.).
            
        Returns:
            A tuple containing (success, message).
            - success: True if the export was successful, False otherwise.
            - message: A message describing the result.
        """
        if not self._provider:
            return False, "ISA Tools plugin is not initialized"
        
        return self._provider.export_ontology(graph, destination_path, format)
    
    def import_isa_json(self, file_path: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        Import ISA metadata from a JSON file.
        
        Args:
            file_path: The path to the ISA JSON file.
            
        Returns:
            A tuple containing (success, result).
            - success: True if the import was successful, False otherwise.
            - result: The imported metadata if successful, or an error message if not.
        """
        if not self._provider:
            return False, "ISA Tools plugin is not initialized"
        
        return self._provider.import_isa_json(file_path)
    
    def search(self, query: str, data: Dict[str, Any]) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Search for resources in ISA metadata.
        
        Args:
            query: The search query.
            data: The data to search in.
            
        Returns:
            A tuple containing (success, result).
            - success: True if the search was successful, False otherwise.
            - result: The search results if successful, or an error message if not.
        """
        if not self._provider:
            return False, "ISA Tools plugin is not initialized"
        
        return self._provider.search(query, data)
    
    def import_to_neo4j(self, data: Dict[str, Any], db_manager: Any) -> Tuple[bool, str]:
        """
        Import ISA metadata into Neo4j.
        
        Args:
            data: The ISA metadata to import.
            db_manager: The Neo4j database manager to use for importing.
            
        Returns:
            A tuple containing (success, message).
            - success: True if the import was successful, False otherwise.
            - message: A message describing the result.
        """
        if not self._provider:
            return False, "ISA Tools plugin is not initialized"
        
        return self._provider.import_to_neo4j(data, db_manager)
    
    def import_ontology_to_neo4j(self, graph: rdflib.Graph, db_manager: Any) -> Tuple[bool, str]:
        """
        Import an ontology graph into Neo4j.
        
        Args:
            graph: The ontology graph to import.
            db_manager: The Neo4j database manager to use for importing.
            
        Returns:
            A tuple containing (success, message).
            - success: True if the import was successful, False otherwise.
            - message: A message describing the result.
        """
        if not self._provider:
            return False, "ISA Tools plugin is not initialized"
        
        return self._provider.import_ontology_to_neo4j(graph, db_manager)
    
    def process_and_import(self, file_path: str, db_manager: Any) -> Tuple[bool, str]:
        """
        Process an ISA JSON file and import it into Neo4j.
        
        This is a convenience method that combines import_isa_json and import_to_neo4j.
        
        Args:
            file_path: The path to the ISA JSON file.
            db_manager: The Neo4j database manager to use for importing.
            
        Returns:
            A tuple containing (success, message).
            - success: True if the process was successful, False otherwise.
            - message: A message describing the result.
        """
        if not self._provider:
            return False, "ISA Tools plugin is not initialized"
        
        return self._provider.process_and_import(file_path, db_manager)