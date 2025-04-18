import streamlit as st
import pandas as pd
from pathlib import Path
from neo4j import GraphDatabase


if __name__ == "__main__":
    st.set_page_config(
        page_title="Science Data Toolkit",
        page_icon="🖥️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://adam-patch.mit.edu',
            'Report a bug': "https://adam-patch.mit.edu",
            'About': "# Data Science 4 Science Data!"
        }
    )

    # Initialize session state
    if "folder" not in st.session_state:
        st.session_state["folder"] = None
    if "scan_completed" not in st.session_state:
        st.session_state["scan_completed"] = False
    if "scanned_files" not in st.session_state:
        st.session_state["scanned_files"] = pd.DataFrame()
    if "ncdu_output" not in st.session_state:
        st.session_state["ncdu_output"] = ""
    if "ncdu_json_path" not in st.session_state:
        st.session_state["ncdu_json_path"] = str(Path.home() / "ncdu_scan.json")  # Default JSON path

    if "entities_df" not in st.session_state:
        st.session_state["entities_df"] = None
    if "selected_entity_index" not in st.session_state:
        st.session_state["selected_entity_index"] = None
    if "label_column" not in st.session_state:
        st.session_state["label_column"] = None
    if "property_columns" not in st.session_state:
        st.session_state["property_columns"] = []
    if "available_labels" not in st.session_state:
        st.session_state["available_labels"] = []

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

    # Initialize session state variables
    if "entities_df" not in st.session_state:
        st.session_state["entities_df"] = None
    if "taxonomy_keys" not in st.session_state:
        st.session_state["taxonomy_keys"] = []
    if "taxonomy" not in st.session_state:
        st.session_state["taxonomy"] = None
    if "taxonomy_set" not in st.session_state:
        st.session_state["taxonomy_set"] = False


    if "container_status" not in st.session_state:
        st.session_state["container_status"] = None
    if "container_name" not in st.session_state:
        st.session_state["container_name"] = "neo4j-instance"
    if "http_port" not in st.session_state:
        st.session_state["http_port"] = 7474
    if "bolt_port" not in st.session_state:
        st.session_state["bolt_port"] = 7687
    if "username" not in st.session_state:
        st.session_state["username"] = "neo4j"
    if "password" not in st.session_state:
        st.session_state["password"] = "neo4jiscool"
    if "credentials_locked" not in st.session_state:
        st.session_state["credentials_locked"] = False  # Prevent changes after start
    if "db_connection" not in st.session_state:
        st.session_state["db_connection"] = GraphDatabase.driver(
            f"bolt://localhost:{st.session_state['bolt_port']}",
            auth=(st.session_state['username'],
                  st.session_state['password'])
        )

    ## main block
    if "connected" not in st.session_state:
        st.session_state.connected = False

    if "selected_db" not in st.session_state:
        st.session_state.selected_db = None

    # Initialize NeoDash session state variables
    if "neodash_container_name" not in st.session_state:
        st.session_state["neodash_container_name"] = "dsk-neodash-instance"
    if "neodash_port" not in st.session_state:
        st.session_state["neodash_port"] = 5005
    if "neodash_connected" not in st.session_state:
        st.session_state["neodash_connected"] = False
    if "neodash_host_ip" not in st.session_state:
        st.session_state["neodash_host_ip"] = "localhost"

    from menu import menu
    menu()

    # st.title("Get started...")
    #
    # st.markdown(
    #     """
    #     *... simplifying FAIR+ data in your lab.*
    #
    #     ### What is this?
    #     **Science Data Toolkit** helps you index, curate, and integrate multimodal research data.
    #
    #     ### Science Data Toolkit helps you...
    #     |  |  |
    #     | ---: | --- |
    #     |  **start** | *using this toolkit* |
    #     |  **index** | *filetree metadata* |
    #     |  **resolve** | *data entities* |
    #     |  **relate** | *entities via schema* |
    #     |  **explore** | *data in context* |
    #     |  **integrate** | *other workflows* |
    #     |  **ground** | *large language models* |
    #     |  **learn** | *more about this toolkit* |
    #
    #     ## FAIR+ Data
    #     The FAIR(+) Data Principles have been established (and appended).
    #
    #     Let's follow them. We can have *nice things*.
    #
    #     Science data that is...
    #
    #     - **F**indable
    #     - **A**ccessible
    #     - **I**nteroperable
    #     - **R**eusable
    #     - **+** (Computable)
    #
    #     ... is *nice things* science data. Let's have it!
    #     """
    #     # TODO: Make an infographic for this description
    #     #### Getting Started
    #     # Using the navigation menu on the left:
    #     # 1. Go to **Scan** to analyze your filesystem.
    #     # 2. Visit **Edit** to review metadata.
    #     # 3. Proceed to **Curate** for organizing datasets.
    #     # 4. Explore schema and data relationships under **Explore**.
    #     # 5. Finally, use **Integrate** to export or connect your work.
    #     # For **Learn** for detailed documentation about each step!
    # )
    #
