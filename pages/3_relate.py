import streamlit as st
import pandas as pd

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

# Initialize session state variables
if "entities_df" not in st.session_state:
    st.session_state["entities_df"] = None
if "taxonomy_keys" not in st.session_state:
    st.session_state["taxonomy_keys"] = []
if "taxonomy" not in st.session_state:
    st.session_state["taxonomy"] = None

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

# If the dataframe is loaded, proceed with taxonomy creation
if st.session_state["entities_df"] is not None:
    st.subheader("Select Keys for Taxonomy")

    # Display available keys
    available_keys = st.session_state["entities_df"].columns.tolist()
    selected_keys = st.multiselect(
        "Select keys to define taxonomy levels:",
        options=available_keys,
        default=st.session_state["taxonomy_keys"]
    )

    # Update session state with selected keys
    if selected_keys:
        st.session_state["taxonomy_keys"] = selected_keys

    # Display the selected keys as the hierarchical structure
    if st.session_state["taxonomy_keys"]:
        st.subheader("Preview Taxonomy Structure")
        st.markdown("**Selected Hierarchy:**")
        for i, key in enumerate(st.session_state["taxonomy_keys"], 1):
            st.write(f"Level {i}: {key}")

        # Create the taxonomy by grouping the dataframe
        try:
            taxonomy_df = (
                st.session_state["entities_df"]
                .groupby(st.session_state["taxonomy_keys"])
                .size()
                .reset_index(name="Count")
            )
            st.session_state["taxonomy"] = taxonomy_df

            # Display the resulting taxonomy
            st.write("**Generated Taxonomy:**")
            st.dataframe(taxonomy_df, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating taxonomy: {e}")

    # # # # # Option to save the taxonomy in the database
    # # # # st.subheader("Save Taxonomy to Database")
    # # # # if st.button("Push Taxonomy to Database"):
    # # # #     with st.session_state["db_connection"].session() as session:
    # # # #         try:
    # # # #             for _, row in st.session_state["taxonomy"].iterrows():
    # # # #                 taxonomy_node = {key: row[key] for key in selected_keys}
    # # # #                 query = f"""
    # # # #                 MERGE (t:Taxonomy {taxonomy_node})
    # # # #                 ON CREATE SET t.count = {row['Count']}
    # # # #                 ON MATCH SET t.count = {row['Count']}
    # # # #                 """
    # # # #                 session.run(query)
    # # # #             st.success("Taxonomy pushed to database successfully!")
    # # # #         except Exception as e:
    # # # #             st.error(f"Error saving taxonomy: {e}")
    # # #
    # # # st.subheader("Save Taxonomy to Database")
    # # # if st.button("Push Taxonomy to Database"):
    # # #     with st.session_state["db_connection"].session() as session:
    # # #         try:
    # # #             for _, row in st.session_state["taxonomy"].iterrows():
    # # #                 prev_node = None
    # # #                 for col in st.session_state["taxonomy_keys"]:
    # # #                     instance_value = row[col]
    # # #                     query = f"""
    # # #                     MERGE (f:{col} {{is: $instance_value}})
    # # #                     RETURN f
    # # #                     """
    # # #                     result = session.run(query, instance_value=instance_value)
    # # #                     current_node = result.single()["f"]
    # # #                     if prev_node:
    # # #                         session.run(
    # # #                             """
    # # #                             MERGE (prev)-[:PART_OF]->(curr)
    # # #                             """,
    # # #                             prev=prev_node,
    # # #                             curr=current_node
    # # #                         )
    # # #                     prev_node = current_node
    # # #             st.success("Taxonomy pushed to database successfully!")
    # # #         except Exception as e:
    # # #             st.error(f"Error saving taxonomy: {e}")
    # #
    # # # Option to save the taxonomy in the database
    # # st.subheader("Save Taxonomy to Database")
    # # if st.button("Push Taxonomy to Database"):
    # #     with st.session_state["db_connection"].session() as session:
    # #         try:
    # #             for _, row in st.session_state["taxonomy"].iterrows():
    # #                 prev_node_id = None
    # #                 for col in st.session_state["taxonomy_keys"]:
    # #                     instance_value = row[col]
    # #                     query = f"""
    # #                     MERGE (f:{col} {{is: $instance_value}})
    # #                     RETURN id(f) as node_id
    # #                     """
    # #                     result = session.run(query, instance_value=instance_value)
    # #                     current_node_id = result.single()["node_id"]
    # #
    # #                     if prev_node_id is not None:
    # #                         session.run(
    # #                             """
    # #                             MATCH (prev), (curr)
    # #                             WHERE id(prev) = $prev_id AND id(curr) = $curr_id
    # #                             MERGE (prev)-[:PART_OF]->(curr)
    # #                             """,
    # #                             prev_id=prev_node_id,
    # #                             curr_id=current_node_id
    # #                         )
    # #
    # #                     prev_node_id = current_node_id
    # #
    # #             st.success("Taxonomy pushed to database successfully!")
    # #         except Exception as e:
    # #             st.error(f"Error saving taxonomy: {e}")
    #
    # # Option to save the taxonomy in the database
    # st.subheader("Save Taxonomy to Database")
    #
    # # Select fields to match entities
    # st.subheader("Match Final Taxonomy Nodes to Entities")
    # available_columns = st.session_state["entities_df"].columns.tolist() if st.session_state[
    #                                                                             "entities_df"] is not None else []
    # match_columns = st.multiselect("Select columns to match with entity nodes:", options=available_columns)
    # entity_label = st.selectbox("Select entity label to connect to:", options=["Dataset", "Experiment", "Sample"])
    # relationship_type = st.text_input("Define Relationship Type (e.g., BELONGS_TO, PART_OF):")
    #
    # if st.button("Push Taxonomy to Database"):
    #     with st.session_state["db_connection"].session() as session:
    #         try:
    #             for _, row in st.session_state["taxonomy"].iterrows():
    #                 prev_node_id = None
    #                 for col in st.session_state["taxonomy_keys"]:
    #                     instance_value = row[col]
    #                     query = f"""
    #                     MERGE (f:{col} {{is: $instance_value}})
    #                     RETURN id(f) as node_id
    #                     """
    #                     result = session.run(query, instance_value=instance_value)
    #                     current_node_id = result.single()["node_id"]
    #
    #                     if prev_node_id is not None:
    #                         session.run(
    #                             """
    #                             MATCH (prev), (curr)
    #                             WHERE id(prev) = $prev_id AND id(curr) = $curr_id
    #                             MERGE (prev)-[:PART_OF]->(curr)
    #                             """,
    #                             prev_id=prev_node_id,
    #                             curr_id=current_node_id
    #                         )
    #                     prev_node_id = current_node_id
    #
    #                 # Match the final node with an existing entity
    #                 match_conditions = " AND ".join([f"e.{col} = $col_{col}" for col in match_columns])
    #                 match_params = {f"col_{col}": row[col] for col in match_columns}
    #                 entity_query = f"""
    #                 MATCH (e:{entity_label}) WHERE {match_conditions}
    #                 MATCH (t) WHERE id(t) = $final_node_id
    #                 MERGE (t)-[:{relationship_type}]->(e)
    #                 """
    #                 session.run(entity_query, final_node_id=prev_node_id, **match_params)
    #
    #             st.success("Taxonomy pushed to database and linked to entities successfully!")
    #         except Exception as e:
    #             st.error(f"Error saving taxonomy: {e}")

    # Fetch available entity labels from Neo4j
    def fetch_entity_labels():
        with st.session_state["db_connection"].session() as session:
            result = session.run("CALL db.labels()")
            return [record[0] for record in result]


    st.session_state["available_entity_labels"] = fetch_entity_labels()

    # Option to save the taxonomy in the database
    st.subheader("Save Taxonomy to Database")

    # Select fields to match entities
    st.subheader("Match Final Taxonomy Nodes to Entities")
    available_columns = st.session_state["entities_df"].columns.tolist() if st.session_state[
                                                                                "entities_df"] is not None else []
    match_columns = st.multiselect("Select columns to match with entity nodes:", options=available_columns)
    entity_label = st.selectbox("Select entity label to connect to:",
                                options=st.session_state["available_entity_labels"])
    relationship_type = st.text_input("Define Relationship Type (e.g., BELONGS_TO, PART_OF):")

    if st.button("Push Taxonomy to Database"):
        with st.session_state["db_connection"].session() as session:
            try:
                for _, row in st.session_state["taxonomy"].iterrows():
                    _path_id_chain = []
                    prev_node_id = None
                    for col in st.session_state["taxonomy_keys"]:
                        instance_value = row[col]
                        _path_id_chain.append(instance_value)
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

