"""
MQTT Provider for Science Data Kit

This module provides a provider for connecting to MQTT brokers, allowing
the Science Data Kit to interact with MQTT for IoT and messaging applications.
"""

import json
import time
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import paho.mqtt.client as mqtt

from ...providers.registry import BaseProvider, ProviderType
from ...providers.abstract_providers import MessagingProvider


class MQTTProvider(MessagingProvider):
    """
    Provider for MQTT broker connections.
    
    This class provides functionality for connecting to MQTT brokers
    and interacting with topics for publishing and subscribing to messages.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the MQTT provider.
        
        Args:
            config: Configuration dictionary containing connection details
                   Required keys:
                   - host: MQTT broker host (default: localhost)
                   - port: MQTT broker port (default: 1883)
                   
                   Optional:
                   - client_id: Client ID for MQTT (default: sdk-mqtt-client-{random})
                   - username: Username for authentication
                   - password: Password for authentication
                   - use_tls: Whether to use TLS (default: False)
                   - tls_options: TLS options (if using TLS)
                   - keep_alive: Keep alive interval in seconds (default: 60)
                   - clean_session: Whether to use clean session (default: True)
                   - qos: Quality of Service level (default: 0)
                   - retain: Whether to retain messages (default: False)
        """
        super().__init__(config)
        self.client = None
        self.host = self.config.get('host', 'localhost')
        self.port = self.config.get('port', 1883)
        self.client_id = self.config.get('client_id', f'sdk-mqtt-client-{int(time.time())}')
        self.username = self.config.get('username', None)
        self.password = self.config.get('password', None)
        self.use_tls = self.config.get('use_tls', False)
        self.tls_options = self.config.get('tls_options', None)
        self.keep_alive = self.config.get('keep_alive', 60)
        self.clean_session = self.config.get('clean_session', True)
        self.qos = self.config.get('qos', 0)
        self.retain = self.config.get('retain', False)
        self.topics = {}  # Dictionary to track subscribed topics
        self.message_buffer = {}  # Buffer for received messages
        
    async def initialize(self) -> bool:
        """
        Initialize the MQTT provider with the provided configuration.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Create MQTT client
            self.client = mqtt.Client(client_id=self.client_id, clean_session=self.clean_session)
            
            # Set up authentication if provided
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            # Set up TLS if enabled
            if self.use_tls:
                if self.tls_options:
                    self.client.tls_set(**self.tls_options)
                else:
                    self.client.tls_set()
            
            # Set up callbacks
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect
            
            # Connect to broker
            self.client.connect(self.host, self.port, self.keep_alive)
            
            # Start the loop in a separate thread
            self.client.loop_start()
            
            # Wait for connection to establish
            for _ in range(10):  # Wait up to 5 seconds
                if self.client.is_connected():
                    self.is_initialized = True
                    return True
                time.sleep(0.5)
            
            # If we get here, connection failed
            self.client.loop_stop()
            self.is_initialized = False
            return False
            
        except Exception as e:
            print(f"Error initializing MQTT provider: {str(e)}")
            self.is_initialized = False
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the client connects to the broker.
        
        Args:
            client: MQTT client instance
            userdata: User data
            flags: Connection flags
            rc: Connection result code
        """
        if rc == 0:
            print("Connected to MQTT broker")
        else:
            print(f"Failed to connect to MQTT broker, return code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """
        Callback for when a message is received from the broker.
        
        Args:
            client: MQTT client instance
            userdata: User data
            msg: Received message
        """
        try:
            # Decode message payload
            payload = msg.payload.decode('utf-8')
            
            # Parse JSON if possible
            try:
                data = json.loads(payload)
            except:
                data = payload
            
            # Create message object
            message = {
                'topic': msg.topic,
                'value': data,
                'qos': msg.qos,
                'retain': msg.retain,
                'timestamp': time.time()
            }
            
            # Add message to buffer for the topic
            if msg.topic not in self.message_buffer:
                self.message_buffer[msg.topic] = []
            self.message_buffer[msg.topic].append(message)
            
            # Limit buffer size
            max_buffer_size = 1000
            if len(self.message_buffer[msg.topic]) > max_buffer_size:
                self.message_buffer[msg.topic] = self.message_buffer[msg.topic][-max_buffer_size:]
            
        except Exception as e:
            print(f"Error processing MQTT message: {str(e)}")
    
    def _on_disconnect(self, client, userdata, rc):
        """
        Callback for when the client disconnects from the broker.
        
        Args:
            client: MQTT client instance
            userdata: User data
            rc: Disconnection result code
        """
        if rc != 0:
            print(f"Unexpected disconnection from MQTT broker, return code: {rc}")
        else:
            print("Disconnected from MQTT broker")
    
    async def health_check(self) -> bool:
        """
        Check if the MQTT connection is healthy.
        
        Returns:
            True if the connection is healthy, False otherwise
        """
        if not self.is_initialized or not self.client:
            return False
        
        try:
            # Check if client is connected
            return self.client.is_connected()
        except Exception as e:
            print(f"MQTT health check failed: {str(e)}")
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the provider.
        
        Returns:
            Dictionary of provider capabilities
        """
        capabilities = {
            "type": ProviderType.MESSAGING.value,
            "name": "mqtt",
            "features": [
                "topic_subscription",
                "message_publishing",
                "message_consumption",
                "dataframe_integration",
                "quality_of_service",
                "retained_messages"
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
        List available topics in the MQTT broker.
        
        In MQTT, there is no standard way to list all topics on a broker.
        This method returns the topics that have been subscribed to through this provider.
        
        Returns:
            List of topic metadata dictionaries
        """
        if not self.is_initialized or not self.client:
            raise Exception("MQTT provider not initialized")
        
        try:
            # Return the list of topics that have been subscribed to
            topics = []
            for topic_name, topic_info in self.topics.items():
                topics.append({
                    "name": topic_name,
                    "qos": topic_info.get("qos", 0),
                    "subscribed_at": topic_info.get("subscribed_at", "")
                })
            
            return topics
        
        except Exception as e:
            print(f"Error listing topics: {str(e)}")
            raise
    
    async def create_topic(self, topic_name: str, partitions: int = 1, 
                          replication_factor: int = 1) -> bool:
        """
        Create a new topic in the MQTT broker.
        
        In MQTT, topics are created implicitly when publishing or subscribing.
        This method subscribes to the topic to ensure it exists.
        The partitions and replication_factor parameters are ignored as they are not applicable to MQTT.
        
        Args:
            topic_name: Name of the topic to create
            partitions: Ignored in MQTT
            replication_factor: Ignored in MQTT
            
        Returns:
            True if topic was created successfully, False otherwise
        """
        if not self.is_initialized or not self.client:
            raise Exception("MQTT provider not initialized")
        
        try:
            # In MQTT, topics are created implicitly
            # We'll subscribe to the topic to ensure it exists
            result, _ = self.client.subscribe(topic_name, qos=self.qos)
            
            if result == mqtt.MQTT_ERR_SUCCESS:
                # Register the topic in the internal registry
                import datetime
                self.topics[topic_name] = {
                    "qos": self.qos,
                    "subscribed_at": datetime.datetime.now().isoformat()
                }
                return True
            else:
                return False
        
        except Exception as e:
            print(f"Error creating topic: {str(e)}")
            return False
    
    async def delete_topic(self, topic_name: str) -> bool:
        """
        Delete a topic from the MQTT broker.
        
        In MQTT, there is no standard way to delete a topic.
        This method unsubscribes from the topic and removes it from the internal registry.
        
        Args:
            topic_name: Name of the topic to delete
            
        Returns:
            True if topic was deleted successfully, False otherwise
        """
        if not self.is_initialized or not self.client:
            raise Exception("MQTT provider not initialized")
        
        try:
            # Unsubscribe from the topic
            result, _ = self.client.unsubscribe(topic_name)
            
            if result == mqtt.MQTT_ERR_SUCCESS:
                # Remove the topic from the internal registry
                if topic_name in self.topics:
                    del self.topics[topic_name]
                
                # Clear message buffer for the topic
                if topic_name in self.message_buffer:
                    del self.message_buffer[topic_name]
                
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
        Publish a message to an MQTT topic.
        
        Args:
            topic_name: Name of the topic to publish to
            message: Message to publish (will be serialized to JSON)
            key: Ignored in MQTT (MQTT doesn't have message keys)
            headers: Ignored in MQTT (MQTT doesn't have message headers)
            
        Returns:
            True if message was published successfully, False otherwise
        """
        if not self.is_initialized or not self.client:
            raise Exception("MQTT provider not initialized")
        
        try:
            # Serialize message to JSON if it's not already a string
            if not isinstance(message, str):
                message_data = json.dumps(message)
            else:
                message_data = message
            
            # Publish message
            result = self.client.publish(
                topic=topic_name,
                payload=message_data,
                qos=self.qos,
                retain=self.retain
            )
            
            # Check result
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                # Wait for message to be published
                result.wait_for_publish()
                return True
            else:
                return False
        
        except Exception as e:
            print(f"Error publishing message: {str(e)}")
            return False
    
    async def publish_dataframe(self, topic_name: str, df: pd.DataFrame, 
                               key_column: Optional[str] = None) -> int:
        """
        Publish a pandas DataFrame to an MQTT topic, with each row as a separate message.
        
        Args:
            topic_name: Name of the topic to publish to
            df: Pandas DataFrame to publish
            key_column: Ignored in MQTT (MQTT doesn't have message keys)
            
        Returns:
            Number of messages published
        """
        if not self.is_initialized or not self.client:
            raise Exception("MQTT provider not initialized")
        
        try:
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            # Publish each record as a message
            messages_published = 0
            for record in records:
                # Publish message
                success = await self.publish_message(topic_name, record)
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
        Consume messages from an MQTT topic with a callback function.
        
        Args:
            topic_name: Name of the topic to consume from
            group_id: Ignored in MQTT (MQTT doesn't have consumer groups)
            callback: Callback function to process each message
            max_messages: Maximum number of messages to consume (None for unlimited)
            timeout_ms: Timeout in milliseconds
            
        Returns:
            Number of messages consumed
        """
        if not self.is_initialized or not self.client:
            raise Exception("MQTT provider not initialized")
        
        try:
            # Subscribe to the topic if not already subscribed
            if topic_name not in self.topics:
                await self.create_topic(topic_name)
            
            # Clear message buffer for the topic
            if topic_name in self.message_buffer:
                self.message_buffer[topic_name] = []
            else:
                self.message_buffer[topic_name] = []
            
            # Wait for messages to arrive
            start_time = time.time()
            end_time = start_time + (timeout_ms / 1000.0)
            
            # Process messages
            messages_consumed = 0
            while time.time() < end_time:
                # Check if we've reached the maximum number of messages
                if max_messages is not None and messages_consumed >= max_messages:
                    break
                
                # Check if there are messages in the buffer
                if topic_name in self.message_buffer and self.message_buffer[topic_name]:
                    # Get the next message
                    message = self.message_buffer[topic_name].pop(0)
                    
                    # Call callback function
                    callback(message)
                    
                    messages_consumed += 1
                else:
                    # No messages, sleep briefly
                    time.sleep(0.01)
            
            return messages_consumed
        
        except Exception as e:
            print(f"Error consuming messages: {str(e)}")
            raise
    
    async def consume_to_dataframe(self, topic_name: str, group_id: str,
                                  max_messages: int = 1000,
                                  timeout_ms: int = 1000) -> pd.DataFrame:
        """
        Consume messages from an MQTT topic and return as a pandas DataFrame.
        
        Args:
            topic_name: Name of the topic to consume from
            group_id: Ignored in MQTT (MQTT doesn't have consumer groups)
            max_messages: Maximum number of messages to consume
            timeout_ms: Timeout in milliseconds
            
        Returns:
            Pandas DataFrame containing the messages
        """
        if not self.is_initialized or not self.client:
            raise Exception("MQTT provider not initialized")
        
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
                values = [msg['value'] for msg in messages]
                
                # If values are dictionaries, create DataFrame directly
                if all(isinstance(v, dict) for v in values):
                    df = pd.DataFrame(values)
                else:
                    # Otherwise, create DataFrame with a single column
                    df = pd.DataFrame({'value': values})
                
                # Add metadata columns
                df['topic'] = [msg['topic'] for msg in messages]
                df['qos'] = [msg['qos'] for msg in messages]
                df['retain'] = [msg['retain'] for msg in messages]
                df['timestamp'] = [msg['timestamp'] for msg in messages]
                
                return df
            else:
                return pd.DataFrame()
        
        except Exception as e:
            print(f"Error consuming to DataFrame: {str(e)}")
            raise
    
    async def get_topic_info(self, topic_name: str) -> Dict[str, Any]:
        """
        Get information about an MQTT topic.
        
        Args:
            topic_name: Name of the topic
            
        Returns:
            Dictionary containing topic information
        """
        if not self.is_initialized or not self.client:
            raise Exception("MQTT provider not initialized")
        
        try:
            # Check if the topic exists in our registry
            if topic_name not in self.topics:
                raise Exception(f"Topic '{topic_name}' not found")
            
            # Get topic information
            topic_info = self.topics[topic_name].copy()
            topic_info["name"] = topic_name
            
            # Add message count if available
            if topic_name in self.message_buffer:
                topic_info["message_count"] = len(self.message_buffer[topic_name])
            else:
                topic_info["message_count"] = 0
            
            return topic_info
        
        except Exception as e:
            print(f"Error getting topic info: {str(e)}")
            raise