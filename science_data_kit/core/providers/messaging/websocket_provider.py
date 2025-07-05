"""
WebSocket Provider for Science Data Kit

This module provides a provider for WebSocket streaming, allowing
the Science Data Kit to interact with WebSocket endpoints for real-time
data streaming and bidirectional communication.
"""

import json
import asyncio
import websockets
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from urllib.parse import urlparse

from ...providers.registry import BaseProvider, ProviderType
from ...providers.abstract_providers import MessagingProvider


class WebSocketProvider(MessagingProvider):
    """
    Provider for WebSocket connections.
    
    This class provides functionality for connecting to WebSocket endpoints
    and streaming data in real-time with bidirectional communication.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the WebSocket provider.
        
        Args:
            config: Configuration dictionary containing connection details
                   Required keys:
                   - url: WebSocket server URL (e.g., ws://localhost:8765)
                   
                   Optional:
                   - headers: Headers to include in the WebSocket handshake
                   - auth: Authentication details (username, password)
                   - ping_interval: Interval in seconds for sending ping frames (default: 20)
                   - ping_timeout: Timeout in seconds for ping responses (default: 20)
                   - close_timeout: Timeout in seconds for close handshake (default: 10)
                   - max_size: Maximum size of incoming messages in bytes (default: 1MB)
                   - max_queue: Maximum number of messages to queue (default: 32)
        """
        super().__init__(config)
        self.websocket = None
        self.url = self.config.get('url', 'ws://localhost:8765')
        self.headers = self.config.get('headers', {})
        self.auth = self.config.get('auth', None)
        self.ping_interval = self.config.get('ping_interval', 20)
        self.ping_timeout = self.config.get('ping_timeout', 20)
        self.close_timeout = self.config.get('close_timeout', 10)
        self.max_size = self.config.get('max_size', 2**20)  # 1MB
        self.max_queue = self.config.get('max_queue', 32)
        self.topics = {}  # Dictionary to track active topics/channels
        
    async def initialize(self) -> bool:
        """
        Initialize the WebSocket provider with the provided configuration.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Parse URL to extract authentication if provided in URL
            parsed_url = urlparse(self.url)
            if parsed_url.username and parsed_url.password and not self.auth:
                self.auth = {
                    'username': parsed_url.username,
                    'password': parsed_url.password
                }
            
            # Build extra_headers for authentication if needed
            extra_headers = self.headers.copy()
            if self.auth:
                import base64
                auth_str = f"{self.auth.get('username', '')}:{self.auth.get('password', '')}"
                auth_header = base64.b64encode(auth_str.encode()).decode()
                extra_headers['Authorization'] = f"Basic {auth_header}"
            
            # Test connection by connecting briefly
            async with websockets.connect(
                self.url,
                extra_headers=extra_headers,
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout,
                close_timeout=self.close_timeout,
                max_size=self.max_size,
                max_queue=self.max_queue
            ) as websocket:
                # Send a test message
                await websocket.send(json.dumps({"type": "connection_test"}))
                # Wait for a response with a timeout
                try:
                    await asyncio.wait_for(websocket.recv(), timeout=5.0)
                except asyncio.TimeoutError:
                    # Some WebSocket servers don't respond to test messages, which is fine
                    pass
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"Error initializing WebSocket provider: {str(e)}")
            self.is_initialized = False
            return False
    
    async def health_check(self) -> bool:
        """
        Check if the WebSocket connection is healthy.
        
        Returns:
            True if the connection is healthy, False otherwise
        """
        if not self.is_initialized:
            return False
        
        try:
            # Test connection by connecting briefly
            async with websockets.connect(
                self.url,
                extra_headers=self.headers,
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout,
                close_timeout=self.close_timeout,
                max_size=self.max_size,
                max_queue=self.max_queue
            ) as websocket:
                # Send a ping frame
                pong_waiter = await websocket.ping()
                await asyncio.wait_for(pong_waiter, timeout=5.0)
                return True
        except Exception as e:
            print(f"WebSocket health check failed: {str(e)}")
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the provider.
        
        Returns:
            Dictionary of provider capabilities
        """
        capabilities = {
            "type": ProviderType.MESSAGING.value,
            "name": "websocket",
            "features": [
                "bidirectional_communication",
                "real_time_streaming",
                "message_publishing",
                "message_consumption",
                "dataframe_integration"
            ],
            "supported_operations": [
                "create_topic",
                "delete_topic",
                "list_topics",
                "publish_message",
                "consume_messages",
                "publish_dataframe",
                "consume_to_dataframe"
            ]
        }
        
        return capabilities
    
    async def list_topics(self) -> List[Dict[str, Any]]:
        """
        List available topics/channels in the WebSocket connection.
        
        In WebSocket, topics are virtual and managed by the application layer.
        This method returns the topics that have been created through this provider.
        
        Returns:
            List of topic metadata dictionaries
        """
        if not self.is_initialized:
            raise Exception("WebSocket provider not initialized")
        
        try:
            # Return the list of topics that have been created
            topics = []
            for topic_name, topic_info in self.topics.items():
                topics.append({
                    "name": topic_name,
                    "subscribers": topic_info.get("subscribers", 0),
                    "created_at": topic_info.get("created_at", "")
                })
            
            return topics
        
        except Exception as e:
            print(f"Error listing topics: {str(e)}")
            raise
    
    async def create_topic(self, topic_name: str, partitions: int = 1, 
                          replication_factor: int = 1) -> bool:
        """
        Create a new topic/channel for the WebSocket connection.
        
        In WebSocket, topics are virtual and managed by the application layer.
        This method registers a new topic in the provider's internal registry.
        The partitions and replication_factor parameters are ignored as they are not applicable to WebSockets.
        
        Args:
            topic_name: Name of the topic to create
            partitions: Ignored in WebSocket
            replication_factor: Ignored in WebSocket
            
        Returns:
            True if topic was created successfully, False otherwise
        """
        if not self.is_initialized:
            raise Exception("WebSocket provider not initialized")
        
        try:
            # Register the topic in the internal registry
            import datetime
            self.topics[topic_name] = {
                "subscribers": 0,
                "created_at": datetime.datetime.now().isoformat()
            }
            
            return True
        
        except Exception as e:
            print(f"Error creating topic: {str(e)}")
            return False
    
    async def delete_topic(self, topic_name: str) -> bool:
        """
        Delete a topic/channel from the WebSocket connection.
        
        In WebSocket, topics are virtual and managed by the application layer.
        This method removes a topic from the provider's internal registry.
        
        Args:
            topic_name: Name of the topic to delete
            
        Returns:
            True if topic was deleted successfully, False otherwise
        """
        if not self.is_initialized:
            raise Exception("WebSocket provider not initialized")
        
        try:
            # Remove the topic from the internal registry
            if topic_name in self.topics:
                del self.topics[topic_name]
                return True
            else:
                return False
        
        except Exception as e:
            print(f"Error deleting topic: {str(e)}")
            return False
    
    async def publish_message(self, topic_name: str, message: Any, 
                             key: Optional[str] = None, 
                             headers: Optional[Dict[str, str]] = None) -> bool:
        """
        Publish a message to a WebSocket topic/channel.
        
        Args:
            topic_name: Name of the topic to publish to
            message: Message to publish (will be serialized to JSON)
            key: Optional message key
            headers: Optional message headers
            
        Returns:
            True if message was published successfully, False otherwise
        """
        if not self.is_initialized:
            raise Exception("WebSocket provider not initialized")
        
        try:
            # Check if the topic exists
            if topic_name not in self.topics:
                await self.create_topic(topic_name)
            
            # Build extra_headers for authentication if needed
            extra_headers = self.headers.copy()
            if self.auth:
                import base64
                auth_str = f"{self.auth.get('username', '')}:{self.auth.get('password', '')}"
                auth_header = base64.b64encode(auth_str.encode()).decode()
                extra_headers['Authorization'] = f"Basic {auth_header}"
            
            # Connect to the WebSocket server
            async with websockets.connect(
                self.url,
                extra_headers=extra_headers,
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout,
                close_timeout=self.close_timeout,
                max_size=self.max_size,
                max_queue=self.max_queue
            ) as websocket:
                # Prepare the message
                if not isinstance(message, str):
                    message_data = json.dumps(message)
                else:
                    message_data = message
                
                # Create a wrapper with topic and headers
                wrapper = {
                    "topic": topic_name,
                    "payload": message_data
                }
                
                if key:
                    wrapper["key"] = key
                
                if headers:
                    wrapper["headers"] = headers
                
                # Send the message
                await websocket.send(json.dumps(wrapper))
                
                return True
        
        except Exception as e:
            print(f"Error publishing message: {str(e)}")
            return False
    
    async def publish_dataframe(self, topic_name: str, df: pd.DataFrame, 
                               key_column: Optional[str] = None) -> int:
        """
        Publish a pandas DataFrame to a WebSocket topic/channel, with each row as a separate message.
        
        Args:
            topic_name: Name of the topic to publish to
            df: Pandas DataFrame to publish
            key_column: Optional column to use as message key
            
        Returns:
            Number of messages published
        """
        if not self.is_initialized:
            raise Exception("WebSocket provider not initialized")
        
        try:
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            # Publish each record as a message
            messages_published = 0
            for record in records:
                # Get key if key_column is specified
                key = None
                if key_column and key_column in record:
                    key = str(record[key_column])
                
                # Publish message
                success = await self.publish_message(topic_name, record, key)
                if success:
                    messages_published += 1
            
            return messages_published
        
        except Exception as e:
            print(f"Error publishing DataFrame: {str(e)}")
            raise
    
    async def consume_messages(self, topic_name: str, group_id: str, 
                              callback: Callable[[Dict[str, Any]], None],
                              max_messages: Optional[int] = None,
                              timeout_ms: int = 1000) -> int:
        """
        Consume messages from a WebSocket topic/channel with a callback function.
        
        Args:
            topic_name: Name of the topic to consume from
            group_id: Consumer group ID (used for identification in WebSocket)
            callback: Callback function to process each message
            max_messages: Maximum number of messages to consume (None for unlimited)
            timeout_ms: Timeout in milliseconds
            
        Returns:
            Number of messages consumed
        """
        if not self.is_initialized:
            raise Exception("WebSocket provider not initialized")
        
        try:
            # Check if the topic exists
            if topic_name not in self.topics:
                await self.create_topic(topic_name)
            
            # Update subscriber count
            self.topics[topic_name]["subscribers"] = self.topics[topic_name].get("subscribers", 0) + 1
            
            # Build extra_headers for authentication if needed
            extra_headers = self.headers.copy()
            if self.auth:
                import base64
                auth_str = f"{self.auth.get('username', '')}:{self.auth.get('password', '')}"
                auth_header = base64.b64encode(auth_str.encode()).decode()
                extra_headers['Authorization'] = f"Basic {auth_header}"
            
            # Connect to the WebSocket server
            async with websockets.connect(
                self.url,
                extra_headers=extra_headers,
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout,
                close_timeout=self.close_timeout,
                max_size=self.max_size,
                max_queue=self.max_queue
            ) as websocket:
                # Send subscription message
                subscription_message = {
                    "type": "subscribe",
                    "topic": topic_name,
                    "group_id": group_id
                }
                await websocket.send(json.dumps(subscription_message))
                
                # Set up message counter
                messages_consumed = 0
                
                # Calculate end time for timeout
                end_time = asyncio.get_event_loop().time() + (timeout_ms / 1000.0)
                
                # Consume messages
                while True:
                    # Check if we've reached the maximum number of messages
                    if max_messages is not None and messages_consumed >= max_messages:
                        break
                    
                    # Calculate remaining timeout
                    remaining_time = end_time - asyncio.get_event_loop().time()
                    if remaining_time <= 0:
                        break
                    
                    # Receive message with timeout
                    try:
                        message_str = await asyncio.wait_for(websocket.recv(), timeout=remaining_time)
                        
                        # Parse message
                        try:
                            message_data = json.loads(message_str)
                        except:
                            message_data = message_str
                        
                        # Check if it's a message for our topic
                        if isinstance(message_data, dict) and message_data.get("topic") == topic_name:
                            # Create message object
                            message = {
                                'topic': message_data.get("topic"),
                                'value': message_data.get("payload"),
                                'timestamp': message_data.get("timestamp")
                            }
                            
                            # Add key if present
                            if "key" in message_data:
                                message["key"] = message_data["key"]
                            
                            # Add headers if present
                            if "headers" in message_data:
                                message["headers"] = message_data["headers"]
                            
                            # Call callback function
                            callback(message)
                            
                            messages_consumed += 1
                    except asyncio.TimeoutError:
                        # Timeout reached
                        break
                
                # Send unsubscribe message
                unsubscribe_message = {
                    "type": "unsubscribe",
                    "topic": topic_name,
                    "group_id": group_id
                }
                await websocket.send(json.dumps(unsubscribe_message))
                
                # Update subscriber count
                self.topics[topic_name]["subscribers"] = max(0, self.topics[topic_name].get("subscribers", 1) - 1)
                
                return messages_consumed
        
        except Exception as e:
            print(f"Error consuming messages: {str(e)}")
            raise
    
    async def consume_to_dataframe(self, topic_name: str, group_id: str,
                                  max_messages: int = 1000,
                                  timeout_ms: int = 1000) -> pd.DataFrame:
        """
        Consume messages from a WebSocket topic/channel and return as a pandas DataFrame.
        
        Args:
            topic_name: Name of the topic to consume from
            group_id: Consumer group ID (used for identification in WebSocket)
            max_messages: Maximum number of messages to consume
            timeout_ms: Timeout in milliseconds
            
        Returns:
            Pandas DataFrame containing the messages
        """
        if not self.is_initialized:
            raise Exception("WebSocket provider not initialized")
        
        try:
            # Collect messages
            messages = []
            
            # Define callback function to collect messages
            def collect_message(message):
                messages.append(message)
            
            # Consume messages
            await self.consume_messages(
                topic_name=topic_name,
                group_id=group_id,
                callback=collect_message,
                max_messages=max_messages,
                timeout_ms=timeout_ms
            )
            
            # Convert messages to DataFrame
            if messages:
                # Extract values from messages
                values = []
                for msg in messages:
                    if isinstance(msg['value'], str):
                        try:
                            value = json.loads(msg['value'])
                        except:
                            value = msg['value']
                    else:
                        value = msg['value']
                    values.append(value)
                
                # If values are dictionaries, create DataFrame directly
                if all(isinstance(v, dict) for v in values):
                    df = pd.DataFrame(values)
                else:
                    # Otherwise, create DataFrame with a single column
                    df = pd.DataFrame({'value': values})
                
                # Add metadata columns
                df['topic'] = [msg['topic'] for msg in messages]
                if 'timestamp' in messages[0]:
                    df['timestamp'] = [msg['timestamp'] for msg in messages]
                if 'key' in messages[0]:
                    df['key'] = [msg.get('key') for msg in messages]
                
                return df
            else:
                return pd.DataFrame()
        
        except Exception as e:
            print(f"Error consuming to DataFrame: {str(e)}")
            raise
    
    async def get_topic_info(self, topic_name: str) -> Dict[str, Any]:
        """
        Get information about a WebSocket topic/channel.
        
        Args:
            topic_name: Name of the topic
            
        Returns:
            Dictionary containing topic information
        """
        if not self.is_initialized:
            raise Exception("WebSocket provider not initialized")
        
        try:
            # Check if the topic exists
            if topic_name not in self.topics:
                raise Exception(f"Topic '{topic_name}' not found")
            
            # Return topic information
            topic_info = self.topics[topic_name].copy()
            topic_info["name"] = topic_name
            
            return topic_info
        
        except Exception as e:
            print(f"Error getting topic info: {str(e)}")
            raise