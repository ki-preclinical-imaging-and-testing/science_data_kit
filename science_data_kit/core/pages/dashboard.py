"""
Dashboard Page Module for Science Data Kit Core

This module provides the Dashboard page for the Science Data Kit application.
It defines the framework-independent core functionality for the Dashboard page.
"""

from typing import Dict, Any, List
import pandas as pd

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import DashboardPageData
from science_data_kit.core.db.db_manager import db_manager

class DashboardPage(BasePage):
    """
    Dashboard page serving as the main entry point for the application.
    
    This class provides the core business logic for the Dashboard page,
    independent of any UI framework.
    """
    
    def __init__(self, db_connection=None):
        """Initialize the Dashboard page."""
        super().__init__(db_connection)
        self.db_manager = db_manager
        
        # Default connected services state
        self.connected_services = {
            "neo4j": False,
            "jupyter": False,
            "neodash": False,
            "msgraph": False,
            "dropbox": False,
            "google_drive": False
        }
    
    def get_page_data(self) -> DashboardPageData:
        """
        Return data needed to render the Dashboard page.
        
        Returns:
            An instance of DashboardPageData containing the data needed
            to render the Dashboard page.
        """
        return DashboardPageData(
            title="Dashboard",
            requires_auth=True,
            metrics=self._get_metrics(),
            charts=self._get_charts(),
            tables=self._get_tables(),
            status_items=self._get_status_items(),
            connected_services=self.connected_services,
            recent_activities=self._get_recent_activities(),
            feature_categories=self._get_feature_categories()
        )
    
    def connect_to_database(self, uri: str, username: str, password: str, database: str, conn_name: str = None) -> Dict[str, Any]:
        """
        Connect to a database.
        
        Args:
            uri: The URI of the Neo4j server.
            username: The username for authentication.
            password: The password for authentication.
            database: The name of the database to connect to.
            conn_name: The name of the connection (optional).
            
        Returns:
            A dictionary with connection status and error message if any.
        """
        result = {
            "success": False,
            "error": None
        }
        
        try:
            # Update connection details
            self.db_manager.uri = uri
            self.db_manager.user = username
            self.db_manager.password = password
            self.db_manager.database = database
            
            # Connect to the database with the specified connection name
            connection_successful = self.db_manager._connect(conn_name)
            
            if not connection_successful:
                error_msg = self.db_manager._connection_error or "Unknown connection error"
                result["error"] = f"Failed to connect to Neo4j: {error_msg}"
                return result
            
            # Update connected services
            self.connected_services["neo4j"] = True
            
            result["success"] = True
            return result
        except Exception as e:
            result["error"] = f"Failed to connect to Neo4j: {str(e)}"
            return result
    
    def disconnect_from_database(self) -> Dict[str, Any]:
        """
        Disconnect from the database.
        
        Returns:
            A dictionary with disconnection status and error message if any.
        """
        result = {
            "success": False,
            "error": None
        }
        
        try:
            # Close the connection
            self.db_manager.close()
            
            # Update connected services
            self.connected_services["neo4j"] = False
            
            result["success"] = True
            return result
        except Exception as e:
            result["error"] = f"Failed to disconnect from Neo4j: {str(e)}"
            return result
    
    def _get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get metrics for the Dashboard page.
        
        Returns:
            A list of dictionaries containing metric data.
        """
        metrics = []
        
        # Add connected services metric
        connected_count = sum(1 for status in self.connected_services.values() if status)
        total_count = len(self.connected_services)
        
        metrics.append({
            "title": "Connected Services",
            "value": connected_count,
            "total": total_count,
            "unit": "services",
            "trend": None
        })
        
        # Add more metrics as needed
        
        return metrics
    
    def _get_charts(self) -> List[Dict[str, Any]]:
        """
        Get charts for the Dashboard page.
        
        Returns:
            A list of dictionaries containing chart data.
        """
        charts = []
        
        # Add service status chart
        services = list(self.connected_services.keys())
        status = [1 if self.connected_services[s] else 0 for s in services]
        display_names = [s.replace('_', ' ').title() for s in services]
        
        charts.append({
            "title": "Service Connection Status",
            "type": "bar",
            "data": {
                "labels": display_names,
                "values": status
            },
            "options": {
                "x_label": "Service",
                "y_label": "Status",
                "colors": ["green" if s else "red" for s in status]
            }
        })
        
        # Add project progress chart
        categories = ['Data Sources', 'Analysis', 'Visualization', 'Integration']
        values = [85, 70, 60, 40]
        
        charts.append({
            "title": "Project Progress by Category",
            "type": "bar",
            "data": {
                "labels": categories,
                "values": values
            },
            "options": {
                "x_label": "Category",
                "y_label": "Completion (%)",
                "color": "skyblue"
            }
        })
        
        return charts
    
    def _get_tables(self) -> List[Dict[str, Any]]:
        """
        Get tables for the Dashboard page.
        
        Returns:
            A list of dictionaries containing table data.
        """
        tables = []
        
        # Add recent activities table
        tables.append({
            "title": "Recent Activities",
            "data": self._get_recent_activities(),
            "columns": ["Date", "Activity", "Category"]
        })
        
        return tables
    
    def _get_status_items(self) -> List[Dict[str, Any]]:
        """
        Get status items for the Dashboard page.
        
        Returns:
            A list of dictionaries containing status item data.
        """
        status_items = []
        
        # Add service status items
        for service, connected in self.connected_services.items():
            display_name = service.replace('_', ' ').title()
            status_items.append({
                "name": display_name,
                "status": "connected" if connected else "disconnected",
                "color": "green" if connected else "red"
            })
        
        return status_items
    
    def _get_recent_activities(self) -> List[Dict[str, Any]]:
        """
        Get recent activities for the Dashboard page.
        
        Returns:
            A list of dictionaries containing recent activity data.
        """
        return [
            {
                "Date": "2025-07-20",
                "Activity": "Implemented data validation rules engine",
                "Category": "Data Modeling"
            },
            {
                "Date": "2025-07-19",
                "Activity": "Implemented data migration tools",
                "Category": "Data Modeling"
            },
            {
                "Date": "2025-07-18",
                "Activity": "Updated roadmap to prioritize data modeling enhancements",
                "Category": "Planning"
            },
            {
                "Date": "2025-07-17",
                "Activity": "Implemented command-line interface",
                "Category": "API"
            },
            {
                "Date": "2025-07-16",
                "Activity": "Implemented client-side caching",
                "Category": "API"
            }
        ]
    
    def _get_feature_categories(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get feature categories for the Dashboard page.
        
        Returns:
            A dictionary mapping category names to lists of feature dictionaries.
        """
        feature_categories = {}
        
        # Data Sources
        feature_categories["data_sources"] = [
            {
                "Source": "Neo4j",
                "Status": "Available",
                "Description": "Graph database for storing and querying connected data"
            },
            {
                "Source": "Microsoft Graph API",
                "Status": "Available",
                "Description": "Access Microsoft 365 services including Teams, SharePoint, and OneDrive"
            },
            {
                "Source": "Dropbox",
                "Status": "Available",
                "Description": "Access files stored in Dropbox"
            },
            {
                "Source": "Google Drive",
                "Status": "Available",
                "Description": "Access files stored in Google Drive, including Google Sheets"
            },
            {
                "Source": "Local Storage",
                "Status": "Available",
                "Description": "Access files stored on the local file system"
            }
        ]
        
        # Analysis Capabilities
        feature_categories["analysis_capabilities"] = [
            {
                "Capability": "Query Execution",
                "Status": "Available",
                "Description": "Execute Cypher queries against Neo4j database"
            },
            {
                "Capability": "Data Validation",
                "Status": "Available",
                "Description": "Validate data against defined schemas and rules"
            },
            {
                "Capability": "Schema Analysis",
                "Status": "Available",
                "Description": "Analyze and visualize database schema"
            },
            {
                "Capability": "Relationship Analysis",
                "Status": "Available",
                "Description": "Analyze relationships between entities"
            },
            {
                "Capability": "Data Export",
                "Status": "Available",
                "Description": "Export data to various formats (CSV, Excel, JSON)"
            }
        ]
        
        # Visualization Components
        feature_categories["visualization_components"] = [
            {
                "Component": "Schema Visualization",
                "Status": "Available",
                "Description": "Visualize database schema as a network graph"
            },
            {
                "Component": "Basic Data Charts",
                "Status": "Available",
                "Description": "Create basic bar, line, and scatter charts from query results"
            },
            {
                "Component": "Simple Network Graphs",
                "Status": "Available",
                "Description": "Visualize data as simple network graphs"
            },
            {
                "Component": "Custom Visualization Templates",
                "Status": "Available",
                "Description": "Create and apply custom visualization templates"
            },
            {
                "Component": "Dashboard Widgets",
                "Status": "Available",
                "Description": "Create customizable dashboard widgets for monitoring and reporting"
            },
            {
                "Component": "NeoDash Integration",
                "Status": "Available",
                "Description": "Integration with NeoDash for creating advanced dashboards"
            },
            {
                "Component": "Advanced Dashboards",
                "Status": "Available via NeoDash",
                "Description": "Create complex, interactive dashboards with NeoDash"
            }
        ]
        
        # Integration Capabilities
        feature_categories["integration_capabilities"] = [
            {
                "Capability": "Jupyter Notebook",
                "Status": "Available",
                "Description": "Integration with Jupyter notebooks for data analysis"
            },
            {
                "Capability": "NExtSEEK",
                "Status": "Planned",
                "Description": "Integration with NExtSEEK platform"
            },
            {
                "Capability": "FAIRDOM-Hub",
                "Status": "Planned",
                "Description": "Integration with FAIRDOM-Hub platform"
            },
            {
                "Capability": "API Access",
                "Status": "Available",
                "Description": "Access SDK functionality through API"
            },
            {
                "Capability": "Command-Line Interface",
                "Status": "Available",
                "Description": "Access SDK functionality through command-line interface"
            }
        ]
        
        return feature_categories