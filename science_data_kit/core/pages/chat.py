"""
Chat Page Module for Science Data Kit Core

This module provides the core functionality for the Chat page,
allowing users to chat with their data using retrieval-augmented generation.
"""

import time
import datetime
import uuid
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import json
import requests

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import ChatPageData
from science_data_kit.core.db.db_manager import Neo4jManager, load_db_config

# Try to import GraphRAG
try:
    from neo4j import GraphDatabase
    from neo4j_graphrag.generation import GraphRAG
    from neo4j_graphrag.retrievers import VectorRetriever, Text2CypherRetriever
    from neo4j_graphrag.embeddings import OpenAIEmbeddings, OllamaEmbeddings
    from neo4j_graphrag.llm import OpenAILLM, OllamaLLM
    GRAPHRAG_AVAILABLE = True
except ImportError:
    GRAPHRAG_AVAILABLE = False

def get_ollama_models(base_url="http://localhost:11434"):
    """
    Get a list of available models from Ollama API.

    Args:
        base_url (str): The base URL for the Ollama API

    Returns:
        list: A list of available model names
    """
    try:
        response = requests.get(f"{base_url}/api/tags")
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            # Extract model names from the response
            model_names = [model.get("name") for model in models_data if model.get("name")]
            return model_names
        else:
            return ["llama2", "mistral", "mixtral", "phi"]  # Fallback to default models
    except Exception as e:
        return ["llama2", "mistral", "mixtral", "phi"]  # Fallback to default models

class ChatPage(BasePage):
    """
    Core functionality for the Chat page.
    
    This class provides the backend functionality for chatting with data using
    retrieval-augmented generation (GraphRAG).
    """
    
    def __init__(self):
        """Initialize the Chat page."""
        super().__init__()
        self.title = "Chat with your data"
        self.icon = "💬"
        
        # Initialize LLM settings
        self.llm_provider = "OpenAI"
        self.llm_api_key = ""
        self.llm_model = "gpt-3.5-turbo"
        self.llm_temperature = 0.7
        self.llm_max_tokens = 1000
        
        # Initialize Ollama-specific settings
        self.ollama_base_url = "http://localhost:11434"
        self.ollama_auth_enabled = False
        self.ollama_username = ""
        self.ollama_password = ""
        self.ollama_available_models = ["llama2", "mistral", "mixtral", "phi"]
        
        # Try to refresh models on startup
        try:
            available_models = get_ollama_models(self.ollama_base_url)
            if available_models:
                self.ollama_available_models = available_models
        except:
            # Silently fail if Ollama is not available
            pass
        
        # Initialize Neo4j connection settings
        self.neo4j_uri = ""
        self.neo4j_user = ""
        self.neo4j_password = ""
        self.neo4j_database = ""
        self.neo4j_schema = None
        
        # Initialize connection status
        self.connection_status = {}
        self.connection_errors = {}
        
        # Initialize chat history
        self.chat_history = []
        
        # Initialize GraphRAG
        self.graph_rag = None
        
    def get_page_data(self) -> ChatPageData:
        """
        Return data needed to render the Chat page.
        
        Returns:
            An instance of ChatPageData containing the data needed
            to render the page.
        """
        # Create page data
        page_data = ChatPageData(
            title=self.title,
            chat_history=self.chat_history,
            llm_provider=self.llm_provider,
            llm_api_key=self.llm_api_key,
            llm_model=self.llm_model,
            llm_temperature=self.llm_temperature,
            llm_max_tokens=self.llm_max_tokens,
            ollama_base_url=self.ollama_base_url,
            ollama_auth_enabled=self.ollama_auth_enabled,
            ollama_username=self.ollama_username,
            ollama_password=self.ollama_password,
            ollama_available_models=self.ollama_available_models,
            neo4j_uri=self.neo4j_uri,
            neo4j_user=self.neo4j_user,
            neo4j_password=self.neo4j_password,
            neo4j_database=self.neo4j_database,
            neo4j_schema=self.neo4j_schema,
            connection_status=self.connection_status,
            connection_errors=self.connection_errors,
            graphrag_available=GRAPHRAG_AVAILABLE
        )
        
        return page_data
    
    def connect_to_neo4j(self, uri: str, user: str, password: str, database: str) -> Dict[str, Any]:
        """
        Connect to Neo4j database.
        
        Args:
            uri: Neo4j URI
            user: Neo4j username
            password: Neo4j password
            database: Neo4j database name
            
        Returns:
            A dictionary with the result of the operation.
        """
        try:
            neo4j_config = {
                "uri": uri,
                "user": user,
                "password": password,
                "database": database
            }
            
            # Create a new connection
            manager = Neo4jManager(**neo4j_config)
            
            # Test the connection
            if manager.test_connection():
                self.neo4j_uri = uri
                self.neo4j_user = user
                self.neo4j_password = password
                self.neo4j_database = database
                self.connection_status["neo4j"] = True
                
                # Fetch available labels from Neo4j
                try:
                    labels = manager.fetch_labels()
                    
                    # Extract schema from the database
                    try:
                        # Get relationships between labels
                        query = """
                        MATCH (a)-[r]->(b)
                        RETURN DISTINCT labels(a)[0] AS source, type(r) AS relationship, labels(b)[0] AS target
                        """
                        results = manager.execute_query(query)
                        
                        # Convert to triples
                        triples = set()
                        for record in results:
                            if record["source"] and record["relationship"] and record["target"]:
                                triples.add((record["source"], record["relationship"], record["target"]))
                        
                        # Generate schema
                        schema = self._schema_from_triples(labels, triples)
                        self.neo4j_schema = schema
                        
                        return {"success": True, "message": "Successfully connected to Neo4j and extracted schema"}
                    except Exception as e:
                        self.connection_errors["neo4j_schema"] = str(e)
                        return {"success": True, "message": "Connected to Neo4j but couldn't extract schema", "warning": str(e)}
                except Exception as e:
                    self.connection_errors["neo4j_labels"] = str(e)
                    return {"success": True, "message": "Connected to Neo4j but couldn't fetch labels", "warning": str(e)}
            else:
                self.connection_status["neo4j"] = False
                self.connection_errors["neo4j"] = "Failed to connect to Neo4j"
                return {"success": False, "error": "Failed to connect to Neo4j"}
        except Exception as e:
            self.connection_status["neo4j"] = False
            self.connection_errors["neo4j"] = str(e)
            return {"success": False, "error": f"Error connecting to Neo4j: {str(e)}"}
    
    def initialize_graph_rag(self) -> Dict[str, Any]:
        """
        Initialize GraphRAG with current settings.
        
        Returns:
            A dictionary with the result of the operation.
        """
        if not GRAPHRAG_AVAILABLE:
            return {"success": False, "error": "GraphRAG is not available. Please install the required packages."}
        
        if not self.neo4j_uri or not self.neo4j_user or not self.neo4j_password:
            return {"success": False, "error": "Neo4j connection is required to initialize GraphRAG."}
        
        try:
            # Create a connection pool for Neo4j
            driver = GraphDatabase.driver(
                self.neo4j_uri, 
                auth=(self.neo4j_user, self.neo4j_password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=60
            )
            
            # Get schema from session state
            schema = self.neo4j_schema
            
            # Initialize Text2Cypher retriever with schema
            if schema:
                retriever_type = "Text2Cypher"
            else:
                # Fall back to VectorRetriever if schema extraction fails
                retriever = VectorRetriever(driver)
                retriever_type = "Vector"
            
            # Initialize GraphRAG with the appropriate LLM based on provider
            if self.llm_provider == "OpenAI" and self.llm_api_key:
                llm = OpenAILLM(api_key=self.llm_api_key, model_name=self.llm_model,
                                model_params={
                                    'temperature': self.llm_temperature,
                                    'max_tokens': self.llm_max_tokens
                                })
                examples = ["""
                USER INPUT: 'Which actors starred in the Matrix?' 
                QUERY: MATCH (p:Person)-[:ACTED_IN]->(m:Movie) WHERE m.title = 'The Matrix' RETURN p.name
                """]
                retriever = Text2CypherRetriever(driver, neo4j_schema=schema, llm=llm, examples=examples)
                self.graph_rag = GraphRAG(retriever, llm=llm)
                return {"success": True, "message": "GraphRAG initialized with OpenAI LLM", "retriever_type": retriever_type}
            elif self.llm_provider == "Anthropic" and self.llm_api_key:
                try:
                    from neo4j_graphrag.llm import AnthropicLLM
                    llm = AnthropicLLM(api_key=self.llm_api_key, model=self.llm_model or "claude-2")
                    embeddings = None  # Use default embeddings
                    self.graph_rag = GraphRAG(retriever, llm=llm, embeddings=embeddings)
                    return {"success": True, "message": "GraphRAG initialized with Anthropic LLM", "retriever_type": retriever_type}
                except ImportError:
                    return {"success": False, "error": "Anthropic LLM is not available. Please install the required packages."}
            elif self.llm_provider == "Ollama":
                # Configure Ollama with authentication if enabled
                ollama_config = {
                    "base_url": self.ollama_base_url,
                    "model": self.llm_model or "llama2"
                }
                
                if self.ollama_auth_enabled and self.ollama_username and self.ollama_password:
                    ollama_config["auth"] = (self.ollama_username, self.ollama_password)
                
                # Initialize Ollama LLM and embeddings with the configuration
                try:
                    llm = OllamaLLM(**ollama_config)
                    # Use the same model for embeddings as for LLM by default
                    embeddings = OllamaEmbeddings(model=self.llm_model or "llama2", base_url=self.ollama_base_url)
                    if self.ollama_auth_enabled and self.ollama_username and self.ollama_password:
                        # Set auth for embeddings if supported
                        try:
                            embeddings.client.auth = (self.ollama_username, self.ollama_password)
                        except:
                            pass
                    
                    self.graph_rag = GraphRAG(retriever, llm=llm, embeddings=embeddings)
                    return {"success": True, "message": "GraphRAG initialized with Ollama LLM", "retriever_type": retriever_type}
                except Exception as e:
                    return {"success": False, "error": f"Error initializing Ollama: {str(e)}"}
            else:
                # Default to a basic GraphRAG instance
                self.graph_rag = GraphRAG(retriever)
                return {"success": True, "message": "GraphRAG initialized with default settings", "retriever_type": retriever_type}
        except Exception as e:
            return {"success": False, "error": f"Error initializing GraphRAG: {str(e)}"}
    
    def update_llm_settings(self, provider: str, api_key: Optional[str], model: str, 
                           temperature: float, max_tokens: int) -> Dict[str, Any]:
        """
        Update LLM settings.
        
        Args:
            provider: LLM provider (OpenAI, Anthropic, Ollama)
            api_key: API key for the LLM provider
            model: Model name for the LLM provider
            temperature: Temperature for the LLM
            max_tokens: Maximum tokens for the LLM
            
        Returns:
            A dictionary with the result of the operation.
        """
        try:
            self.llm_provider = provider
            self.llm_api_key = api_key
            self.llm_model = model
            self.llm_temperature = temperature
            self.llm_max_tokens = max_tokens
            
            return {"success": True, "message": "LLM settings updated successfully"}
        except Exception as e:
            return {"success": False, "error": f"Error updating LLM settings: {str(e)}"}
    
    def update_ollama_settings(self, base_url: str, auth_enabled: bool, 
                              username: Optional[str], password: Optional[str]) -> Dict[str, Any]:
        """
        Update Ollama settings.
        
        Args:
            base_url: Base URL for the Ollama API
            auth_enabled: Whether authentication is enabled
            username: Username for authentication
            password: Password for authentication
            
        Returns:
            A dictionary with the result of the operation.
        """
        try:
            self.ollama_base_url = base_url
            self.ollama_auth_enabled = auth_enabled
            self.ollama_username = username if auth_enabled else ""
            self.ollama_password = password if auth_enabled else ""
            
            return {"success": True, "message": "Ollama settings updated successfully"}
        except Exception as e:
            return {"success": False, "error": f"Error updating Ollama settings: {str(e)}"}
    
    def refresh_ollama_models(self) -> Dict[str, Any]:
        """
        Refresh the list of available Ollama models.
        
        Returns:
            A dictionary with the result of the operation.
        """
        try:
            available_models = get_ollama_models(self.ollama_base_url)
            if available_models:
                self.ollama_available_models = available_models
                return {"success": True, "message": f"Found {len(available_models)} models", "models": available_models}
            else:
                return {"success": False, "error": "No models found"}
        except Exception as e:
            return {"success": False, "error": f"Error refreshing Ollama models: {str(e)}"}
    
    def send_message(self, message: str) -> Dict[str, Any]:
        """
        Send a message to the chat and get a response.
        
        Args:
            message: The message to send
            
        Returns:
            A dictionary with the result of the operation.
        """
        if not self.graph_rag:
            return {"success": False, "error": "GraphRAG is not initialized. Please connect to Neo4j and configure your LLM settings first."}
        
        try:
            # Append user input to chat history
            self.chat_history.append({"role": "user", "content": message})
            
            # Generate response using GraphRAG with error handling and timeout
            start_time = time.time()
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Generate response using GraphRAG
                    if GRAPHRAG_AVAILABLE:
                        response = self.graph_rag.search(query_text=message)
                    else:
                        # Fallback if GraphRAG is not available
                        response = "GraphRAG is not available. This is a placeholder response. Please install the GraphRAG library to enable full functionality."
                    
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise e
                    time.sleep(1)  # Wait before retrying
            
            # Add response to chat history
            self.chat_history.append({"role": "assistant", "content": response})
            
            return {"success": True, "message": "Message sent successfully", "response": response}
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            self.chat_history.append({"role": "assistant", "content": error_message})
            return {"success": False, "error": error_message}
    
    def clear_chat_history(self) -> Dict[str, Any]:
        """
        Clear the chat history.
        
        Returns:
            A dictionary with the result of the operation.
        """
        try:
            self.chat_history = []
            return {"success": True, "message": "Chat history cleared successfully"}
        except Exception as e:
            return {"success": False, "error": f"Error clearing chat history: {str(e)}"}
    
    def _schema_from_triples(self, labels, triples, properties=None):
        """
        Generate a schema from labels and triples.
        
        Args:
            labels: List of node labels
            triples: Set of (source, relationship, target) triples
            properties: Dictionary of label properties
            
        Returns:
            Schema string
        """
        nodes = {}
        _node_fstrs = []
        for label in labels:
            nodes[label] = {
                'label': label,
                'var_name': label.lower(),
                'properties': {}
            }
            _properties_fstr = ""
            if isinstance(properties, dict) and label in properties.keys():
                nodes[label]['properties'] = properties[label]
                _properties_fstr = " {"
                for _prop, _type in properties[label].items():
                    _properties_fstr += f"{_prop}: {_type}"
                    if _prop != list(properties[label].keys())[-1]:
                        _properties_fstr += ", "
                _properties_fstr += "}"
            _node_fstrs.append(f"({nodes[label]['var_name']}:{label}{_properties_fstr})")
        
        relationships = {}
        _rel_fstrs = []
        for subject, predicate, object_ in triples:
            if subject in nodes.keys() and object_ in nodes.keys():
                _sub_var_name = nodes[subject]['var_name']
                _obj_var_name = nodes[object_]['var_name']
                relationships[subject, predicate, object_] = {
                    'subject': subject,
                    'predicate': predicate,
                    'object': object_,
                }
                _rel_fstrs.append(f"({_sub_var_name})-[:{predicate}]->({_obj_var_name})")
        
        schema = f"Nodes:\n"
        schema += "\n".join(_node_fstrs)
        schema += "\n\nRelationships:\n"
        schema += "\n".join(_rel_fstrs)
        
        return schema