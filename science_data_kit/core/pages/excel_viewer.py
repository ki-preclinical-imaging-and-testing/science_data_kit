"""
Microsoft Excel Viewer Page for Science Data Kit

This module defines the ExcelViewerPage class, which provides functionality for
viewing and interacting with Excel files stored in OneDrive or SharePoint.
"""

from typing import Dict, Any, Optional, List
import os
import json
import pandas as pd
import base64
import io

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import ExcelViewerPageData
from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
from science_data_kit.core.db.msgraph_adapter import MSGraphAdapter

class ExcelViewerPage(BasePage):
    """
    Microsoft Excel viewer page for the Science Data Kit.
    
    This page provides functionality for viewing and interacting with Excel files
    stored in OneDrive or SharePoint, including listing worksheets, viewing worksheet
    data, and working with charts and tables.
    """
    
    def __init__(self):
        """
        Initialize the ExcelViewerPage.
        """
        super().__init__()
        self.page_data = ExcelViewerPageData(title="Microsoft Excel Viewer")
        self.connection_manager = None
        self.adapter = None
    
    def get_page_data(self) -> ExcelViewerPageData:
        """
        Get the page data for the Excel viewer page.
        
        Returns:
            ExcelViewerPageData: The page data for the Excel viewer page.
        """
        return self.page_data
    
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
    
    def get_file_metadata(self, drive_id: Optional[str] = None, item_id: str = None, 
                         site_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metadata for an Excel file.
        
        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive).
            item_id: ID of the Excel file.
            site_id: ID of the SharePoint site (if the file is in SharePoint).
            
        Returns:
            Dict[str, Any]: A dictionary with the file metadata.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            if not item_id:
                return {
                    "success": False,
                    "message": "Item ID is required"
                }
            
            # Store parameters in page data
            self.page_data.drive_id = drive_id
            self.page_data.item_id = item_id
            self.page_data.site_id = site_id
            
            # Get file metadata
            metadata = self.connection_manager.get_excel_file_metadata(drive_id, item_id, site_id)
            
            # Store file metadata in page data
            self.page_data.file_metadata = metadata
            
            return {
                "success": True,
                "message": "File metadata retrieved successfully",
                "metadata": metadata
            }
        except Exception as e:
            self.page_data.connection_errors["metadata"] = str(e)
            return {
                "success": False,
                "message": f"Error getting file metadata: {str(e)}"
            }
    
    def get_worksheets(self, drive_id: Optional[str] = None, item_id: str = None, 
                      site_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a list of worksheets in an Excel file.
        
        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive).
            item_id: ID of the Excel file.
            site_id: ID of the SharePoint site (if the file is in SharePoint).
            
        Returns:
            Dict[str, Any]: A dictionary with the worksheets.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            if not item_id:
                return {
                    "success": False,
                    "message": "Item ID is required"
                }
            
            # Store parameters in page data if not already stored
            if not self.page_data.drive_id:
                self.page_data.drive_id = drive_id
            if not self.page_data.item_id:
                self.page_data.item_id = item_id
            if not self.page_data.site_id:
                self.page_data.site_id = site_id
            
            # Get worksheets
            worksheets = self.connection_manager.get_excel_worksheets(drive_id, item_id, site_id)
            
            # Store worksheets in page data
            self.page_data.worksheets = worksheets
            
            return {
                "success": True,
                "message": f"Retrieved {len(worksheets)} worksheets",
                "worksheets": worksheets
            }
        except Exception as e:
            self.page_data.connection_errors["worksheets"] = str(e)
            return {
                "success": False,
                "message": f"Error getting worksheets: {str(e)}"
            }
    
    def get_worksheet_data(self, drive_id: Optional[str] = None, item_id: str = None, 
                          worksheet_id: str = None, site_id: Optional[str] = None,
                          range_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get data from an Excel worksheet.
        
        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive).
            item_id: ID of the Excel file.
            worksheet_id: ID or name of the worksheet.
            site_id: ID of the SharePoint site (if the file is in SharePoint).
            range_address: Address of the range to get (e.g., "A1:C10").
            
        Returns:
            Dict[str, Any]: A dictionary with the worksheet data.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            if not item_id:
                return {
                    "success": False,
                    "message": "Item ID is required"
                }
            
            if not worksheet_id:
                return {
                    "success": False,
                    "message": "Worksheet ID is required"
                }
            
            # Store parameters in page data if not already stored
            if not self.page_data.drive_id:
                self.page_data.drive_id = drive_id
            if not self.page_data.item_id:
                self.page_data.item_id = item_id
            if not self.page_data.site_id:
                self.page_data.site_id = site_id
            self.page_data.range_address = range_address
            
            # Get worksheet data
            worksheet_data = self.connection_manager.get_excel_worksheet_data(
                drive_id, item_id, worksheet_id, site_id, range_address
            )
            
            # Store worksheet data in page data
            self.page_data.worksheet_data = worksheet_data
            
            # Store selected worksheet in page data
            for worksheet in self.page_data.worksheets:
                if worksheet.get("id") == worksheet_id or worksheet.get("name") == worksheet_id:
                    self.page_data.selected_worksheet = worksheet
                    break
            
            # Create visualization data
            if worksheet_data and "values" in worksheet_data:
                # Convert to DataFrame for easier manipulation
                values = worksheet_data.get("values", [])
                if values and len(values) > 0:
                    # Use first row as header if it exists
                    headers = values[0] if len(values) > 0 else []
                    data = values[1:] if len(values) > 1 else []
                    
                    # Create visualization data
                    visualization_data = {
                        "type": "worksheet",
                        "headers": headers,
                        "data": data,
                        "row_count": len(data),
                        "column_count": len(headers) if headers else 0
                    }
                    
                    # Store visualization data in page data
                    self.page_data.visualization_data = visualization_data
            
            return {
                "success": True,
                "message": "Worksheet data retrieved successfully",
                "worksheet_data": worksheet_data,
                "visualization_data": self.page_data.visualization_data
            }
        except Exception as e:
            self.page_data.connection_errors["worksheet_data"] = str(e)
            return {
                "success": False,
                "message": f"Error getting worksheet data: {str(e)}"
            }
    
    def get_charts(self, drive_id: Optional[str] = None, item_id: str = None, 
                  worksheet_id: str = None, site_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a list of charts in an Excel worksheet.
        
        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive).
            item_id: ID of the Excel file.
            worksheet_id: ID or name of the worksheet.
            site_id: ID of the SharePoint site (if the file is in SharePoint).
            
        Returns:
            Dict[str, Any]: A dictionary with the charts.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            if not item_id:
                return {
                    "success": False,
                    "message": "Item ID is required"
                }
            
            if not worksheet_id:
                return {
                    "success": False,
                    "message": "Worksheet ID is required"
                }
            
            # Store parameters in page data if not already stored
            if not self.page_data.drive_id:
                self.page_data.drive_id = drive_id
            if not self.page_data.item_id:
                self.page_data.item_id = item_id
            if not self.page_data.site_id:
                self.page_data.site_id = site_id
            
            # Get charts
            charts = self.connection_manager.get_excel_charts(drive_id, item_id, worksheet_id, site_id)
            
            # Store charts in page data
            self.page_data.charts = charts
            
            return {
                "success": True,
                "message": f"Retrieved {len(charts)} charts",
                "charts": charts
            }
        except Exception as e:
            self.page_data.connection_errors["charts"] = str(e)
            return {
                "success": False,
                "message": f"Error getting charts: {str(e)}"
            }
    
    def get_chart_data(self, drive_id: Optional[str] = None, item_id: str = None, 
                      worksheet_id: str = None, chart_id: str = None, 
                      site_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get data from an Excel chart.
        
        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive).
            item_id: ID of the Excel file.
            worksheet_id: ID or name of the worksheet.
            chart_id: ID of the chart.
            site_id: ID of the SharePoint site (if the file is in SharePoint).
            
        Returns:
            Dict[str, Any]: A dictionary with the chart data.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            if not item_id:
                return {
                    "success": False,
                    "message": "Item ID is required"
                }
            
            if not worksheet_id:
                return {
                    "success": False,
                    "message": "Worksheet ID is required"
                }
            
            if not chart_id:
                return {
                    "success": False,
                    "message": "Chart ID is required"
                }
            
            # Store parameters in page data if not already stored
            if not self.page_data.drive_id:
                self.page_data.drive_id = drive_id
            if not self.page_data.item_id:
                self.page_data.item_id = item_id
            if not self.page_data.site_id:
                self.page_data.site_id = site_id
            
            # Get chart data
            chart_data = self.connection_manager.get_excel_chart_data(
                drive_id, item_id, worksheet_id, chart_id, site_id
            )
            
            # Store chart data in page data
            self.page_data.chart_data = chart_data
            
            # Store selected chart in page data
            for chart in self.page_data.charts:
                if chart.get("id") == chart_id:
                    self.page_data.selected_chart = chart
                    break
            
            return {
                "success": True,
                "message": "Chart data retrieved successfully",
                "chart_data": chart_data
            }
        except Exception as e:
            self.page_data.connection_errors["chart_data"] = str(e)
            return {
                "success": False,
                "message": f"Error getting chart data: {str(e)}"
            }
    
    def get_tables(self, drive_id: Optional[str] = None, item_id: str = None, 
                  worksheet_id: str = None, site_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a list of tables in an Excel worksheet.
        
        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive).
            item_id: ID of the Excel file.
            worksheet_id: ID or name of the worksheet.
            site_id: ID of the SharePoint site (if the file is in SharePoint).
            
        Returns:
            Dict[str, Any]: A dictionary with the tables.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            if not item_id:
                return {
                    "success": False,
                    "message": "Item ID is required"
                }
            
            if not worksheet_id:
                return {
                    "success": False,
                    "message": "Worksheet ID is required"
                }
            
            # Store parameters in page data if not already stored
            if not self.page_data.drive_id:
                self.page_data.drive_id = drive_id
            if not self.page_data.item_id:
                self.page_data.item_id = item_id
            if not self.page_data.site_id:
                self.page_data.site_id = site_id
            
            # Get tables
            tables = self.connection_manager.get_excel_tables(drive_id, item_id, worksheet_id, site_id)
            
            # Store tables in page data
            self.page_data.tables = tables
            
            return {
                "success": True,
                "message": f"Retrieved {len(tables)} tables",
                "tables": tables
            }
        except Exception as e:
            self.page_data.connection_errors["tables"] = str(e)
            return {
                "success": False,
                "message": f"Error getting tables: {str(e)}"
            }
    
    def get_table_data(self, drive_id: Optional[str] = None, item_id: str = None, 
                      worksheet_id: str = None, table_id: str = None, 
                      site_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get data from an Excel table.
        
        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive).
            item_id: ID of the Excel file.
            worksheet_id: ID or name of the worksheet.
            table_id: ID of the table.
            site_id: ID of the SharePoint site (if the file is in SharePoint).
            
        Returns:
            Dict[str, Any]: A dictionary with the table data.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            if not item_id:
                return {
                    "success": False,
                    "message": "Item ID is required"
                }
            
            if not worksheet_id:
                return {
                    "success": False,
                    "message": "Worksheet ID is required"
                }
            
            if not table_id:
                return {
                    "success": False,
                    "message": "Table ID is required"
                }
            
            # Store parameters in page data if not already stored
            if not self.page_data.drive_id:
                self.page_data.drive_id = drive_id
            if not self.page_data.item_id:
                self.page_data.item_id = item_id
            if not self.page_data.site_id:
                self.page_data.site_id = site_id
            
            # Get table data
            table_data = self.connection_manager.get_excel_table_data(
                drive_id, item_id, worksheet_id, table_id, site_id
            )
            
            # Store table data in page data
            self.page_data.table_data = table_data
            
            # Store selected table in page data
            for table in self.page_data.tables:
                if table.get("id") == table_id:
                    self.page_data.selected_table = table
                    break
            
            # Create visualization data
            if table_data and "values" in table_data:
                # Convert to DataFrame for easier manipulation
                values = table_data.get("values", [])
                if values and len(values) > 0:
                    # Use first row as header if it exists
                    headers = values[0] if len(values) > 0 else []
                    data = values[1:] if len(values) > 1 else []
                    
                    # Create visualization data
                    visualization_data = {
                        "type": "table",
                        "headers": headers,
                        "data": data,
                        "row_count": len(data),
                        "column_count": len(headers) if headers else 0
                    }
                    
                    # Store visualization data in page data
                    self.page_data.visualization_data = visualization_data
            
            return {
                "success": True,
                "message": "Table data retrieved successfully",
                "table_data": table_data,
                "visualization_data": self.page_data.visualization_data
            }
        except Exception as e:
            self.page_data.connection_errors["table_data"] = str(e)
            return {
                "success": False,
                "message": f"Error getting table data: {str(e)}"
            }
    
    def export_data(self, data_type: str, format: str) -> Dict[str, Any]:
        """
        Export data to a file.
        
        Args:
            data_type: Type of data to export (worksheet, chart, table).
            format: Format to export to (csv, json, excel).
            
        Returns:
            Dict[str, Any]: A dictionary with the export result.
        """
        try:
            # Determine data to export
            if data_type == "worksheet":
                if not self.page_data.worksheet_data:
                    return {
                        "success": False,
                        "message": "No worksheet data to export"
                    }
                
                # Convert worksheet data to DataFrame
                values = self.page_data.worksheet_data.get("values", [])
                if not values or len(values) == 0:
                    return {
                        "success": False,
                        "message": "No data in worksheet"
                    }
                
                # Use first row as header if it exists
                headers = values[0] if len(values) > 0 else []
                data_rows = values[1:] if len(values) > 1 else []
                
                # Create DataFrame
                data = pd.DataFrame(data_rows, columns=headers)
                filename = "excel_worksheet_data"
            elif data_type == "chart":
                if not self.page_data.chart_data:
                    return {
                        "success": False,
                        "message": "No chart data to export"
                    }
                
                # Convert chart data to DataFrame (simplified)
                data = pd.DataFrame([self.page_data.chart_data])
                filename = "excel_chart_data"
            elif data_type == "table":
                if not self.page_data.table_data:
                    return {
                        "success": False,
                        "message": "No table data to export"
                    }
                
                # Convert table data to DataFrame
                values = self.page_data.table_data.get("values", [])
                if not values or len(values) == 0:
                    return {
                        "success": False,
                        "message": "No data in table"
                    }
                
                # Use first row as header if it exists
                headers = values[0] if len(values) > 0 else []
                data_rows = values[1:] if len(values) > 1 else []
                
                # Create DataFrame
                data = pd.DataFrame(data_rows, columns=headers)
                filename = "excel_table_data"
            else:
                return {
                    "success": False,
                    "message": f"Unsupported data type: {data_type}"
                }
            
            # Export data in the specified format
            if format == "csv":
                csv = data.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                return {
                    "success": True,
                    "message": "Data exported to CSV",
                    "data": b64,
                    "filename": f"{filename}.csv",
                    "mime_type": "text/csv"
                }
            elif format == "json":
                json_str = data.to_json(orient="records")
                b64 = base64.b64encode(json_str.encode()).decode()
                return {
                    "success": True,
                    "message": "Data exported to JSON",
                    "data": b64,
                    "filename": f"{filename}.json",
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
                    "filename": f"{filename}.xlsx",
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