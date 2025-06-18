"""
Explore Page Module for Science Data Kit

This module provides the Explore page for the Science Data Kit application.
The Explore page handles visualizing and analyzing data from the knowledge graph.
"""

import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
import json

from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.ui.components.sidebar import render_database_sidebar
from science_data_kit.core.db.db_manager import db_manager

class ExplorePage(BasePage):
    """
    Explore page for visualizing and analyzing data.
    
    This page provides functionality for:
    - Viewing schema visualizations
    - Extracting and exploring node data
    - Exporting data for further analysis
    """
    
    def __init__(self):
        """Initialize the Explore page."""
        super().__init__("Explore", "🏞️")
        self._setup_sidebar()
        self.db_manager = db_manager
        
        # Initialize session state variables
        if "schema_data" not in st.session_state:
            st.session_state["schema_data"] = None
        
        if "query_results" not in st.session_state:
            st.session_state["query_results"] = None
        
        if "current_query" not in st.session_state:
            st.session_state["current_query"] = ""
    
    def _setup_sidebar(self):
        """Set up the sidebar items for the Explore page."""
        self.add_sidebar_item(
            render_database_sidebar,
            on_connect=self._on_database_connect,
            on_disconnect=self._on_database_disconnect
        )
    
    def _on_database_connect(self, uri: str, username: str, password: str, database: str):
        """
        Handle database connection.
        
        Args:
            uri: The URI of the Neo4j server.
            username: The username for authentication.
            password: The password for authentication.
            database: The name of the database to connect to.
        """
        try:
            # Update connection details
            self.db_manager.uri = uri
            self.db_manager.user = username
            self.db_manager.password = password
            self.db_manager.database = database
            
            # Connect to the database
            self.db_manager._connect()
            
            # Update session state
            st.session_state["connected"] = True
            st.session_state["neo4j_uri"] = uri
            st.session_state["neo4j_user"] = username
            st.session_state["neo4j_password"] = password
            st.session_state["neo4j_database"] = database
            
            st.success(f"Connected to Neo4j database at {uri}")
        except Exception as e:
            st.error(f"Failed to connect to Neo4j: {e}")
    
    def _on_database_disconnect(self):
        """Handle database disconnection."""
        try:
            # Close the connection
            self.db_manager.close()
            
            # Update session state
            st.session_state["connected"] = False
            
            st.success("Disconnected from Neo4j database")
        except Exception as e:
            st.error(f"Failed to disconnect from Neo4j: {e}")
    
    def _fetch_schema(self) -> Dict[str, Any]:
        """
        Fetch the database schema.
        
        Returns:
            A dictionary containing the schema data.
        """
        if not self.db_manager.is_connected():
            st.error("Not connected to Neo4j. Please connect first.")
            return {}
        
        try:
            # Fetch node labels
            labels_query = """
            MATCH (n)
            WITH DISTINCT labels(n) AS labels
            UNWIND labels AS label
            RETURN DISTINCT label
            ORDER BY label
            """
            labels_result = self.db_manager.execute_query(labels_query)
            labels = [record["label"] for record in labels_result]
            
            # Fetch relationships
            rels_query = """
            MATCH (a)-[r]->(b)
            RETURN DISTINCT
                labels(a)[0] AS source_label,
                type(r) AS relationship_type,
                labels(b)[0] AS target_label,
                count(r) AS count
            ORDER BY source_label, relationship_type, target_label
            """
            rels_result = self.db_manager.execute_query(rels_query)
            
            # Build schema data
            schema_data = {
                "labels": labels,
                "relationships": [
                    {
                        "source": record["source_label"],
                        "type": record["relationship_type"],
                        "target": record["target_label"],
                        "count": record["count"]
                    }
                    for record in rels_result
                ]
            }
            
            return schema_data
        except Exception as e:
            st.error(f"Error fetching schema: {e}")
            return {}
    
    def _create_schema_visualization(self, schema_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a visualization of the database schema.
        
        Args:
            schema_data: Dictionary containing the schema data.
            
        Returns:
            Base64-encoded image data for the visualization.
        """
        if not schema_data or not schema_data.get("relationships"):
            return None
        
        try:
            # Create a directed graph
            G = nx.DiGraph()
            
            # Add nodes
            for label in schema_data.get("labels", []):
                G.add_node(label)
            
            # Add edges
            for rel in schema_data.get("relationships", []):
                source = rel["source"]
                target = rel["target"]
                rel_type = rel["type"]
                count = rel["count"]
                
                # Add edge with attributes
                G.add_edge(source, target, type=rel_type, count=count, weight=count)
            
            # Create figure
            plt.figure(figsize=(12, 8))
            
            # Create layout
            pos = nx.spring_layout(G, k=0.5, iterations=50)
            
            # Draw nodes
            nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="lightblue", alpha=0.8)
            
            # Draw node labels
            nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, width=2, alpha=0.7, arrowsize=20)
            
            # Draw edge labels
            edge_labels = {(u, v): d["type"] for u, v, d in G.edges(data=True)}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
            
            # Set title
            plt.title("Database Schema Visualization", fontsize=16)
            
            # Remove axis
            plt.axis("off")
            
            # Save figure to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
            plt.close()
            
            # Convert to base64
            buf.seek(0)
            img_data = base64.b64encode(buf.read()).decode("utf-8")
            
            return img_data
        except Exception as e:
            st.error(f"Error creating schema visualization: {e}")
            return None
    
    def _execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a Cypher query and return the results as a DataFrame.
        
        Args:
            query: The Cypher query to execute.
            
        Returns:
            A DataFrame containing the query results.
        """
        if not self.db_manager.is_connected():
            st.error("Not connected to Neo4j. Please connect first.")
            return pd.DataFrame()
        
        try:
            # Execute the query
            results = self.db_manager.execute_query(query)
            
            # Convert to DataFrame
            df = pd.DataFrame(results)
            
            return df
        except Exception as e:
            st.error(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def _export_data(self, data: pd.DataFrame, format: str) -> Optional[bytes]:
        """
        Export data to the specified format.
        
        Args:
            data: The DataFrame to export.
            format: The format to export to (csv, excel, json).
            
        Returns:
            The exported data as bytes.
        """
        try:
            if format == "csv":
                return data.to_csv(index=False).encode("utf-8")
            elif format == "excel":
                output = io.BytesIO()
                data.to_excel(output, index=False)
                output.seek(0)
                return output.getvalue()
            elif format == "json":
                return data.to_json(orient="records", indent=2).encode("utf-8")
            else:
                st.error(f"Unsupported export format: {format}")
                return None
        except Exception as e:
            st.error(f"Error exporting data: {e}")
            return None
    
    def _get_sample_queries(self) -> Dict[str, str]:
        """
        Get a dictionary of sample queries.
        
        Returns:
            A dictionary mapping query names to query strings.
        """
        return {
            "Get all node labels": "MATCH (n) RETURN DISTINCT labels(n) AS labels",
            "Get all relationship types": "MATCH ()-[r]->() RETURN DISTINCT type(r) AS relationship_type",
            "Count nodes by label": """
                MATCH (n)
                WITH labels(n) AS labels
                UNWIND labels AS label
                RETURN label, count(*) AS count
                ORDER BY count DESC
            """,
            "Count relationships by type": """
                MATCH ()-[r]->()
                RETURN type(r) AS relationship_type, count(*) AS count
                ORDER BY count DESC
            """,
            "Find connected nodes": """
                MATCH (n)-[r]->(m)
                RETURN labels(n)[0] AS source_label, n.name AS source_name,
                       type(r) AS relationship_type,
                       labels(m)[0] AS target_label, m.name AS target_name
                LIMIT 100
            """
        }
    
    def render_content(self) -> None:
        """Render the Explore page content."""
        st.write("Visualize and analyze your data from the knowledge graph.")
        
        # Schema visualization
        st.header("Schema Visualization")
        
        if st.button("Fetch Schema"):
            if not st.session_state.get("connected", False):
                st.error("Not connected to Neo4j. Please connect first.")
            else:
                with st.spinner("Fetching schema..."):
                    schema_data = self._fetch_schema()
                    st.session_state["schema_data"] = schema_data
                    
                    if schema_data:
                        st.success("Schema fetched successfully")
                    else:
                        st.error("Failed to fetch schema")
        
        # Display schema visualization if available
        if st.session_state["schema_data"]:
            # Create visualization
            img_data = self._create_schema_visualization(st.session_state["schema_data"])
            
            if img_data:
                # Display visualization
                st.image(f"data:image/png;base64,{img_data}", use_column_width=True)
                
                # Display schema details
                with st.expander("Schema Details"):
                    # Node labels
                    st.subheader("Node Labels")
                    labels = st.session_state["schema_data"].get("labels", [])
                    st.write(f"Found {len(labels)} node labels:")
                    st.write(", ".join(labels))
                    
                    # Relationships
                    st.subheader("Relationships")
                    rels = st.session_state["schema_data"].get("relationships", [])
                    st.write(f"Found {len(rels)} relationship types:")
                    
                    # Create relationship table
                    rel_df = pd.DataFrame([
                        {
                            "Source": rel["source"],
                            "Relationship": rel["type"],
                            "Target": rel["target"],
                            "Count": rel["count"]
                        }
                        for rel in rels
                    ])
                    
                    st.dataframe(rel_df)
            else:
                st.warning("Could not create schema visualization")
        
        # Query execution
        st.header("Query Execution")
        
        # Sample queries
        sample_queries = self._get_sample_queries()
        selected_sample = st.selectbox(
            "Sample Queries",
            options=[""] + list(sample_queries.keys())
        )
        
        if selected_sample:
            st.session_state["current_query"] = sample_queries[selected_sample]
        
        # Query input
        query = st.text_area(
            "Cypher Query",
            value=st.session_state["current_query"],
            height=150
        )
        
        # Execute query button
        if st.button("Execute Query"):
            if not query:
                st.error("Please enter a query")
            elif not st.session_state.get("connected", False):
                st.error("Not connected to Neo4j. Please connect first.")
            else:
                with st.spinner("Executing query..."):
                    results = self._execute_query(query)
                    st.session_state["query_results"] = results
                    st.session_state["current_query"] = query
                    
                    if not results.empty:
                        st.success(f"Query executed successfully. Found {len(results)} results.")
                    else:
                        st.warning("Query executed successfully, but no results were returned.")
        
        # Display query results if available
        if st.session_state["query_results"] is not None and not st.session_state["query_results"].empty:
            st.subheader("Query Results")
            
            # Display results
            st.dataframe(st.session_state["query_results"])
            
            # Export options
            st.subheader("Export Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                export_format = st.selectbox(
                    "Export Format",
                    options=["csv", "excel", "json"]
                )
            
            with col2:
                if st.button("Export"):
                    # Export data
                    exported_data = self._export_data(st.session_state["query_results"], export_format)
                    
                    if exported_data:
                        # Create download button
                        st.download_button(
                            label=f"Download {export_format.upper()}",
                            data=exported_data,
                            file_name=f"query_results.{export_format}",
                            mime={
                                "csv": "text/csv",
                                "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                "json": "application/json"
                            }[export_format]
                        )
        
        # Data analysis
        if st.session_state["query_results"] is not None and not st.session_state["query_results"].empty:
            st.header("Data Analysis")
            
            # Data summary
            with st.expander("Data Summary"):
                # Display summary statistics
                st.write("Summary Statistics:")
                
                # Only include numeric columns
                numeric_cols = st.session_state["query_results"].select_dtypes(include=["number"]).columns
                
                if not numeric_cols.empty:
                    st.dataframe(st.session_state["query_results"][numeric_cols].describe())
                else:
                    st.info("No numeric columns found for summary statistics.")
                
                # Display column info
                st.write("Column Information:")
                
                # Create column info table
                col_info = pd.DataFrame([
                    {
                        "Column": col,
                        "Type": str(st.session_state["query_results"][col].dtype),
                        "Unique Values": st.session_state["query_results"][col].nunique(),
                        "Missing Values": st.session_state["query_results"][col].isna().sum()
                    }
                    for col in st.session_state["query_results"].columns
                ])
                
                st.dataframe(col_info)
            
            # Data visualization
            with st.expander("Data Visualization"):
                # Only show if there are numeric columns
                numeric_cols = st.session_state["query_results"].select_dtypes(include=["number"]).columns
                
                if not numeric_cols.empty:
                    # Select columns for visualization
                    x_col = st.selectbox("X-axis", options=st.session_state["query_results"].columns)
                    y_col = st.selectbox("Y-axis", options=numeric_cols)
                    
                    # Select chart type
                    chart_type = st.selectbox(
                        "Chart Type",
                        options=["Bar", "Line", "Scatter"]
                    )
                    
                    # Create chart
                    if chart_type == "Bar":
                        st.bar_chart(st.session_state["query_results"], x=x_col, y=y_col)
                    elif chart_type == "Line":
                        st.line_chart(st.session_state["query_results"], x=x_col, y=y_col)
                    else:  # Scatter
                        st.scatter_chart(st.session_state["query_results"], x=x_col, y=y_col)
                else:
                    st.info("No numeric columns found for visualization.")

def render():
    """Render the Explore page."""
    page = ExplorePage()
    page.render()