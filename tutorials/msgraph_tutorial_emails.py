"""
Microsoft Graph API Tutorial: Email Analysis

This tutorial demonstrates how to use the Microsoft Graph API integration
with the Science Data Kit (SDK) to analyze emails in Microsoft 365.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import networkx as nx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import re
from collections import Counter

from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
from science_data_kit.core.db.msgraph_adapter import MSGraphAdapter
from science_data_kit.ui.components.msgraph_visualizations import render_communication_network


def connect_to_msgraph() -> Optional[MSGraphConnectionManager]:
    """
    Connect to Microsoft Graph API using configuration from environment variables or user input.
    
    Returns:
        MSGraphConnectionManager: The connection manager if connection is successful, None otherwise.
    """
    # Try to get configuration from environment variables
    tenant_id = os.environ.get("MSGRAPH_TENANT_ID")
    client_id = os.environ.get("MSGRAPH_CLIENT_ID")
    client_secret = os.environ.get("MSGRAPH_CLIENT_SECRET")
    auth_method = os.environ.get("MSGRAPH_AUTH_METHOD", "device_code")
    
    # If running in Streamlit, allow user input
    if st._is_running_with_streamlit:
        st.title("Microsoft Graph API: Email Analysis")
        
        st.header("Connect to Microsoft Graph API")
        
        # Authentication method selection
        auth_method = st.selectbox(
            "Authentication Method",
            ["device_code", "client_credentials", "interactive"],
            index=0 if auth_method not in ["client_credentials", "interactive"] else 
                  (1 if auth_method == "client_credentials" else 2)
        )
        
        # Tenant ID and Client ID
        tenant_id = st.text_input("Tenant ID", value=tenant_id or "")
        client_id = st.text_input("Client ID", value=client_id or "")
        
        # Client Secret (only for client_credentials)
        if auth_method == "client_credentials":
            client_secret = st.text_input("Client Secret", value=client_secret or "", type="password")
        
        # Connect button
        if not st.button("Connect to Microsoft Graph API"):
            st.info("Please enter your credentials and click 'Connect to Microsoft Graph API'")
            return None
    
    # Create connection manager
    connection_manager = MSGraphConnectionManager(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret if auth_method == "client_credentials" else None,
        auth_method=auth_method
    )
    
    # Connect to Microsoft Graph API
    if connection_manager.connect():
        if st._is_running_with_streamlit:
            st.success("Connected to Microsoft Graph API")
        else:
            print("Connected to Microsoft Graph API")
        return connection_manager
    else:
        if st._is_running_with_streamlit:
            st.error("Failed to connect to Microsoft Graph API")
        else:
            print("Failed to connect to Microsoft Graph API")
        return None


def get_emails(connection_manager: MSGraphConnectionManager, days: int = 30, top: int = 100) -> pd.DataFrame:
    """
    Get emails from the last specified number of days.
    
    Args:
        connection_manager: The Microsoft Graph API connection manager.
        days: Number of days to look back.
        top: Maximum number of emails to retrieve.
        
    Returns:
        pd.DataFrame: DataFrame containing email information.
    """
    # Calculate the date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format dates for the filter
    start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Get emails
    emails = connection_manager.query_to_dataframe('/me/messages', {
        'select': 'id,subject,receivedDateTime,from,toRecipients,ccRecipients,importance,hasAttachments,bodyPreview',
        'filter': f"receivedDateTime ge {start_date_str}",
        'orderby': 'receivedDateTime desc',
        'top': top
    })
    
    if st._is_running_with_streamlit:
        st.header("Emails")
        st.write(f"Found {len(emails)} emails from the last {days} days")
        
        # Allow user to adjust parameters
        with st.expander("Adjust Parameters"):
            new_days = st.slider("Days to look back", min_value=1, max_value=365, value=days)
            new_top = st.slider("Maximum number of emails", min_value=10, max_value=500, value=top)
            
            if new_days != days or new_top != top:
                if st.button("Refresh Emails"):
                    return get_emails(connection_manager, new_days, new_top)
    else:
        print(f"Found {len(emails)} emails from the last {days} days")
    
    return emails


def analyze_email_volume(emails: pd.DataFrame) -> None:
    """
    Analyze email volume over time.
    
    Args:
        emails: DataFrame containing email information.
    """
    if emails.empty:
        if st._is_running_with_streamlit:
            st.warning("No emails found")
        else:
            print("No emails found")
        return
    
    # Convert receivedDateTime to datetime if it's not already
    if 'receivedDateTime' in emails.columns:
        if not pd.api.types.is_datetime64_any_dtype(emails['receivedDateTime']):
            emails['receivedDateTime'] = pd.to_datetime(emails['receivedDateTime'])
        
        # Extract date
        emails['date'] = emails['receivedDateTime'].dt.date
        
        # Count emails by date
        email_counts = emails.groupby('date').size().reset_index(name='count')
        
        if st._is_running_with_streamlit:
            st.header("Email Volume Analysis")
            
            # Plot email volume over time
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(email_counts['date'], email_counts['count'], marker='o')
            ax.set_xlabel('Date')
            ax.set_ylabel('Number of Emails')
            ax.set_title('Email Volume Over Time')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            st.pyplot(fig)
            
            # Email volume by day of week
            emails['day_of_week'] = emails['receivedDateTime'].dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_counts = emails['day_of_week'].value_counts().reindex(day_order).reset_index()
            day_counts.columns = ['Day of Week', 'Count']
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(day_counts['Day of Week'], day_counts['Count'])
            ax.set_xlabel('Day of Week')
            ax.set_ylabel('Number of Emails')
            ax.set_title('Email Volume by Day of Week')
            plt.tight_layout()
            
            st.pyplot(fig)
            
            # Email volume by hour of day
            emails['hour_of_day'] = emails['receivedDateTime'].dt.hour
            hour_counts = emails['hour_of_day'].value_counts().sort_index().reset_index()
            hour_counts.columns = ['Hour of Day', 'Count']
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.bar(hour_counts['Hour of Day'], hour_counts['Count'])
            ax.set_xlabel('Hour of Day')
            ax.set_ylabel('Number of Emails')
            ax.set_title('Email Volume by Hour of Day')
            ax.set_xticks(range(0, 24))
            plt.tight_layout()
            
            st.pyplot(fig)
        else:
            print("\nEmail Volume Analysis:")
            print("\nEmail Volume by Date:")
            print(email_counts)
            
            # Email volume by day of week
            emails['day_of_week'] = emails['receivedDateTime'].dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_counts = emails['day_of_week'].value_counts().reindex(day_order)
            
            print("\nEmail Volume by Day of Week:")
            print(day_counts)
            
            # Email volume by hour of day
            emails['hour_of_day'] = emails['receivedDateTime'].dt.hour
            hour_counts = emails['hour_of_day'].value_counts().sort_index()
            
            print("\nEmail Volume by Hour of Day:")
            print(hour_counts)


def analyze_senders_recipients(emails: pd.DataFrame) -> None:
    """
    Analyze email senders and recipients.
    
    Args:
        emails: DataFrame containing email information.
    """
    if emails.empty:
        if st._is_running_with_streamlit:
            st.warning("No emails found")
        else:
            print("No emails found")
        return
    
    # Extract senders
    senders = []
    if 'from' in emails.columns:
        for sender in emails['from']:
            if isinstance(sender, dict) and 'emailAddress' in sender:
                email = sender['emailAddress'].get('address', '')
                name = sender['emailAddress'].get('name', '')
                if email:
                    senders.append((email, name))
    
    # Extract recipients
    recipients = []
    if 'toRecipients' in emails.columns:
        for to_list in emails['toRecipients']:
            if isinstance(to_list, list):
                for recipient in to_list:
                    if isinstance(recipient, dict) and 'emailAddress' in recipient:
                        email = recipient['emailAddress'].get('address', '')
                        name = recipient['emailAddress'].get('name', '')
                        if email:
                            recipients.append((email, name))
    
    # Extract CC recipients
    cc_recipients = []
    if 'ccRecipients' in emails.columns:
        for cc_list in emails['ccRecipients']:
            if isinstance(cc_list, list):
                for recipient in cc_list:
                    if isinstance(recipient, dict) and 'emailAddress' in recipient:
                        email = recipient['emailAddress'].get('address', '')
                        name = recipient['emailAddress'].get('name', '')
                        if email:
                            cc_recipients.append((email, name))
    
    if st._is_running_with_streamlit:
        st.header("Sender and Recipient Analysis")
        
        # Top senders
        if senders:
            sender_counts = Counter([s[0] for s in senders])
            top_senders = pd.DataFrame(sender_counts.most_common(10), columns=['Sender', 'Count'])
            
            st.subheader("Top Senders")
            st.dataframe(top_senders)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(top_senders['Sender'], top_senders['Count'])
            ax.set_xlabel('Sender')
            ax.set_ylabel('Number of Emails')
            ax.set_title('Top Email Senders')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            st.pyplot(fig)
        
        # Top recipients
        if recipients:
            recipient_counts = Counter([r[0] for r in recipients])
            top_recipients = pd.DataFrame(recipient_counts.most_common(10), columns=['Recipient', 'Count'])
            
            st.subheader("Top Recipients")
            st.dataframe(top_recipients)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(top_recipients['Recipient'], top_recipients['Count'])
            ax.set_xlabel('Recipient')
            ax.set_ylabel('Number of Emails')
            ax.set_title('Top Email Recipients')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            st.pyplot(fig)
        
        # Top domains
        all_emails = [s[0] for s in senders] + [r[0] for r in recipients] + [r[0] for r in cc_recipients]
        domains = [email.split('@')[1] for email in all_emails if '@' in email]
        domain_counts = Counter(domains)
        top_domains = pd.DataFrame(domain_counts.most_common(10), columns=['Domain', 'Count'])
        
        st.subheader("Top Domains")
        st.dataframe(top_domains)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(top_domains['Domain'], top_domains['Count'])
        ax.set_xlabel('Domain')
        ax.set_ylabel('Number of Emails')
        ax.set_title('Top Email Domains')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        st.pyplot(fig)
    else:
        print("\nSender and Recipient Analysis:")
        
        # Top senders
        if senders:
            sender_counts = Counter([s[0] for s in senders])
            print("\nTop Senders:")
            for sender, count in sender_counts.most_common(10):
                print(f"{sender}: {count}")
        
        # Top recipients
        if recipients:
            recipient_counts = Counter([r[0] for r in recipients])
            print("\nTop Recipients:")
            for recipient, count in recipient_counts.most_common(10):
                print(f"{recipient}: {count}")
        
        # Top domains
        all_emails = [s[0] for s in senders] + [r[0] for r in recipients] + [r[0] for r in cc_recipients]
        domains = [email.split('@')[1] for email in all_emails if '@' in email]
        domain_counts = Counter(domains)
        print("\nTop Domains:")
        for domain, count in domain_counts.most_common(10):
            print(f"{domain}: {count}")


def analyze_subject_keywords(emails: pd.DataFrame) -> None:
    """
    Analyze keywords in email subjects.
    
    Args:
        emails: DataFrame containing email information.
    """
    if emails.empty or 'subject' not in emails.columns:
        if st._is_running_with_streamlit:
            st.warning("No emails or subject data found")
        else:
            print("No emails or subject data found")
        return
    
    # Extract words from subjects
    words = []
    for subject in emails['subject']:
        if isinstance(subject, str):
            # Remove special characters and split into words
            clean_subject = re.sub(r'[^\w\s]', '', subject.lower())
            words.extend(clean_subject.split())
    
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'of', 'from'}
    filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
    
    # Count word frequencies
    word_counts = Counter(filtered_words)
    
    if st._is_running_with_streamlit:
        st.header("Subject Keyword Analysis")
        
        # Top keywords
        top_keywords = pd.DataFrame(word_counts.most_common(20), columns=['Keyword', 'Count'])
        
        st.subheader("Top Keywords in Email Subjects")
        st.dataframe(top_keywords)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(top_keywords['Keyword'], top_keywords['Count'])
        ax.set_xlabel('Keyword')
        ax.set_ylabel('Frequency')
        ax.set_title('Top Keywords in Email Subjects')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        st.pyplot(fig)
        
        # Word cloud (if wordcloud package is available)
        try:
            from wordcloud import WordCloud
            
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_counts)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title('Word Cloud of Email Subjects')
            
            st.pyplot(fig)
        except ImportError:
            st.info("Install the 'wordcloud' package to generate word clouds.")
    else:
        print("\nSubject Keyword Analysis:")
        print("\nTop Keywords in Email Subjects:")
        for word, count in word_counts.most_common(20):
            print(f"{word}: {count}")


def create_communication_network(emails: pd.DataFrame) -> None:
    """
    Create a communication network visualization based on email data.
    
    Args:
        emails: DataFrame containing email information.
    """
    if emails.empty:
        if st._is_running_with_streamlit:
            st.warning("No emails found")
        else:
            print("No emails found")
        return
    
    if st._is_running_with_streamlit:
        st.header("Communication Network")
        
        try:
            # Use the visualization component from the SDK
            render_communication_network(emails)
        except Exception as e:
            st.error(f"Error creating communication network: {str(e)}")
            
            # Fallback to manual network creation
            st.info("Creating a simplified communication network...")
            
            # Create a graph
            G = nx.Graph()
            
            # Extract senders and recipients
            for _, email in emails.iterrows():
                sender = None
                if isinstance(email.get('from'), dict) and 'emailAddress' in email['from']:
                    sender = email['from']['emailAddress'].get('address', '')
                
                recipients = []
                if isinstance(email.get('toRecipients'), list):
                    for recipient in email['toRecipients']:
                        if isinstance(recipient, dict) and 'emailAddress' in recipient:
                            recipient_email = recipient['emailAddress'].get('address', '')
                            if recipient_email:
                                recipients.append(recipient_email)
                
                # Add nodes and edges
                if sender and recipients:
                    if sender not in G:
                        G.add_node(sender, type='sender')
                    
                    for recipient in recipients:
                        if recipient not in G:
                            G.add_node(recipient, type='recipient')
                        
                        # Add or update edge weight (number of emails)
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
            max_weight = max(edge_weights) if edge_weights else 1
            nx.draw_networkx_edges(
                G, pos,
                width=[w/max_weight*5 for w in edge_weights],
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
            
            st.pyplot(fig)
    else:
        print("\nCommunication Network:")
        print("This feature requires a graphical environment.")


def main():
    """Main function to run the tutorial."""
    # Connect to Microsoft Graph API
    connection_manager = connect_to_msgraph()
    
    if connection_manager:
        # Get emails
        emails = get_emails(connection_manager)
        
        # Analyze email volume
        analyze_email_volume(emails)
        
        # Analyze senders and recipients
        analyze_senders_recipients(emails)
        
        # Analyze subject keywords
        analyze_subject_keywords(emails)
        
        # Create communication network
        create_communication_network(emails)
        
        if not st._is_running_with_streamlit:
            print("\nTutorial completed successfully!")


if __name__ == "__main__":
    # Check if running with Streamlit
    if not hasattr(st, "_is_running_with_streamlit"):
        st._is_running_with_streamlit = False
    
    main()