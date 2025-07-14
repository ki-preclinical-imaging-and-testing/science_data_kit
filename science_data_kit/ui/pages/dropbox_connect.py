"""
Dropbox Connection Page for Science Data Kit

This module provides a Streamlit page for connecting to Dropbox API.
"""

import os
import json
import streamlit as st
from typing import Dict, Any, Optional

from science_data_kit_extensions.dropbox.connector import DropboxConnector


def render_dropbox_connect_page():
    """Render the Dropbox connection page."""
    dropbox_connect_page()


def dropbox_connect_page():
    """
    Render the Dropbox connection page.
    """
    st.title("Connect to Dropbox")

    # Check if Dropbox SDK is available
    try:
        import dropbox
        dropbox_available = True
    except ImportError:
        dropbox_available = False
        st.error(
            "Dropbox SDK is not installed. "
            "Please install it with 'pip install dropbox'."
        )
        st.stop()

    # Create tabs for different connection methods
    tab1, tab2, tab3 = st.tabs(["Configuration", "Connection Status", "Help"])

    with tab1:
        st.header("Dropbox API Configuration")

        # App key and secret
        app_key = st.text_input(
            "App Key",
            value=st.session_state.get("dropbox_app_key", ""),
            help="The app key for your Dropbox application."
        )

        app_secret = st.text_input(
            "App Secret",
            value=st.session_state.get("dropbox_app_secret", ""),
            type="password",
            help="The app secret for your Dropbox application."
        )

        # Refresh token (if already available)
        refresh_token = st.text_input(
            "Refresh Token (Optional)",
            value=st.session_state.get("dropbox_refresh_token", ""),
            type="password",
            help="If you already have a refresh token, you can enter it here."
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
                value=st.session_state.get("dropbox_config_file", "dropbox_config.json"),
                help="The path to save the configuration to."
            )

        # Connect button
        if st.button("Connect to Dropbox"):
            try:
                # Create connector
                connector = DropboxConnector(
                    app_key=app_key,
                    app_secret=app_secret,
                    refresh_token=refresh_token
                )

                # Save configuration if requested
                if save_config and config_file:
                    config = {
                        "app_key": app_key,
                        "app_secret": app_secret,
                        "refresh_token": refresh_token if refresh_token else None
                    }

                    with open(config_file, 'w') as f:
                        json.dump(config, f, indent=4)
                    st.success(f"Configuration saved to {config_file}")

                # Try to connect
                if connector.is_connected():
                    st.success("Connected to Dropbox API")

                    # Store connector in session state
                    st.session_state["dropbox_connector"] = connector

                    # Store configuration in session state
                    st.session_state["dropbox_app_key"] = app_key
                    st.session_state["dropbox_app_secret"] = app_secret
                    st.session_state["dropbox_refresh_token"] = refresh_token
                    if save_config:
                        st.session_state["dropbox_config_file"] = config_file
                else:
                    # If not connected and no refresh token, start OAuth flow
                    if not refresh_token:
                        auth_url = connector.authenticate()
                        st.info(f"Please visit the following URL to authorize the application: {auth_url}")

                        auth_code = st.text_input(
                            "Authorization Code",
                            help="Enter the authorization code from the Dropbox website."
                        )

                        if auth_code and st.button("Complete Authentication"):
                            if connector.complete_authentication(auth_code):
                                st.success("Connected to Dropbox API")

                                # Store connector in session state
                                st.session_state["dropbox_connector"] = connector

                                # Store configuration in session state
                                st.session_state["dropbox_app_key"] = app_key
                                st.session_state["dropbox_app_secret"] = app_secret
                                st.session_state["dropbox_refresh_token"] = connector.refresh_token
                                if save_config:
                                    st.session_state["dropbox_config_file"] = config_file

                                    # Update saved configuration with new refresh token
                                    if config_file:
                                        config = {
                                            "app_key": app_key,
                                            "app_secret": app_secret,
                                            "refresh_token": connector.refresh_token
                                        }

                                        with open(config_file, 'w') as f:
                                            json.dump(config, f, indent=4)
                            else:
                                st.error("Failed to complete authentication. Please check the authorization code.")
                    else:
                        st.error("Failed to connect to Dropbox API. Please check your credentials.")
            except Exception as e:
                st.error(f"Error connecting to Dropbox API: {str(e)}")

    with tab2:
        st.header("Connection Status")

        # Check if connected
        if "dropbox_connector" in st.session_state:
            connector = st.session_state["dropbox_connector"]
            if connector.is_connected():
                st.success("Connected to Dropbox API")

                # Display current account information
                try:
                    account_info = connector.get_account_info()
                    st.subheader("Account Information")
                    st.write(f"Name: {account_info.get('name', 'N/A')}")
                    st.write(f"Email: {account_info.get('email', 'N/A')}")
                    st.write(f"Account ID: {account_info.get('account_id', 'N/A')}")
                    if account_info.get('team'):
                        st.write(f"Team: {account_info.get('team', 'N/A')}")
                        st.write(f"Team Member ID: {account_info.get('team_member_id', 'N/A')}")
                except Exception as e:
                    st.error(f"Error retrieving account information: {str(e)}")

                # Disconnect button
                if st.button("Disconnect"):
                    # Remove connector from session state
                    del st.session_state["dropbox_connector"]
                    st.success("Disconnected from Dropbox API")
                    st.experimental_rerun()
            else:
                st.error("Not connected to Dropbox API")
        else:
            st.info("Not connected to Dropbox API")

    with tab3:
        st.header("Help")

        st.subheader("Authentication")

        st.markdown("""
        ### OAuth2 Authentication Flow

        The Dropbox extension uses OAuth2 for authentication. The process works as follows:

        1. Enter your App Key and App Secret
        2. Click "Connect to Dropbox"
        3. You will be prompted to visit a URL to authorize the application
        4. After authorization, you will receive an authorization code
        5. Enter the authorization code and click "Complete Authentication"
        6. The connection will be established and a refresh token will be stored for future use

        ### Using a Refresh Token

        If you already have a refresh token, you can enter it directly in the "Refresh Token" field to connect without going through the OAuth2 flow again.

        ### Saving Configuration

        You can save your configuration to a file for future use. The configuration file will contain your App Key, App Secret, and Refresh Token.
        """)

        st.subheader("Configuration")

        st.markdown("""
        ### App Key and App Secret

        To use the Dropbox API, you need to create an app in the Dropbox App Console:

        1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
        2. Click "Create app"
        3. Choose "Scoped access" for API
        4. Choose "Full Dropbox" for access type
        5. Give your app a name
        6. Click "Create app"
        7. On the app settings page, find your App Key and App Secret

        ### Permissions

        Your app needs the following permissions:

        - `files.metadata.read`: To read file and folder metadata
        - `files.content.read`: To read file content
        - `files.content.write`: To write file content
        - `sharing.read`: To read sharing information
        - `team_data.member`: To access team member information (for team folders)

        You can set these permissions in the "Permissions" tab of your app settings.
        """)
