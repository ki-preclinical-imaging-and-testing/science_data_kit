import streamlit as st
from neo4j import GraphDatabase
#from graphrag import GraphRAG  # Importing GraphRAG module
#from neo4j_graphrag.embeddings import OllamaEmbeddings
#from neo4j_graphrag.llm import OllamaLLM


# Session state initialization
if "neo4j_uri" not in st.session_state:
    st.session_state["neo4j_uri"] = "bolt://localhost:7687"
if "neo4j_user" not in st.session_state:
    st.session_state["neo4j_user"] = "neo4j"
if "neo4j_password" not in st.session_state:
    st.session_state["neo4j_password"] = "neo4jiscool"
if "graph_rag" not in st.session_state:
    st.session_state["graph_rag"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Function to initialize GraphRAG
@st.cache_resource
def initialize_graph_rag(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    #return GraphRAG(driver)
    return driver

# Title and instructions
st.title("Ground: Chat with your data")
st.markdown(
    """Ask the bot (a retrieval-augmented generator) about your dataset"""
)

# Connection settings
st.sidebar.header("Connection Settings")
st.session_state["neo4j_uri"] = st.sidebar.text_input("Neo4j URI", st.session_state["neo4j_uri"])
st.session_state["neo4j_user"] = st.sidebar.text_input("Neo4j User", st.session_state["neo4j_user"])
st.session_state["neo4j_password"] = st.sidebar.text_input("Neo4j Password", st.session_state["neo4j_password"], type="password")

if st.sidebar.button("Connect"):
    try:
        st.session_state["graph_rag"] = initialize_graph_rag(
            st.session_state["neo4j_uri"],
            st.session_state["neo4j_user"],
            st.session_state["neo4j_password"]
        )
        st.sidebar.success("Connected to Neo4j successfully!")
    except Exception as e:
        st.sidebar.error(f"Connection failed: {e}")

# Display chat history
for entry in st.session_state["chat_history"]:
    if entry["role"] == "user":
        st.markdown(f"**You:** {entry['content']}")
    else:
        st.markdown(f"**Bot:** {entry['content']}")

# User input
user_input = st.text_input("Type below", "")
if st.button("Send") and user_input:
    if st.session_state["graph_rag"] is None:
        st.error("Please connect to Neo4j first.")
    else:
        # Append user input to chat history
        st.session_state["chat_history"].append({"role": "user", "content": user_input})

        try:
            # Generate response using GraphRAG
            response = st.session_state["graph_rag"].query(user_input)
            st.session_state["chat_history"].append({"role": "bot", "content": response})
        except Exception as e:
            st.session_state["chat_history"].append({"role": "bot", "content": f"Error: {e}"})

        # Refresh page to display chat history
        st.rerun()

