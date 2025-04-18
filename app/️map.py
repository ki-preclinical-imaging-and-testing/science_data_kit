import streamlit as st
import pandas as pd
from pathlib import Path
from utils.models import  merge_nodes_with_existing
from utils.database import fetch_available_labels, fetch_entity_labels, fetch_node_properties, fetch_nodes_with_properties

st.session_state["available_labels"] = fetch_available_labels()

# Title and description
st.header("Entities")

with st.expander("Resolve and define node labels", expanded=True):
    # Create two columns layout
    col1, col2 = st.columns(2)

    # Right column for instructions
    with col2:
        st.markdown(
            """
            ## Review and Edit Entities
            1. Load entities from a file or database.
            2. Select label and properties.
            3. Review dataset row by row.
            4. Define relationships and push to the database.
            """
        )

    # Left column for functionality
    with col1:
        # Data source selection
        data_source = st.radio(
            "Get entities from:",
            ["File", "Database", "NCDU Scan"]
        )

        if data_source == "File":
            # File type selection
            file_type = st.radio(
                "File type:",
                ["CSV", "Excel", "JSON"]
            )

            if file_type in ["CSV", "JSON"]:
                # File uploader for CSV or JSON
                file_types = {"CSV": ["csv"], "JSON": ["json"]}
                uploaded_file = st.file_uploader(f"Upload {file_type} file:", type=file_types[file_type])
                file_path = st.text_input(f"Or enter {file_type} file path:")

                if st.button("Load File") and file_path:
                    try:
                        if file_type == "CSV":
                            st.session_state["entities_df"] = pd.read_csv(file_path)
                        else:  # JSON
                            st.session_state["entities_df"] = pd.read_json(file_path)
                        st.session_state["file_uploaded"] = file_path
                    except Exception as e:
                        st.error(f"Error loading file: {e}")

                if uploaded_file:
                    try:
                        if file_type == "CSV":
                            st.session_state["entities_df"] = pd.read_csv(uploaded_file)
                        else:  # JSON
                            st.session_state["entities_df"] = pd.read_json(uploaded_file)
                        st.session_state["file_uploaded"] = uploaded_file.name
                    except Exception as e:
                        st.error(f"Error loading file: {e}")

            elif file_type == "Excel":
                # Excel file handling with sheet selection
                uploaded_excel = st.file_uploader("Upload Excel file:", type=["xlsx", "xls"])
                excel_path = st.text_input("Or enter Excel file path:")

                excel_file = uploaded_excel if uploaded_excel else (excel_path if excel_path else None)

                if excel_file:
                    try:
                        if isinstance(excel_file, str):  # Path provided
                            xls = pd.ExcelFile(excel_path)
                        else:  # File uploaded
                            xls = pd.ExcelFile(excel_file)

                        sheet_names = xls.sheet_names
                        selected_sheet = st.selectbox("Select sheet:", options=sheet_names)

                        if st.button("Load Sheet"):
                            if isinstance(excel_file, str):  # Path provided
                                st.session_state["entities_df"] = pd.read_excel(excel_path, sheet_name=selected_sheet)
                                st.session_state["file_uploaded"] = f"{excel_path} (Sheet: {selected_sheet})"
                            else:  # File uploaded
                                st.session_state["entities_df"] = pd.read_excel(excel_file, sheet_name=selected_sheet)
                                st.session_state["file_uploaded"] = f"{uploaded_excel.name} (Sheet: {selected_sheet})"
                    except Exception as e:
                        st.error(f"Error loading Excel file: {e}")

        elif data_source == "Database":
            # Database entity loading
            if st.session_state.connected:
                st.session_state["available_entity_labels"] = fetch_entity_labels(st.session_state["db_connection"].session())
                entity_label = st.selectbox("Select Node Label:", st.session_state["available_entity_labels"])

                if entity_label and st.button("Pull Entities from Database"):
                    try:
                        properties = fetch_node_properties(st.session_state["db_connection"].session(), entity_label)
                        entities_data = fetch_nodes_with_properties(
                            st.session_state["db_connection"].session(),
                            entity_label, 
                            properties
                        )
                        st.session_state["entities_df"] = entities_data
                        st.session_state["file_uploaded"] = f"Database: {entity_label} nodes"
                        st.success(f"Loaded {len(entities_data)} entities from database")
                    except Exception as e:
                        st.error(f"Error loading entities from database: {e}")
            else:
                st.warning("Please connect to a database first")

        elif data_source == "NCDU Scan":
            # NCDU scan results handling
            ncdu_source = st.radio(
                "NCDU source:",
                ["Survey Page Results", "NCDU JSON File"]
            )

            if ncdu_source == "Survey Page Results":
                if "scanned_files" in st.session_state and not st.session_state["scanned_files"].empty:
                    if st.button("Load Survey Scan Results"):
                        st.session_state["entities_df"] = st.session_state["scanned_files"]
                        st.session_state["file_uploaded"] = "NCDU Survey Scan Results"
                else:
                    st.warning("No scan results available. Please run a scan on the Survey page first.")

            else:  # NCDU JSON File
                uploaded_ncdu = st.file_uploader("Upload NCDU JSON file:", type=["json"])
                ncdu_path = st.text_input("Or enter NCDU JSON file path:")

                if st.button("Load NCDU File") and (uploaded_ncdu or ncdu_path):
                    try:
                        import json

                        # Load the JSON file
                        if uploaded_ncdu:
                            ncdu_data = json.load(uploaded_ncdu)
                            file_source = uploaded_ncdu.name
                        else:
                            with open(ncdu_path, 'r') as f:
                                ncdu_data = json.load(f)
                            file_source = ncdu_path

                        # Parse NCDU JSON (similar to survey.py implementation)
                        def parse_ncdu_json(node, parent_path=""):
                            path = f"{parent_path}/{node['name']}" if parent_path else node["name"]
                            file_info = {
                                "Path": path,
                                "Size (Bytes)": node.get("asize", 0),
                                "Disk Usage (Bytes)": node.get("dsize", 0),
                                "Type": "Directory" if "children" in node else "File"
                            }
                            parsed_files = [file_info]
                            if "children" in node:
                                for child in node["children"]:
                                    parsed_files.extend(parse_ncdu_json(child, path))
                            return parsed_files

                        # Transform to dataframe
                        parsed_files = parse_ncdu_json(ncdu_data)
                        st.session_state["entities_df"] = pd.DataFrame(parsed_files)
                        st.session_state["file_uploaded"] = f"NCDU: {file_source}"

                    except Exception as e:
                        st.error(f"Error loading NCDU file: {e}")

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


### pasting from 03 _ relate.py (current file was previously 2_resolve

# Title and description
st.header("Structure")

with st.expander("Assemble ontology, taxonomy, or schema using properties", expanded=True):
    # Create two columns layout
    col1, col2 = st.columns(2)

    # Right column for instructions
    with col2:
        st.markdown(
            """
            ## Define Relationships and Build Taxonomy
            1. Select keys to define a hierarchical taxonomy.
            2. Rearrange or nest keys to organize the structure.
            3. Save the taxonomy schema.
            """
        )

    # Left column for functionality
    with col1:
        st.subheader("Select Data Source")

        data_source = st.radio(
            "Relate entities from:",
            ["File", "Database"]
        )

        entities_df = st.session_state.get("entities_df", None)

        if data_source == "File":
            # File type selection
            if st.session_state["entities_df"] is None:
                file_type = st.radio(
                    "File type:",
                    ["CSV", "Excel", "JSON"]
                )

                if file_type in ["CSV", "JSON"]:
                    # File uploader for CSV or JSON
                    file_types = {"CSV": ["csv"], "JSON": ["json"]}
                    uploaded_file = st.file_uploader(f"Upload {file_type} file:", type=file_types[file_type])

                    if uploaded_file:
                        try:
                            if file_type == "CSV":
                                st.session_state["entities_df"] = pd.read_csv(uploaded_file)
                            else:  # JSON
                                st.session_state["entities_df"] = pd.read_json(uploaded_file)
                            st.success(f"{file_type} file loaded successfully!")
                        except Exception as e:
                            st.error(f"Error loading file: {e}")

                elif file_type == "Excel":
                    # Excel file handling with sheet selection
                    uploaded_excel = st.file_uploader("Upload Excel file:", type=["xlsx", "xls"])

                    if uploaded_excel:
                        try:
                            xls = pd.ExcelFile(uploaded_excel)
                            sheet_names = xls.sheet_names
                            selected_sheet = st.selectbox("Select sheet:", options=sheet_names)

                            if st.button("Load Sheet"):
                                st.session_state["entities_df"] = pd.read_excel(uploaded_excel, sheet_name=selected_sheet)
                                st.success(f"Excel sheet '{selected_sheet}' loaded successfully!")
                        except Exception as e:
                            st.error(f"Error loading Excel file: {e}")

            entities_df = st.session_state["entities_df"]

        elif data_source == "Database":
            # Fetch available node labels from Neo4j
            st.session_state["available_entity_labels"] = fetch_entity_labels(st.session_state["db_connection"].session())
            # Allow the user to select a label type
            entity_label = st.selectbox("Select Node Label to Use:", st.session_state["available_entity_labels"])
            if entity_label:
                st.session_state["entity_properties"] = fetch_node_properties(st.session_state["db_connection"].session(), entity_label)
                entities_df = pd.DataFrame(columns=st.session_state['entity_properties'])

    # Move back to full width for the taxonomy creation
    with st.container():
        # If the dataframe is loaded, proceed with taxonomy creation
        if entities_df is not None:
            # Create two columns for the taxonomy section
            tax_col1, tax_col2 = st.columns(2)

            with tax_col1:
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

                st.session_state["taxonomy_set"] = st.toggle("Set Taxonomy", value=False)

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

            with tax_col2:
                # Create the taxonomy by grouping the dataframe
                if st.session_state["taxonomy_keys"]:
                    try:
                        if not st.session_state["taxonomy_set"]:
                            taxonomy_df = (
                                st.session_state["entities_df"].groupby(st.session_state["taxonomy_keys"])
                                .size()
                                .reset_index(name="Count")
                            )
                            st.session_state["taxonomy"] = taxonomy_df

                        # Display the resulting taxonomy
                        st.subheader("**Generated Taxonomy:**")
                        taxonomy_df = st.session_state["taxonomy"]
                        st.dataframe(taxonomy_df, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error generating taxonomy: {e}")
                else:
                    st.info("Select keys on the left to build a taxonomy")

                # Option to save the taxonomy in the database
                st.subheader("Save Taxonomy to Database")

                # Fetch available entity labels from Neo4j
                st.session_state["available_entity_labels"] = fetch_entity_labels(st.session_state["db_connection"].session())

                # Select fields to match entities
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
        else:
            st.warning("No file loaded yet. Please load a file or pull entities from the database.")
