import streamlit as st
from neo4j import GraphDatabase
import pandas as pd
from pyvis.network import Network
from io import BytesIO
import json
from pathlib import Path
from utils.sidebar import database_sidebar




# Path to store saved queries
QUERIES_FILE = Path("saved_queries.json")

st.set_page_config(
    page_title="Science Data Toolkit",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://adam-patch.mit.edu',
        'Report a bug': "https://adam-patch.mit.edu",
        'About': "# Science Data for Data Science!"
    }

)

database_sidebar()

# Utility Functions
def load_saved_queries():
    """Load saved queries from the JSON file."""
    if QUERIES_FILE.exists():
        with open(QUERIES_FILE, "r") as file:
            return json.load(file)
    return {}


def save_queries(queries):
    """Save queries to the JSON file."""
    with open(QUERIES_FILE, "w") as file:
        json.dump(queries, file, indent=4)


# Streamlit Query Management Section
def manage_queries(recall_query):
    # Load saved queries
    saved_queries = load_saved_queries()

    # Save current query
    query_name = st.text_input("Save Current Query As")
    if st.button("Save Query"):
        if query_name:
            saved_queries[query_name] = recall_query
            save_queries(saved_queries)
            st.success(f"Query '{query_name}' saved successfully!")
        else:
            st.error("Please provide a name for the query.")

    # Load a query
    if saved_queries:
        selected_query_name = st.selectbox("Load Saved Query", [""]
                                           + list(saved_queries.keys()), label_visibility="visible")
        if selected_query_name:
            recall_query = saved_queries[selected_query_name]

    # Delete a query
    if saved_queries:
        delete_query_name = st.selectbox("Delete Saved Query",
                                         [""] + list(saved_queries.keys()), label_visibility="visible",
                                         key="delete_query")
        if delete_query_name and st.button(f"Delete Query '{delete_query_name}'"):
            saved_queries.pop(delete_query_name, None)
            save_queries(saved_queries)

    return recall_query


# Neo4j Connection
def get_neo4j_session(uri, user, password, database=None):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    session = driver.session(database=database) if database else driver.session()
    return session


# Fetch available databases
def fetch_databases(session):
    query = "SHOW DATABASES"
    results = session.run(query)
    return [record["name"] for record in results]


# Schema Extraction Algorithm
def extract_schema(results):
    triples = set()
    for record in results:
        triples.add((record["subjectLabel"], record["predicateType"], record["objectLabel"]))
    nodes = {label for triple in triples for label in (triple[0], triple[2])}
    return triples, nodes


# Pyvis Graph Creation with Layout Options
def create_pyvis_graph(triples, layout, physics_enabled):
    net = Network(notebook=False, height="750px", width="100%")

    # Common node and edge settings
    common_options = {
        "nodes": {
            "font": {
                "size": 16,
                "bold": True,
                "align": "center",
            },  # Font size for node labels
        },
        "edges": {
            "arrows": {"to": {"enabled": True}},  # Add arrows for directionality
            "smooth": {"enabled": True},  # Enable smooth edges
            "font": {
                "size": 12,
                "align": "middle"
            }
        },
        "interaction": {
            "hover": True,  # Enable hover effects
            "navigationButtons": True  # Add zoom and pan buttons
        },
        "physics": {
            "enabled": physics_enabled
        }
    }

    # Layout-specific settings
    if layout == "Hierarchical":
        layout_options = {
            "layout": {
                "hierarchical": {
                    "enabled": True,
                    "levelSeparation": 150,  # Distance between levels
                    "nodeSpacing": 100,  # Horizontal spacing
                    "treeSpacing": 200,  # Spacing between subtrees
                    "direction": "UD",  # Up-to-Down layout
                    "sortMethod": "directed"  # Sort by hub size: "hubsize"
                }
            }
        }
    else:  # Force-Directed Layout
        layout_options = {
            "physics": {
                "barnesHut": {
                    "gravitationalConstant": -4000,  # Strength of gravity
                    "centralGravity": 0.5,  # Pull toward center
                    "springLength": 170,  # Ideal edge length
                    "springConstant": 0.05,  # Spring stiffness
                    "damping": 0.09  # Motion damping factor
                }
            },
            "layout": {"improvedLayout": True}  # Optimize node positioning
        }

    # Combine common options with layout-specific options
    options = {**common_options, **layout_options}

    # Apply options to the network
    net.set_options(json.dumps(options))

    # Add nodes and edges from triples
    for subject, predicate, object_ in triples:
        net.add_node(subject, label=subject)
        net.add_node(object_, label=object_)
        net.add_edge(subject, object_, label=predicate, arrows="to")  # Directionality

    return net

def fetch_nodes_by_label(session, label, with_clause):
    query = f"""
    {with_clause}
    MATCH (n:{label})
    RETURN n AS node
    UNION
    {with_clause}
    MATCH (m:{label})
    RETURN m AS node
    """
    results = session.run(query)

    # Collect unique nodes from both queries
    nodes = [dict(record["node"]) for record in results]
    return pd.DataFrame(nodes).drop_duplicates()


## main block
if "connected" not in st.session_state:
    st.session_state.connected = False

if "selected_db" not in st.session_state:
    st.session_state.selected_db = None

st.sidebar.title("Connect")
with st.sidebar.expander("Connection", expanded=False):
    # Connection Details in Sidebar
    uri = st.text_input("URI", f"bolt://localhost:{st.session_state['bolt_port']}")
    user = st.text_input("Username", st.session_state['username'])
    password = st.text_input("Password", st.session_state['password'], type="password")
    if st.button("Connect"):
        with st.spinner("Connecting to Neo4j..."):
            try:
                session = get_neo4j_session(uri, user, password)
                st.session_state.session = session
                st.session_state.connected = True
                st.success("Connected!")
            except Exception as e:
                st.sidebar.error(f"Connection failed: {e}")
                st.session_state.connected = False
    if st.session_state.connected:
        with st.spinner("Fetching available databases..."):
            databases = fetch_databases(st.session_state.session)
            selected_db = st.sidebar.selectbox(
                "Database",
                databases,
                index=databases.index(st.session_state.selected_db) if st.session_state.selected_db else 0
            )
            st.session_state.selected_db = selected_db


if st.session_state.connected:

    # Schema Sampling Section
    st.sidebar.title("Recall Schema")


    # Initialize recall_query in session_state
    if "recall_query" not in st.session_state:
        st.session_state.recall_query = "MATCH (n)-[r]->(m)\nWITH DISTINCT n, r, m "

    # Callback function to handle query updates
    def update_recall_query():
        st.session_state.recall_query = st.session_state.recall_query_input


    st.sidebar.text_area(
        "Query",
        value=st.session_state.recall_query,
        key="recall_query_input",
        on_change=update_recall_query,
    )

    with st.sidebar.expander("Recall Query", expanded=False):
        # Sidebar input for Recall Query

        recall_query = manage_queries(st.session_state.recall_query)

        st.session_state.recall_query = recall_query
        if st.button('Update'):
            st.success(f"Updated.'")
            st.rerun()

    sample_size = st.sidebar.number_input("Sample Size", min_value=1, value=100, step=10)
    include_all = st.sidebar.checkbox("Include All (No Limit)", value=False)
    layout = st.sidebar.radio("Schema Layout", ["Hierarchical", "Force-Directed"], index=0)
    physics_enabled = st.sidebar.checkbox("Elasticity", value=True)

    if st.sidebar.button("Sample Schema"):
        session = get_neo4j_session(uri, user, password, database=st.session_state.selected_db)
        limit_clause = "" if include_all else f"LIMIT {sample_size}"
        with_clause = recall_query.strip() if recall_query.strip() else ""
        query = f"""
        {with_clause}
        MATCH (n)-[r]->(m)
        RETURN labels(n)[0] AS subjectLabel, type(r) AS predicateType, labels(m)[0] AS objectLabel
        {limit_clause}
        """
        with st.spinner("Sampling schema..."):
            results = session.run(query)
            results_list = [record.data() for record in results]
            st.success(f"Sampled {len(results_list)} rows from the schema!")

            triples, nodes = extract_schema(results_list)
            st.session_state.cached_triples = triples
            st.session_state.cached_labels = sorted(nodes)  # Ensure this is updated

    # Graph Visualization
    if "cached_triples" in st.session_state:
        st.title("Sample Schema")
        net = create_pyvis_graph(st.session_state.cached_triples, layout,
                                 physics_enabled)
        net_html = net.generate_html()
        st.components.v1.html(net_html, height=800)

    # Node Data Extraction
    st.sidebar.title("Recalled Nodes")
    if "cached_labels" in st.session_state:
        selected_labels = st.sidebar.multiselect("Select Node Labels", st.session_state.cached_labels)

        if st.sidebar.button("Fetch Nodes"):
            with st.spinner(f"Fetching nodes for labels: {', '.join(selected_labels)}"):
                session = get_neo4j_session(uri, user, password, database=st.session_state.selected_db)
                node_dataframes = {}
                for label in selected_labels:
                    node_data = fetch_nodes_by_label(session, label, recall_query.strip())
                    node_dataframes[label] = pd.DataFrame(node_data)
                st.session_state.node_dataframes = node_dataframes

    if "node_dataframes" in st.session_state:
        tabs = st.tabs(st.session_state.node_dataframes.keys())
        for label, tab in zip(st.session_state.node_dataframes.keys(), tabs):
            with tab:
                st.write(f"Nodes: {label}")
                st.dataframe(st.session_state.node_dataframes[label], use_container_width=True)

        # Option to set filename
        st.write("### Export")
        st.text("Individual dataframes can be exported to CSV...\n... just hover over top right of sheet")
        st.text("All sheets can be exported together to XLSX...")

        # Set filename input outside of button press
        filename = st.text_input("Enter filename for Excel workbook", value="node_data.xlsx")
        # Export all to Excel
        if st.button("Export XLSX Workbook"):
            if not filename.endswith(".xlsx"):
                st.error("Filename must end with .xlsx")
            else:
                with st.spinner("Preparing Excel workbook..."):
                    output = BytesIO()
                    try:
                        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                            for label, df in st.session_state.node_dataframes.items():
                                df.to_excel(writer, index=False, sheet_name=label)
                        output.seek(0)

                        # Once ready, provide the download button
                        st.download_button(
                            label="Download",
                            data=output,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception as e:
                        st.error(f"Failed to export workbook: {e}")

