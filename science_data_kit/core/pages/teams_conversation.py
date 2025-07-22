"""
Microsoft Teams Conversation Browser Page for Science Data Kit

This module defines the TeamsConversationPage class, which provides functionality for
browsing and analyzing Microsoft Teams conversations.
"""

from typing import Dict, Any, Optional, List
import os
import json
import pandas as pd
import base64
import io

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import TeamsConversationPageData
from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
from science_data_kit.core.db.msgraph_adapter import MSGraphAdapter

class TeamsConversationPage(BasePage):
    """
    Microsoft Teams conversation browser page for the Science Data Kit.
    
    This page provides functionality for browsing and analyzing Teams conversations,
    including listing teams, channels, and messages, as well as analyzing conversations
    and extracting topics.
    """
    
    def __init__(self):
        """
        Initialize the TeamsConversationPage.
        """
        super().__init__()
        self.page_data = TeamsConversationPageData(title="Microsoft Teams Conversation Browser")
        self.connection_manager = None
        self.adapter = None
    
    def get_page_data(self) -> TeamsConversationPageData:
        """
        Get the page data for the Teams conversation browser page.
        
        Returns:
            TeamsConversationPageData: The page data for the Teams conversation browser page.
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
    
    def get_teams(self) -> Dict[str, Any]:
        """
        Get a list of Microsoft Teams.
        
        Returns:
            Dict[str, Any]: A dictionary with the teams.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            # Get teams
            teams = self.connection_manager.get_teams()
            
            # Store teams in page data
            self.page_data.teams = teams
            
            return {
                "success": True,
                "message": f"Retrieved {len(teams)} teams",
                "teams": teams
            }
        except Exception as e:
            self.page_data.connection_errors["teams"] = str(e)
            return {
                "success": False,
                "message": f"Error getting teams: {str(e)}"
            }
    
    def get_channels(self, team_id: str) -> Dict[str, Any]:
        """
        Get channels for a team.
        
        Args:
            team_id: ID of the team.
            
        Returns:
            Dict[str, Any]: A dictionary with the channels.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            # Get channels
            channels = self.connection_manager.get_channels(team_id)
            
            # Store channels in page data
            self.page_data.channels = channels
            
            # Store selected team in page data
            for team in self.page_data.teams:
                if team.get("id") == team_id:
                    self.page_data.selected_team = team
                    break
            
            return {
                "success": True,
                "message": f"Retrieved {len(channels)} channels",
                "channels": channels
            }
        except Exception as e:
            self.page_data.connection_errors["channels"] = str(e)
            return {
                "success": False,
                "message": f"Error getting channels: {str(e)}"
            }
    
    def get_messages(self, team_id: str, channel_id: str) -> Dict[str, Any]:
        """
        Get messages from a channel.
        
        Args:
            team_id: ID of the team.
            channel_id: ID of the channel.
            
        Returns:
            Dict[str, Any]: A dictionary with the messages.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            # Get messages
            messages = self.connection_manager.get_messages(team_id, channel_id)
            
            # Store messages in page data
            self.page_data.messages = messages
            
            # Store selected channel in page data
            for channel in self.page_data.channels:
                if channel.get("id") == channel_id:
                    self.page_data.selected_channel = channel
                    break
            
            return {
                "success": True,
                "message": f"Retrieved {len(messages)} messages",
                "messages": messages
            }
        except Exception as e:
            self.page_data.connection_errors["messages"] = str(e)
            return {
                "success": False,
                "message": f"Error getting messages: {str(e)}"
            }
    
    def get_message_replies(self, team_id: str, channel_id: str, message_id: str) -> Dict[str, Any]:
        """
        Get replies to a message.
        
        Args:
            team_id: ID of the team.
            channel_id: ID of the channel.
            message_id: ID of the message.
            
        Returns:
            Dict[str, Any]: A dictionary with the message replies.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            # Get message replies
            replies = self.connection_manager.get_message_replies(team_id, channel_id, message_id)
            
            # Store message replies in page data
            self.page_data.message_replies = replies
            
            # Store selected message in page data
            for message in self.page_data.messages:
                if message.get("id") == message_id:
                    self.page_data.selected_message = message
                    break
            
            return {
                "success": True,
                "message": f"Retrieved {len(replies)} replies",
                "replies": replies
            }
        except Exception as e:
            self.page_data.connection_errors["replies"] = str(e)
            return {
                "success": False,
                "message": f"Error getting message replies: {str(e)}"
            }
    
    def analyze_conversation(self, team_id: str, channel_id: str) -> Dict[str, Any]:
        """
        Analyze a Teams channel conversation.
        
        Args:
            team_id: ID of the team.
            channel_id: ID of the channel.
            
        Returns:
            Dict[str, Any]: A dictionary with the conversation analysis.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            # Analyze conversation
            analysis = self.connection_manager.analyze_conversation(team_id, channel_id)
            
            # Store conversation analysis in page data
            self.page_data.conversation_analysis = analysis
            
            # Create visualization data
            visualization_data = {
                "type": "conversation",
                "message_count": analysis.get("message_count", 0),
                "participant_count": analysis.get("participant_count", 0),
                "participants": analysis.get("participants", []),
                "timeline": analysis.get("timeline", {}),
                "top_active_periods": analysis.get("top_active_periods", {})
            }
            
            # Store visualization data in page data
            self.page_data.visualization_data = visualization_data
            
            return {
                "success": True,
                "message": "Conversation analyzed successfully",
                "analysis": analysis,
                "visualization_data": visualization_data
            }
        except Exception as e:
            self.page_data.connection_errors["analysis"] = str(e)
            return {
                "success": False,
                "message": f"Error analyzing conversation: {str(e)}"
            }
    
    def extract_topics(self, team_id: str, channel_id: str) -> Dict[str, Any]:
        """
        Extract topics from a Teams channel conversation.
        
        Args:
            team_id: ID of the team.
            channel_id: ID of the channel.
            
        Returns:
            Dict[str, Any]: A dictionary with the extracted topics.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            # Extract topics
            topics = self.connection_manager.extract_conversation_topics(team_id, channel_id)
            
            # Store topic analysis in page data
            self.page_data.topic_analysis = topics
            
            return {
                "success": True,
                "message": "Topics extracted successfully",
                "topics": topics
            }
        except Exception as e:
            self.page_data.connection_errors["topics"] = str(e)
            return {
                "success": False,
                "message": f"Error extracting topics: {str(e)}"
            }
    
    def search_messages(self, team_id: str, channel_id: str, query: str) -> Dict[str, Any]:
        """
        Search for messages in a channel.
        
        Args:
            team_id: ID of the team.
            channel_id: ID of the channel.
            query: Search query.
            
        Returns:
            Dict[str, Any]: A dictionary with the search results.
        """
        try:
            if not self.connection_manager or not self.connection_manager.connected:
                return {
                    "success": False,
                    "message": "Not connected to Microsoft Graph API"
                }
            
            # Get all messages
            messages = self.connection_manager.get_messages(team_id, channel_id)
            
            # Filter messages by query
            search_results = []
            for message in messages:
                content = message.get("body", {}).get("content", "")
                if query.lower() in content.lower():
                    search_results.append(message)
            
            # Store search query and results in page data
            self.page_data.search_query = query
            self.page_data.search_results = search_results
            
            return {
                "success": True,
                "message": f"Found {len(search_results)} messages matching '{query}'",
                "results": search_results
            }
        except Exception as e:
            self.page_data.connection_errors["search"] = str(e)
            return {
                "success": False,
                "message": f"Error searching messages: {str(e)}"
            }
    
    def export_data(self, data_type: str, format: str) -> Dict[str, Any]:
        """
        Export data to a file.
        
        Args:
            data_type: Type of data to export (messages, analysis, topics).
            format: Format to export to (csv, json, excel).
            
        Returns:
            Dict[str, Any]: A dictionary with the export result.
        """
        try:
            # Determine data to export
            if data_type == "messages":
                if not self.page_data.messages:
                    return {
                        "success": False,
                        "message": "No messages to export"
                    }
                data = pd.DataFrame(self.page_data.messages)
                filename = "teams_messages"
            elif data_type == "analysis":
                if not self.page_data.conversation_analysis:
                    return {
                        "success": False,
                        "message": "No conversation analysis to export"
                    }
                data = pd.DataFrame({
                    "metric": ["message_count", "participant_count"],
                    "value": [
                        self.page_data.conversation_analysis.get("message_count", 0),
                        self.page_data.conversation_analysis.get("participant_count", 0)
                    ]
                })
                filename = "teams_conversation_analysis"
            elif data_type == "topics":
                if not self.page_data.topic_analysis:
                    return {
                        "success": False,
                        "message": "No topic analysis to export"
                    }
                data = pd.DataFrame(self.page_data.topic_analysis.get("potential_topics", []))
                filename = "teams_topics"
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