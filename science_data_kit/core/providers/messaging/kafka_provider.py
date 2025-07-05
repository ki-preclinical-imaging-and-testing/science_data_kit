"""
Kafka Provider for Science Data Kit

This module provides a provider for connecting to Kafka message brokers, allowing
the Science Data Kit to interact with Kafka for streaming data processing.
"""

import json
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError, TopicPartition
from confluent_kafka.admin import AdminClient, NewTopic, ConfigResource, ConfigResourceType

from ...providers.registry import BaseProvider, ProviderType
from ...providers.abstract_providers import MessagingProvider


class KafkaProvider(MessagingProvider):
    """
    Provider for Kafka message broker connections.
    
    This class provides functionality for connecting to Kafka message brokers
    and interacting with topics for publishing and consuming messages.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Kafka provider.
        
        Args:
            config: Configuration dictionary containing connection details
                   Required keys:
                   - bootstrap_servers: Comma-separated list of Kafka brokers (default: localhost:9092)
                   
                   Optional:
                   - client_id: Client ID for Kafka (default: sdk-kafka-client)
                   - security_protocol: Security protocol (default: PLAINTEXT)
                   - sasl_mechanism: SASL mechanism (if using SASL)
                   - sasl_username: SASL username (if using SASL)
                   - sasl_password: SASL password (if using SASL)
                   - ssl_cafile: Path to CA file (if using SSL)
                   - ssl_certfile: Path to certificate file (if using SSL)
                   - ssl_keyfile: Path to key file (if using SSL)
        """
        super().__init__(config)
        self.producer = None
        self.admin_client = None
        self.bootstrap_servers = self.config.get('bootstrap_servers', 'localhost:9092')
        self.client_id = self.config.get('client_id', 'sdk-kafka-client')
        
    async def initialize(self) -> bool:
        """
        Initialize the Kafka provider with the provided configuration.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Build Kafka configuration
            kafka_config = {
                'bootstrap.servers': self.bootstrap_servers,
                'client.id': self.client_id,
            }
            
            # Add security configuration if provided
            security_protocol = self.config.get('security_protocol', 'PLAINTEXT')
            kafka_config['security.protocol'] = security_protocol
            
            if security_protocol in ['SASL_PLAINTEXT', 'SASL_SSL']:
                sasl_mechanism = self.config.get('sasl_mechanism', 'PLAIN')
                kafka_config['sasl.mechanism'] = sasl_mechanism
                
                if sasl_mechanism in ['PLAIN', 'SCRAM-SHA-256', 'SCRAM-SHA-512']:
                    kafka_config['sasl.username'] = self.config.get('sasl_username', '')
                    kafka_config['sasl.password'] = self.config.get('sasl_password', '')
            
            if security_protocol in ['SSL', 'SASL_SSL']:
                ssl_cafile = self.config.get('ssl_cafile')
                ssl_certfile = self.config.get('ssl_certfile')
                ssl_keyfile = self.config.get('ssl_keyfile')
                
                if ssl_cafile:
                    kafka_config['ssl.ca.location'] = ssl_cafile
                if ssl_certfile:
                    kafka_config['ssl.certificate.location'] = ssl_certfile
                if ssl_keyfile:
                    kafka_config['ssl.key.location'] = ssl_keyfile
            
            # Create producer
            self.producer = Producer(kafka_config)
            
            # Create admin client
            self.admin_client = AdminClient(kafka_config)
            
            # Test connection
            cluster_metadata = self.admin_client.list_topics(timeout=10)
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"Error initializing Kafka provider: {str(e)}")
            self.is_initialized = False
            return False
    
    async def health_check(self) -> bool:
        """
        Check if the Kafka connection is healthy.
        
        Returns:
            True if the connection is healthy, False otherwise
        """
        if not self.is_initialized or not self.producer or not self.admin_client:
            return False
        
        try:
            # Test connection by listing topics
            self.admin_client.list_topics(timeout=5)
            return True
        except Exception as e:
            print(f"Kafka health check failed: {str(e)}")
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the provider.
        
        Returns:
            Dictionary of provider capabilities
        """
        capabilities = {
            "type": ProviderType.MESSAGING.value,
            "name": "kafka",
            "features": [
                "topic_management",
                "message_publishing",
                "message_consumption",
                "dataframe_integration",
                "streaming_data"
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
        List available topics in the Kafka cluster.
        
        Returns:
            List of topic metadata dictionaries
        """
        if not self.is_initialized or not self.admin_client:
            raise Exception("Kafka provider not initialized")
        
        try:
            # Get topic metadata
            topics_metadata = self.admin_client.list_topics(timeout=10)
            
            # Extract topic information
            topics = []
            for topic_name, topic_metadata in topics_metadata.topics.items():
                # Skip internal topics
                if topic_name.startswith('__'):
                    continue
                
                # Get partition information
                partitions = []
                for partition_id, partition_metadata in topic_metadata.partitions.items():
                    partitions.append({
                        "id": partition_id,
                        "leader": partition_metadata.leader,
                        "replicas": partition_metadata.replicas,
                        "isrs": partition_metadata.isrs
                    })
                
                # Add topic to the list
                topics.append({
                    "name": topic_name,
                    "partitions": partitions,
                    "partition_count": len(partitions)
                })
            
            return topics
        
        except Exception as e:
            print(f"Error listing topics: {str(e)}")
            raise
    
    async def create_topic(self, topic_name: str, partitions: int = 1, 
                          replication_factor: int = 1) -> bool:
        """
        Create a new topic in the Kafka cluster.
        
        Args:
            topic_name: Name of the topic to create
            partitions: Number of partitions for the topic
            replication_factor: Replication factor for the topic
            
        Returns:
            True if topic was created successfully, False otherwise
        """
        if not self.is_initialized or not self.admin_client:
            raise Exception("Kafka provider not initialized")
        
        try:
            # Create new topic
            new_topic = NewTopic(
                topic_name,
                num_partitions=partitions,
                replication_factor=replication_factor
            )
            
            # Create topic in Kafka
            result = self.admin_client.create_topics([new_topic])
            
            # Wait for operation to complete
            for topic, future in result.items():
                try:
                    future.result()  # Wait for completion
                    return True
                except Exception as e:
                    print(f"Failed to create topic {topic}: {str(e)}")
                    return False
            
            return False
        
        except Exception as e:
            print(f"Error creating topic: {str(e)}")
            return False
    
    async def delete_topic(self, topic_name: str) -> bool:
        """
        Delete a topic from the Kafka cluster.
        
        Args:
            topic_name: Name of the topic to delete
            
        Returns:
            True if topic was deleted successfully, False otherwise
        """
        if not self.is_initialized or not self.admin_client:
            raise Exception("Kafka provider not initialized")
        
        try:
            # Delete topic
            result = self.admin_client.delete_topics([topic_name])
            
            # Wait for operation to complete
            for topic, future in result.items():
                try:
                    future.result()  # Wait for completion
                    return True
                except Exception as e:
                    print(f"Failed to delete topic {topic}: {str(e)}")
                    return False
            
            return False
        
        except Exception as e:
            print(f"Error deleting topic: {str(e)}")
            return False
    
    async def publish_message(self, topic_name: str, message: Any, 
                             key: Optional[str] = None, 
                             headers: Optional[Dict[str, str]] = None) -> bool:
        """
        Publish a message to a Kafka topic.
        
        Args:
            topic_name: Name of the topic to publish to
            message: Message to publish (will be serialized to JSON)
            key: Optional message key
            headers: Optional message headers
            
        Returns:
            True if message was published successfully, False otherwise
        """
        if not self.is_initialized or not self.producer:
            raise Exception("Kafka provider not initialized")
        
        try:
            # Serialize message to JSON if it's not already a string
            if not isinstance(message, str):
                message = json.dumps(message)
            
            # Convert headers to Kafka format if provided
            kafka_headers = None
            if headers:
                kafka_headers = [(k, v.encode('utf-8')) for k, v in headers.items()]
            
            # Encode key if provided
            kafka_key = None
            if key:
                kafka_key = key.encode('utf-8')
            
            # Publish message
            self.producer.produce(
                topic=topic_name,
                value=message.encode('utf-8'),
                key=kafka_key,
                headers=kafka_headers,
                callback=self._delivery_callback
            )
            
            # Flush to ensure message is sent
            self.producer.flush()
            
            return True
        
        except Exception as e:
            print(f"Error publishing message: {str(e)}")
            return False
    
    def _delivery_callback(self, err, msg):
        """
        Callback function for message delivery reports.
        
        Args:
            err: Error (if any)
            msg: Message that was delivered
        """
        if err:
            print(f"Message delivery failed: {str(err)}")
        else:
            pass  # Message delivered successfully
    
    async def publish_dataframe(self, topic_name: str, df: pd.DataFrame, 
                               key_column: Optional[str] = None) -> int:
        """
        Publish a pandas DataFrame to a Kafka topic, with each row as a separate message.
        
        Args:
            topic_name: Name of the topic to publish to
            df: Pandas DataFrame to publish
            key_column: Optional column to use as message key
            
        Returns:
            Number of messages published
        """
        if not self.is_initialized or not self.producer:
            raise Exception("Kafka provider not initialized")
        
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
        Consume messages from a Kafka topic with a callback function.
        
        Args:
            topic_name: Name of the topic to consume from
            group_id: Consumer group ID
            callback: Callback function to process each message
            max_messages: Maximum number of messages to consume (None for unlimited)
            timeout_ms: Timeout in milliseconds
            
        Returns:
            Number of messages consumed
        """
        if not self.is_initialized:
            raise Exception("Kafka provider not initialized")
        
        try:
            # Create consumer configuration
            consumer_config = {
                'bootstrap.servers': self.bootstrap_servers,
                'group.id': group_id,
                'auto.offset.reset': 'earliest',
                'enable.auto.commit': True
            }
            
            # Add security configuration if provided
            security_protocol = self.config.get('security_protocol', 'PLAINTEXT')
            consumer_config['security.protocol'] = security_protocol
            
            if security_protocol in ['SASL_PLAINTEXT', 'SASL_SSL']:
                sasl_mechanism = self.config.get('sasl_mechanism', 'PLAIN')
                consumer_config['sasl.mechanism'] = sasl_mechanism
                
                if sasl_mechanism in ['PLAIN', 'SCRAM-SHA-256', 'SCRAM-SHA-512']:
                    consumer_config['sasl.username'] = self.config.get('sasl_username', '')
                    consumer_config['sasl.password'] = self.config.get('sasl_password', '')
            
            if security_protocol in ['SSL', 'SASL_SSL']:
                ssl_cafile = self.config.get('ssl_cafile')
                ssl_certfile = self.config.get('ssl_certfile')
                ssl_keyfile = self.config.get('ssl_keyfile')
                
                if ssl_cafile:
                    consumer_config['ssl.ca.location'] = ssl_cafile
                if ssl_certfile:
                    consumer_config['ssl.certificate.location'] = ssl_certfile
                if ssl_keyfile:
                    consumer_config['ssl.key.location'] = ssl_keyfile
            
            # Create consumer
            consumer = Consumer(consumer_config)
            
            # Subscribe to topic
            consumer.subscribe([topic_name])
            
            # Consume messages
            messages_consumed = 0
            running = True
            
            while running:
                # Check if we've reached the maximum number of messages
                if max_messages is not None and messages_consumed >= max_messages:
                    break
                
                # Poll for messages
                msg = consumer.poll(timeout=timeout_ms / 1000.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition, not an error
                        continue
                    else:
                        print(f"Consumer error: {msg.error()}")
                        break
                
                # Process message
                try:
                    # Decode message value
                    value = msg.value().decode('utf-8')
                    
                    # Parse JSON if possible
                    try:
                        data = json.loads(value)
                    except:
                        data = value
                    
                    # Create message object
                    message = {
                        'topic': msg.topic(),
                        'partition': msg.partition(),
                        'offset': msg.offset(),
                        'key': msg.key().decode('utf-8') if msg.key() else None,
                        'value': data,
                        'timestamp': msg.timestamp()[1]
                    }
                    
                    # Add headers if present
                    if msg.headers():
                        message['headers'] = {k: v.decode('utf-8') for k, v in msg.headers()}
                    
                    # Call callback function
                    callback(message)
                    
                    messages_consumed += 1
                    
                except Exception as e:
                    print(f"Error processing message: {str(e)}")
            
            # Close consumer
            consumer.close()
            
            return messages_consumed
        
        except Exception as e:
            print(f"Error consuming messages: {str(e)}")
            raise
    
    async def consume_to_dataframe(self, topic_name: str, group_id: str,
                                  max_messages: int = 1000,
                                  timeout_ms: int = 1000) -> pd.DataFrame:
        """
        Consume messages from a Kafka topic and return as a pandas DataFrame.
        
        Args:
            topic_name: Name of the topic to consume from
            group_id: Consumer group ID
            max_messages: Maximum number of messages to consume
            timeout_ms: Timeout in milliseconds
            
        Returns:
            Pandas DataFrame containing the messages
        """
        if not self.is_initialized:
            raise Exception("Kafka provider not initialized")
        
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
                df['partition'] = [msg['partition'] for msg in messages]
                df['offset'] = [msg['offset'] for msg in messages]
                df['timestamp'] = [msg['timestamp'] for msg in messages]
                df['key'] = [msg['key'] for msg in messages]
                
                return df
            else:
                return pd.DataFrame()
        
        except Exception as e:
            print(f"Error consuming to DataFrame: {str(e)}")
            raise
    
    async def get_topic_info(self, topic_name: str) -> Dict[str, Any]:
        """
        Get information about a Kafka topic.
        
        Args:
            topic_name: Name of the topic
            
        Returns:
            Dictionary containing topic information
        """
        if not self.is_initialized or not self.admin_client:
            raise Exception("Kafka provider not initialized")
        
        try:
            # Get topic metadata
            topics_metadata = self.admin_client.list_topics(topic=topic_name, timeout=10)
            
            # Check if topic exists
            if topic_name not in topics_metadata.topics:
                raise Exception(f"Topic '{topic_name}' not found")
            
            # Get topic metadata
            topic_metadata = topics_metadata.topics[topic_name]
            
            # Get partition information
            partitions = []
            for partition_id, partition_metadata in topic_metadata.partitions.items():
                partitions.append({
                    "id": partition_id,
                    "leader": partition_metadata.leader,
                    "replicas": partition_metadata.replicas,
                    "isrs": partition_metadata.isrs
                })
            
            # Get topic configuration
            config_resource = ConfigResource(ConfigResourceType.TOPIC, topic_name)
            result = self.admin_client.describe_configs([config_resource])
            
            # Wait for operation to complete
            configs = {}
            for resource, future in result.items():
                try:
                    config = future.result()
                    for name, entry in config.items():
                        if not entry.is_default:
                            configs[name] = entry.value
                except Exception as e:
                    print(f"Failed to get topic configuration: {str(e)}")
            
            # Create topic info
            topic_info = {
                "name": topic_name,
                "partitions": partitions,
                "partition_count": len(partitions),
                "configs": configs
            }
            
            return topic_info
        
        except Exception as e:
            print(f"Error getting topic info: {str(e)}")
            raise