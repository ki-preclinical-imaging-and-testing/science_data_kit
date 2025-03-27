import streamlit as st
import pandas as pd
from pathlib import Path
from utils.models import  merge_nodes_with_existing
from utils.sidebar import database_sidebar, jupyter_sidebar

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

jupyter_sidebar()
database_sidebar()

# Initialize session state variables
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


# Function to fetch available labels from Neo4j
def fetch_available_labels():
    with st.session_state["db_connection"].session() as session:
        result = session.run("CALL db.labels()")
        labels = [record[0] for record in result]
        return labels

st.session_state["available_labels"] = fetch_available_labels()

# Title and description
st.title("Resolve Entities")

st.markdown(
    """
    ## Review and Edit Entities
    1. Load entities from a file.
    2. Select label and properties.
    3. Review dataset row by row.
    4. Define relationships and push to the database.
    """
)

# File uploader for checkpointed file
uploaded_file = st.file_uploader("Upload entity file (CSV or JSON):", type=["csv", "json"])
file_path = st.text_input("Or enter file path:")
if st.button("Load File") and file_path:
    try:
        file_extension = Path(file_path).suffix
        if file_extension == ".csv":
            st.session_state["entities_df"] = pd.read_csv(file_path)
        elif file_extension == ".json":
            st.session_state["entities_df"] = pd.read_json(file_path)
        else:
            st.error("Unsupported file format.")
        st.session_state["file_uploaded"] = file_path
    except Exception as e:
        st.error(f"Error loading file: {e}")

if uploaded_file:
    try:
        file_extension = Path(uploaded_file.name).suffix
        if file_extension == ".csv":
            st.session_state["entities_df"] = pd.read_csv(uploaded_file)
        elif file_extension == ".json":
            st.session_state["entities_df"] = pd.read_json(uploaded_file)
        else:
            st.error("Unsupported file format.")
        st.session_state["file_uploaded"] = uploaded_file.name
    except Exception as e:
        st.error(f"Error loading file: {e}")

# Display the dataframe if loaded
if st.session_state["entities_df"] is not None:
    st.markdown(f"`{st.session_state['file_uploaded']}`")
    st.subheader("Input DataFrame")
    st.dataframe(st.session_state["entities_df"], use_container_width=True)

    # Select label column
    st.subheader("Define Entity Structure")
    st.session_state["label_column"] = st.selectbox("Select Label Column:",
                                                    options=st.session_state["entities_df"].columns)
    st.session_state["property_columns"] = st.multiselect("Select Property Columns:",
                                                          options=st.session_state["entities_df"].columns)

    # Display individual entity view
    entity_indices = st.session_state["entities_df"].index.tolist()
    selected_entity_index = st.selectbox("Select entity to edit:", options=entity_indices, format_func=lambda
        x: f"{st.session_state['entities_df'].at[x, st.session_state['label_column']]}" if st.session_state[
        "label_column"] else f"Entity {x}")

    if selected_entity_index is not None:
        st.session_state["selected_entity_index"] = selected_entity_index
        selected_entity = st.session_state["entities_df"].iloc[selected_entity_index][
            st.session_state["property_columns"]].to_dict()

        selected_entity_df = pd.DataFrame(list(selected_entity.items()), columns=["Key", "Value"])

        edited_entity_df = st.data_editor(
            selected_entity_df,
            key="individual_entity_editor",
            use_container_width=True,
            num_rows="dynamic"
        )

    # Define relationships
    st.subheader("Define Relationships")
    target_label = st.selectbox("Select Target Node Label:", options=st.session_state["available_labels"])
    match_columns = st.multiselect("Select Matching Properties:", options=st.session_state["entities_df"].columns)
    relationship_type = st.text_input("Define Relationship Type (e.g., STORED_IN):")

    # Submit to database
    if st.button("Push to Database"):
        with st.spinner("Pushing to database..."):
            try:
                # Generate Neomodel classes dynamically if not already defined
                neomodel_map = {}
                for _label in st.session_state["entities_df"][st.session_state["label_column"]].unique():
                    neomodel_map[_label] = {
                        col: 'String' for col in st.session_state["property_columns"]
                    }

                # Merge new nodes with existing nodes in the database
                merge_nodes_with_existing(
                    db_connection=st.session_state["db_connection"],
                    entities_df=st.session_state["entities_df"],
                    label_column=st.session_state["label_column"],
                    property_columns=st.session_state["property_columns"],
                    target_label=target_label,
                    match_columns=match_columns,
                    relationship_type=relationship_type
                )

                st.success("Entities and relationships pushed successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
