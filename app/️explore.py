import streamlit as st
import pandas as pd
from io import BytesIO
from utils.database import get_neo4j_session, create_pyvis_graph, fetch_nodes_by_label, manage_queries, extract_schema

# st.sidebar.title("Connect")

if st.session_state.connected:

    # Schema Sampling Section
    # st.sidebar.title("Schema Sample")
    with st.sidebar.expander("🕸️ Schema Recall", expanded=False):
        # Initialize recall_query in session_state
        if "recall_query" not in st.session_state:
            st.session_state.recall_query = "MATCH (n)-[r]->(m)\nWITH DISTINCT n, r, m "
    
        # Callback function to handle query updates
        def update_recall_query():
            st.session_state.recall_query = st.session_state.recall_query_input
    
        st.text_area(
            "Recall Query",
            value=st.session_state.recall_query,
            key="recall_query_input",
            on_change=update_recall_query,
        )

        recall_query = manage_queries(st.session_state.recall_query)

        st.session_state.recall_query = recall_query
        if st.button('Update'):
            st.success(f"Updated.'")
            st.rerun()


    with st.sidebar.expander("🕷️ Schema Sampling", expanded=False):
        uri = st.session_state['neo4j_uri']
        user = st.session_state['neo4j_user']
        password = st.session_state['neo4j_password']

        st.text("Summarize schema of recall query")
        sample_mag = st.number_input("Order (1E??)", min_value=1, value=3, step=1)
        sample_size = 10**sample_mag
        st.text(f"Randomly sampling {sample_size} nodes")
        include_all = st.checkbox("Include All (No Limit)", value=False)        
        layout = st.radio("Schema Layout", ["Hierarchical", "Force-Directed"], index=1)
        physics_enabled = st.checkbox("Elasticity", value=False)

        if st.button("Pull Schema"):
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
        with st.expander("Schema", expanded=True):
            net = create_pyvis_graph(st.session_state.cached_triples, layout,
                                     physics_enabled)
            net_html = net.generate_html()
            st.components.v1.html(net_html, height=800)

    # Node Data Extraction
    # st.sidebar.title("Node Label Index")
    if "cached_labels" in st.session_state:
        with st.sidebar.expander("📇 Label Index", expanded=False):

            selected_labels = st.multiselect("Labels", st.session_state.cached_labels)
    
            if st.button("Pull Index"):
                with st.spinner(f"Fetching nodes for labels: {', '.join(selected_labels)}"):
                    session = get_neo4j_session(uri, user, password, database=st.session_state.selected_db)
                    node_dataframes = {}
                    for label in selected_labels:
                        node_data = fetch_nodes_by_label(session, label, recall_query.strip())
                        node_dataframes[label] = pd.DataFrame(node_data)
                    st.session_state.node_dataframes = node_dataframes

    if "node_dataframes" in st.session_state:
        with st.expander("Nodes", expanded=True):
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
else:
    st.sidebar.success("Link database (DB) to recall and explore ontological maps stored in a graph")
