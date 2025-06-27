"""
Microsoft Graph API Connection Page for Science Data Kit

This module provides a Streamlit page for connecting to Microsoft Graph API.
"""

import os
import json
import streamlit as st
from typing import Dict, Any, Optional

from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
from science_data_kit.core.db.msgraph_adapter import MSGraphAdapter
from science_data_kit.core.utils.msgraph_utils import create_msgraph_config


def msgraph_connect_page():
    """
    Render the Microsoft Graph API connection page.
    """
    st.title("Connect to Microsoft Graph API")
    
    # Check if Microsoft Graph SDK is available
    try:
        from msgraph.core import GraphClient
        from azure.identity import ClientSecretCredential, DeviceCodeCredential, InteractiveBrowserCredential
        msgraph_available = True
    except ImportError:
        msgraph_available = False
        st.error(
            "Microsoft Graph SDK is not installed. "
            "Please install it with 'pip install msgraph-sdk-python azure-identity'."
        )
        st.stop()
    
    # Create tabs for different connection methods
    tab1, tab2, tab3 = st.tabs(["Configuration", "Connection Status", "Help"])
    
    with tab1:
        st.header("Microsoft Graph API Configuration")
        
        # Authentication method selection
        auth_method = st.selectbox(
            "Authentication Method",
            ["device_code", "client_credentials", "interactive"],
            index=0,
            help="Select the authentication method to use for Microsoft Graph API."
        )
        
        # Common fields
        tenant_id = st.text_input(
            "Tenant ID",
            value=st.session_state.get("msgraph_tenant_id", ""),
            help="The tenant ID for your Microsoft 365 account."
        )
        
        client_id = st.text_input(
            "Client ID",
            value=st.session_state.get("msgraph_client_id", ""),
            help="The client ID for your application."
        )
        
        # Client secret (only for client_credentials)
        client_secret = ""
        if auth_method == "client_credentials":
            client_secret = st.text_input(
                "Client Secret",
                value=st.session_state.get("msgraph_client_secret", ""),
                type="password",
                help="The client secret for your application."
            )
        
        # Save configuration
        save_config = st.checkbox(
            "Save Configuration",
            value=False,
            help="Save the configuration to a file."
        )
        
        config_file = None
        if save_config:
            config_file = st.text_input(
                "Configuration File",
                value=st.session_state.get("msgraph_config_file", "msgraph_config.json"),
                help="The path to save the configuration to."
            )
        
        # Connect button
        if st.button("Connect to Microsoft Graph API"):
            try:
                # Save configuration if requested
                if save_config and config_file:
                    config = create_msgraph_config(
                        tenant_id=tenant_id,
                        client_id=client_id,
                        client_secret=client_secret if auth_method == "client_credentials" else None,
                        auth_method=auth_method,
                        output_file=config_file
                    )
                    st.success(f"Configuration saved to {config_file}")
                
                # Create connection manager
                connection_manager = MSGraphConnectionManager(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=client_secret if auth_method == "client_credentials" else None,
                    auth_method=auth_method,
                    config_file=config_file if save_config else None
                )
                
                # Connect to Microsoft Graph API
                if connection_manager.connect():
                    st.success("Connected to Microsoft Graph API")
                    
                    # Store connection manager in session state
                    st.session_state["msgraph_connection_manager"] = connection_manager
                    
                    # Store adapter in session state
                    st.session_state["msgraph_adapter"] = MSGraphAdapter(connection_manager=connection_manager)
                    
                    # Store configuration in session state
                    st.session_state["msgraph_tenant_id"] = tenant_id
                    st.session_state["msgraph_client_id"] = client_id
                    if auth_method == "client_credentials":
                        st.session_state["msgraph_client_secret"] = client_secret
                    st.session_state["msgraph_auth_method"] = auth_method
                    if save_config:
                        st.session_state["msgraph_config_file"] = config_file
                else:
                    st.error("Failed to connect to Microsoft Graph API")
            except Exception as e:
                st.error(f"Error connecting to Microsoft Graph API: {str(e)}")
    
    with tab2:
        st.header("Connection Status")
        
        # Check if connected
        if "msgraph_connection_manager" in st.session_state:
            connection_manager = st.session_state["msgraph_connection_manager"]
            if connection_manager.connected:
                st.success("Connected to Microsoft Graph API")
                
                # Display current user information
                try:
                    me = connection_manager.get_me()
                    st.subheader("Current User")
                    st.write(f"Display Name: {me.get('displayName', 'N/A')}")
                    st.write(f"Email: {me.get('mail', 'N/A')}")
                    st.write(f"User Principal Name: {me.get('userPrincipalName', 'N/A')}")
                    st.write(f"Department: {me.get('department', 'N/A')}")
                    st.write(f"Job Title: {me.get('jobTitle', 'N/A')}")
                except Exception as e:
                    st.error(f"Error retrieving user information: {str(e)}")
                
                # Disconnect button
                if st.button("Disconnect"):
                    # Remove connection manager from session state
                    del st.session_state["msgraph_connection_manager"]
                    if "msgraph_adapter" in st.session_state:
                        del st.session_state["msgraph_adapter"]
                    st.success("Disconnected from Microsoft Graph API")
                    st.experimental_rerun()
            else:
                st.error("Not connected to Microsoft Graph API")
        else:
            st.info("Not connected to Microsoft Graph API")
    
    with tab3:
        st.header("Help")
        
        st.subheader("Authentication Methods")
        
        st.markdown("""
        ### Device Code Flow
        
        The device code flow is designed for devices and applications that don't have a web browser or have limited input capabilities. This is the recommended method for command-line tools.
        
        1. Enter your Tenant ID and Client ID
        2. Click "Connect to Microsoft Graph API"
        3. You will be prompted to visit a URL and enter a code
        4. After authentication, the connection will be established
        
        ### Client Credentials Flow
        
        The client credentials flow is designed for daemon or service applications that run without user interaction. This method requires a client secret.
        
        1. Enter your Tenant ID, Client ID, and Client Secret
        2. Click "Connect to Microsoft Graph API"
        3. The connection will be established using the provided credentials
        
        ### Interactive Flow
        
        The interactive flow is designed for web applications that can open a browser window for authentication.
        
        1. Enter your Tenant ID and Client ID
        2. Click "Connect to Microsoft Graph API"
        3. A browser window will open for authentication
        4. After authentication, the connection will be established
        """)
        
        st.subheader("Configuration")
        
        st.markdown("""
        ### Tenant ID
        
        The tenant ID is a unique identifier for your Microsoft 365 tenant. You can find it in the Azure Portal under "Azure Active Directory" > "Properties" > "Directory ID".
        
        ### Client ID
        
        The client ID is a unique identifier for your application. You can create a new application in the Azure Portal under "Azure Active Directory" > "App registrations" > "New registration".
        
        ### Client Secret
        
        The client secret is a password for your application. You can create a new client secret in the Azure Portal under "Azure Active Directory" > "App registrations" > [Your App] > "Certificates & secrets" > "New client secret".
        """)