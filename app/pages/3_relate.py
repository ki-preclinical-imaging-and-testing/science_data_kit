import streamlit as st
import pandas as pd
from utils.sidebar import database_sidebar
from utils.database import (
    fetch_entity_labels,
    fetch_node_properties,
    fetch_nodes_with_properties
)

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


# Initialize session state variables
if "entities_df" not in st.session_state:
    st.session_state["entities_df"] = None
if "taxonomy_keys" not in st.session_state:
    st.session_state["taxonomy_keys"] = []
if "taxonomy" not in st.session_state:
    st.session_state["taxonomy"] = None
if "taxonomy_set" not in st.session_state:
    st.session_state["taxonomy_set"] = False

# Title and description
st.title("Relate: Build Taxonomy")

st.markdown(
    """
    ## Define Relationships and Build Taxonomy
    1. Select keys to define a hierarchical taxonomy.
    2. Rearrange or nest keys to organize the structure.
    3. Save the taxonomy schema.
    """
)

st.subheader("Select Data Source")

data_source = st.radio(
    "Relate entities from:",
    ["Dataframe", "Database"]
)

entities_df = st.session_state.get("entities_df", None)

if data_source == "Dataframe":
    # Load the edited entities dataframe
    if st.session_state["entities_df"] is None:
        uploaded_file = st.file_uploader("Upload entity file (CSV or JSON):", type=["csv", "json"])
        if uploaded_file:
            try:
                file_extension = uploaded_file.name.split(".")[-1]
                if file_extension == "csv":
                    st.session_state["entities_df"] = pd.read_csv(uploaded_file)
                elif file_extension == "json":
                    st.session_state["entities_df"] = pd.read_json(uploaded_file)
                else:
                    st.error("Unsupported file format.")
                st.success("Entity dataset loaded successfully!")
            except Exception as e:
                st.error(f"Error loading file: {e}")
    entities_df = st.session_state["entities_df"]

elif data_source == "Database":
    # Fetch available node labels from Neo4j
    st.session_state["available_entity_labels"] = fetch_entity_labels(st.session_state["db_connection"].session())
    # Allow the user to select a label type
    entity_label = st.selectbox("Select Node Label to Use:", st.session_state["available_entity_labels"])
    if entity_label:
        st.session_state["entity_properties"] = fetch_node_properties(st.session_state["db_connection"].session(), entity_label)
        entities_df = pd.DataFrame(columns=st.session_state['entity_properties'])

# If the dataframe is loaded, proceed with taxonomy creation
if entities_df is not None:
    st.subheader("Select Keys for Taxonomy")
    # Display available keys
    available_keys = st.session_state["entity_properties"]
    taxa_keys_tmp = st.session_state["taxonomy_keys"]
    selected_keys = st.multiselect(
        "Select keys to define taxonomy levels:",
        options=available_keys,
        default=[]
    )
    # Update session state with selected keys
    if selected_keys:
        st.session_state["taxonomy_keys"] = selected_keys
    extra_keys = st.multiselect(
        "Select keys for useful context:",
        options=list(set(available_keys)-set(selected_keys)),
        default=[]
    )
    all_selected_keys = selected_keys.copy()
    if extra_keys:
        all_selected_keys += extra_keys
    # Display the selected keys as the hierarchical structure
    if st.session_state["taxonomy_keys"]:
        st.subheader("**Schema Hierarchy:**")
        for i, key in enumerate(st.session_state["taxonomy_keys"], 1):
            st.write(f"Level {i}: {key}")
        if st.button("Pull Entities from Database"):
            entities_df = fetch_nodes_with_properties(st.session_state["db_connection"].session(),
                                                      entity_label, all_selected_keys)
            st.session_state["entities_df"] = entities_df

        # Create the taxonomy by grouping the dataframe
        try:
            if not st.session_state["taxonomy_set"]:
                taxonomy_df = (
                    st.session_state["entities_df"].groupby(st.session_state["taxonomy_keys"])
                    .size()
                    .reset_index(name="Count")
                )
                st.session_state["taxonomy"] = taxonomy_df

            # Display the resulting taxonomy
            st.write("**Generated Taxonomy:**")
            taxonomy_df = st.session_state["taxonomy"]
            st.dataframe(taxonomy_df, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating taxonomy: {e}")

    st.session_state["taxonomy_set"] = st.toggle("Set Taxonomy", value=False)

    # # Fetch available entity labels from Neo4j
    # def fetch_entity_labels():
    #     with st.session_state["db_connection"].session() as session:
    #         result = session.run("CALL db.labels()")
    #         return [record[0] for record in result]

    st.session_state["available_entity_labels"] = fetch_entity_labels(st.session_state["db_connection"].session())

    # Option to save the taxonomy in the database
    st.subheader("Save Taxonomy to Database")

    # Select fields to match entities
    st.subheader("Connect Taxonomy to Entities")
    available_columns = entities_df.columns.tolist() if entities_df is not None else []
    available_labels = st.session_state["available_entity_labels"]
    entity_label = st.selectbox("Select entity label to connect to:",
                                options=available_labels)
    match_columns = st.multiselect("Select columns to match with entity nodes:",
                                   options=available_columns)
    relationship_type = st.text_input("Define Relationship Type (e.g., BELONGS_TO, PART_OF):")

    if st.button("Push Taxonomy to Database"):
        with st.session_state["db_connection"].session() as session:
            try:
                for _, row in st.session_state["taxonomy"].iterrows():
                    _path_id_chain = []
                    prev_node_id = None
                    for col in st.session_state["taxonomy_keys"]:
                        instance_value = row[col]
                        _path_id_chain.append(str(instance_value))
                        query = f"""
                        MERGE (f:{col} {{is: $instance_value, path_id: $path_id}})
                        RETURN id(f) as node_id
                        """
                        result = session.run(
                                query,
                                instance_value=instance_value, 
                                path_id='-'.join(_path_id_chain)
                                )
                        current_node_id = result.single()["node_id"]

                        if prev_node_id is not None:
                            session.run(
                                """
                                MATCH (prev), (curr)
                                WHERE id(prev) = $prev_id AND id(curr) = $curr_id
                                MERGE (prev)<-[:OF]-(curr)
                                """,
                                prev_id=prev_node_id,
                                curr_id=current_node_id
                            )
                        prev_node_id = current_node_id

                    # Match the final node with an existing entity
                    match_conditions = " AND ".join([f"e.{col} = $col_{col}" for col in match_columns])
                    match_params = {f"col_{col}": row[col] for col in match_columns}
                    entity_query = f"""
                    MATCH (e:{entity_label}) WHERE {match_conditions}
                    MATCH (t) WHERE id(t) = $final_node_id
                    MERGE (t)-[:{relationship_type}]->(e)
                    """
                    session.run(entity_query, final_node_id=prev_node_id, **match_params)

                st.success("Taxonomy pushed to database and linked to entities successfully!")
            except Exception as e:
                st.error(f"Error saving taxonomy: {e}")

    # Option to save the taxonomy
    st.subheader("Save Taxonomy")
    save_format = st.selectbox("Select file format:", ["CSV", "JSON"])

    if st.session_state["taxonomy"] is not None:
        if save_format == "CSV":
            csv_data = st.session_state["taxonomy"].to_csv(index=False)
            st.download_button(
                label="Download Taxonomy as CSV",
                data=csv_data,
                file_name="taxonomy.csv",
                mime="text/csv",
            )
        elif save_format == "JSON":
            json_data = st.session_state["taxonomy"].to_json(orient="records")
            st.download_button(
                label="Download Taxonomy as JSON",
                data=json_data,
                file_name="taxonomy.json",
                mime="application/json",
            )
    else:
        st.warning("No taxonomy generated yet. Select keys to build the taxonomy.")

