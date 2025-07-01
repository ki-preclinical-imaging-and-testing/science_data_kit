import streamlit as st
from neo4j import GraphDatabase
from utils.db_adapter import get_neo4j_session, create_pyvis_graph
import time
import requests
import json


def schema_from_triples(labels, triples, properties=None):
    """
    Generate a schema representation from labels and triples.

    This function creates a textual representation of a graph schema based on the
    provided labels, triples (subject-predicate-object relationships), and optional
    property definitions.

    Args:
        labels (list): A list of node labels in the graph.
        triples (list): A list of tuples, each containing (subject, predicate, object)
                       representing relationships in the graph.
        properties (dict, optional): A dictionary mapping labels to their properties.
                                    Each property is a key-value pair where the key is
                                    the property name and the value is the property type.
                                    Defaults to None.

    Returns:
        str: A formatted string representation of the graph schema, including nodes
             and relationships.
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


# Uncommented GraphRAG imports
try:
    from neo4j_graphrag.generation import GraphRAG  # Importing GraphRAG module
    from neo4j_graphrag.retrievers import VectorRetriever, Text2CypherRetriever
    from neo4j_graphrag.embeddings import OpenAIEmbeddings, OllamaEmbeddings
    from neo4j_graphrag.llm import OpenAILLM, OllamaLLM
    GRAPHRAG_AVAILABLE = True
except ImportError:
    GRAPHRAG_AVAILABLE = False

# Function to get available Ollama models
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
            st.warning(f"Failed to get Ollama models: {response.status_code}")
            return ["llama2", "mistral", "mixtral", "phi"]  # Fallback to default models
    except Exception as e:
        st.warning(f"Error connecting to Ollama API: {e}")
        return ["llama2", "mistral", "mixtral", "phi"]  # Fallback to default models

# Initialize session state for LLM settings if not already present
if "llm_provider" not in st.session_state:
    st.session_state["llm_provider"] = "OpenAI"
if "llm_api_key" not in st.session_state:
    st.session_state["llm_api_key"] = ""
if "llm_model" not in st.session_state:
    st.session_state["llm_model"] = "gpt-3.5-turbo"
if "llm_temperature" not in st.session_state:
    st.session_state["llm_temperature"] = 0.7
if "llm_max_tokens" not in st.session_state:
    st.session_state["llm_max_tokens"] = 1000

# Initialize Ollama-specific settings
if "ollama_base_url" not in st.session_state:
    st.session_state["ollama_base_url"] = "http://localhost:11434"
if "ollama_auth_enabled" not in st.session_state:
    st.session_state["ollama_auth_enabled"] = False
if "ollama_username" not in st.session_state:
    st.session_state["ollama_username"] = ""
if "ollama_password" not in st.session_state:
    st.session_state["ollama_password"] = ""
if "ollama_available_models" not in st.session_state:
    st.session_state["ollama_available_models"] = ["llama2", "mistral", "mixtral", "phi"]
    # Try to refresh models on startup
    try:
        available_models = get_ollama_models(st.session_state["ollama_base_url"])
        if available_models:
            st.session_state["ollama_available_models"] = available_models
    except:
        # Silently fail if Ollama is not available
        pass

# Initialize session state for graph visualization if not already present
if "cached_triples" not in st.session_state:
    st.session_state["cached_triples"] = set()
if "cached_labels" not in st.session_state:
    st.session_state["cached_labels"] = []
if "cached_layout" not in st.session_state:
    st.session_state["cached_layout"] = "Hierarchical"
if "cached_physics_enabled" not in st.session_state:
    st.session_state["cached_physics_enabled"] = False

# Initialize other required session state variables if not already present
if "graph_rag" not in st.session_state:
    st.session_state["graph_rag"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "neo4j_schema" not in st.session_state:
    st.session_state["neo4j_schema"] = None

def chat():
    """
    Render the chat interface for interacting with the graph database using natural language.

    This function creates a Streamlit page that allows users to:
    1. Configure LLM settings (provider, API key, model, temperature, max tokens)
    2. Connect to a Neo4j database
    3. Chat with the data using natural language queries
    4. View the graph schema

    The function uses GraphRAG (Graph Retrieval Augmented Generation) to convert
    natural language queries into Cypher queries that are executed against the
    Neo4j database, with the results used to generate responses.

    Returns:
        None
    """
    # Function to initialize GraphRAG with connection pooling
    @st.cache_resource
    def initialize_graph_rag(uri, user, password, llm_provider=None, llm_api_key=None, llm_model=None):
        """
        Initialize a GraphRAG instance with connection pooling.

        This function creates a connection to a Neo4j database and initializes a GraphRAG
        instance with the appropriate LLM (Language Learning Model) based on the provider.
        It also extracts the schema from the database for use with the Text2Cypher retriever.

        Args:
            uri (str): The URI of the Neo4j database.
            user (str): The username for the Neo4j database.
            password (str): The password for the Neo4j database.
            llm_provider (str, optional): The LLM provider to use (OpenAI, Anthropic, Ollama).
                                         Defaults to None.
            llm_api_key (str, optional): The API key for the LLM provider. Defaults to None.
            llm_model (str, optional): The specific model to use from the LLM provider.
                                      Defaults to None.

        Returns:
            GraphRAG or neo4j.Driver: A GraphRAG instance if initialization is successful,
                                     or a Neo4j driver if GraphRAG is not available.

        Raises:
            Exception: If there is an error initializing GraphRAG.
        """
        st.markdown(f"""
        **Initializing GraphRAG...**
        URI: {uri}
        User: {user}
        Password: {password}
        LLM Provider: {llm_provider}
        LLM Model: {llm_model}
        LLM API Key: {llm_api_key}
        """)
        try:
            # Create a connection pool for Neo4j
            driver = GraphDatabase.driver(
                uri, 
                auth=(user, password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=60
            )

            # Check if GraphRAG is available
            if not GRAPHRAG_AVAILABLE:
                st.warning("GraphRAG library is not installed. Using basic Neo4j connection instead.")
                return driver

            # Extract schema from the database
            try:
                from utils.sidebar import schema_sample_widget
                triples = st.session_state.cached_triples
                labels = st.session_state.cached_labels
                schema = schema_from_triples(labels, triples)
                st.session_state["neo4j_schema"] = schema
                st.success("Successfully extracted schema from Neo4j database")
            except Exception as e:
                st.warning(f"Could not extract schema: {e}. Using default schema.")
                schema = None
                st.session_state["neo4j_schema"] = None

            # Initialize Text2Cypher retriever with schema
            if schema:
                st.session_state["retriever_type"] = "Text2Cypher"
            else:
                # Fall back to VectorRetriever if schema extraction fails
                retriever = VectorRetriever(driver)
                st.session_state["retriever_type"] = "Vector"

            # Initialize GraphRAG with the appropriate LLM based on provider
            if llm_provider == "OpenAI" and llm_api_key:
                from neo4j_graphrag.llm import OpenAILLM
                llm = OpenAILLM(api_key=llm_api_key, model_name=llm_model or "gpt-3.5-turbo",
                                model_params={
                                    'temperature': st.session_state["llm_temperature"],
                                    'max_tokens': st.session_state["llm_max_tokens"]
                                })
                examples = ["""
                USER INPUT: 'Which actors starred in the Matrix?' 
                QUERY: MATCH (p:Person)-[:ACTED_IN]->(m:Movie) WHERE m.title = 'The Matrix' RETURN p.name
                """]
                retriever = Text2CypherRetriever(driver, neo4j_schema=schema, llm=llm, examples=examples)
                # embeddings = None  # Use default embeddings
                return GraphRAG(retriever, llm=llm)
            elif llm_provider == "Anthropic" and llm_api_key:
                from neo4j_graphrag.llm import AnthropicLLM
                llm = AnthropicLLM(api_key=llm_api_key, model=llm_model or "claude-2")
                embeddings = None  # Use default embeddings
                return GraphRAG(retriever, llm=llm, embeddings=embeddings)
            elif llm_provider == "Ollama":
                # Get Ollama settings from session state
                base_url = st.session_state.get("ollama_base_url", "http://localhost:11434")
                auth_enabled = st.session_state.get("ollama_auth_enabled", False)
                username = st.session_state.get("ollama_username", "")
                password = st.session_state.get("ollama_password", "")

                # Configure Ollama with authentication if enabled
                ollama_config = {
                    "base_url": base_url,
                    "model": llm_model or "llama2"
                }

                if auth_enabled and username and password:
                    ollama_config["auth"] = (username, password)
                    st.info(f"Using authentication for Ollama with username: {username}")

                # Initialize Ollama LLM and embeddings with the configuration
                try:
                    llm = OllamaLLM(**ollama_config)
                    # Use the same model for embeddings as for LLM by default
                    embeddings = OllamaEmbeddings(model=llm_model or "llama2", base_url=base_url)
                    if auth_enabled and username and password:
                        # Set auth for embeddings if supported
                        try:
                            embeddings.client.auth = (username, password)
                        except:
                            st.warning("Authentication for embeddings might not be supported in this version")

                    return GraphRAG(retriever, llm=llm, embeddings=embeddings)
                except Exception as e:
                    st.error(f"Error initializing Ollama: {e}")
                    # Fallback to a basic configuration
                    llm = OllamaLLM(model=llm_model or "llama2")
                    embeddings = OllamaEmbeddings(model=llm_model or "llama2")
                    return GraphRAG(retriever, llm=llm, embeddings=embeddings)
            else:
                # Default to a basic GraphRAG instance
                return GraphRAG(retriever)
        except Exception as e:
            st.error(f"Error initializing GraphRAG: {e}")
            return None

    # Title and instructions
    st.header("Chat with your data")
    st.markdown("""
    Ask a retrieval-augmented generator questions about your dataset. 
    Connect your trusted LLM provider in the settings panel below.

    ### Supported LLM Providers:
    - **OpenAI**: Requires API key
    - **Anthropic**: Requires API key
    - **Ollama**: Local LLM, supports any available model
      - Automatically detects available models
      - Optional authentication support
      - Customizable base URL for remote Ollama instances
    """)
    row = st.columns(2)
    with row[0]:
        with st.expander("LLM Connection", expanded=False):
            # LLM Settings Form
            with st.form("llm_settings_form"):
                col1, col2 = st.columns(2)

                with col1:
                    llm_provider = st.selectbox(
                        "LLM Provider",
                        options=["OpenAI", "Anthropic", "Ollama", "Other"],
                        index=["OpenAI", "Anthropic", "Ollama", "Other"].index(st.session_state["llm_provider"])
                    )

                    # Show API key input for OpenAI and Anthropic, but not for Ollama
                    if llm_provider != "Ollama":
                        llm_api_key = st.text_input(
                            "API Key",
                            type="password",
                            value=st.session_state["llm_api_key"]
                        )

                    # Show Ollama-specific settings if Ollama is selected
                    if llm_provider == "Ollama":
                        ollama_base_url = st.text_input(
                            "Ollama Base URL",
                            value=st.session_state["ollama_base_url"]
                        )

                        # Authentication toggle
                        ollama_auth_enabled = st.checkbox(
                            "Enable Authentication",
                            value=st.session_state["ollama_auth_enabled"]
                        )

                        # Show authentication fields if enabled
                        if ollama_auth_enabled:
                            ollama_username = st.text_input(
                                "Username",
                                value=st.session_state["ollama_username"]
                            )

                            ollama_password = st.text_input(
                                "Password",
                                type="password",
                                value=st.session_state["ollama_password"]
                            )
                        else:
                            ollama_username = ""
                            ollama_password = ""

                        # Try to fetch available models from Ollama
                        if st.button("Refresh Models"):
                            with st.spinner("Fetching available models from Ollama..."):
                                available_models = get_ollama_models(ollama_base_url)
                                st.session_state["ollama_available_models"] = available_models
                                st.success(f"Found {len(available_models)} models")
                                st.rerun()

                with col2:
                    if llm_provider == "OpenAI":
                        model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
                    elif llm_provider == "Anthropic":
                        model_options = ["claude-2", "claude-instant-1", "claude-3-opus", "claude-3-sonnet"]
                    elif llm_provider == "Ollama":
                        # Use available models from Ollama API
                        model_options = st.session_state["ollama_available_models"]
                    else:
                        model_options = ["custom-model"]

                    llm_model = st.selectbox(
                        "Model",
                        options=model_options,
                        index=0 if st.session_state["llm_model"] not in model_options else model_options.index(
                            st.session_state["llm_model"])
                    )

                    llm_temperature = st.slider(
                        "Temperature",
                        min_value=0.0,
                        max_value=1.0,
                        value=st.session_state["llm_temperature"],
                        step=0.1
                    )

                    llm_max_tokens = st.number_input(
                        "Max Tokens",
                        min_value=100,
                        max_value=4000,
                        value=st.session_state["llm_max_tokens"],
                        step=100
                    )

                submitted = st.form_submit_button("Save Settings")

                if submitted:
                    # Save settings to session state
                    st.session_state["llm_provider"] = llm_provider

                    # Save provider-specific settings
                    if llm_provider != "Ollama":
                        st.session_state["llm_api_key"] = llm_api_key
                    else:
                        # Save Ollama-specific settings
                        st.session_state["ollama_base_url"] = ollama_base_url
                        st.session_state["ollama_auth_enabled"] = ollama_auth_enabled
                        if ollama_auth_enabled:
                            st.session_state["ollama_username"] = ollama_username
                            st.session_state["ollama_password"] = ollama_password
                        else:
                            st.session_state["ollama_username"] = ""
                            st.session_state["ollama_password"] = ""

                    st.session_state["llm_model"] = llm_model
                    st.session_state["llm_temperature"] = llm_temperature
                    st.session_state["llm_max_tokens"] = llm_max_tokens

                    # Reinitialize GraphRAG with new settings
                    if st.session_state["neo4j_uri"] and st.session_state["neo4j_user"] and st.session_state[
                        "neo4j_password"]:
                        with st.spinner("Initializing GraphRAG with new settings..."):
                            st.session_state["graph_rag"] = initialize_graph_rag(
                                st.session_state["neo4j_uri"],
                                st.session_state["neo4j_user"],
                                st.session_state["neo4j_password"],
                                llm_provider,
                                llm_api_key if llm_provider != "Ollama" else None,
                                llm_model
                            )
                        st.success("LLM settings updated successfully!")
                        time.sleep(1)
                        st.rerun()

            col3, col4 = st.columns(2)
            with col3:
                st.markdown(
                    """        
                    This implementation uses **Text2Cypher to convert your natural language questions into Cypher queries** 
                    that are executed against your Neo4j database. The results are then used to generate a response.
                    """
                )
                st.button("Connect LLM", key="connect_LLM", use_container_width=False)
            with col4:
                st.markdown(
                    """            
                    This is experimental, so here's what you need to do:
                    1. Your **database must be connected**
                    2. Choose your preferred LLM provider:
                       - **OpenAI/Anthropic**: Provide your API key
                       - **Ollama**: Configure base URL and optional authentication
                    3. For Ollama, click "Refresh Models" to see all available models
                    4. Ask questions about the data in your database
                    """
                )
        # Display chat history with improved formatting
        with st.expander("Conversation", expanded=True):
            chat_container = st.container(height=800, border=True)
            with chat_container:
                for entry in st.session_state["chat_history"]:
                    if entry["role"] == "user":
                        with st.chat_message("user"):
                            st.write(entry["content"])
                    else:
                        with st.chat_message("assistant"):
                            # st.write(f"{entry['content']['answer']}\n[Retriever: {entry['content']['retriever']}]")
                            st.write(entry['content'])

                # User input with improved UI
                user_input = st.text_area("Your message", height=100)
                col1, col2 = st.columns([4, 1])

                with col1:
                    if st.button("Send", use_container_width=True, type="primary") and user_input:
                        if st.session_state["graph_rag"] is None:
                            st.error("Please connect to Neo4j and configure your LLM settings first.")
                        else:
                            # Append user input to chat history
                            st.session_state["chat_history"].append({"role": "user", "content": user_input})

                            with st.spinner("Generating response..."):
                                try:
                                    # Generate response using GraphRAG with error handling and timeout
                                    start_time = time.time()
                                    max_retries = 3
                                    retry_count = 0

                                    while retry_count < max_retries:
                                        try:
                                            # Generate response using GraphRAG
                                            if GRAPHRAG_AVAILABLE:
                                                response = st.session_state["graph_rag"].search(
                                                    query_text=user_input
                                                )
                                            else:
                                                # Fallback if GraphRAG is not available
                                                response = "GraphRAG is not available. This is a placeholder response. Please install the GraphRAG library to enable full functionality."

                                            # Add context information from the graph
                                            if GRAPHRAG_AVAILABLE:
                                                try:
                                                    # Get related nodes from the graph
                                                    session = get_neo4j_session(
                                                        st.session_state["neo4j_uri"],
                                                        st.session_state["neo4j_user"],
                                                        st.session_state["neo4j_password"]
                                                    )
                                                    # This is a simplified example - in a real implementation, you would extract entities from the user query
                                                    # and find related nodes in the graph
                                                    context_info = "\n\n*Related information from the knowledge graph might appear here.*"
                                                    response += context_info
                                                except Exception as e:
                                                    # Silently handle context retrieval errors
                                                    pass

                                            break
                                        except Exception as e:
                                            retry_count += 1
                                            if retry_count >= max_retries:
                                                raise e
                                            time.sleep(1)  # Wait before retrying

                                    # Add response to chat history
                                    st.session_state["chat_history"].append({"role": "bot", "content": response})

                                except Exception as e:
                                    error_message = f"Error generating response: {str(e)}"
                                    st.session_state["chat_history"].append({"role": "bot", "content": error_message})

                            # Refresh page to display chat history
                            st.rerun()

                with col2:
                    if st.button("Clear Chat", use_container_width=True):
                        st.session_state["chat_history"] = []
                        st.rerun()


    # Initialize GraphRAG if not already initialized
    if st.session_state["graph_rag"] is None:
        st.warning("GraphRAG is not initialized. Please connect to Neo4j and configure your LLM settings.")
        if st.session_state["neo4j_uri"] and st.session_state["neo4j_user"] and st.session_state["neo4j_password"]:
            with st.spinner("Initializing GraphRAG..."):
                st.session_state["graph_rag"] = initialize_graph_rag(
                    st.session_state["neo4j_uri"],
                    st.session_state["neo4j_user"],
                    st.session_state["neo4j_password"],
                    st.session_state["llm_provider"],
                    st.session_state["llm_api_key"],
                    st.session_state["llm_model"]
                )
                st.success("Connected to Neo4j and GraphRAG is initialized.")
                retriever_type = st.session_state.get("retriever_type", "Unknown")
                st.info(f"Using {retriever_type} retriever for queries")

    # Display schema information if available
    with (row[1]):
        with st.expander("Visual Schema", expanded=False):
            net = create_pyvis_graph(
                st.session_state.cached_triples,
                st.session_state.cached_layout,
                st.session_state.cached_physics_enabled
            )
            net_html = net.generate_html()
            st.components.v1.html(net_html, height=800)

        with st.expander("Cypher Schema", expanded=False):
            if "neo4j_schema" not in st.session_state:
                schema = schema_from_triples(
                    st.session_state["cached_labels"],
                    st.session_state["cached_triples"]
                )
                st.session_state["neo4j_schema"] = schema
            else:
                schema = st.session_state["neo4j_schema"]

            st.markdown(f"```\n{schema}\n```")
