"""
Microsoft Graph API Visualization Components for Science Data Kit

This module provides visualization components for Microsoft Graph API data,
including organizational charts, communication networks, and document collaboration graphs.
"""

import streamlit as st
import pandas as pd
import networkx as nx
try:
    import matplotlib.pyplot as plt
except ImportError:
    st.error("matplotlib is not installed. Please install it with 'pip install matplotlib'.")
    plt = None
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Any, Union
import io
import base64

def render_organizational_chart(users_df: pd.DataFrame, manager_column: str = "manager") -> None:
    """
    Render an organizational chart based on user data from Microsoft Graph API.

    Args:
        users_df: DataFrame containing user data from Microsoft Graph API.
        manager_column: Column name containing the manager's ID or email.
    """
    if users_df.empty:
        st.warning("No user data available for organizational chart.")
        return

    # Check if manager column exists
    if manager_column not in users_df.columns:
        st.warning(f"Manager column '{manager_column}' not found in user data.")
        return

    # Create a graph
    G = nx.DiGraph()

    # Add nodes (users)
    for _, user in users_df.iterrows():
        user_id = user.get('id', '')
        display_name = user.get('displayName', '')
        job_title = user.get('jobTitle', '')
        department = user.get('department', '')

        # Add node with attributes
        G.add_node(
            user_id,
            name=display_name,
            title=job_title,
            department=department
        )

    # Add edges (manager relationships)
    for _, user in users_df.iterrows():
        user_id = user.get('id', '')
        manager_id = user.get(manager_column, '')

        if manager_id and manager_id in G:
            G.add_edge(manager_id, user_id)

    # Create a hierarchical layout
    pos = nx.nx_agraph.graphviz_layout(G, prog='dot')

    # Create the figure
    fig, ax = plt.subplots(figsize=(12, 10))

    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos,
        node_color='skyblue',
        node_size=500,
        alpha=0.8
    )

    # Draw edges
    nx.draw_networkx_edges(
        G, pos,
        arrows=True,
        arrowsize=15,
        width=1.5,
        alpha=0.7
    )

    # Draw labels
    node_labels = {node: f"{G.nodes[node]['name']}\n{G.nodes[node]['title']}" for node in G.nodes()}
    nx.draw_networkx_labels(
        G, pos,
        labels=node_labels,
        font_size=8,
        font_weight='bold'
    )

    plt.axis('off')
    plt.title('Organizational Chart')

    # Display the figure
    st.pyplot(fig)

    # Add download button
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)

    btn = st.download_button(
        label="Download Organizational Chart",
        data=buf,
        file_name="organizational_chart.png",
        mime="image/png"
    )

def render_communication_network(messages_df: pd.DataFrame) -> None:
    """
    Render a communication network based on message data from Microsoft Graph API.

    Args:
        messages_df: DataFrame containing message data from Microsoft Graph API.
    """
    if messages_df.empty:
        st.warning("No message data available for communication network.")
        return

    # Check if required columns exist
    required_columns = ['from', 'toRecipients']
    for col in required_columns:
        if col not in messages_df.columns:
            st.warning(f"Required column '{col}' not found in message data.")
            return

    # Create a graph
    G = nx.Graph()

    # Process messages to extract sender and recipients
    for _, message in messages_df.iterrows():
        # Extract sender
        sender = None
        if isinstance(message['from'], dict) and 'emailAddress' in message['from']:
            sender = message['from']['emailAddress'].get('address', '')

        # Extract recipients
        recipients = []
        if isinstance(message['toRecipients'], list):
            for recipient in message['toRecipients']:
                if isinstance(recipient, dict) and 'emailAddress' in recipient:
                    email = recipient['emailAddress'].get('address', '')
                    if email:
                        recipients.append(email)

        # Add nodes and edges
        if sender and recipients:
            if sender not in G:
                G.add_node(sender, type='sender')

            for recipient in recipients:
                if recipient not in G:
                    G.add_node(recipient, type='recipient')

                # Add or update edge weight (number of messages)
                if G.has_edge(sender, recipient):
                    G[sender][recipient]['weight'] += 1
                else:
                    G.add_edge(sender, recipient, weight=1)

    # Check if graph has nodes
    if not G.nodes():
        st.warning("No valid communication data found for network visualization.")
        return

    # Create a spring layout
    pos = nx.spring_layout(G, k=0.3, iterations=50)

    # Create the figure
    fig, ax = plt.subplots(figsize=(12, 10))

    # Draw nodes with different colors for senders and recipients
    sender_nodes = [node for node, attr in G.nodes(data=True) if attr.get('type') == 'sender']
    recipient_nodes = [node for node, attr in G.nodes(data=True) if attr.get('type') == 'recipient']

    nx.draw_networkx_nodes(
        G, pos,
        nodelist=sender_nodes,
        node_color='red',
        node_size=300,
        alpha=0.8,
        label='Senders'
    )

    nx.draw_networkx_nodes(
        G, pos,
        nodelist=recipient_nodes,
        node_color='blue',
        node_size=200,
        alpha=0.8,
        label='Recipients'
    )

    # Draw edges with width based on weight
    edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
    nx.draw_networkx_edges(
        G, pos,
        width=[w/max(edge_weights)*5 for w in edge_weights],
        alpha=0.5
    )

    # Draw labels
    nx.draw_networkx_labels(
        G, pos,
        font_size=8
    )

    plt.axis('off')
    plt.title('Communication Network')
    plt.legend()

    # Display the figure
    st.pyplot(fig)

    # Add download button
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)

    btn = st.download_button(
        label="Download Communication Network",
        data=buf,
        file_name="communication_network.png",
        mime="image/png"
    )

def render_document_collaboration_graph(files_df: pd.DataFrame, users_df: pd.DataFrame) -> None:
    """
    Render a document collaboration graph based on file and user data from Microsoft Graph API.

    Args:
        files_df: DataFrame containing file data from Microsoft Graph API.
        users_df: DataFrame containing user data from Microsoft Graph API.
    """
    if files_df.empty or users_df.empty:
        st.warning("No file or user data available for document collaboration graph.")
        return

    # Check if required columns exist
    file_required_columns = ['id', 'name', 'lastModifiedBy']
    for col in file_required_columns:
        if col not in files_df.columns:
            st.warning(f"Required column '{col}' not found in file data.")
            return

    # Create a graph
    G = nx.Graph()

    # Add nodes for users
    for _, user in users_df.iterrows():
        user_id = user.get('id', '')
        display_name = user.get('displayName', '')

        if user_id:
            G.add_node(user_id, type='user', name=display_name)

    # Add nodes for files and edges for collaboration
    for _, file in files_df.iterrows():
        file_id = file.get('id', '')
        file_name = file.get('name', '')

        if file_id:
            G.add_node(file_id, type='file', name=file_name)

            # Add edge for last modifier
            last_modified_by = None
            if isinstance(file['lastModifiedBy'], dict) and 'user' in file['lastModifiedBy']:
                last_modified_by = file['lastModifiedBy']['user'].get('id', '')

            if last_modified_by and last_modified_by in G:
                G.add_edge(last_modified_by, file_id, relationship='modified')

    # Check if graph has nodes
    if not G.nodes():
        st.warning("No valid collaboration data found for graph visualization.")
        return

    # Create a spring layout
    pos = nx.spring_layout(G, k=0.3, iterations=50)

    # Create the figure
    fig, ax = plt.subplots(figsize=(12, 10))

    # Draw nodes with different colors for users and files
    user_nodes = [node for node, attr in G.nodes(data=True) if attr.get('type') == 'user']
    file_nodes = [node for node, attr in G.nodes(data=True) if attr.get('type') == 'file']

    nx.draw_networkx_nodes(
        G, pos,
        nodelist=user_nodes,
        node_color='green',
        node_size=300,
        alpha=0.8,
        label='Users'
    )

    nx.draw_networkx_nodes(
        G, pos,
        nodelist=file_nodes,
        node_color='orange',
        node_size=200,
        alpha=0.8,
        label='Files'
    )

    # Draw edges
    nx.draw_networkx_edges(
        G, pos,
        width=1.5,
        alpha=0.5
    )

    # Draw labels
    node_labels = {node: G.nodes[node]['name'] for node in G.nodes()}
    nx.draw_networkx_labels(
        G, pos,
        labels=node_labels,
        font_size=8
    )

    plt.axis('off')
    plt.title('Document Collaboration Graph')
    plt.legend()

    # Display the figure
    st.pyplot(fig)

    # Add download button
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)

    btn = st.download_button(
        label="Download Document Collaboration Graph",
        data=buf,
        file_name="document_collaboration_graph.png",
        mime="image/png"
    )

def render_interactive_org_chart(users_df: pd.DataFrame, manager_column: str = "manager") -> None:
    """
    Render an interactive organizational chart using Plotly.

    Args:
        users_df: DataFrame containing user data from Microsoft Graph API.
        manager_column: Column name containing the manager's ID or email.
    """
    if users_df.empty:
        st.warning("No user data available for organizational chart.")
        return

    # Check if manager column exists
    if manager_column not in users_df.columns:
        st.warning(f"Manager column '{manager_column}' not found in user data.")
        return

    # Create a hierarchical structure
    org_data = []

    for _, user in users_df.iterrows():
        user_id = user.get('id', '')
        display_name = user.get('displayName', '')
        job_title = user.get('jobTitle', '')
        department = user.get('department', '')
        manager_id = user.get(manager_column, '')

        org_data.append({
            'id': user_id,
            'name': display_name,
            'title': job_title,
            'department': department,
            'parent': manager_id if manager_id else ''
        })

    # Create a DataFrame for the org chart
    org_df = pd.DataFrame(org_data)

    # Create a Plotly figure
    fig = go.Figure()

    # Add nodes
    for _, row in org_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[0],
            y=[0],
            mode='markers+text',
            marker=dict(size=20, color='skyblue'),
            text=row['name'],
            textposition='bottom center',
            hoverinfo='text',
            hovertext=f"Name: {row['name']}<br>Title: {row['title']}<br>Department: {row['department']}",
            name=row['id']
        ))

    # Add edges
    for _, row in org_df.iterrows():
        if row['parent'] and row['parent'] in org_df['id'].values:
            parent_idx = org_df[org_df['id'] == row['parent']].index[0]
            child_idx = org_df[org_df['id'] == row['id']].index[0]

            fig.add_trace(go.Scatter(
                x=[parent_idx, child_idx],
                y=[0, 0],
                mode='lines',
                line=dict(width=1, color='gray'),
                hoverinfo='none',
                showlegend=False
            ))

    # Update layout
    fig.update_layout(
        title='Interactive Organizational Chart',
        showlegend=False,
        hovermode='closest',
        margin=dict(b=40, l=40, r=40, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        width=800,
        height=600
    )

    # Display the figure
    st.plotly_chart(fig)

def render_msgraph_visualizations(data_type: str, data: pd.DataFrame, users_df: Optional[pd.DataFrame] = None) -> None:
    """
    Render visualizations for Microsoft Graph API data.

    Args:
        data_type: Type of data to visualize ('users', 'messages', 'files').
        data: DataFrame containing the data to visualize.
        users_df: Optional DataFrame containing user data (required for some visualizations).
    """
    if data_type == 'users':
        st.subheader("Organizational Chart")
        render_organizational_chart(data)

        st.subheader("Interactive Organizational Chart")
        render_interactive_org_chart(data)

        st.subheader("Department Distribution")
        if 'department' in data.columns:
            dept_counts = data['department'].value_counts().reset_index()
            dept_counts.columns = ['Department', 'Count']

            fig = px.pie(dept_counts, values='Count', names='Department', title='Department Distribution')
            st.plotly_chart(fig)
        else:
            st.warning("Department column not found in user data.")

    elif data_type == 'messages':
        st.subheader("Communication Network")
        render_communication_network(data)

        st.subheader("Message Timeline")
        if 'receivedDateTime' in data.columns:
            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(data['receivedDateTime']):
                data['receivedDateTime'] = pd.to_datetime(data['receivedDateTime'])

            # Group by date
            data['date'] = data['receivedDateTime'].dt.date
            message_counts = data.groupby('date').size().reset_index()
            message_counts.columns = ['Date', 'Count']

            fig = px.line(message_counts, x='Date', y='Count', title='Message Timeline')
            st.plotly_chart(fig)
        else:
            st.warning("receivedDateTime column not found in message data.")

    elif data_type == 'files':
        st.subheader("Document Collaboration Graph")
        if users_df is not None:
            render_document_collaboration_graph(data, users_df)
        else:
            st.warning("User data is required for document collaboration graph.")

        st.subheader("File Type Distribution")
        if 'file' in data.columns and isinstance(data['file'].iloc[0], dict) and 'mimeType' in data['file'].iloc[0]:
            # Extract mime types
            mime_types = [file.get('mimeType', '') for file in data['file'] if isinstance(file, dict)]
            mime_df = pd.DataFrame({'MimeType': mime_types})
            mime_counts = mime_df['MimeType'].value_counts().reset_index()
            mime_counts.columns = ['MimeType', 'Count']

            fig = px.pie(mime_counts, values='Count', names='MimeType', title='File Type Distribution')
            st.plotly_chart(fig)
        else:
            st.warning("File mime type information not found in file data.")

    else:
        st.warning(f"Unsupported data type: {data_type}")
