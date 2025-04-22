import streamlit as st
import pandas as pd
from io import BytesIO
from utils.database import get_neo4j_session, create_pyvis_graph, fetch_nodes_by_label

# st.sidebar.title("Connect")

if st.session_state.connected:

    # Schema Sampling Section
    # st.sidebar.title("Schema Sample")

    from utils.sidebar import schema_sample_widget
    schema_sample_widget()
    # with st.sidebar.expander("🕷️ Schema Sampling", expanded=False):
    #     uri = st.session_state['neo4j_uri']
    #     user = st.session_state['neo4j_user']
    #     password = st.session_state['neo4j_password']
    #
    #     st.text("Summarize schema of recall query")
    #     sample_mag = st.number_input("Order (1E??)", min_value=1, value=3, step=1)
    #     sample_size = 10**sample_mag
    #     st.text(f"Randomly sampling {sample_size} nodes")
    #     include_all = st.checkbox("Include All (No Limit)", value=False)
    #     layout = st.radio("Schema Layout", ["Hierarchical", "Force-Directed"], index=1)
    #     physics_enabled = st.checkbox("Elasticity", value=False)
    #
    #     if st.button("Pull Schema"):
    #         session = get_neo4j_session(uri, user, password, database=st.session_state.selected_db)
    #         limit_clause = "" if include_all else f"LIMIT {sample_size}"
    #         with_clause = recall_query.strip() if recall_query.strip() else ""
    #         query = f"""
    #         {with_clause}
    #         MATCH (n)-[r]->(m)
    #         RETURN labels(n)[0] AS subjectLabel, type(r) AS predicateType, labels(m)[0] AS objectLabel
    #         {limit_clause}
    #         """
    #         with st.spinner("Sampling schema..."):
    #             results = session.run(query)
    #             results_list = [record.data() for record in results]
    #             st.success(f"Sampled {len(results_list)} rows from the schema!")
    #             triples, nodes = extract_schema(results_list)
    #             st.session_state.cached_triples = triples
    #             st.session_state.cached_labels = sorted(nodes)  # Ensure this is updated

    # Graph Visualization
    if "cached_triples" in st.session_state:
        with st.expander("Schema", expanded=True):
            net = create_pyvis_graph(
                st.session_state.cached_triples,
                st.session_state.cached_layout,
                st.session_state.cached_physics_enabled
            )
            net_html = net.generate_html()
            st.components.v1.html(net_html, height=800)

    # Node Data Extraction
    # st.sidebar.title("Node Label Index")
    if "cached_labels" in st.session_state:
        with st.sidebar.expander("📇 Label Index", expanded=False):

            selected_labels = st.multiselect("Labels", st.session_state.cached_labels)

            if st.button("Pull Index"):
                with st.spinner(f"Fetching nodes for labels: {', '.join(selected_labels)}"):
                    session = get_neo4j_session(
                        st.session_state.neo4j_uri,
                        st.session_state.neo4j_user,
                        st.session_state.neo4j_password,
                        database=st.session_state.selected_db
                    )
                    node_dataframes = {}
                    for label in selected_labels:
                        node_data = fetch_nodes_by_label(
                            session,
                            label,
                            st.session_state.recall_query.strip())
                        node_dataframes[label] = pd.DataFrame(node_data)
                    st.session_state.node_dataframes = node_dataframes

    if "node_dataframes" in st.session_state:
        with st.expander("Nodes", expanded=True):
            tabs = st.tabs(st.session_state.node_dataframes.keys())
            for label, tab in zip(st.session_state.node_dataframes.keys(), tabs):
                with tab:
                    st.write(f"Nodes: {label}")
                    try:
                        # Try to display the full dataframe
                        st.dataframe(st.session_state.node_dataframes[label], use_container_width=True)
                    except Exception as e:
                        if "MessageSizeError" in str(e) or "exceeds the message size limit" in str(e):
                            # If the dataframe is too large, show an abbreviated version
                            st.warning("The node data is too large to display in full. Showing abbreviated version (first 1000 rows).")

                            # Create an abbreviated dataframe
                            abbreviated_df = st.session_state.node_dataframes[label].head(1000)
                            st.dataframe(abbreviated_df, use_container_width=True)

                            # Remind user about export options
                            st.info("Use the export options below to download the complete data.")
                        else:
                            # If it's a different error, show it
                            st.error(f"Error displaying node data: {e}")

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
else:
    st.sidebar.success("Link database (DB) to recall and explore ontological maps stored in a graph")
