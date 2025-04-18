import streamlit as st
import os
from datetime import datetime
from pathlib import Path

from survey import save_filename
from utils.sidebar import database_sidebar, jupyter_sidebar, neo4j_connector
from utils.database import export_graph_to_file, import_graph_from_file

# Title and description
st.header("Data Resources")
st.markdown("""Spin up servers and connect to your data on this page.""")

server_dict = {
    'Servers': None,
    'Host local Neo4j database to stage your data': database_sidebar,
    'Run Jupyter Lab to work with your data': jupyter_sidebar,
    'Drivers': None,
    'Connect to a Neo4j database': neo4j_connector
}


row = {}
row_index = 0
for _text, _widget in server_dict.items():
    row[row_index] = st.columns(2)
    if _widget is None:
        with row[row_index][0]:
            st.divider()
        with row[row_index][1]:
            st.subheader(_text)
    else:
        with row[row_index][0]:
            _widget()
        with row[row_index][1]:
            st.markdown(f"*{_text}*")
    row_index += 1

st.divider()

# Database Management expander for saving and loading the graph
with st.expander("Database Management", expanded=False):
    st.markdown("""
    ## Save and Load Graph Database

    Save your entire labeled property graph to a file or load a previously saved graph.
    """)

    # Create two columns for save and load functionality
    save_col, load_col = st.columns(2)

    with save_col:
        st.subheader("Save Graph")
        st.markdown("Export the entire Neo4j graph to a file.")

        # Default save directory
        default_save_dir = os.path.join(os.path.expanduser("~"), "graph_exports")
        os.makedirs(default_save_dir, exist_ok=True)

        # Generate default filename with timestamp
        default_filename = f"neo4j_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"

        # Save directory input
        save_dir = st.text_input("Save Directory:", value=default_save_dir)

        # Filename input
        if 'db_save_filename' not in st.session_state.keys():
            st.session_state['db_save_filename'] = default_filename
        save_filename = st.session_state['db_save_filename']
        st.session_state['db_save_filename'] = st.text_input("Filename:", value=save_filename)

        # Combine directory and filename
        save_path = os.path.join(save_dir, save_filename)

        # Save button
        if st.button("Save Graph", use_container_width=True):
            if not st.session_state.connected:
                st.error("Please connect to a Neo4j database first.")
            else:
                with st.spinner("Exporting graph..."):
                    success, message = export_graph_to_file(st.session_state.session, save_path)
                    if success:
                        st.success(message)
                        st.info(f"Graph saved to: {save_path}")
                    else:
                        st.error(message)

    with load_col:
        st.subheader("Load Graph")
        st.markdown("Import a graph from a file into Neo4j.")

        # File uploader for graph file
        uploaded_file = st.file_uploader("Upload graph file:", type=["pkl"])

        # Or enter file path
        load_path = st.text_input("Or enter file path:")

        # Warning about overwriting existing data
        st.warning("⚠️ Loading a graph will clear the current database!")

        # Confirmation checkbox
        confirm_load = st.checkbox("I understand that this will overwrite the current database")

        # Load button
        if st.button("Load Graph", use_container_width=True):
            if not st.session_state.connected:
                st.error("Please connect to a Neo4j database first.")
            elif not confirm_load:
                st.error("Please confirm that you understand the consequences of loading a graph.")
            elif uploaded_file:
                # Save the uploaded file to a temporary location
                temp_path = os.path.join(os.path.expanduser("~"), "temp_graph.pkl")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Import the graph
                with st.spinner("Importing graph..."):
                    success, message = import_graph_from_file(st.session_state.session, temp_path)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

                # Clean up the temporary file
                try:
                    os.remove(temp_path)
                except:
                    pass
            elif load_path:
                # Import the graph from the specified path
                with st.spinner("Importing graph..."):
                    success, message = import_graph_from_file(st.session_state.session, load_path)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
            else:
                st.error("Please upload a file or enter a file path.")

with st.expander("API Documentation", expanded=False):
    st.markdown("""
    Explore the API and integrate it into your workflows. You can find documentation, explore the Python driver, and test examples interactively.
    """)

    # Links to Documentation
    st.markdown("""
    ### Documentation Links
    - [API Documentation](https://your-sphinx-docs-link.com)
    - [GitHub Repository](https://github.com/your-repo-link)
    """)

    # Interactive API Tester
    st.subheader("Try the API")
    with st.form("api_form"):
        param1 = st.number_input("Parameter 1 (integer):", min_value=0, value=42)
        param2 = st.text_input("Parameter 2 (string):", value="hello")
        submitted = st.form_submit_button("Run Example")
        if submitted:
            result = example_function(param1, param2)
            st.success(f"Result: {result}")

    # Display Inline Examples
    st.subheader("Example Usage")
    st.code("""
    from science_data_kit import example_function

    # Basic example
    result = example_function(42, "hello")
    print(result)  # Output: '42 hello'
    """, language="python")
