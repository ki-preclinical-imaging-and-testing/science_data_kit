"""
Examples for Messaging Providers in Science Data Kit

This module provides examples of how to use the messaging providers in the Science Data Kit,
including Kafka, RabbitMQ, WebSocket, and MQTT providers.
"""

import asyncio
import json
import pandas as pd
from typing import Dict, Any, List

from ...providers.registry import ProviderRegistry
from ...providers.messaging.kafka_provider import KafkaProvider
from ...providers.messaging.rabbitmq_provider import RabbitMQProvider
from ...providers.messaging.websocket_provider import WebSocketProvider
from ...providers.messaging.mqtt_provider import MQTTProvider


async def example_kafka_provider():
    """
    Example of using the Kafka provider.
    
    This example demonstrates how to:
    1. Initialize a Kafka provider
    2. Create a topic
    3. Publish messages to a topic
    4. Consume messages from a topic
    5. Publish a DataFrame to a topic
    6. Consume messages as a DataFrame
    """
    print("\n=== Kafka Provider Example ===")
    
    # Create Kafka provider configuration
    kafka_config = {
        'bootstrap_servers': 'localhost:9092',
        'client_id': 'sdk-kafka-example'
    }
    
    # Create Kafka provider
    kafka_provider = KafkaProvider(kafka_config)
    
    # Initialize provider
    initialized = await kafka_provider.initialize()
    if not initialized:
        print("Failed to initialize Kafka provider. Make sure Kafka is running.")
        return
    
    print("Kafka provider initialized successfully")
    
    # Get provider capabilities
    capabilities = kafka_provider.get_capabilities()
    print(f"Provider capabilities: {capabilities['name']}")
    print(f"Supported features: {', '.join(capabilities['features'])}")
    
    # Create a topic
    topic_name = "sdk-example-topic"
    created = await kafka_provider.create_topic(topic_name, partitions=3, replication_factor=1)
    if created:
        print(f"Created topic: {topic_name}")
    
    # List topics
    topics = await kafka_provider.list_topics()
    print(f"Available topics: {[topic['name'] for topic in topics]}")
    
    # Publish a message
    message = {
        "id": 1,
        "name": "Example Message",
        "value": 42.0,
        "timestamp": "2023-08-02T12:34:56Z"
    }
    published = await kafka_provider.publish_message(topic_name, message, key="example-key")
    if published:
        print(f"Published message to topic: {topic_name}")
    
    # Publish multiple messages
    for i in range(2, 6):
        message = {
            "id": i,
            "name": f"Example Message {i}",
            "value": 42.0 + i,
            "timestamp": "2023-08-02T12:34:56Z"
        }
        await kafka_provider.publish_message(topic_name, message, key=f"example-key-{i}")
    
    print("Published multiple messages")
    
    # Define a callback function for consuming messages
    def process_message(message):
        print(f"Received message: {message['value']}")
    
    # Consume messages
    print("Consuming messages...")
    count = await kafka_provider.consume_messages(
        topic_name=topic_name,
        group_id="sdk-example-group",
        callback=process_message,
        max_messages=5,
        timeout_ms=5000
    )
    print(f"Consumed {count} messages")
    
    # Create a DataFrame
    df = pd.DataFrame([
        {"id": 10, "name": "DataFrame Row 1", "value": 100.0},
        {"id": 11, "name": "DataFrame Row 2", "value": 110.0},
        {"id": 12, "name": "DataFrame Row 3", "value": 120.0},
        {"id": 13, "name": "DataFrame Row 4", "value": 130.0},
        {"id": 14, "name": "DataFrame Row 5", "value": 140.0}
    ])
    
    # Publish DataFrame
    print("Publishing DataFrame...")
    count = await kafka_provider.publish_dataframe(topic_name, df, key_column="id")
    print(f"Published {count} messages from DataFrame")
    
    # Consume to DataFrame
    print("Consuming to DataFrame...")
    result_df = await kafka_provider.consume_to_dataframe(
        topic_name=topic_name,
        group_id="sdk-example-group-2",
        max_messages=5,
        timeout_ms=5000
    )
    
    print("Received DataFrame:")
    print(result_df.head())
    
    # Get topic info
    topic_info = await kafka_provider.get_topic_info(topic_name)
    print(f"Topic info: {topic_info}")
    
    # Delete topic
    deleted = await kafka_provider.delete_topic(topic_name)
    if deleted:
        print(f"Deleted topic: {topic_name}")


async def example_rabbitmq_provider():
    """
    Example of using the RabbitMQ provider.
    
    This example demonstrates how to:
    1. Initialize a RabbitMQ provider
    2. Create an exchange
    3. Publish messages to an exchange
    4. Consume messages from a queue bound to an exchange
    5. Publish a DataFrame to an exchange
    6. Consume messages as a DataFrame
    """
    print("\n=== RabbitMQ Provider Example ===")
    
    # Create RabbitMQ provider configuration
    rabbitmq_config = {
        'host': 'localhost',
        'port': 5672,
        'virtual_host': '/',
        'username': 'guest',
        'password': 'guest'
    }
    
    # Create RabbitMQ provider
    rabbitmq_provider = RabbitMQProvider(rabbitmq_config)
    
    # Initialize provider
    initialized = await rabbitmq_provider.initialize()
    if not initialized:
        print("Failed to initialize RabbitMQ provider. Make sure RabbitMQ is running.")
        return
    
    print("RabbitMQ provider initialized successfully")
    
    # Get provider capabilities
    capabilities = rabbitmq_provider.get_capabilities()
    print(f"Provider capabilities: {capabilities['name']}")
    print(f"Supported features: {', '.join(capabilities['features'])}")
    
    # Create an exchange
    exchange_name = "sdk-example-exchange"
    created = await rabbitmq_provider.create_topic(exchange_name)
    if created:
        print(f"Created exchange: {exchange_name}")
    
    # List exchanges
    exchanges = await rabbitmq_provider.list_topics()
    print(f"Available exchanges: {[exchange['name'] for exchange in exchanges]}")
    
    # Publish a message
    message = {
        "id": 1,
        "name": "Example Message",
        "value": 42.0,
        "timestamp": "2023-08-02T12:34:56Z"
    }
    published = await rabbitmq_provider.publish_message(exchange_name, message, key="example-key")
    if published:
        print(f"Published message to exchange: {exchange_name}")
    
    # Publish multiple messages
    for i in range(2, 6):
        message = {
            "id": i,
            "name": f"Example Message {i}",
            "value": 42.0 + i,
            "timestamp": "2023-08-02T12:34:56Z"
        }
        await rabbitmq_provider.publish_message(exchange_name, message, key=f"example-key-{i}")
    
    print("Published multiple messages")
    
    # Define a callback function for consuming messages
    def process_message(message):
        print(f"Received message: {message['value']}")
    
    # Consume messages
    print("Consuming messages...")
    count = await rabbitmq_provider.consume_messages(
        topic_name=exchange_name,
        group_id="sdk-example-queue",
        callback=process_message,
        max_messages=5,
        timeout_ms=5000
    )
    print(f"Consumed {count} messages")
    
    # Create a DataFrame
    df = pd.DataFrame([
        {"id": 10, "name": "DataFrame Row 1", "value": 100.0},
        {"id": 11, "name": "DataFrame Row 2", "value": 110.0},
        {"id": 12, "name": "DataFrame Row 3", "value": 120.0},
        {"id": 13, "name": "DataFrame Row 4", "value": 130.0},
        {"id": 14, "name": "DataFrame Row 5", "value": 140.0}
    ])
    
    # Publish DataFrame
    print("Publishing DataFrame...")
    count = await rabbitmq_provider.publish_dataframe(exchange_name, df, key_column="id")
    print(f"Published {count} messages from DataFrame")
    
    # Consume to DataFrame
    print("Consuming to DataFrame...")
    result_df = await rabbitmq_provider.consume_to_dataframe(
        topic_name=exchange_name,
        group_id="sdk-example-queue-2",
        max_messages=5,
        timeout_ms=5000
    )
    
    print("Received DataFrame:")
    print(result_df.head())
    
    # Get exchange info
    exchange_info = await rabbitmq_provider.get_topic_info(exchange_name)
    print(f"Exchange info: {exchange_info}")
    
    # Delete exchange
    deleted = await rabbitmq_provider.delete_topic(exchange_name)
    if deleted:
        print(f"Deleted exchange: {exchange_name}")


async def example_websocket_provider():
    """
    Example of using the WebSocket provider.
    
    This example demonstrates how to:
    1. Initialize a WebSocket provider
    2. Create a topic
    3. Publish messages to a topic
    4. Consume messages from a topic
    5. Publish a DataFrame to a topic
    6. Consume messages as a DataFrame
    
    Note: This example requires a WebSocket server running at the specified URL.
    You can use a simple WebSocket echo server for testing.
    """
    print("\n=== WebSocket Provider Example ===")
    
    # Create WebSocket provider configuration
    websocket_config = {
        'url': 'ws://localhost:8765',
        'headers': {
            'User-Agent': 'SDK WebSocket Client'
        }
    }
    
    # Create WebSocket provider
    websocket_provider = WebSocketProvider(websocket_config)
    
    # Initialize provider
    initialized = await websocket_provider.initialize()
    if not initialized:
        print("Failed to initialize WebSocket provider. Make sure a WebSocket server is running.")
        return
    
    print("WebSocket provider initialized successfully")
    
    # Get provider capabilities
    capabilities = websocket_provider.get_capabilities()
    print(f"Provider capabilities: {capabilities['name']}")
    print(f"Supported features: {', '.join(capabilities['features'])}")
    
    # Create a topic
    topic_name = "sdk-example-topic"
    created = await websocket_provider.create_topic(topic_name)
    if created:
        print(f"Created topic: {topic_name}")
    
    # List topics
    topics = await websocket_provider.list_topics()
    print(f"Available topics: {[topic['name'] for topic in topics]}")
    
    # Publish a message
    message = {
        "id": 1,
        "name": "Example Message",
        "value": 42.0,
        "timestamp": "2023-08-02T12:34:56Z"
    }
    published = await websocket_provider.publish_message(topic_name, message, key="example-key")
    if published:
        print(f"Published message to topic: {topic_name}")
    
    # Publish multiple messages
    for i in range(2, 6):
        message = {
            "id": i,
            "name": f"Example Message {i}",
            "value": 42.0 + i,
            "timestamp": "2023-08-02T12:34:56Z"
        }
        await websocket_provider.publish_message(topic_name, message, key=f"example-key-{i}")
    
    print("Published multiple messages")
    
    # Define a callback function for consuming messages
    def process_message(message):
        print(f"Received message: {message['value']}")
    
    # Consume messages
    print("Consuming messages...")
    count = await websocket_provider.consume_messages(
        topic_name=topic_name,
        group_id="sdk-example-group",
        callback=process_message,
        max_messages=5,
        timeout_ms=5000
    )
    print(f"Consumed {count} messages")
    
    # Create a DataFrame
    df = pd.DataFrame([
        {"id": 10, "name": "DataFrame Row 1", "value": 100.0},
        {"id": 11, "name": "DataFrame Row 2", "value": 110.0},
        {"id": 12, "name": "DataFrame Row 3", "value": 120.0},
        {"id": 13, "name": "DataFrame Row 4", "value": 130.0},
        {"id": 14, "name": "DataFrame Row 5", "value": 140.0}
    ])
    
    # Publish DataFrame
    print("Publishing DataFrame...")
    count = await websocket_provider.publish_dataframe(topic_name, df, key_column="id")
    print(f"Published {count} messages from DataFrame")
    
    # Consume to DataFrame
    print("Consuming to DataFrame...")
    result_df = await websocket_provider.consume_to_dataframe(
        topic_name=topic_name,
        group_id="sdk-example-group-2",
        max_messages=5,
        timeout_ms=5000
    )
    
    print("Received DataFrame:")
    print(result_df.head())
    
    # Get topic info
    topic_info = await websocket_provider.get_topic_info(topic_name)
    print(f"Topic info: {topic_info}")
    
    # Delete topic
    deleted = await websocket_provider.delete_topic(topic_name)
    if deleted:
        print(f"Deleted topic: {topic_name}")


async def example_mqtt_provider():
    """
    Example of using the MQTT provider.
    
    This example demonstrates how to:
    1. Initialize an MQTT provider
    2. Create a topic
    3. Publish messages to a topic
    4. Consume messages from a topic
    5. Publish a DataFrame to a topic
    6. Consume messages as a DataFrame
    
    Note: This example requires an MQTT broker running at the specified host and port.
    You can use Mosquitto or another MQTT broker for testing.
    """
    print("\n=== MQTT Provider Example ===")
    
    # Create MQTT provider configuration
    mqtt_config = {
        'host': 'localhost',
        'port': 1883,
        'client_id': 'sdk-mqtt-example',
        'qos': 1,
        'retain': False
    }
    
    # Create MQTT provider
    mqtt_provider = MQTTProvider(mqtt_config)
    
    # Initialize provider
    initialized = await mqtt_provider.initialize()
    if not initialized:
        print("Failed to initialize MQTT provider. Make sure an MQTT broker is running.")
        return
    
    print("MQTT provider initialized successfully")
    
    # Get provider capabilities
    capabilities = mqtt_provider.get_capabilities()
    print(f"Provider capabilities: {capabilities['name']}")
    print(f"Supported features: {', '.join(capabilities['features'])}")
    
    # Create a topic
    topic_name = "sdk/example/topic"
    created = await mqtt_provider.create_topic(topic_name)
    if created:
        print(f"Created topic: {topic_name}")
    
    # List topics
    topics = await mqtt_provider.list_topics()
    print(f"Available topics: {[topic['name'] for topic in topics]}")
    
    # Publish a message
    message = {
        "id": 1,
        "name": "Example Message",
        "value": 42.0,
        "timestamp": "2023-08-02T12:34:56Z"
    }
    published = await mqtt_provider.publish_message(topic_name, message)
    if published:
        print(f"Published message to topic: {topic_name}")
    
    # Publish multiple messages
    for i in range(2, 6):
        message = {
            "id": i,
            "name": f"Example Message {i}",
            "value": 42.0 + i,
            "timestamp": "2023-08-02T12:34:56Z"
        }
        await mqtt_provider.publish_message(topic_name, message)
    
    print("Published multiple messages")
    
    # Define a callback function for consuming messages
    def process_message(message):
        print(f"Received message: {message['value']}")
    
    # Consume messages
    print("Consuming messages...")
    count = await mqtt_provider.consume_messages(
        topic_name=topic_name,
        group_id="sdk-example-group",  # Ignored in MQTT
        callback=process_message,
        max_messages=5,
        timeout_ms=5000
    )
    print(f"Consumed {count} messages")
    
    # Create a DataFrame
    df = pd.DataFrame([
        {"id": 10, "name": "DataFrame Row 1", "value": 100.0},
        {"id": 11, "name": "DataFrame Row 2", "value": 110.0},
        {"id": 12, "name": "DataFrame Row 3", "value": 120.0},
        {"id": 13, "name": "DataFrame Row 4", "value": 130.0},
        {"id": 14, "name": "DataFrame Row 5", "value": 140.0}
    ])
    
    # Publish DataFrame
    print("Publishing DataFrame...")
    count = await mqtt_provider.publish_dataframe(topic_name, df)
    print(f"Published {count} messages from DataFrame")
    
    # Consume to DataFrame
    print("Consuming to DataFrame...")
    result_df = await mqtt_provider.consume_to_dataframe(
        topic_name=topic_name,
        group_id="sdk-example-group-2",  # Ignored in MQTT
        max_messages=5,
        timeout_ms=5000
    )
    
    print("Received DataFrame:")
    print(result_df.head())
    
    # Get topic info
    topic_info = await mqtt_provider.get_topic_info(topic_name)
    print(f"Topic info: {topic_info}")
    
    # Delete topic
    deleted = await mqtt_provider.delete_topic(topic_name)
    if deleted:
        print(f"Deleted topic: {topic_name}")


async def example_provider_registry():
    """
    Example of using the provider registry with messaging providers.
    
    This example demonstrates how to:
    1. Register messaging providers with the provider registry
    2. Get providers by type
    3. Get a specific provider by name
    4. Use a provider from the registry
    """
    print("\n=== Provider Registry Example ===")
    
    # Create provider registry
    registry = ProviderRegistry()
    
    # Create provider configurations
    kafka_config = {
        'bootstrap_servers': 'localhost:9092',
        'client_id': 'sdk-kafka-example'
    }
    
    rabbitmq_config = {
        'host': 'localhost',
        'port': 5672,
        'virtual_host': '/',
        'username': 'guest',
        'password': 'guest'
    }
    
    websocket_config = {
        'url': 'ws://localhost:8765',
        'headers': {
            'User-Agent': 'SDK WebSocket Client'
        }
    }
    
    mqtt_config = {
        'host': 'localhost',
        'port': 1883,
        'client_id': 'sdk-mqtt-example',
        'qos': 1,
        'retain': False
    }
    
    # Create providers
    kafka_provider = KafkaProvider(kafka_config)
    rabbitmq_provider = RabbitMQProvider(rabbitmq_config)
    websocket_provider = WebSocketProvider(websocket_config)
    mqtt_provider = MQTTProvider(mqtt_config)
    
    # Register providers
    registry.register_provider(kafka_provider)
    registry.register_provider(rabbitmq_provider)
    registry.register_provider(websocket_provider)
    registry.register_provider(mqtt_provider)
    
    # Get providers by type
    messaging_providers = registry.get_providers_by_type("messaging")
    print(f"Messaging providers: {[provider.get_capabilities()['name'] for provider in messaging_providers]}")
    
    # Get specific provider by name
    kafka = registry.get_provider("kafka")
    if kafka:
        print(f"Got Kafka provider: {kafka.get_capabilities()['name']}")
    
    # Use provider from registry
    websocket = registry.get_provider("websocket")
    if websocket and await websocket.initialize():
        topic_name = "registry-example-topic"
        await websocket.create_topic(topic_name)
        
        message = {
            "id": 1,
            "name": "Registry Example Message",
            "value": 42.0
        }
        
        published = await websocket.publish_message(topic_name, message)
        if published:
            print(f"Published message using provider from registry")
        
        await websocket.delete_topic(topic_name)


async def run_examples():
    """Run all examples."""
    try:
        # Uncomment the examples you want to run
        # Note: These examples require the respective messaging systems to be running
        
        # await example_kafka_provider()
        # await example_rabbitmq_provider()
        # await example_websocket_provider()
        # await example_mqtt_provider()
        # await example_provider_registry()
        
        print("\nTo run these examples, uncomment the desired examples in the run_examples() function.")
        print("Note that you need to have the respective messaging systems running:")
        print("- Kafka: localhost:9092")
        print("- RabbitMQ: localhost:5672")
        print("- WebSocket server: ws://localhost:8765")
        print("- MQTT broker: localhost:1883")
    except Exception as e:
        print(f"Error running examples: {str(e)}")


if __name__ == "__main__":
    asyncio.run(run_examples())