"""
RabbitMQ Provider for Science Data Kit

This module provides a provider for connecting to RabbitMQ message brokers, allowing
the Science Data Kit to interact with RabbitMQ for messaging and event-driven architecture.
"""

import json
import pandas as pd
import pika
from typing import Dict, List, Optional, Any, Union, Tuple, Callable

from ...providers.registry import BaseProvider, ProviderType
from ...providers.abstract_providers import MessagingProvider


class RabbitMQProvider(MessagingProvider):
    """
    Provider for RabbitMQ message broker connections.
    
    This class provides functionality for connecting to RabbitMQ message brokers
    and interacting with exchanges and queues for publishing and consuming messages.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the RabbitMQ provider.
        
        Args:
            config: Configuration dictionary containing connection details
                   Required keys:
                   - host: RabbitMQ host (default: localhost)
                   - port: RabbitMQ port (default: 5672)
                   
                   Optional:
                   - virtual_host: Virtual host (default: /)
                   - username: Username for authentication (default: guest)
                   - password: Password for authentication (default: guest)
                   - ssl: Whether to use SSL (default: False)
                   - ssl_options: SSL options (if using SSL)
                   - connection_attempts: Number of connection attempts (default: 3)
                   - retry_delay: Delay between connection attempts in seconds (default: 2)
                   - heartbeat: Heartbeat interval in seconds (default: 60)
        """
        super().__init__(config)
        self.connection = None
        self.channel = None
        self.host = self.config.get('host', 'localhost')
        self.port = self.config.get('port', 5672)
        self.virtual_host = self.config.get('virtual_host', '/')
        self.username = self.config.get('username', 'guest')
        self.password = self.config.get('password', 'guest')
        self.ssl = self.config.get('ssl', False)
        self.ssl_options = self.config.get('ssl_options', None)
        self.connection_attempts = self.config.get('connection_attempts', 3)
        self.retry_delay = self.config.get('retry_delay', 2)
        self.heartbeat = self.config.get('heartbeat', 60)
        
    async def initialize(self) -> bool:
        """
        Initialize the RabbitMQ provider with the provided configuration.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Build connection parameters
            credentials = pika.PlainCredentials(self.username, self.password)
            
            connection_params = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                ssl=self.ssl,
                ssl_options=self.ssl_options,
                connection_attempts=self.connection_attempts,
                retry_delay=self.retry_delay,
                heartbeat=self.heartbeat
            )
            
            # Create connection
            self.connection = pika.BlockingConnection(connection_params)
            
            # Create channel
            self.channel = self.connection.channel()
            
            # Test connection
            self.channel.exchange_declare(
                exchange='sdk.test',
                exchange_type='direct',
                passive=False,
                durable=True,
                auto_delete=True
            )
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"Error initializing RabbitMQ provider: {str(e)}")
            self.is_initialized = False
            return False
    
    async def health_check(self) -> bool:
        """
        Check if the RabbitMQ connection is healthy.
        
        Returns:
            True if the connection is healthy, False otherwise
        """
        if not self.is_initialized or not self.connection or not self.channel:
            return False
        
        try:
            # Check if connection is open
            if not self.connection.is_open:
                return False
            
            # Check if channel is open
            if not self.channel.is_open:
                return False
            
            return True
        except Exception as e:
            print(f"RabbitMQ health check failed: {str(e)}")
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the provider.
        
        Returns:
            Dictionary of provider capabilities
        """
        capabilities = {
            "type": ProviderType.MESSAGING.value,
            "name": "rabbitmq",
            "features": [
                "exchange_management",
                "queue_management",
                "message_publishing",
                "message_consumption",
                "dataframe_integration",
                "routing_keys"
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
        List available exchanges in the RabbitMQ server.
        
        In RabbitMQ, exchanges are analogous to topics in other messaging systems.
        
        Returns:
            List of exchange metadata dictionaries
        """
        if not self.is_initialized or not self.connection or not self.channel:
            raise Exception("RabbitMQ provider not initialized")
        
        try:
            # Unfortunately, RabbitMQ doesn't provide a direct API to list exchanges
            # We'll return a list of common exchanges that are typically available
            
            exchanges = [
                {
                    "name": "",
                    "type": "direct",
                    "description": "Default exchange"
                },
                {
                    "name": "amq.direct",
                    "type": "direct",
                    "description": "Direct exchange"
                },
                {
                    "name": "amq.topic",
                    "type": "topic",
                    "description": "Topic exchange"
                },
                {
                    "name": "amq.fanout",
                    "type": "fanout",
                    "description": "Fanout exchange"
                },
                {
                    "name": "amq.headers",
                    "type": "headers",
                    "description": "Headers exchange"
                }
            ]
            
            # Add any custom exchanges created by the SDK
            # This is a limitation of the RabbitMQ API, as it doesn't provide a way to list all exchanges
            
            return exchanges
        
        except Exception as e:
            print(f"Error listing exchanges: {str(e)}")
            raise
    
    async def create_topic(self, topic_name: str, partitions: int = 1, 
                          replication_factor: int = 1) -> bool:
        """
        Create a new exchange in the RabbitMQ server.
        
        In RabbitMQ, exchanges are analogous to topics in other messaging systems.
        The partitions and replication_factor parameters are ignored as they are not applicable to RabbitMQ.
        
        Args:
            topic_name: Name of the exchange to create
            partitions: Ignored in RabbitMQ
            replication_factor: Ignored in RabbitMQ
            
        Returns:
            True if exchange was created successfully, False otherwise
        """
        if not self.is_initialized or not self.connection or not self.channel:
            raise Exception("RabbitMQ provider not initialized")
        
        try:
            # Create exchange
            self.channel.exchange_declare(
                exchange=topic_name,
                exchange_type='topic',  # Using topic exchange as default
                passive=False,
                durable=True,
                auto_delete=False
            )
            
            return True
        
        except Exception as e:
            print(f"Error creating exchange: {str(e)}")
            return False
    
    async def delete_topic(self, topic_name: str) -> bool:
        """
        Delete an exchange from the RabbitMQ server.
        
        In RabbitMQ, exchanges are analogous to topics in other messaging systems.
        
        Args:
            topic_name: Name of the exchange to delete
            
        Returns:
            True if exchange was deleted successfully, False otherwise
        """
        if not self.is_initialized or not self.connection or not self.channel:
            raise Exception("RabbitMQ provider not initialized")
        
        try:
            # Delete exchange
            self.channel.exchange_delete(
                exchange=topic_name,
                if_unused=False
            )
            
            return True
        
        except Exception as e:
            print(f"Error deleting exchange: {str(e)}")
            return False
    
    async def publish_message(self, topic_name: str, message: Any, 
                             key: Optional[str] = None, 
                             headers: Optional[Dict[str, str]] = None) -> bool:
        """
        Publish a message to a RabbitMQ exchange.
        
        Args:
            topic_name: Name of the exchange to publish to
            message: Message to publish (will be serialized to JSON)
            key: Optional routing key
            headers: Optional message headers
            
        Returns:
            True if message was published successfully, False otherwise
        """
        if not self.is_initialized or not self.connection or not self.channel:
            raise Exception("RabbitMQ provider not initialized")
        
        try:
            # Serialize message to JSON if it's not already a string
            if not isinstance(message, str):
                message = json.dumps(message)
            
            # Convert headers to RabbitMQ format if provided
            properties = pika.BasicProperties(
                content_type='application/json',
                delivery_mode=2,  # make message persistent
                headers=headers
            )
            
            # Use default routing key if not provided
            routing_key = key if key else 'default'
            
            # Publish message
            self.channel.basic_publish(
                exchange=topic_name,
                routing_key=routing_key,
                body=message.encode('utf-8'),
                properties=properties
            )
            
            return True
        
        except Exception as e:
            print(f"Error publishing message: {str(e)}")
            return False
    
    async def publish_dataframe(self, topic_name: str, df: pd.DataFrame, 
                               key_column: Optional[str] = None) -> int:
        """
        Publish a pandas DataFrame to a RabbitMQ exchange, with each row as a separate message.
        
        Args:
            topic_name: Name of the exchange to publish to
            df: Pandas DataFrame to publish
            key_column: Optional column to use as routing key
            
        Returns:
            Number of messages published
        """
        if not self.is_initialized or not self.connection or not self.channel:
            raise Exception("RabbitMQ provider not initialized")
        
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
        Consume messages from a RabbitMQ queue bound to an exchange.
        
        Args:
            topic_name: Name of the exchange to consume from
            group_id: Queue name (analogous to consumer group ID in other systems)
            callback: Callback function to process each message
            max_messages: Maximum number of messages to consume (None for unlimited)
            timeout_ms: Timeout in milliseconds
            
        Returns:
            Number of messages consumed
        """
        if not self.is_initialized or not self.connection or not self.channel:
            raise Exception("RabbitMQ provider not initialized")
        
        try:
            # Declare queue
            result = self.channel.queue_declare(queue=group_id, durable=True)
            queue_name = result.method.queue
            
            # Bind queue to exchange
            self.channel.queue_bind(
                exchange=topic_name,
                queue=queue_name,
                routing_key='#'  # Bind to all routing keys
            )
            
            # Set up message counter
            messages_consumed = 0
            
            # Define message handler
            def message_handler(ch, method, properties, body):
                nonlocal messages_consumed
                
                try:
                    # Decode message body
                    message_str = body.decode('utf-8')
                    
                    # Parse JSON if possible
                    try:
                        data = json.loads(message_str)
                    except:
                        data = message_str
                    
                    # Create message object
                    message = {
                        'exchange': method.exchange,
                        'routing_key': method.routing_key,
                        'delivery_tag': method.delivery_tag,
                        'value': data,
                        'timestamp': properties.timestamp
                    }
                    
                    # Add headers if present
                    if properties.headers:
                        message['headers'] = properties.headers
                    
                    # Call callback function
                    callback(message)
                    
                    # Acknowledge message
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                    messages_consumed += 1
                    
                    # Stop consuming if we've reached the maximum number of messages
                    if max_messages is not None and messages_consumed >= max_messages:
                        ch.stop_consuming()
                    
                except Exception as e:
                    print(f"Error processing message: {str(e)}")
                    # Negative acknowledgement to requeue the message
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
            # Set up consumer
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=message_handler
            )
            
            # Start consuming with timeout
            if max_messages is None:
                # If no max_messages is specified, consume for a fixed time
                self.connection.call_later(timeout_ms / 1000.0, self.channel.stop_consuming)
            
            # Start consuming
            self.channel.start_consuming()
            
            return messages_consumed
        
        except Exception as e:
            print(f"Error consuming messages: {str(e)}")
            raise
    
    async def consume_to_dataframe(self, topic_name: str, group_id: str,
                                  max_messages: int = 1000,
                                  timeout_ms: int = 1000) -> pd.DataFrame:
        """
        Consume messages from a RabbitMQ queue bound to an exchange and return as a pandas DataFrame.
        
        Args:
            topic_name: Name of the exchange to consume from
            group_id: Queue name (analogous to consumer group ID in other systems)
            max_messages: Maximum number of messages to consume
            timeout_ms: Timeout in milliseconds
            
        Returns:
            Pandas DataFrame containing the messages
        """
        if not self.is_initialized or not self.connection or not self.channel:
            raise Exception("RabbitMQ provider not initialized")
        
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
                df['exchange'] = [msg['exchange'] for msg in messages]
                df['routing_key'] = [msg['routing_key'] for msg in messages]
                df['delivery_tag'] = [msg['delivery_tag'] for msg in messages]
                if 'timestamp' in messages[0]:
                    df['timestamp'] = [msg['timestamp'] for msg in messages]
                
                return df
            else:
                return pd.DataFrame()
        
        except Exception as e:
            print(f"Error consuming to DataFrame: {str(e)}")
            raise
    
    async def get_topic_info(self, topic_name: str) -> Dict[str, Any]:
        """
        Get information about a RabbitMQ exchange.
        
        Args:
            topic_name: Name of the exchange
            
        Returns:
            Dictionary containing exchange information
        """
        if not self.is_initialized or not self.connection or not self.channel:
            raise Exception("RabbitMQ provider not initialized")
        
        try:
            # Check if exchange exists by declaring it passively
            try:
                self.channel.exchange_declare(
                    exchange=topic_name,
                    passive=True
                )
                exists = True
            except Exception:
                exists = False
            
            if not exists:
                raise Exception(f"Exchange '{topic_name}' not found")
            
            # Get bound queues
            # Note: RabbitMQ doesn't provide a direct API to get this information
            # This is a limitation of the RabbitMQ API
            
            # Return basic exchange info
            exchange_info = {
                "name": topic_name,
                "exists": exists,
                "type": "unknown",  # RabbitMQ doesn't provide a way to get this information
                "queues": []  # RabbitMQ doesn't provide a way to get this information
            }
            
            return exchange_info
        
        except Exception as e:
            print(f"Error getting exchange info: {str(e)}")
            raise