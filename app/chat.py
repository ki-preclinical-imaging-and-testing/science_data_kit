import streamlit as st
from neo4j import GraphDatabase
#from graphrag import GraphRAG  # Importing GraphRAG module
#from neo4j_graphrag.embeddings import OllamaEmbeddings
#from neo4j_graphrag.llm import OllamaLLM

def chat():
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

