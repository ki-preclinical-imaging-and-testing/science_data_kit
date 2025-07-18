"""
Microsoft Graph Exploration Page for Science Data Kit

This module defines the MSGraphExplorePage class, which provides functionality for
exploring the Microsoft Graph API.
"""

from typing import Dict, Any, Optional, List
import os
import json
import pandas as pd
import base64
import io

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import MSGraphExplorePageData
from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
from science_data_kit.core.db.msgraph_adapter import MSGraphAdapter
from science_data_kit.core.utils.msgraph_utils import (
    build_msgraph_query, msgraph_to_dataframe, msgraph_to_network,
    extract_user_data, extract_group_data, extract_message_data
)

class MSGraphExplorePage(BasePage):
    """
    Microsoft Graph exploration page for the Science Data Kit.
    
    This page provides functionality for exploring Microsoft Graph API data,
    executing queries, and visualizing the results.
    """
    
    def __init__(self):
        """
        Initialize the MSGraphExplorePage.
        """
        super().__init__()
        self.page_data = MSGraphExplorePageData(title="Microsoft Graph API Explorer")
        self.connection_manager = None
        self.adapter = None
        
        # Initialize sample queries
        self._initialize_sample_queries()
    
    def get_page_data(self) -> MSGraphExplorePageData:
        """
        Get the page data for the Microsoft Graph exploration page.
        
        Returns:
            MSGraphExplorePageData: The page data for the Microsoft Graph exploration page.
        """
        return self.page_data
    
    def _initialize_sample_queries(self):
        """
        Initialize sample queries for Microsoft Graph API.
        """
        self.page_data.sample_queries = {
            "Get current user": {
                "resource_path": "/me",
                "query_parameters": {}
            },
            "Get users": {
                "resource_path": "/users",
                "query_parameters": {
                    "top": "10"
                }
            },
            "Get groups": {
                "resource_path": "/groups",
                "query_parameters": {
                    "top": "10"
                }
            },
            "Get my messages": {
                "resource_path": "/me/messages",
                "query_parameters": {
                    "top": "10"
                }
            },
            "Get my events": {
                "resource_path": "/me/events",
                "query_parameters": {
                    "top": "10"
                }
            },
            "Get my files": {
                "resource_path": "/me/drive/root/children",
                "query_parameters": {
                    "top": "10"
                }
            }
        }
    
    def check_connection(self, connection_manager: Optional[MSGraphConnectionManager] = None) -> bool:
        """
        Check if connected to Microsoft Graph API.
        
        Args:
            connection_manager: Optional connection manager to use.
            
        Returns:
            bool: True if connected, False otherwise.
        """
        if connection_manager:
            self.connection_manager = connection_manager
            if self.connection_manager.connected:
                self.adapter = MSGraphAdapter(connection_manager=self.connection_manager)
                self.page_data.connection_status["msgraph"] = True
                return True
        
        self.page_data.connection_status["msgraph"] = False
        self.page_data.connection_errors["msgraph"] = "Not connected to Microsoft Graph API"
        return False
    
    def execute_query(self, resource_path: str, query_parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a query against Microsoft Graph API.
        
        Args:
            resource_path: The resource path to query (e.g., '/me', '/users').
            query_parameters: Optional query parameters.
            
        Returns:
            Dict[str, Any]: A dictionary with the query result.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            # Store query in page data
            self.page_data.resource_path = resource_path
            self.page_data.query_parameters = query_parameters or {}
            
            # Execute query
            response = self.connection_manager.execute_query(resource_path, query_parameters)
            
            # Store response in page data
            self.page_data.response = response
            
            # Convert response to DataFrame
            df = msgraph_to_dataframe(response)
            
            # Store DataFrame in page data
            self.page_data.dataframe = df
            
            # Determine entity type
            entity_type = "unknown"
            if "/users" in resource_path:
                entity_type = "users"
            elif "/groups" in resource_path:
                entity_type = "groups"
            elif "/messages" in resource_path:
                entity_type = "messages"
            elif "/events" in resource_path:
                entity_type = "events"
            elif "/drive" in resource_path:
                entity_type = "drive"
            
            # Store entity type in page data
            self.page_data.entity_type = entity_type
            
            # Create visualization data if applicable
            if entity_type in ["users", "groups"]:
                # Create network visualization data
                G = msgraph_to_network(response, entity_type)
                
                # Store visualization data in page data
                self.page_data.visualization_data = {
                    "type": "network",
                    "entity_type": entity_type,
                    "nodes": list(G.nodes(data=True)),
                    "edges": list(G.edges(data=True))
                }
            
            return {
                "success": True,
                "message": "Query executed successfully",
                "response": response,
                "dataframe": df.to_dict(orient="records") if df is not None else None,
                "entity_type": entity_type,
                "visualization_data": self.page_data.visualization_data
            }
        except Exception as e:
            self.page_data.connection_errors["query"] = str(e)
            return {
                "success": False,
                "message": f"Error executing query: {str(e)}"
            }
    
    def export_data(self, format: str) -> Dict[str, Any]:
        """
        Export data to a file.
        
        Args:
            format: The format to export to (csv, json, excel).
            
        Returns:
            Dict[str, Any]: A dictionary with the export result.
        """
        try:
            if self.page_data.dataframe is None:
                return {
                    "success": False,
                    "message": "No data to export"
                }
            
            data = self.page_data.dataframe
            
            if format == "csv":
                csv = data.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                return {
                    "success": True,
                    "message": "Data exported to CSV",
                    "data": b64,
                    "filename": "msgraph_data.csv",
                    "mime_type": "text/csv"
                }
            elif format == "json":
                json_str = data.to_json(orient="records")
                b64 = base64.b64encode(json_str.encode()).decode()
                return {
                    "success": True,
                    "message": "Data exported to JSON",
                    "data": b64,
                    "filename": "msgraph_data.json",
                    "mime_type": "application/json"
                }
            elif format == "excel":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    data.to_excel(writer, sheet_name="Sheet1", index=False)
                b64 = base64.b64encode(output.getvalue()).decode()
                return {
                    "success": True,
                    "message": "Data exported to Excel",
                    "data": b64,
                    "filename": "msgraph_data.xlsx",
                    "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                }
            else:
                return {
                    "success": False,
                    "message": f"Unsupported export format: {format}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error exporting data: {str(e)}"
            }